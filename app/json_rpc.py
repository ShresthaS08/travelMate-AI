import json
from typing import Any, Callable


# ============================================================
# JSON-RPC 2.0 ERROR CODES
# ============================================================

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


# ============================================================
# JSON-RPC TOOL ROUTER
# ============================================================

class JSONRPCToolRouter:
    """
    Simple JSON-RPC 2.0 router for TravelMate tools.

    Receives JSON-RPC requests and routes them to
    registered Python functions.
    """

    def __init__(self):

        self.tools: dict[str, Callable] = {}

    # ========================================================
    # TOOL REGISTRATION
    # ========================================================

    def register_tool(
        self,
        name: str,
        function: Callable
    ):
        """
        Register a Python function as a JSON-RPC tool.
        """

        self.tools[name] = function

    # ========================================================
    # TOOL DISCOVERY
    # ========================================================

    def list_tools(self) -> list[dict]:
        """
        Return the tools available to the JSON-RPC router.
        """

        return [
            {
                "name": name,
                "description": function.__doc__ or "",
            }
            for name, function in self.tools.items()
        ]

    # ========================================================
    # REQUEST HANDLING
    # ========================================================

    def handle_request(
        self,
        request: dict
    ) -> dict:

        # ----------------------------------------------------
        # Validate JSON-RPC version
        # ----------------------------------------------------

        if request.get("jsonrpc") != "2.0":

            return self._error_response(
                request.get("id"),
                INVALID_REQUEST,
                "Invalid JSON-RPC request."
            )

        # ----------------------------------------------------
        # Validate method
        # ----------------------------------------------------

        method = request.get("method")

        if not isinstance(method, str):

            return self._error_response(
                request.get("id"),
                INVALID_REQUEST,
                "Method must be a string."
            )

        # ----------------------------------------------------
        # Tool discovery
        # ----------------------------------------------------

        if method == "tools/list":

            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "tools": self.list_tools()
                }
            }

        # ----------------------------------------------------
        # Tool execution
        # ----------------------------------------------------

        if method == "tools/call":

            params = request.get("params", {})

            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if not tool_name:

                return self._error_response(
                    request.get("id"),
                    INVALID_PARAMS,
                    "Tool name is required."
                )

            if tool_name not in self.tools:

                return self._error_response(
                    request.get("id"),
                    METHOD_NOT_FOUND,
                    f"Tool '{tool_name}' not found."
                )

            if not isinstance(arguments, dict):

                return self._error_response(
                    request.get("id"),
                    INVALID_PARAMS,
                    "Tool arguments must be an object."
                )

            # ------------------------------------------------
            # Execute Python function
            # ------------------------------------------------

            try:

                function = self.tools[tool_name]

                result = function(**arguments)

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": result
                    }
                }

            except TypeError as e:

                return self._error_response(
                    request.get("id"),
                    INVALID_PARAMS,
                    str(e)
                )

            except Exception as e:

                return self._error_response(
                    request.get("id"),
                    INTERNAL_ERROR,
                    str(e)
                )

        # ----------------------------------------------------
        # Unknown method
        # ----------------------------------------------------

        return self._error_response(
            request.get("id"),
            METHOD_NOT_FOUND,
            f"Method '{method}' not found."
        )

    # ========================================================
    # ERROR RESPONSE
    # ========================================================

    @staticmethod
    def _error_response(
        request_id: Any,
        code: int,
        message: str
    ) -> dict:

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }


# ============================================================
# JSON STRING HANDLER
# ============================================================

def handle_json_rpc(
    request_json: str,
    router: JSONRPCToolRouter
) -> str:
    """
    Parse a JSON-RPC request string, execute it,
    and return a JSON-RPC response string.
    """

    try:

        request = json.loads(request_json)

    except json.JSONDecodeError:

        response = router._error_response(
            None,
            PARSE_ERROR,
            "Invalid JSON."
        )

        return json.dumps(response)

    response = router.handle_request(request)

    return json.dumps(response)