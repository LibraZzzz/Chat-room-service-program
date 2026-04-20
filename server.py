import socket
import threading
from typing import Dict, Tuple


HOST = "127.0.0.1"
PORT = 9009


class ChatServer:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients: Dict[socket.socket, str] = {}
        self.lock = threading.Lock()

    def broadcast(self, message: str, sender: socket.socket | None = None) -> None:
        with self.lock:
            dead_clients = []
            for client in self.clients:
                if client is sender:
                    continue
                try:
                    client.sendall((message + "\n").encode("utf-8"))
                except OSError:
                    dead_clients.append(client)

            for dead in dead_clients:
                self.remove_client(dead)

    def remove_client(self, client: socket.socket) -> None:
        with self.lock:
            name = self.clients.pop(client, "Unknown")
        try:
            client.close()
        except OSError:
            pass
        self.broadcast(f"[SYSTEM] {name} left the room.")

    def handle_client(self, client: socket.socket, address: Tuple[str, int]) -> None:
        try:
            client.sendall(b"Enter your name: ")
            raw_name = client.recv(1024)
            if not raw_name:
                client.close()
                return

            name = raw_name.decode("utf-8").strip() or f"Guest-{address[1]}"
            with self.lock:
                self.clients[client] = name

            client.sendall(b"[SYSTEM] Welcome to the chat room!\n")
            self.broadcast(f"[SYSTEM] {name} joined the room.", sender=client)

            while True:
                data = client.recv(4096)
                if not data:
                    break
                message = data.decode("utf-8").strip()
                if not message:
                    continue
                if message.lower() == "/quit":
                    break
                self.broadcast(f"[{name}] {message}", sender=client)
        except (ConnectionError, OSError):
            pass
        finally:
            self.remove_client(client)

    def start(self) -> None:
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Chat server started on {self.host}:{self.port}")
        print("Press Ctrl+C to stop.")

        try:
            while True:
                try:
                    client, address = self.server_socket.accept()
                except OSError:
                    break
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client, address),
                    daemon=True,
                )
                thread.start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            with self.lock:
                for client in list(self.clients.keys()):
                    try:
                        client.close()
                    except OSError:
                        pass
                self.clients.clear()
            self.server_socket.close()


if __name__ == "__main__":
    ChatServer(HOST, PORT).start()
