from dotenv import load_dotenv
from langfuse import get_client


load_dotenv()


print("\n")
print("=" * 60)
print("          TRAVELMATE AI - LANGFUSE TEST")
print("=" * 60)

print("\nInitializing Langfuse client...")

langfuse = get_client()


print("\nChecking Langfuse authentication...")

if langfuse.auth_check():
    print("\nLangfuse authentication successful.")
else:
    print("\nLangfuse authentication failed.")


print("\n")
print("=" * 60)
print("              TEST COMPLETE")
print("=" * 60)