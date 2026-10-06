"""
TravelMate AI - Task 9A
LLM-as-a-Judge Evaluation

This script:
1. Fetches historical Langfuse observations.
2. Groups them into unique traces.
3. Selects up to 10 historical traces.
4. Sends the traces to an LLM judge.
5. Scores Error Recovery from 1-5.
6. Writes the scores back to Langfuse.
"""

import json
import os
import re
from collections import defaultdict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse import Langfuse


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY is not configured in the .env file."
    )


# ============================================================
# LANGFUSE CLIENT
# ============================================================

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_BASE_URL"),
)


# ============================================================
# CONFIGURATION
# ============================================================

# IMPORTANT:
# gemini-2.5-flash previously hit the 20 requests/day quota.
#
# We are using the Gemini model that successfully worked
# for the TravelMate trace generation.
JUDGE_MODEL = "gemini-3.5-flash-lite"

MAX_TRACES = 10


# ============================================================
# HISTORICAL TRACE FETCH
# ============================================================

def fetch_historical_traces(limit: int = 100):
    """
    Fetch historical Langfuse observations and group them by trace ID.
    """

    print("\n" + "=" * 60)
    print("       TRAVELMATE AI - HISTORICAL TRACE FETCH")
    print("=" * 60)

    print("\nFetching historical observations from Langfuse...")

    observations = langfuse.api.observations.get_many(
        limit=limit,
        fields="core,basic,io",
    )

    observation_items = getattr(observations, "data", observations)

    print(f"Retrieved {len(observation_items)} observations.")

    traces = defaultdict(list)

    for observation in observation_items:

        trace_id = getattr(observation, "trace_id", None)

        if not trace_id:
            continue

        traces[trace_id].append(observation)

    print(f"Found {len(traces)} unique historical traces.")

    return traces


# ============================================================
# OBSERVATION SERIALIZATION
# ============================================================

def observation_to_dict(observation):
    """
    Convert a Langfuse observation into a compact JSON-safe object.
    """

    def get_value(name, default=None):
        value = getattr(observation, name, default)

        if value is None:
            return default

        return value

    return {
        "id": get_value("id"),
        "trace_id": get_value("trace_id"),
        "type": get_value("type"),
        "name": get_value("name"),
        "input": get_value("input"),
        "output": get_value("output"),
        "metadata": get_value("metadata"),
        "start_time": str(get_value("start_time"))
        if get_value("start_time")
        else None,
        "end_time": str(get_value("end_time"))
        if get_value("end_time")
        else None,
    }


# ============================================================
# TRACE PREPARATION
# ============================================================

def prepare_traces(traces, max_traces=10):
    """
    Select the latest traces and convert them into compact
    JSON-safe structures for the LLM judge.
    """

    trace_items = []

    for trace_id, observations in traces.items():

        serialized_observations = [
            observation_to_dict(obs)
            for obs in observations
        ]

        trace_items.append(
            {
                "trace_id": trace_id,
                "observations": serialized_observations,
            }
        )

    # Sort approximately by the latest observation timestamp.
    trace_items.sort(
        key=lambda trace: (
            trace["observations"][-1].get("end_time")
            or trace["observations"][-1].get("start_time")
            or ""
        ),
        reverse=True,
    )

    selected = trace_items[:max_traces]

    print(f"\nSelected the latest {len(selected)} traces.")

    return selected


# ============================================================
# COMPACT TRACE FORMAT
# ============================================================

def compact_trace(trace):
    """
    Reduce the amount of data sent to the judge.

    This is important because Langfuse traces can contain
    large inputs/outputs.
    """

    compact_observations = []

    for observation in trace["observations"]:

        input_value = observation.get("input")
        output_value = observation.get("output")

        if isinstance(input_value, (dict, list)):
            input_value = json.dumps(
                input_value,
                ensure_ascii=False,
                default=str,
            )

        if isinstance(output_value, (dict, list)):
            output_value = json.dumps(
                output_value,
                ensure_ascii=False,
                default=str,
            )

        compact_observations.append(
            {
                "type": observation.get("type"),
                "name": observation.get("name"),
                "input": str(input_value)[:3000],
                "output": str(output_value)[:3000],
            }
        )

    return {
        "trace_id": trace["trace_id"],
        "observations": compact_observations,
    }


# ============================================================
# JUDGE PROMPT
# ============================================================

def build_judge_prompt(traces):
    """
    Build the LLM-as-a-Judge prompt.
    """

    compact_traces = [
        compact_trace(trace)
        for trace in traces
    ]

    traces_json = json.dumps(
        compact_traces,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

    prompt = f"""
You are an expert evaluator for an AI travel planning and
booking agent called TravelMate-AI.

You are evaluating historical execution traces.

Your task is to evaluate ONLY the criterion:

ERROR RECOVERY

Evaluate how well the agent handles tool failures, invalid
tool requests, API errors, missing information, or other
execution problems.

Use this scoring rubric:

1 = Very poor error recovery
    - Agent fails completely.
    - Does not recover from errors.
    - Produces an incorrect or unusable result.

2 = Poor error recovery
    - Agent notices some problems but recovery is weak.
    - Requires significant intervention.

3 = Acceptable error recovery
    - Agent recognizes errors.
    - Makes a reasonable attempt to recover.
    - Recovery may be incomplete.

4 = Good error recovery
    - Agent correctly identifies errors.
    - Adapts its next action appropriately.
    - Successfully continues in most cases.

5 = Excellent error recovery
    - Agent detects errors quickly.
    - Corrects the tool request or reasoning.
    - Continues successfully with minimal disruption.

IMPORTANT:

Return ONLY valid JSON.

The JSON must have this structure:

{{
  "evaluations": [
    {{
      "trace_id": "trace-id",
      "error_recovery": 1,
      "reason": "short explanation"
    }}
  ]
}}

The "error_recovery" value MUST be an integer from 1 to 5.

Evaluate every trace.

Here are the historical traces:

{traces_json}
"""

    return prompt


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text):
    """
    Extract JSON from an LLM response.

    Handles responses wrapped in markdown code fences.
    """

    if not isinstance(text, str):
        text = str(text)

    text = text.strip()

    # Remove markdown fences.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Try direct JSON parsing first.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find the first JSON object.
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        candidate = text[start : end + 1]

        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    raise ValueError(
        "Could not extract valid JSON from judge response."
    )


# ============================================================
# LLM JUDGE
# ============================================================

def run_llm_judge(prompt):
    """
    Run the LLM-as-a-Judge.

    Uses gemini-3.5-flash-lite instead of the exhausted
    gemini-2.5-flash model.
    """

    print("\n" + "=" * 60)
    print("                 LLM-AS-A-JUDGE")
    print("=" * 60)

    print(f"\nJudge model: {JUDGE_MODEL}")
    print("Sending historical traces to the judge...")

    model = ChatGoogleGenerativeAI(
        model=JUDGE_MODEL,
        temperature=0,
        google_api_key=GOOGLE_API_KEY,
        max_retries=1,
    )

    response = model.invoke(prompt)

    content = response.content

    # Gemini can return either a string or a list of
    # structured content blocks.
    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, dict):

                text = item.get("text")

                if text:
                    text_parts.append(str(text))

            elif isinstance(item, str):

                text_parts.append(item)

            elif hasattr(item, "text"):

                text = getattr(item, "text", None)

                if text:
                    text_parts.append(str(text))

        raw_response = "\n".join(text_parts)

    else:

        raw_response = str(content)

    print("\nJudge response received.")

    return raw_response


# ============================================================
# VALIDATE EVALUATION
# ============================================================

def validate_evaluations(result, selected_traces):
    """
    Validate the judge output before writing scores.
    """

    if not isinstance(result, dict):
        raise ValueError(
            "Judge response is not a JSON object."
        )

    evaluations = result.get("evaluations")

    if not isinstance(evaluations, list):
        raise ValueError(
            "Judge response does not contain an 'evaluations' list."
        )

    expected_trace_ids = {
        trace["trace_id"]
        for trace in selected_traces
    }

    received_trace_ids = set()

    for evaluation in evaluations:

        trace_id = evaluation.get("trace_id")
        score = evaluation.get("error_recovery")

        if not trace_id:
            raise ValueError(
                "Evaluation is missing trace_id."
            )

        if trace_id not in expected_trace_ids:
            raise ValueError(
                f"Unknown trace ID returned by judge: {trace_id}"
            )

        if not isinstance(score, int):
            raise ValueError(
                f"Score for {trace_id} is not an integer."
            )

        if score < 1 or score > 5:
            raise ValueError(
                f"Invalid Error Recovery score for "
                f"{trace_id}: {score}"
            )

        received_trace_ids.add(trace_id)

    missing = expected_trace_ids - received_trace_ids

    if missing:
        print(
            "\nWARNING: Judge did not evaluate these traces:"
        )

        for trace_id in missing:
            print(" -", trace_id)

    return evaluations


# ============================================================
# WRITE SCORES TO LANGFUSE
# ============================================================

def write_scores(evaluations):
    """
    Write Error Recovery scores back to Langfuse.
    """

    print("\n" + "=" * 60)
    print("              WRITING SCORES")
    print("=" * 60)

    successful = 0
    failed = 0

    for evaluation in evaluations:

        trace_id = evaluation["trace_id"]
        score = evaluation["error_recovery"]
        reason = evaluation.get("reason", "")

        print(
            f"\nTrace: {trace_id}"
        )

        print(
            f"Error Recovery: {score}/5"
        )

        print(
            f"Reason: {reason}"
        )

        try:

            langfuse.create_score(
                name="error_recovery",
                value=score,
                trace_id=trace_id,
                comment=reason,
            )

            successful += 1

        except Exception as e:

            print(
                f"Failed to write score: {e}"
            )

            failed += 1

    print("\nScores written successfully:", successful)
    print("Scores failed:", failed)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 60)
    print("       TRAVELMATE AI - TASK 9A")
    print("       LLM-AS-A-JUDGE EVALUATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Fetch historical traces
    # --------------------------------------------------------

    traces = fetch_historical_traces()

    if not traces:
        print(
            "\nERROR: No historical traces were found."
        )
        return

    # --------------------------------------------------------
    # 2. Select latest 10 traces
    # --------------------------------------------------------

    selected_traces = prepare_traces(
        traces,
        max_traces=MAX_TRACES,
    )

    if len(selected_traces) < MAX_TRACES:

        print(
            f"\nWARNING: Only {len(selected_traces)} "
            f"historical traces are available."
        )

    print(
        f"\nPrepared {len(selected_traces)} traces "
        "for evaluation."
    )

    # --------------------------------------------------------
    # 3. Build judge prompt
    # --------------------------------------------------------

    prompt = build_judge_prompt(
        selected_traces
    )

    # --------------------------------------------------------
    # 4. Run LLM judge
    # --------------------------------------------------------

    try:

        raw_response = run_llm_judge(
            prompt
        )

    except Exception as e:

        print("\n" + "=" * 60)
        print("                 JUDGE FAILED")
        print("=" * 60)

        print(
            f"\nError: {e}"
        )

        print(
            "\nThe historical trace collection succeeded, "
            "but the LLM judge could not be executed."
        )

        return

    # --------------------------------------------------------
    # 5. Parse JSON
    # --------------------------------------------------------

    print("\nParsing judge response...")

    try:

        result = extract_json(
            raw_response
        )

    except Exception as e:

        print(
            "\nERROR: Failed to parse judge response."
        )

        print(
            "Parser error:",
            e,
        )

        print(
            "\nRaw judge response:"
        )

        print(raw_response)

        return

    # --------------------------------------------------------
    # 6. Validate
    # --------------------------------------------------------

    print("Validating evaluation results...")

    try:

        evaluations = validate_evaluations(
            result,
            selected_traces,
        )

    except Exception as e:

        print(
            "\nERROR: Invalid judge output."
        )

        print(
            "Validation error:",
            e,
        )

        print(
            "\nParsed result:"
        )

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
                default=str,
            )
        )

        return

    # --------------------------------------------------------
    # 7. Display results
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("              EVALUATION RESULTS")
    print("=" * 60)

    for evaluation in evaluations:

        print(
            f"\nTrace: {evaluation['trace_id']}"
        )

        print(
            f"Error Recovery: "
            f"{evaluation['error_recovery']}/5"
        )

        print(
            f"Reason: "
            f"{evaluation.get('reason', '')}"
        )

    # --------------------------------------------------------
    # 8. Write scores to Langfuse
    # --------------------------------------------------------

    write_scores(
        evaluations
    )

    # --------------------------------------------------------
    # 9. Flush Langfuse
    # --------------------------------------------------------

    try:

        langfuse.flush()

    except Exception:
        pass

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("          TASK 9A EVALUATION COMPLETE")
    print("=" * 60)

    print(
        "\nHistorical traces evaluated:",
        len(evaluations),
    )

    print(
        "\nEvaluation criterion:"
    )

    print(
        "Error Recovery: 1-5"
    )

    print(
        "\nScores have been submitted to Langfuse."
    )

    print(
        "\nNext step:"
    )

    print(
        "Task 9B - Docker + Render deployment"
    )


if __name__ == "__main__":
    main()