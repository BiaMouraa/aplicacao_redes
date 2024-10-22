import socket
import random

#configuracao do ip e da porta
IP_SERV = '15.228.191.109'
PORTA_SERV = 50000           

#criando socket UDP (indicado pelo SOCK_DGRAM)
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def menu():
    print("Escolha uma das opções:")
    print("1. Data e hora atual")
    print("2. Mensagem motivacional")
    print("3. Quantidade de respostas do servidor")
    print("4. Sair")

def opcoes():
    op = input("Digite sua opção (1-4): ")
    return int(op)

def montar_req(op):
    #req/res = 0000 para requisição
    req_res = 0x00
    #gera um identificador aleatório (2 bytes)
    identificador = random.randint(1, 65535)
    
    #mensagem de requisição
    mensagem = bytearray(3)  #3 bytes para req/res, op, e identificador
    mensagem[0] = req_res | op  #combina req/res e op
    mensagem[1] = (identificador >> 8) & 0xFF  #primeiro byte do identificador
    mensagem[2] = identificador & 0xFF          #segundo byte do identificador
    
    return mensagem, identificador

def enviar_req(op):
    mensagem, identificador = montar_req(op)
    cliente_socket.sendto(mensagem, (IP_SERV, PORTA_SERV))
    print(f"Requisição enviada (ID: {identificador})")

def receber_resp(op):
    resposta, endereco = cliente_socket.recvfrom(1024)  #tam máximo do pacote é 1024 bytes
    #print(f"Resposta do servidor: {resposta}")
    match op:
        case 1: #mensagem de resposta a partir do 4 bte
            data_hora = resposta[4:-1].decode('utf-8') 
            print(f"Data e hora atual: {data_hora}")
        case 2: #mensagem de resposta a partir do 4 bte
            mensagem_motivacional = resposta[4:-1].decode('utf-8')
            print(f"Mensagem motivacional: {mensagem_motivacional}")
        case 3: #mensagem de resposta são os últimos 4 bytes
            quantidade_respostas = int.from_bytes(resposta[4:8], byteorder='big')
            print(f"Quantidade de respostas do servidor: {quantidade_respostas}")
        case _:
            print("erro")

while True:
    menu()
    op = opcoes()
    match op:
        case 1:
            enviar_req(0x00)  #Data e hora
        case 2:
            enviar_req(0x01)  #Mensagem motivacional
        case 3:
            enviar_req(0x02)  #Quantidade de respostas
        case 4:
            print("Encerrando o cliente.")
            break
        case _:
            print("Escolha inválida, tente novamente.")
    
    receber_resp(op)

cliente_socket.close()
