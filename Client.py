import socket
from pynput.keyboard import Controller as KeyboardController, Key, KeyCode
from pynput.mouse import Button, Controller as MouseController

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '192.168.1.217'
    port = 5050

    keyboard = KeyboardController()
    mouse = MouseController()

    server_socket.bind((host, port    ))
    server_socket.listen(1)
    print("Server is listening on port", port)

    client_socket, addr = server_socket.accept()
    print("Got a connection from", addr)

    buffer = ""
    pressed_keys = set()

    def process_key(action, key):
        try:
            print(f"Processing key: {action} {key}")  # Debugging line
            # Handle special keys
            if key.startswith('Key.'):
                key = getattr(Key, key.split('.')[1])
            else:
                key = KeyCode.from_char(key)

            if action == "press":
                keyboard.press(key)
                pressed_keys.add(key)
            elif action == "release":
                keyboard.release(key)
                if key in pressed_keys:
                    pressed_keys.remove(key)
                
            # Handle key combinations like Ctrl+C
            if Key.ctrl_l in pressed_keys or Key.ctrl_r in pressed_keys:
                if key == KeyCode.from_char('a'):
                    print("Ctrl+A pressed")
                elif key == KeyCode.from_char('c'):
                    print("Ctrl+C pressed")
            
            # Handle Caps Lock
            if key == Key.caps_lock:
                print("Caps Lock pressed")
                
        except Exception as e:
            print(f"Error processing key: {key}, {e}")

    def process_mouse(action, x, y, button=None, dx=0, dy=0):
        try:
            print(f"Processing mouse: {action} at ({x}, {y}) with {button if button else ''}")  # Debugging line
            if action == "move":
                mouse.position = (x, y)
            elif action == "press":
                mouse.press(button)
            elif action == "release":
                mouse.release(button)
            elif action == "scroll":
                mouse.scroll(dx, dy)
        except Exception as e:
            print(f"Error processing mouse action: {action}, {e}")

    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        
        buffer += data
        
        while '\n' in buffer:
            message, buffer = buffer.split('\n', 1)
            message = message.strip()
            print(f"Received data: {message}")  # Debugging line

            parts = message.split('|')
            if len(parts) < 2:
                print(f"Invalid data format: {message}")
                continue

            action = parts[0]

            if action in ["press", "release"]:
                if len(parts) == 3 and parts[2] in ['left', 'right']:  # Handling mouse click actions
                    x, y = map(int, parts[1].split(','))
                    button = Button.left if parts[2] == 'left' else Button.right
                    process_mouse(action, x, y, button=button)
                else:
                    key = parts[1]
                    process_key(action, key)
            elif action in ["move", "scroll"]:
                try:
                    x, y = map(int, parts[1].split(','))
                    if action == "move":
                        dx, dy = map(int, parts[2].split(','))
                        process_mouse(action, x, y, dx=dx, dy=dy)
                    elif action == "scroll":
                        dx, dy = map(int, parts[2].split(','))
                        process_mouse(action, x, y, dx=dx, dy=dy)
                except ValueError as e:
                    print(f"Error parsing mouse data: {e}")

    client_socket.close()

if __name__ == "__main__":
    start_server()

