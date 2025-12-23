from genlm.control.potential.base import Potential
import ast
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

class LSP(Potential):
    def __init__(
        self,
        lsp_command: list[str],
    ):
        super().__init__(vocabulary=list(range(256)))
        self.lsp_command = lsp_command
        self.lsp_process = None
        self.request_id = 1
        self.stderr_task = None
        logger.info(
            f"LSPPotential initialized with command: {self.lsp_command}"
        )

    async def _read_stderr(self):
        """Reads from the LSP server's stderr and logs it."""
        while (
            self.lsp_process
            and self.lsp_process.stderr
            and not self.lsp_process.stderr.at_eof()
        ):
            try:
                line = await self.lsp_process.stderr.readline()
                if line:
                    logger.error(f"[LSP stderr] {line.decode().strip()}")
            except Exception as e:
                logger.error(f"Error reading LSP stderr: {e}")
                break

    async def _lint(self, code: str) -> float:
        """Helper method to initialize server if needed and get diagnostics."""
        if not self.lsp_process or self.lsp_process.returncode is not None:
            await self.initialize_server()

        diagnostics = await self.get_diagnostics(code)
        for d in diagnostics:
            if d.get("severity") == 1:  # 1 is for Error
                logger.warning(f"LSP Error found: {d['message']}")
                return float("-inf")  # Penalize heavily

        return 0.0  # No errors found

    async def start_server(
        self,
    ):
        """Starts the LSP server as a subprocess."""

        if self.lsp_process and self.lsp_process.returncode is None:
            logger.info("LSP server already running.")
            return

        try:
            logger.info(
                f"Starting LSP server with command: {' '.join(self.lsp_command)}"
            )
            self.lsp_process = await asyncio.create_subprocess_exec(
                *self.lsp_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            logger.info(f"LSP server started with PID: {self.lsp_process.pid}")
            self.stderr_task = asyncio.create_task(self._read_stderr())
        except FileNotFoundError:
            logger.error(
                f"LSP command not found: {self.lsp_command[0]}. Please ensure it's installed and in your PATH."
            )
            raise
        except Exception as e:
            logger.error(f"Failed to start LSP server: {e}")
            raise

    async def _send_message(
        self,
        message: dict,
    ):
        if not self.lsp_process or not self.lsp_process.stdin:
            raise ConnectionError("LSP server is not running.")

        json_message = json.dumps(message)
        body = json_message.encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
        self.lsp_process.stdin.write(header + body)
        await self.lsp_process.stdin.drain()
        logger.debug(f"Sent: {json_message}")

    async def _read_message(
        self,
    ) -> dict:
        if not self.lsp_process or not self.lsp_process.stdout:
            raise ConnectionError("LSP server is not running.")
        header_bytes = await self.lsp_process.stdout.readuntil(b"\r\n\r\n")
        header = header_bytes.decode("utf-8")
        content_length_str = header.strip().split(": ")[1]
        content_length = int(content_length_str)
        body_bytes = await self.lsp_process.stdout.readexactly(content_length)
        body = body_bytes.decode("utf-8")
        logger.debug(f"Received: {body}")
        return json.loads(body)

    async def initialize_server(
        self,
    ):
        await self.start_server()
        init_request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "initialize",
            "params": {
                "processId": None,
                "rootUri": None,
                "capabilities": {},
            },
        }
        await self._send_message(init_request)
        self.request_id += 1
        response = await self._read_message()
        if "error" in response:
            raise RuntimeError(
                f"LSP server failed to initialize: {response['error']}"
            )
        logger.info("Server initialized successfully.")
        await self._send_message(
            {
                "jsonrpc": "2.0",
                "method": "initialized",
                "params": {},
            }
        )
        logger.info("Sent 'initialized' notification.")

    async def get_diagnostics(
        self,
        code: str,
    ) -> list:
        doc_uri = "file:///temp_file.py"

        open_notification = {
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {
                "textDocument": {
                    "uri": doc_uri,
                    "languageId": "python",
                    "version": 1,
                    "text": code,
                }
            },
        }
        await self._send_message(open_notification)

        try:
            while True:
                message = await asyncio.wait_for(
                    self._read_message(), timeout=2.0
                )
                # Check if the message is the diagnostic notification we're waiting for
                if message.get("method") == "textDocument/publishDiagnostics":
                    if message["params"]["uri"] == doc_uri:
                        logger.info(
                            f"Received diagnostics for {doc_uri}: {message['params']['diagnostics']}"
                        )
                        # We got them! Return the diagnostics
                        return message["params"]["diagnostics"]
                    else:
                        logger.debug(
                            f"Ignoring diagnostics for other document: {message['params']['uri']}"
                        )
                else:
                    logger.debug(f"Ignoring LSP message: {message}")
        except asyncio.TimeoutError:
            logger.warning(f"Timed out waiting for diagnostics for {doc_uri}")
            return []

    async def prefix(
        self,
        context,
    ):
        try:
            code = context.decode("utf-8")
        except UnicodeDecodeError:
            return float("-inf")
        try:
            ast.parse(code)
        except (
            SyntaxError,
            IndentationError,
        ):
            return 0.0
        return await self._lint(code)

    async def complete(
        self,
        context,
    ):

        # The 'complete' method should lint the final output.
        # Its logic is very similar to 'prefix' but it doesn't need the ast.parse check.
        try:
            code = context.decode("utf-8")
        except UnicodeDecodeError:
            return float("-inf")
        if not self.lsp_process or self.lsp_process.returncode is not None:
            await self.initialize_server()
        return await self._lint(code)

    async def close(
        self,
    ):
        if not self.lsp_process or self.lsp_process.returncode is not None:
            return
        shutdown_req = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "shutdown",
        }
        await self._send_message(shutdown_req)
        await self._read_message()  # Wait for shutdown response

        await self._send_message(
            {
                "jsonrpc": "2.0",
                "method": "exit",
            }
        )

        if self.stderr_task:
            self.stderr_task.cancel()
        try:
            await self.stderr_task
        except asyncio.CancelledError:
            pass

        await self.lsp_process.wait()
        logger.info("LSP server shut down gracefully.")
        self.lsp_process = None

    def __repr__(
        self,
    ):
        return f"LSP(lsp_command={self.lsp_command})"

    def spawn(
        self,
    ):
        return LSP(self.lsp_command)

    # Get the correct diagnostics info that you want --------- linter error message

    async def diagnostic_messages(self, code: str):
            """
            Return normalized diagnostics with message, severity score,
            and code range.
            """

            if isinstance(code, bytes):
                code = code.decode("utf-8", errors="replace")

            if not self.lsp_process or self.lsp_process.returncode is not None:
                await self.initialize_server()

            raw_diagnostics = await self.get_diagnostics(code)

            normalized = []

            for d in raw_diagnostics:
                severity = d.get("severity", 3)

                normalized.append({
                    "message": d.get("message", "No error found"),
                    "severity": severity,
                    "range": {
                        "start": {
                            "line": d["range"]["start"]["line"],
                            "character": d["range"]["start"]["character"],
                        },
                        "end": {
                            "line": d["range"]["end"]["line"],
                            "character": d["range"]["end"]["character"],
                        },
                    }
                })

            return normalized
