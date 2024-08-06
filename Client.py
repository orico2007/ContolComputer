import socket
from pynput import mouse, keyboard

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 5050

    try:
        client_socket.connect((host, port))
        print("Connected to server")
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return

    def on_move(x, y):
        try:
            client_socket.send(f"move {(x, y)}".encode())
        except Exception as e:
            print(f"Error sending move data: {e}")

    def on_click(x, y, button, pressed):
        action = "press" if pressed else "release"
        try:
            client_socket.send(f"{action} {button}".encode())
        except Exception as e:
            print(f"Error sending click data: {e}")

    def on_scroll(x, y, dx, dy):
        try:
            client_socket.send(f"scroll {(dx, dy)}".encode())
        except Exception as e:
            print(f"Error sending scroll data: {e}")

    def on_press(key):
        try:
            client_socket.send(f"keypress {key}".encode())
        except Exception as e:
            print(f"Error sending keypress data: {e}")

    def on_release(key):
        try:
            client_socket.send(f"keyrelease {key}".encode())
        except Exception as e:
            print(f"Error sending keyrelease data: {e}")

    # Collect events until released
    with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        with keyboard.Listener(on_press=on_press, on_release=on_release) as k_listener:
            listener.join()
            k_listener.join()

    client_socket.close()

if __name__ == "__main__":
    start_client()
