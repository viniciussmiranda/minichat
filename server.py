from __future__ import annotations
import socket
import threading
import argparse
from typing import Dict, Tuple

ENCODING = "utf-8"
BUFSIZE = 4096

class ChatServer:
    def __init__(self, host: str, port: int):
        self.addr = (host, port)
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients_lock = threading.Lock()

        self.clients: Dict[str, Tuple[socket.socket, Tuple[str, int]]] = {}

    def start(self):
        self.server_sock.bind(self.addr)
        self.server_sock.listen()
        print(f"[server] listening on {self.addr[0]}:{self.addr[1]}")
        try:
            while True:
                conn, caddr = self.server_sock.accept()
                threading.Thread(target=self._handle_client, args=(conn, caddr), daemon=True).start()
        except KeyboardInterrupt:
            print("\n[server] shutting down...")
        finally:
            with self.clients_lock:
                for nick, (c, _) in list(self.clients.items()):
                    try:
                        c.shutdown(socket.SHUT_RDWR)
                    except Exception:
                        pass
                    c.close()
                self.clients.clear()
            self.server_sock.close()

    def _handle_client(self, conn: socket.socket, caddr: Tuple[str, int]):
        nick = None
        try:
            self._send_line(conn, "WELCOME Choose a nickname with: NICK <apelido>")
            while True:
                line = self._recv_line(conn)
                if line is None:
                    return
                if line.upper().startswith("NICK "):
                    candidate = line[5:].strip()
                    if not self._is_valid_nick(candidate):
                        self._send_line(conn, "ERR invalid_nick")
                        continue
                    with self.clients_lock:
                        if candidate in self.clients:
                            self._send_line(conn, "ERR nickname_in_use")
                            continue
                        self.clients[candidate] = (conn, caddr)
                        nick = candidate
                    self._send_line(conn, f"OK nick {nick}")
                    self._broadcast_system(f"User {nick} joined", exclude={nick})
                    break
                else:
                    self._send_line(conn, "ERR identify_with_NICK_first")

            while True:
                line = self._recv_line(conn)
                if line is None:
                    return
                if not line:
                    continue
                cmd = line.split(" ", 1)[0].upper()
                if cmd == "MSG":
                    payload = line[4:] if len(line) > 4 else ""
                    if payload.startswith("@"):
                        try:
                            dest, msg = payload.split(" ", 1)
                        except ValueError:
                            self._send_line(conn, "ERR invalid_dm_format")
                            continue
                        dest_nick = dest[1:]
                        if not dest_nick:
                            self._send_line(conn, "ERR invalid_dm_format")
                            continue
                        if not self._send_dm(nick, dest_nick, msg):
                            self._send_line(conn, "ERR user_not_found")
                    else:
                        self._broadcast_msg(nick, payload)
                elif cmd == "WHO":
                    users = self._list_users()
                    self._send_line(conn, f"USERS {', '.join(users)}")
                elif cmd == "QUIT":
                    self._send_line(conn, "BYE")
                    return
                else:
                    self._send_line(conn, "ERR unknown_command")
        except Exception as e:
            print(f"[server] error with {caddr} ({nick}): {e}")
        finally:
            if nick:
                with self.clients_lock:
                    if nick in self.clients and self.clients[nick][0] is conn:
                        del self.clients[nick]
                self._broadcast_system(f"User {nick} left", exclude=set())
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            conn.close()

    def _is_valid_nick(self, nick: str) -> bool:
        if not (3 <= len(nick) <= 20):
            return False
        return all(c.isalnum() or c in ("_", "-") for c in nick)

    def _list_users(self):
        with self.clients_lock:
            return sorted(self.clients.keys())

    def _broadcast_system(self, text: str, exclude: set[str] | None = None):
        msg = f"SYSTEM: {text}"
        self._broadcast_raw(msg, exclude or set())

    def _broadcast_msg(self, sender: str, text: str):
        msg = f"FROM {sender} [all]: {text}"
        self._broadcast_raw(msg, exclude={sender})
        with self.clients_lock:
            if sender in self.clients:
                self._send_line(self.clients[sender][0], msg)

    def _broadcast_raw(self, text: str, exclude: set[str]):
        with self.clients_lock:
            for nick, (c, _) in list(self.clients.items()):
                if nick in exclude:
                    continue
                try:
                    self._send_line(c, text)
                except Exception:
                    try:
                        c.close()
                    except Exception:
                        pass
                    del self.clients[nick]

    def _send_dm(self, sender: str, dest: str, text: str) -> bool:
        with self.clients_lock:
            target = self.clients.get(dest)
            me = self.clients.get(sender)
        if not target or not me:
            return False
        to_msg = f"FROM {sender} [dm]: {text}"
        me_msg = f"TO @{dest} [dm]: {text}"
        self._send_line(target[0], to_msg)
        self._send_line(me[0], me_msg)
        return True

    def _send_line(self, conn: socket.socket, text: str):
        data = (text + "\n").encode(ENCODING)
        conn.sendall(data)

    def _recv_line(self, conn: socket.socket) -> str | None:
        buf = bytearray()
        while True:
            chunk = conn.recv(BUFSIZE)
            if not chunk:
                return None
            buf.extend(chunk)
            if b"\n" in chunk:
                break
        return buf.decode(ENCODING).strip()


def main():
    parser = argparse.ArgumentParser(description="Mini-Chat TCP Server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    ChatServer(args.host, args.port).start()

if __name__ == "__main__":
    main()
