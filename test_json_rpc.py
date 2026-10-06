import json

from app.json_rpc import handle_json_rpc
from app.tools.json_rpc_tools import router


print("\n")
print("=" * 60)
print("       TRAVELMATE AI - JSON-RPC TEST")
print("=" * 60)


# ============================================================
# TEST 1 — TOOL DISCOVERY
# ============================================================

print("\n")
print("TEST 1: JSON-RPC tools/list")

list_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
}


list_response = handle_json_rpc(
    json.dumps(list_request),
    router
)

print("\nRequest:")
print(json.dumps(
    list_request,
    indent=2
))

print("\nResponse:")
print(json.dumps(
    json.loads(list_response),
    indent=2
))


# ============================================================
# TEST 2 — TOOL EXECUTION
# ============================================================

print("\n")
print("TEST 2: JSON-RPC tools/call")

call_request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "search_flights",
        "arguments": {
            "origin": "Delhi",
            "destination": "Goa",
            "date": "2026-11-10",
            "passengers": 2
        }
    }
}


call_response = handle_json_rpc(
    json.dumps(call_request),
    router
)

print("\nRequest:")
print(json.dumps(
    call_request,
    indent=2
))

print("\nResponse:")
print(json.dumps(
    json.loads(call_response),
    indent=2
))


# ============================================================
# TEST 3 — UNKNOWN TOOL
# ============================================================

print("\n")
print("TEST 3: Unknown tool")

invalid_request = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "unknown_tool",
        "arguments": {}
    }
}


invalid_response = handle_json_rpc(
    json.dumps(invalid_request),
    router
)

print("\nResponse:")
print(json.dumps(
    json.loads(invalid_response),
    indent=2
))


print("\n")
print("=" * 60)
print("             TEST COMPLETE")
print("=" * 60)