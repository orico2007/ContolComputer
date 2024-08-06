import socket
from pynput.keyboard import Listener as KeyboardListener, Key
from pynput.mouse import Listener as MouseListener, Button

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = '192.168.1.217'
    port = 5050

    client_socket.connect((host, port))

    # Keyboard
    def on_press(key):
        try:
            client_socket.send(f"press {key.char}".encode())
        except AttributeError:
            client_socket.send(f"press {key}".encode())

    def on_release(key):
        try:
            client_socket.send(f"release {key.char}".encode())
        except AttributeError:
            client_socket.send(f"release {key}".encode())
        if key == Key.esc:
            return False  # Stop the listener

    # Start the keyboard listener in a separate thread
    keyboard_listener = KeyboardListener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    # Mouse
    def on_move(x, y):
        client_socket.send(f"move {(x, y)}".encode())

    def on_click(x, y, button, pressed):
        action = "press" if pressed else "release"
        client_socket.send(f"{action} {(x, y, button)}".encode())

    def on_scroll(x, y, dx, dy):
        client_socket.send(f"scroll {(x, y, dx, dy)}".encode())

    # Start the mouse listener in the main thread
    with MouseListener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()

    client_socket.close()

if __name__ == "__main__":
    start_client()
