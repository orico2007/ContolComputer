import socket
import cv2
import numpy as np
import io
from pynput.keyboard import Listener as KeyboardListener, Key, KeyCode
from pynput.mouse import Listener as MouseListener, Button

def startClient():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '84.229.209.209'  # Change this to your server IP address
    port = 5050

    clientSocket.connect((host, port))

    # Initialize OpenCV window in full screen mode
    cv2.namedWindow('Screen Viewer', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Screen Viewer', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

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
                # Convert the byte data to a numpy array and then decode it
                image_data = np.frombuffer(data, dtype=np.uint8)
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

                if image is not None:
                    # Get the dimensions of the image
                    img_height, img_width = image.shape[:2]

                    # Calculate the scale factor to fit the image to full screen
                    screen_width = cv2.getWindowImageRect('Screen Viewer')[2]
                    screen_height = cv2.getWindowImageRect('Screen Viewer')[3]
                    scale_factor = min(screen_width / img_width, screen_height / img_height)
                    new_width = int(img_width * scale_factor)
                    new_height = int(img_height * scale_factor)

                    # Resize the image
                    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

                    # Display the resized image
                    cv2.imshow('Screen Viewer', resized_image)

                    # Handle window events
                    key = cv2.waitKey(1)
                    if key == 27:  # ESC key
                        break

        except Exception as e:
            print(f"Error receiving or displaying image: {e}")
            break

    clientSocket.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    startClient()
