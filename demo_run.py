import socket
import threading
import time
from typing import List

from server import ChatServer, HOST, PORT


def fake_client(name: str, messages: List[str], delay: float = 0.3) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    def recv_loop() -> None:
        while True:
            try:
                packet = sock.recv(4096)
                if not packet:
                    break
                print(f"[{name} recv] {packet.decode('utf-8').strip()}")
            except OSError:
                break

    receiver = threading.Thread(target=recv_loop, daemon=True)
    receiver.start()

    time.sleep(0.1)
    sock.sendall((name + "\n").encode("utf-8"))

    time.sleep(delay)
    for msg in messages:
        print(f"[{name} send] {msg}")
        sock.sendall((msg + "\n").encode("utf-8"))
        time.sleep(delay)
    print(f"[{name} send] /quit")
    sock.sendall(b"/quit\n")
    time.sleep(0.2)
    sock.close()


def main() -> None:
    server = ChatServer(HOST, PORT)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()

    time.sleep(0.6)

    alice = threading.Thread(
        target=fake_client,
        args=("Alice", ["Hi everyone!", "How are you?"]),
        daemon=True,
    )
    bob = threading.Thread(
        target=fake_client,
        args=("Bob", ["Hello Alice!", "I am great."]),
        daemon=True,
    )

    alice.start()
    bob.start()
    alice.join()
    bob.join()

    time.sleep(0.8)
    server.server_socket.close()
    print("Demo completed.")


if __name__ == "__main__":
    main()
