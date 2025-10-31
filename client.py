import socket
import threading
import sys
import argparse
import time

ENCODING = "utf-8"
BUFSIZE = 4096

class ChatClient:
    def __init__(self, host: str, port: int, nick: str | None = None):
        self.addr = (host, port)
        self.nick = nick
        self.sock = None
        self.running = False

    def start(self):
        """Inicia o cliente e gerencia o ciclo de vida da conexão"""
        try:
            self._connect()
            self._register_nick()
            self._chat_loop()
        except ConnectionRefusedError:
            print(f"❌ Erro: Não foi possível conectar ao servidor em {self.addr[0]}:{self.addr[1]}")
            print("   Verifique se o servidor está rodando.")
        except KeyboardInterrupt:
            print("\n\n👋 Encerrando cliente...")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
        finally:
            self._cleanup()

    def _connect(self):
        """Estabelece conexão com o servidor"""
        print(f"🔌 Conectando ao servidor {self.addr[0]}:{self.addr[1]}...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.addr)
        self.running = True
        
        # Inicia thread para receber mensagens
        threading.Thread(target=self._receiver, daemon=True).start()
        print("✅ Conectado com sucesso!\n")

    def _register_nick(self):
        """Registra o nickname do usuário"""
        # Recebe mensagem de boas-vindas
        welcome = self._recv_line()
        if welcome:
            print(welcome)
        
        # Solicita nick se não foi fornecido
        while True:
            if not self.nick:
                print("\n💡 Dica: Use 3-20 caracteres (letras, números, _ ou -)")
                self.nick = input("Escolha seu NICK: ").strip()
            
            if not self.nick:
                print("⚠️  Nick não pode ser vazio!")
                self.nick = None
                continue
            
            # Envia nick para o servidor
            self._send_line(f"NICK {self.nick}")
            resp = self._recv_line()
            
            if resp:
                print(resp)
                
                if resp.startswith("OK "):
                    print(f"\n✅ Bem-vindo(a), {self.nick}!")
                    break
                elif "nickname_in_use" in resp:
                    print("⚠️  Este nick já está em uso. Escolha outro.")
                    self.nick = None
                elif "invalid_nick" in resp:
                    print("⚠️  Nick inválido. Tente outro.")
                    self.nick = None
                else:
                    print("❌ Falha ao registrar NICK. Encerrando.")
                    self.running = False
                    return

    def _chat_loop(self):
        """Loop principal de chat"""
        if not self.running:
            return
        
        self._print_help()
        
        try:
            while self.running:
                try:
                    line = input("> ").strip()
                except EOFError:
                    break
                
                if not line:
                    continue
                
                # Comandos especiais
                if line.upper() == "HELP":
                    self._print_help()
                    continue
                elif line.upper() == "CLEAR":
                    self._clear_screen()
                    continue
                
                # Envia comando ao servidor
                self._send_line(line)
                
                if line.upper().startswith("QUIT"):
                    print("\n👋 Desconectando...")
                    time.sleep(0.5)  # Aguarda confirmação do servidor
                    break
                    
        except KeyboardInterrupt:
            print("\n")
            self._send_line("QUIT")

    def _receiver(self):
        """Thread que recebe mensagens do servidor"""
        buffer = ""
        try:
            while self.running:
                try:
                    data = self.sock.recv(BUFSIZE)
                    if not data:
                        if self.running:
                            print("\n\n❌ Conexão encerrada pelo servidor")
                        break
                    
                    buffer += data.decode(ENCODING)
                    
                    # Processa linhas completas
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            self._format_message(line)
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"\n⚠️  Erro ao receber dados: {e}")
                    break
                    
        finally:
            self.running = False

    def _format_message(self, line: str):
        """Formata e exibe mensagens recebidas"""
        # Mensagens do sistema
        if line.startswith("SYSTEM:"):
            print(f"\r🔔 {line}\n> ", end="", flush=True)
        # Mensagens broadcast
        elif "[all]:" in line:
            print(f"\r💬 {line}\n> ", end="", flush=True)
        # Mensagens diretas recebidas
        elif line.startswith("FROM") and "[dm]:" in line:
            print(f"\r📩 {line}\n> ", end="", flush=True)
        # Mensagens diretas enviadas (confirmação)
        elif line.startswith("TO") and "[dm]:" in line:
            print(f"\r📤 {line}\n> ", end="", flush=True)
        # Erros
        elif line.startswith("ERR"):
            print(f"\r❌ Erro: {line[4:]}\n> ", end="", flush=True)
        # Lista de usuários
        elif line.startswith("USERS"):
            users = line[6:].strip()
            print(f"\r👥 Usuários online: {users}\n> ", end="", flush=True)
        # Outras mensagens
        else:
            print(f"\r{line}\n> ", end="", flush=True)

    def _print_help(self):
        """Exibe ajuda de comandos"""
        print("\n" + "="*60)
        print("📖 COMANDOS DISPONÍVEIS")
        print("="*60)
        print("  MSG <texto>          - Envia mensagem para todos (broadcast)")
        print("  MSG @nick <texto>    - Envia mensagem direta (DM)")
        print("  WHO                  - Lista usuários conectados")
        print("  QUIT                 - Sair do chat")
        print("  HELP                 - Mostra esta ajuda")
        print("  CLEAR                - Limpa a tela")
        print("="*60)
        print("\n💡 Exemplo de DM: MSG @joao Oi, tudo bem?")
        print("💡 Exemplo broadcast: MSG Olá a todos!\n")

    def _clear_screen(self):
        """Limpa a tela do terminal"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"💬 Chat - Conectado como: {self.nick}")
        print("-" * 60)

    def _send_line(self, text: str):
        """Envia uma linha de texto ao servidor"""
        try:
            self.sock.sendall((text + "\n").encode(ENCODING))
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            self.running = False

    def _recv_line(self):
        """Recebe uma linha de texto do servidor"""
        try:
            data = self.sock.recv(BUFSIZE)
            if not data:
                return None
            return data.decode(ENCODING).strip()
        except Exception:
            return None

    def _cleanup(self):
        """Limpa recursos ao encerrar"""
        self.running = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.sock.close()
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser(
        description="Mini-Chat TCP Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python client.py                           # Conecta em localhost:5000
  python client.py --host 192.168.1.100      # Conecta em outro PC
  python client.py --port 5555               # Usa outra porta
  python client.py --nick ana                # Define nick antecipadamente
        """
    )
    parser.add_argument("--host", default="127.0.0.1", 
                       help="Endereço do servidor (padrão: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000,
                       help="Porta do servidor (padrão: 5000)")
    parser.add_argument("--nick", default=None,
                       help="Nickname (será solicitado se não fornecido)")
    
    args = parser.parse_args()

    print("\n" + "="*60)
    print("🚀 MINI-CHAT TCP - CLIENTE")
    print("="*60 + "\n")

    ChatClient(args.host, args.port, args.nick).start()


if __name__ == "__main__":
    main()