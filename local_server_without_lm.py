import socket
import threading


def process_input(data):
    result = f'Received input - "{data}"'
    return result


def handle_client(client_socket, client_address):
    print(f'[NEW CONNECTION] {client_address} connected.')

    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                print(f'[DISCONNECTED] {client_address}')
                break

            print(f'[RECEIVED from {client_address}]: {data}')
            result = process_input(data)
            client_socket.send(result.encode('utf-8'))
        except ConnectionResetError:
            print(f'[ERROR] Connection with {client_address} was lost.')
            break

    client_socket.close()


def start_server(host='0.0.0.0', port=9999):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))

    server.listen(5)  # simultaneous connections
    print(f'[LISTENING] Server is listening on {host}:{port}')

    while True:
        client_socket, client_address = server.accept()
        client_handler = threading.Thread(
            target=handle_client,
            args=(client_socket, client_address)
        )
        client_handler.start()

        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')


if __name__ == '__main__':
    start_server()
