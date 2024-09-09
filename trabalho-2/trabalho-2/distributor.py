from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)

        # Set the headers
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        # Write the response content
        self.wfile.write(b"OK")


# Define the server address and port
server_address = ("", 5000)  # Listen on all IPs, port 8000

# Create the HTTP server
httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)

# Start the server
print("Serving on port 5000...")
httpd.serve_forever()
