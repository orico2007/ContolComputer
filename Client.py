import socket
import pygame
import io
from pynput.keyboard import Listener as KeyboardListener, Key, KeyCode
from pynput.mouse import Listener as MouseListener, Button

def startClient():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '192.168.1.217'  # Change this to your server IP address
    port = 5050

    clientSocket.connect((host, port))

    pygame.init()

    # Get the screen dimensions
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h

    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption('Screen Viewer')

    def on_press(key):
        try:
            key_str = key.char
        except AttributeError:
            key_str = str(key)
        message = f"press|{key_str}\n"
        clientSocket.send(message.encode())

    def on_release(key):
        try:
            key_str = key.char
        except AttributeError:
            key_str = str(key)
        message = f"release|{key_str}\n"
        clientSocket.send(message.encode())
        if key == Key.esc:
            return False  # Stop the listener

    def on_move(x, y):
        message = f"move|{x},{y}|0,0\n"
        clientSocket.send(message.encode())

    def on_click(x, y, button, pressed):
        action = "press" if pressed else "release"
        button_str = 'left' if button == Button.left else 'right'
        message = f"{action}|{x},{y}|{button_str}\n"
        clientSocket.send(message.encode())

    def on_scroll(x, y, dx, dy):
        message = f"scroll|{x},{y}|{dx},{dy}\n"
        clientSocket.send(message.encode())

    # Start the keyboard and mouse listeners in separate threads
    keyboard_listener = KeyboardListener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    mouse_listener = MouseListener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    mouse_listener.start()

    while True:
        try:
            # Receive the size of the image
            size_info = clientSocket.recv(4)
            if not size_info:
                break
            size = int.from_bytes(size_info, 'big')

            # Receive the image data
            data = b''
            while len(data) < size:
                packet = clientSocket.recv(size - len(data))
                if not packet:
                    break
                data += packet

            if data:
                # Load and resize the image to fit the screen
                image = pygame.image.load(io.BytesIO(data))
                image = pygame.transform.scale(image, (screen_width, screen_height))
                screen.blit(image, (0, 0))
                pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    clientSocket.close()
                    pygame.quit()
                    return

        except Exception as e:
            print(f"Error receiving or displaying image: {e}")
            break

    clientSocket.close()
    pygame.quit()

if __name__ == "__main__":
    startClient()
