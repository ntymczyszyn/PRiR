import pickle
import socket
from PIL import Image
from zad1 import split_image, merge_image

def send_all(sock, data):
    data = pickle.dumps(data)
    sock.sendall(len(data).to_bytes(4, byteorder='big'))
    sock.sendall(data)

def receive_all(sock):
    length = int.from_bytes(sock.recv(4), byteorder='big')
    data = b''
    while len(data) < length:
        packet = sock.recv(4096)
        if not packet:
            break
        data += packet
    return pickle.loads(data)

def server_main(image_path, n_clients):
    image = Image.open(image_path).convert("L") 
    fragments, coords  = split_image(image, n_clients)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('192.168.1.15', 2040))
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
    server_main("strus.jpg", 9)