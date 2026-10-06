from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    RemoveMessage,
)

from app.state import AgentState


MAX_MESSAGES = 10
SUMMARY_COUNT = 8
MAX_TOOL_RESULTS = 5


def format_messages_for_summary(messages):
    """Convert messages into readable text."""

    formatted = []

    for message in messages:
        if isinstance(message, HumanMessage):
            role = "User"
        elif isinstance(message, AIMessage):
            role = "Assistant"
        elif isinstance(message, SystemMessage):
            role = "System"
        else:
            role = "Message"

        formatted.append(f"{role}: {message.content}")

    return "\n".join(formatted)


def summarize_messages(messages):
    """
    Temporary deterministic summarizer for testing.

    We will replace this with the offline LLM once
    the compaction mechanism is verified.
    """

    conversation_text = format_messages_for_summary(messages)

    return (
        "The earlier travel conversation covered the following: "
        + conversation_text.replace("\n", " ")
    )


def context_manager_node(state: AgentState) -> dict:

    messages = state.get("messages", [])

    print("\n========== CONTEXT MANAGER ==========\n")
    print("Messages before compaction:", len(messages))

    # ---------------------------------------------------------
    # CONTEXT COMPACTION
    # ---------------------------------------------------------

    if len(messages) > MAX_MESSAGES:

        messages_to_summarize = messages[:SUMMARY_COUNT]

        print(
            f"More than {MAX_MESSAGES} messages detected."
        )

        print(
            f"Summarizing first {SUMMARY_COUNT} messages..."
        )

        summary = summarize_messages(
            messages_to_summarize
        )

        print("\nGenerated summary:")
        print(summary)

        # Remove the original first 8 messages.
        remove_messages = [
            RemoveMessage(id=message.id)
            for message in messages_to_summarize
        ]

        # Add the summary as one message.
        summary_message = SystemMessage(
            content=f"Conversation summary: {summary}"
        )

        updated_messages = (
            remove_messages
            + [summary_message]
        )

        print(
            f"\nRemoved {len(messages_to_summarize)} old messages."
        )

        print("Inserted 1 summary message.")

        print(
            f"Recent messages retained: "
            f"{len(messages) - SUMMARY_COUNT}"
        )

        print(
            "\nContext compaction completed."
        )

        print(
            "=====================================\n"
        )

        return {
            "messages": updated_messages,
            "step_count": state["step_count"] + 1,
        }

    # ---------------------------------------------------------
    # NO COMPACTION
    # ---------------------------------------------------------

    print("No context compaction required.")

    print(
        f"Messages retained: {len(messages)}"
    )

    print(
        "=====================================\n"
    )

    return {
        "step_count": state["step_count"] + 1,
    }