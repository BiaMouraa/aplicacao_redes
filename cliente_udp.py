import socket
import random

#configuracao do ip e da porta
ip_serv = '15.228.191.109'
porta_serv = 50000           

#criando socket UDP (indicado pelo SOCK_DGRAM)
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#menu de opções para o usuário
def menu():
    print("Escolha uma das opções:")
    print("1. Data e hora atual")
    print("2. Mensagem motivacional")
    print("3. Quantidade de respostas do servidor")
    print("4. Sair")

#recebe o input do usuário
def opcoes():
    op = input("Digite sua opção (1-4): ")
    return op

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
    cliente_socket.sendto(mensagem, (ip_serv, porta_serv))
    print(f"Requisição enviada (ID: {identificador})")

def receber_resp():
    resposta, endereco = cliente_socket.recvfrom(1024)  #tam máximo do pacote é 1024 bytes
    print(f"Resposta do servidor: {resposta}")

while True:
    menu()
    op = opcoes()
    
    if op == '1':
        enviar_req(0x00)  # Tipo 0: Data e hora
    elif op == '2':
        enviar_req(0x01)  # Tipo 1: Mensagem motivacional
    elif op == '3':
        enviar_req(0x02)  # Tipo 2: Quantidade de respostas
    elif op == '4':
        print("Encerrando o cliente.")
        break
    else:
        print("Escolha inválida, tente novamente.")
    
    receber_resp()

    cliente_socket.close()
