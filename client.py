import socket
import threading


HOST = "127.0.0.1"
PORT = 9009


def receive_loop(client_socket: socket.socket) -> None:
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                print("\n[Disconnected] Server closed connection.")
                break
            print(data.decode("utf-8"), end="")
        except OSError:
            break


def main() -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    receiver = threading.Thread(target=receive_loop, args=(client_socket,), daemon=True)
    receiver.start()

    try:
        while True:
            text = input()
            client_socket.sendall((text + "\n").encode("utf-8"))
            if text.lower() == "/quit":
                break
    except (KeyboardInterrupt, EOFError):
        try:
            client_socket.sendall(b"/quit\n")
        except OSError:
            pass
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
