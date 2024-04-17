# метод connect, за допомогою якого ми підключаємось до сервера. 
# З'єднання може не встановлюватися з першого разу. Щоб обробити помилку з'єднання, 
# ми помістили клієнтський код у нескінченний цикл для повторення спроб з'єднатися.

import socket
from time import sleep


def simple_client(host, port):
    with socket.socket() as s:
        while True:
            try:
                s.connect((host, port))
                s.sendall(b"Hello world!")
                data = s.recv(1024)
                print(f"From server: {data}")
                break
            except ConnectionRefusedError:
                sleep(0.5)
