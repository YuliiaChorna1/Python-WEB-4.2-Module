# звичайний ехо-сервер, який відправляє і отримує одні й ті самі дані на сервер. 
# Сервер відкритий на порту 8080 і отримує сокети даних у розмірі 1024 байт.

import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 8080


def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            print(f"Received data: {data.decode()} from: {address}")
            sock.sendto(data, address)
            print(f"Sent data: {data.decode()} to: {address}")
    except KeyboardInterrupt:
        print(f"Server's destroyed")
    finally:
        sock.close()

if __name__ == '__main__':
    run_server(UDP_IP, UDP_PORT)
