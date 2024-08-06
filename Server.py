import socket
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '192.168.1.217'
    port = 5050

    keyboard = KeyboardController()
    mouse = MouseController()

    server_socket.bind((host, port))
    server_socket.listen(1)
    print("Server is listening on port", port)

    client_socket, addr = server_socket.accept()
    print("Got a connection from", addr)

    def process_key(action, key):
        try:
            if action == "press":
                keyboard.press(key)
            elif action == "release":
                keyboard.release(key)
        except ValueError as e:
            print(f"Error processing key: {key}, {e}")

    def process_mouse(action, x, y, button=None, dx=0, dy=0):
        try:
            if action == "move":
                mouse.move(dx, dy)
            elif action == "press":
                mouse.press(button)
            elif action == "release":
                mouse.release(button)
            elif action == "scroll":
                mouse.scroll(dx, dy)
        except ValueError as e:
            print(f"Error processing mouse action: {action}, {e}")

    while True:
        data = client_socket.recv(1024).decode().strip()
        if not data:
            break
        
        print(f"Received data: {data}")  # Debug print
        
        parts = data.split('|')
        if len(parts) < 3:
            print(f"Invalid data format: {data}")
            continue

        action = parts[0]

        if action in ["press", "release"]:
            key = parts[1]
            process_key(action, key)
        elif action in ["move", "click", "scroll"]:
            try:
                x, y = map(int, parts[1].split(','))
                if action == "move":
                    dx, dy = map(int, parts[2].split(','))
                    process_mouse(action, x, y, dx=dx, dy=dy)
                elif action == "click":
                    button = Button.left if parts[2] == 'left' else Button.right
                    process_mouse(action, x, y, button=button)
                elif action == "scroll":
                    dx, dy = map(int, parts[2].split(','))
                    process_mouse(action, x, y, dx=dx, dy=dy)
            except ValueError as e:
                print(f"Error parsing mouse data: {e}")

    client_socket.close()

if __name__ == "__main__":
    start_server()
