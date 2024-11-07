import socket
from zad1 import edge_filter
from server_zad3 import receive_all, send_all


def client_main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('10.104.32.240', 2040))
    fragment = receive_all(client_socket)
    processed_fragment = edge_filter(fragment)
    send_all(client_socket, processed_fragment)
    client_socket.close()
    print("Fragment przetworzony i wysłany z powrotem do serwera")

if __name__ == "__main__":
    client_main()