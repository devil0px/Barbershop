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
    print(f"=== SIMPLE SERVER STARTING ===", flush=True)
    print(f"Python executable: {sys.executable}", flush=True)
    print(f"Python version: {sys.version}", flush=True)
    print(f"Current directory: {os.getcwd()}", flush=True)
    print(f"Files in current directory: {os.listdir('.')}", flush=True)
    
    # Check environment variables
    port_env = os.environ.get('PORT')
    print(f"Environment PORT variable: {port_env}", flush=True)
    print(f"All environment variables: {dict(os.environ)}", flush=True)
    
    try:
        port = int(port_env) if port_env else 8000
        print(f"Using port: {port}", flush=True)
    except (ValueError, TypeError) as e:
        print(f"Error parsing PORT: {e}", flush=True)
        port = 8000
        print(f"Falling back to default port: {port}", flush=True)
    
    try:
        print(f"Creating HTTPServer on 0.0.0.0:{port}", flush=True)
        server = HTTPServer(('0.0.0.0', port), SimpleHandler)
        print(f"HTTPServer created successfully", flush=True)
        print(f"Server address: {server.server_address}", flush=True)
        print(f"Starting server...", flush=True)
        server.serve_forever()
    except Exception as e:
        print(f"Server error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return 1
    except KeyboardInterrupt:
        print("Server stopped by KeyboardInterrupt", flush=True)
        server.shutdown()
        return 0

if __name__ == '__main__':
    main()
