import socket
import threading
import sys
import argparse

ENCODING = "utf-8"
BUFSIZE = 4096

class ChatClient:
    def __init__(self, host: str, port: int, nick: str | None = None):
        self.addr = (host, port)
        self.nick = nick
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

    def start(self):
        self.sock.connect(self.addr)
        self.running = True
        threading.Thread(target=self._receiver, daemon=True).start()

        if not self.nick:
            welcome = self._recv_line()
            if welcome is not None:
                print(welcome)
            self.nick = input("Escolha seu NICK: ").strip()
        self._send_line(f"NICK {self.nick}")
        resp = self._recv_line()
        if resp is not None:
            print(resp)
            if not resp.startswith("OK "):
                print("Falha ao registrar NICK. Encerrando.")
                self.running = False
                self.sock.close()
                return

        print("Comandos: MSG <texto> | MSG @nick <texto> | WHO | QUIT")
        try:
            while self.running:
                try:
                    line = input("> ")
                except EOFError:
                    break
                if not line:
                    continue
                self._send_line(line)
                if line.upper().startswith("QUIT"):
                    break
        finally:
            self.running = False
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            self.sock.close()

    def _receiver(self):
        try:
            while self.running:
                data = self.sock.recv(BUFSIZE)
                if not data:
                    print("\n[conexão encerrada pelo servidor]")
                    break
                for line in data.decode(ENCODING).splitlines():
                    print(f"\r{line}\n> ", end="", flush=True)
        except Exception as e:
            pass
        finally:
            self.running = False

    def _send_line(self, text: str):
        self.sock.sendall((text + "\n").encode(ENCODING))

    def _recv_line(self):
        data = self.sock.recv(BUFSIZE)
        if not data:
            return None
        return data.decode(ENCODING).strip()


def main():
    parser = argparse.ArgumentParser(description="Mini-Chat TCP Client")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    # Removido --nick para sempre pedir ao usuário
    args = parser.parse_args()

    ChatClient(args.host, args.port, nick=None).start()  # Sempre None = sempre pergunta

if __name__ == "__main__":
    main()