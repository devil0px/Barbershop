#!/usr/bin/env python3
"""
Simple HTTP server to test Digital Ocean App Platform environment
"""
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'success',
            'message': 'Barbershop server is running!',
            'python_version': sys.version,
            'port': os.environ.get('PORT', 'NOT SET'),
            'cwd': os.getcwd(),
            'path': sys.path[:3]  # First 3 paths only
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())

def main():
    port = int(os.environ.get('PORT', 8000))
    
    print(f"=== SIMPLE SERVER STARTING ===")
    print(f"Python: {sys.version}")
    print(f"Port: {port}")
    print(f"Directory: {os.getcwd()}")
    print(f"Environment PORT: {os.environ.get('PORT', 'NOT SET')}")
    
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Server running on http://0.0.0.0:{port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped")
        server.shutdown()

if __name__ == '__main__':
    main()
