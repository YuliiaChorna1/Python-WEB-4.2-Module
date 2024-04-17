import os
import typing
import logging
import mimetypes
import dataclasses
import http.server
import urllib.parse

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class GoITResponse:
    status: int
    headers: dict
    body: bytes


@dataclasses.dataclass
class GoITRequest:
    client_address: str
    client_port: int
    headers: dict
    args: dict
    body: str


class GoITEnpointExistsException(Exception):
    pass

class GoITHttpHandler(http.server.BaseHTTPRequestHandler):
    def check_methods(self, method: str, path:str, req: GoITRequest) -> GoITResponse | None:
        if self.server.handlers[method].get(path) is None:
            return None
        
        return self.server.handlers[method][path](req)
    
    def check_static(self, path: str) -> GoITResponse | None:
        if path.startswith(f"/{self.server.static_folder}"):
            system_path = path[1:] # public/index.html

            mt = mimetypes.guess_type(system_path)
            if mt:
                headers = {"Content-type": mt[0]}
            else:
                headers = {"Content-type": "text/plain"}
            
            body = None

            if os.path.exists(system_path):
                with open(system_path, mode="rb") as static_file:
                    body = static_file.read()
            
            return GoITResponse(200, headers, body)
        
    def form_error(self, status: int, req: GoITRequest):
        if self.server.handlers["err"].get(str(status)) is None:
            return GoITResponse(
                status,
                {"Content-type": "text/html"},
                f"Sorry have an error {status}".encode()
            )
        
        return self.server.handlers["err"][str(status)](req)
    
    def _process_request(self, method: str):
        pr_url = urllib.parse.urlparse(self.path)

        args = {}
        if (len(pr_url.query)) > 0:
            for query in pr_url.query.split("&"):
                if "=" in query:
                    args[query.split("=")[0]] = query.split("=")[1]
                else:
                    args[query] = None

        # headers = {header[0]: header[1] for header in self.headers._headers}
        headers = dict(self.headers._headers)
        body = None
        if headers.get("Content-Length"):
            body = self.rfile.read(int(headers["Content-Length"]))
            body = urllib.parse.unquote_plus(body.decode())

        req = GoITRequest(*self.client_address, headers, args, body)

        response = self.check_methods(method, pr_url.path, req)
        if not response:
            if method == "get":
                response = self.check_static(pr_url.path)

            if not response:
                response = self.form_error(404, req)

        self.send_response(response.status)
        for key, val in response.headers.items():
            self.send_header(key, val)
        self.end_headers()
        self.wfile.write(response.body)

    def do_GET(self):
        self._process_request("get")

    def do_POST(self):
        self._process_request("post")

class GoITServer(http.server.HTTPServer):

    def __init__(
            self,
            address: tuple[str | bytes | bytearray | int],
            port: int,
            static_folder: str
    ) -> None:
        
        super().__init__((address, port), GoITHttpHandler)

        self.address = address
        self.port = port

        self.static_folder = static_folder
        self.handlers = {
            "get": {},
            "post": {},
            "err": {}
        }

    def serve_forever(self, poll_interval: float = 0.5) -> None:
        logger.info(f"Serving on {self.address}:{self.port}")
        return super().serve_forever(poll_interval)
    
    def __register_method(
        self, method: str, path: str,
        handler: typing.Callable[[GoITRequest], GoITResponse] # 1 арг. - що приймає, 2 арг - що повертає    
    ):
        logger.info(f"Registred handler {handler} for method '{method} {path}'")

        if path in self.handlers[method].keys():
            raise GoITEnpointExistsException(f"{method} {path}")
        
        self.handlers[method][path] = handler

        return handler
    
    def err(self, status: str):
        return lambda handler: self.__register_method("err", status, handler)
    
    def get(self, path: str):
        return lambda handler: self.__register_method("get", path, handler)
    
    def post(self, path: str):
        return lambda handler: self.__register_method("post", path, handler)

