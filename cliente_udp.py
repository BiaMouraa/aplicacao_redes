import socket
import random

# Configura o IP e porta do servidor
IP_SERV = '15.228.191.109'
PORTA_SERV = 50000           

# Cria o socket UDP (SOCK_DGRAM indica o uso de UDP)
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def menu():
    print("Escolha uma das opções:")
    print("1. Data e hora atual")
    print("2. Mensagem motivacional")
    print("3. Quantidade de respostas do servidor")
    print("4. Sair")

def opcoes():
    # Captura e retorna a opção escolhida pelo usuário
    op = input("Digite sua opção (1-4): ")
    return int(op)

def montar_req(op):
    # Configura requisição com código 0x00 e gera um ID aleatório
    req_res = 0x00
    identificador = random.randint(1, 65535)
    
    # Cria a mensagem de 3 bytes: req/res, op, e identificador
    mensagem = bytearray(3)
    mensagem[0] = req_res | op  # Primeiro byte combina req/res e operação
    mensagem[1] = (identificador >> 8) & 0xFF  # Primeiro byte do identificador
    mensagem[2] = identificador & 0xFF         # Segundo byte do identificador
    
    return mensagem, identificador

def enviar_req(op):
    # Envia a mensagem de requisição ao servidor
    mensagem, identificador = montar_req(op)
    cliente_socket.sendto(mensagem, (IP_SERV, PORTA_SERV))
    print(f"Requisição enviada (ID: {identificador})")

def receber_resp(op):
    # Recebe resposta do servidor (pacote de até 1024 bytes)
    resposta, endereco = cliente_socket.recvfrom(1024)
    
    # Processa a resposta com base na opção escolhida
    match op:
        case 1:  # Extrai data e hora
            data_hora = resposta[4:-1].decode('utf-8')
            print(f"Data e hora atual: {data_hora}")
        case 2:  # Extrai mensagem motivacional
            mensagem_motivacional = resposta[4:-1].decode('utf-8')
            print(f"Mensagem motivacional: {mensagem_motivacional}")
        case 3:  # Extrai quantidade de respostas
            quantidade_respostas = int.from_bytes(resposta[4:8], byteorder='big')
            print(f"Quantidade de respostas do servidor: {quantidade_respostas}")
        case _:
            print("Erro ao processar resposta")

# Loop principal do cliente, para exibir o menu e enviar/receber respostas
while True:
    menu()
    op = opcoes()
    
    # Envia requisição com base na escolha do usuário
    match op:
        case 1:
            enviar_req(0x00)  # Data e hora
        case 2:
            enviar_req(0x01)  # Mensagem motivacional
        case 3:
            enviar_req(0x02)  # Quantidade de respostas
        case 4:
            print("Encerrando o cliente.")
            break
        case _:
            print("Escolha inválida, tente novamente.")
    
    receber_resp(op)  # Recebe e processa a resposta

# Fecha o socket ao final
cliente_socket.close()
