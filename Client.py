import pygame
import socket
import io

def startClient():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '192.168.1.217'  # Change this to your server IP address
    port = 5050

    clientSocket.connect((host, port))

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Screen Viewer')

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
                image = pygame.image.load(io.BytesIO(data))
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
