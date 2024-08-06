import socket
from pynput.keyboard import Key, Controller as KeyboardController
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

    def process_mouse(action, *args):
        try:
            if action == "move":
                dx, dy = args
                mouse.move(dx, dy)
            elif action == "press":
                button = args[0]
                mouse.press(button)
            elif action == "release":
                button = args[0]
                mouse.release(button)
            elif action == "scroll":
                dx, dy = args
                mouse.scroll(dx, dy)
        except ValueError as e:
            print(f"Error processing mouse action: {action}, {e}")

    while True:
        data = client_socket.recv(1024).decode().strip()
        if not data:
            break

        action_data = data.split(" ", 1)
        action = action_data[0]

        if action in ["press", "release"]:
            key = action_data[1]
            process_key(action, key)
        elif action in ["move", "click", "scroll"]:
            args = eval(action_data[1])
            process_mouse(action, *args)

    client_socket.close()

if __name__ == "__main__":
    start_server()
