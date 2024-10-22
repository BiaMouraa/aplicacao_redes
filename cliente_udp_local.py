import socket

# Criar um servidor UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('127.0.0.1', 50000))  # IP local e porta 50000

print("Servidor UDP está rodando e esperando conexões...")

while True:
    mensagem, endereco = server_socket.recvfrom(1024)
    print(f"Recebido {mensagem} de {endereco}")
    resposta = b"Resposta do servidor"  # Resposta simulada
    server_socket.sendto(resposta, endereco)

