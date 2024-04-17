import json
import socket
import pathlib
import logging
import mimetypes
import urllib.parse
from threading import Thread
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler


SOCKET_PORT = 5000
SOCKET_IP = "127.0.0.1"


logger = logging.getLogger()
stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(processName)s %(lineno)s %(message)s")

stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        logger.debug(data)
       
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()
        self.save_to_socket_server(data)

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def save_to_socket_server(self, data):
        socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server = SOCKET_IP, SOCKET_PORT
        socket_UDP.sendto(data, server)
        socket_UDP.close()


def run_http_server():
    server_address = ("0.0.0.0", 3000)
    http = HTTPServer(server_address, HttpHandler)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

def run_socket_server():
    server_address = (SOCKET_IP, SOCKET_PORT)
    socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_UDP.bind(server_address)
    try:
        while True:
            data, address = socket_UDP.recvfrom(1024)
            if data:
                data_parse = urllib.parse.unquote_plus(data.decode())
                logger.debug(data_parse)
                data_dict = {key: value for key, value in [el.split("=") for el in data_parse.split("&")]}
                json_dict = dict()
                            
                with open("storage/data.json", "r") as file:
                    json_dict.update(json.loads(file.read()) or {})
                with open("storage/data.json", "w") as file:
                    json_dict[str(datetime.now())] = data_dict
                    json.dump(json_dict, file)
                    
    except KeyboardInterrupt:
        socket_UDP.close()

if __name__ == '__main__':
    thread_1 = Thread(target=run_http_server, daemon=True)
    thread_2 = Thread(target=run_socket_server, daemon=True)

    thread_1.start()
    thread_2.start()

    thread_1.join()
    thread_2.join()
