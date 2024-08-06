import socket
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    host = '127.0.0.1'
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
        except Exception as e:
            print(f"Error processing key: {key}, {e}")

    def process_mouse(action, *args):
        try:
            if action == "move":
                x, y = args
                mouse.position = (x, y)
            elif action == "press":
                button = Button.left if args[0] == "Button.left" else Button.right
                mouse.press(button)
            elif action == "release":
                button = Button.left if args[0] == "Button.left" else Button.right
                mouse.release(button)
            elif action == "scroll":
                dx, dy = args
                mouse.scroll(dx, dy)
        except Exception as e:
            print(f"Error processing mouse action: {action}, {e}")

    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            action, *params = data.split()
            if action in ["press", "release"]:
                process_key(action, params[0])
            elif action in ["move", "scroll"]:
                process_mouse(action, *eval(params[0]))
            else:
                print(f"Unknown action: {action}")
        except Exception as e:
            print(f"Error handling client data: {e}")
            break

    client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
