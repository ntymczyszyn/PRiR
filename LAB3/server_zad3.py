import socket
import base64
from io import BytesIO
from PIL import Image
from zad1 import split_image, merge_image

def send_all(sock, image):
    image_buffer = BytesIO()
    image.save(image_buffer, format="JPEG", quality=64)
    image_data = image_buffer.getvalue()
    
    encoded_image = base64.b64encode(image_data).decode('utf-8')

    sock.sendall(len(encoded_image).to_bytes(4, byteorder='big'))
    sock.sendall(encoded_image.encode('utf-8'))

def receive_all(sock):
    length = int.from_bytes(sock.recv(4), byteorder='big')
    encoded_data = b''
    while len(encoded_data) < length:
        packet = sock.recv(4096)
        if not packet:
            break
        encoded_data += packet
    
    decoded_data = base64.b64decode(encoded_data)
    
    image_buffer = BytesIO(decoded_data)
    image = Image.open(image_buffer)
    return image

def server_main(image_path, n_clients):
    image = Image.open(image_path).convert("L") 
    fragments, coords  = split_image(image, n_clients)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('10.104.32.240', 2040))
    server_socket.listen(n_clients)
    print("Serwer nasłuchuje...")
    processed_fragments = []

    for i in range(n_clients):
        client_socket, client_address = server_socket.accept()
        print(f"Połączono z klientem {i + 1}: {client_address}")
        send_all(client_socket, fragments[i])
        processed_fragment = receive_all(client_socket)
        processed_fragments.append(processed_fragment)
        client_socket.close()

    result_image = merge_image(processed_fragments, coords, image.size)
    result_image.save("processed_image.png")
    print("Obraz przetworzony zapisany jako processed_image.png")

if __name__ == "__main__":  
    server_main("strus.jpeg", 2)