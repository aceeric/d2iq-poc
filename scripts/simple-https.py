import http.server
import ssl
import tempfile
import subprocess
import socket
import datetime

# echos datetime and hostname

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(str(datetime.datetime.now()) + " -- " + socket.gethostname() + "\n", "utf8"))

with tempfile.TemporaryDirectory() as tmpdir_name:
    subprocess.run(["openssl", "req", "-new", "-x509", "-keyout", tmpdir_name + "/server.pem", "-out", tmpdir_name + "/server.pem", "-days", "365", "-nodes", "-subj", "/CN=frobozz"])
    server_address = ('0.0.0.0', 443)
    httpd = http.server.HTTPServer(server_address, MyHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   server_side=True,
                                   certfile=tmpdir_name + "/server.pem",
                                   ssl_version=ssl.PROTOCOL_TLS)
    httpd.serve_forever()
