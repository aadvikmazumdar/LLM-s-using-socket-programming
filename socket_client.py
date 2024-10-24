import socket


def recvall(sock):
    BUFF_SIZE = 4096
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data.decode()


def client_program():
    host = '127.0.0.1'
    port = 9999

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        message = input("You: ").strip()
        if not message:
            continue

        if message.lower() == 'exit':
            break

        client_socket.send(message.encode())
        response = recvall(client_socket)
        print(f'Server: {response}\n')

    client_socket.close()


if __name__ == '__main__':
    try:
        client_program()
    except KeyboardInterrupt:
        print('\nDisconnected\n')
