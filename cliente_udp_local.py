import socket  # Biblioteca para trabalhar com sockets

# Configura o servidor UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('127.0.0.1', 50000))  # IP local e porta para ouvir conexões

print("Servidor UDP está rodando e esperando conexões...")

while True:
    # Recebe mensagem do cliente e exibe o conteúdo e endereço de origem
    mensagem, endereco = server_socket.recvfrom(1024)
    print(f"Recebido {mensagem} de {endereco}")
    
    # Envia resposta de volta ao cliente
    resposta = b"Resposta do servidor"  # Mensagem de resposta
    server_socket.sendto(resposta, endereco)
