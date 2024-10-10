import socket
import threading
import uuid
import os  # Biblioteca para pegar variáveis de ambiente
from typing import List, Tuple

# Gerencia as conexões ativas
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[Tuple[socket.socket, Tuple[str, int], str, str]] = []

    def connect(self, conn: socket.socket, addr: Tuple[str, int], name: str, client_id: str) -> bool:
        for _, _, _, cid in self.active_connections:
            if cid == client_id:
                return False
        self.active_connections.append((conn, addr, name, client_id))
        return True

    def disconnect(self, conn: socket.socket) -> None:
        for connection, _, _, _ in self.active_connections:
            if connection == conn:
                self.active_connections.remove((connection, _, _, _))
                break

    def broadcast(self, message: str, conn: socket.socket) -> None:
        for connection, _, _, _ in self.active_connections:
            if connection != conn:
                try:
                    connection.sendall(message.encode('utf-8'))
                except:
                    self.disconnect(connection)

# Função para lidar com um cliente
def handle_client(conn: socket.socket, addr: Tuple[str, int], manager: ConnectionManager) -> None:
    try:
        name = conn.recv(1024).decode('utf-8')
        client_id = str(uuid.uuid4())
        is_new_connection = manager.connect(conn, addr, name, client_id)

        if is_new_connection:
            print(f"{name} ({addr}) entrou no chat com ID {client_id}.")
            manager.broadcast(f"{name} entrou no chat.", conn)

        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            message = f"{name}: {data}"
            print(message)
            manager.broadcast(message, conn)

    except:
        pass
    finally:
        print(f"{name} ({addr}) saiu do chat.")
        manager.broadcast(f"{name} saiu do chat.", conn)
        manager.disconnect(conn)
        conn.close()

# Configuração do servidor
def start_server() -> None:
    # Puxando o IP e a PORT da env
    ip = os.getenv('IP', 'localhost')  # Default 'localhost' se não for especificado
    port = int(os.getenv('PORT', 8080))  # Default 8080 se não for especificado

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen()

    print(f"Servidor TCP rodando no IP {ip} e porta {port}...")
    manager = ConnectionManager()

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, manager))
        thread.start()

if __name__ == "__main__":
    start_server()
