from dotenv import load_dotenv
from langfuse import get_client, observe


load_dotenv()


langfuse = get_client()


@observe(
    name="travelmate-test-trace",
    as_type="agent"
)
def test_trace():

    print("\nInside TravelMate test trace...")

    return {
        "status": "success",
        "message": "Langfuse telemetry test completed."
    }


print("\n")
print("=" * 60)
print("       TRAVELMATE AI - LANGFUSE TRACE TEST")
print("=" * 60)


print("\nStarting test trace...")

result = test_trace()

print("\nTrace result:")
print(result)


print("\nFlushing telemetry to Langfuse...")

langfuse.flush()

print("\nTelemetry flushed successfully.")


print("\n")
print("=" * 60)
print("              TEST COMPLETE")
print("=" * 60)