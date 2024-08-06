import socket
from pynput.keyboard import Listener as KeyboardListener, Key
from pynput.mouse import Listener as MouseListener, Button

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '192.168.1.217'
    port = 5050

    client_socket.connect((host, port))

    last_x, last_y = 0, 0

    def on_press(key):
        try:
            key_str = key.char
        except AttributeError:
            key_str = str(key)
        message = f"press|{key_str}\n"
        print(f"Sending: {message.strip()}")  # Debugging line
        client_socket.send(message.encode())

    def on_release(key):
        try:
            key_str = key.char
        except AttributeError:
            key_str = str(key)
        message = f"release|{key_str}\n"
        print(f"Sending: {message.strip()}")  # Debugging line
        client_socket.send(message.encode())
        if key == Key.esc:
            return False  # Stop the listener

    # Start the keyboard listener in a separate thread
    keyboard_listener = KeyboardListener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    def on_move(x, y):
        nonlocal last_x, last_y
        dx = x - last_x
        dy = y - last_y
        message = f"move|{x},{y}|{dx},{dy}\n"
        client_socket.send(message.encode())
        last_x, last_y = x, y

    def on_click(x, y, button, pressed):
        action = "press" if pressed else "release"
        button_str = 'left' if button == Button.left else 'right'
        message = f"{action}|{x},{y}|{button_str}\n"
        print(f"Sending: {message.strip()}")  # Debugging line
        client_socket.send(message.encode())

    def on_scroll(x, y, dx, dy):
        message = f"scroll|{x},{y}|{dx},{dy}\n"
        client_socket.send(message.encode())

    # Start the mouse listener
    with MouseListener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()

    client_socket.close()

if __name__ == "__main__":
    start_client()
