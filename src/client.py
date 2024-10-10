import socket
import threading
import os  # Biblioteca para pegar variáveis de ambiente

def receive_messages(client_socket: socket.socket) -> None:
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(message)
        except:
            print("Conexão encerrada.")
            break

def start_client(name: str) -> None:
    # Puxando o IP e a PORT da env
    ip = os.getenv('IP', 'localhost')  # Default 'localhost' se não for especificado
    port = int(os.getenv('PORT', 8080))  # Default 8080 se não for especificado

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))

    # Enviar o nome do cliente para o servidor
    client_socket.sendall(name.encode('utf-8'))

    # Thread para receber mensagens
    thread = threading.Thread(target=receive_messages, args=(client_socket,))
    thread.start()

    while True:
        message = input()
        if message.lower() == 'sair':
            break
        client_socket.sendall(f"{name}: {message}".encode('utf-8'))

    client_socket.sendall(f"{name} saiu do chat.".encode('utf-8'))
    client_socket.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python client.py <nome>")
        sys.exit()

    name = sys.argv[1]
    start_client(name)
