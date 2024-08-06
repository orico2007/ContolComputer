import socket
import threading
import time
from pynput.keyboard import Controller as KeyboardController, Key, KeyCode
from pynput.mouse import Button, Controller as MouseController
from PIL import ImageGrab
import io

def startServer():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '192.168.1.217'
    port = 5050

    keyboard = KeyboardController()
    mouse = MouseController()

    serverSocket.bind((host, port))
    serverSocket.listen(1)
    print("Server is listening on port", port)

    clientSocket, addr = serverSocket.accept()
    print("Got a connection from", addr)

    buffer = ""
    pressedKeys = set()
    capsLockActive = False  # Initialize caps_lock_active

    def processKey(action, key):
        nonlocal capsLockActive
        try:
            if key.startswith('Key.'):
                key = getattr(Key, key.split('.')[1])
            elif len(key) > 1:  # For special keys that are not single characters
                key = getattr(Key, key)
            else:
                key = KeyCode.from_char(key)
            
            if action == "press":
                if key == Key.caps_lock:
                    capsLockActive = not capsLockActive
                    print(f"Caps Lock is now {'on' if capsLockActive else 'off'}")
                keyboard.press(key)
                pressedKeys.add(key)
            elif action == "release":
                keyboard.release(key)
                if key in pressedKeys:
                    pressedKeys.remove(key)

            # Debugging line to show all pressed keys
            print(f"Currently pressed keys: {pressedKeys}")

        except Exception as e:
            print(f"Error processing key: {key}, {e}")

    def processMouse(action, x, y, button=None, dx=0, dy=0):
        try:
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

    def processScreen():
        while True:
            try:
                screenshot = ImageGrab.grab()
                buffer = io.BytesIO()
                screenshot.save(buffer, format='jpeg')  # Use PNG for lossless quality
                data = buffer.getvalue()

                # Send the size of the image first
                size_info = len(data).to_bytes(4, 'big')
                clientSocket.send(size_info)

                # Send the image data
                clientSocket.sendall(data)
                time.sleep(0.01)
            except Exception as e:
                print(f"Error capturing or sending screen: {e}")
                break

    # Start the screenshot capturing in a separate thread
    threading.Thread(target=processScreen, daemon=True).start()

    while True:
        data = clientSocket.recv(1024).decode()
        if not data:
            break
        
        buffer += data
        
        while '\n' in buffer:
            message, buffer = buffer.split('\n', 1)
            message = message.strip()

            parts = message.split('|')
            if len(parts) < 2:
                print(f"Invalid data format: {message}")
                continue

            action = parts[0]

            if action in ["press", "release"]:
                if len(parts) == 3 and parts[2] in ['left', 'right']:
                    x, y = map(int, parts[1].split(','))
                    button = Button.left if parts[2] == 'left' else Button.right
                    processMouse(action, x, y, button=button)
                else:
                    key = parts[1]
                    processKey(action, key)
            elif action in ["move", "scroll"]:
                try:
                    x, y = map(int, parts[1].split(','))
                    if action == "move":
                        dx, dy = map(int, parts[2].split(','))
                        processMouse(action, x, y, dx=dx, dy=dy)
                    elif action == "scroll":
                        dx, dy = map(int, parts[2].split(','))
                        processMouse(action, x, y, dx=dx, dy=dy)
                except ValueError as e:
                    print(f"Error parsing mouse data: {e}")

    clientSocket.close()

if __name__ == "__main__":
    startServer()
