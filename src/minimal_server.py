#!/usr/bin/env python3
import os
import sys

def main():
    print("MINIMAL SERVER STARTING", flush=True)
    
    # Get port
    port = os.environ.get('PORT', '8000')
    print(f"PORT from env: {port}", flush=True)
    
    try:
        port_int = int(port)
        print(f"Port converted to int: {port_int}", flush=True)
    except:
        print("Failed to convert port to int", flush=True)
        port_int = 8000
    
    # Simple socket server
    import socket
    
    try:
        print("Creating socket", flush=True)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        print(f"Binding to 0.0.0.0:{port_int}", flush=True)
        sock.bind(('0.0.0.0', port_int))
        
        print("Starting to listen", flush=True)
        sock.listen(5)
        
        print(f"Server listening on port {port_int}", flush=True)
        
        while True:
            print("Waiting for connection", flush=True)
            conn, addr = sock.accept()
            print(f"Connection from {addr}", flush=True)
            
            response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nBarbershop Server Running!"
            conn.send(response)
            conn.close()
            print("Response sent", flush=True)
            
    except Exception as e:
        print(f"Socket error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
