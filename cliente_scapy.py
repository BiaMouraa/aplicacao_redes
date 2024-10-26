from scapy.all import *
import random

# Configura o IP e a porta do servidor
IP_SERV = '15.228.191.109'
PORTA_SERV = 50000           

def menu():
    print("Escolha uma das opções:")
    print("1. Data e hora atual")
    print("2. Mensagem motivacional")
    print("3. Quantidade de respostas do servidor")
    print("4. Sair")

def opcoes():
    # Retorna a opção escolhida pelo usuário
    op = input("Digite sua opção (1-4): ")
    return int(op)

def montar_req(tipo):
    # Configura requisição com identificador aleatório
    req_res = 0x00
    identificador = random.randint(1, 65535)
    
    # Cria a mensagem de requisição com 3 bytes: req/res, tipo e identificador
    mensagem = bytearray(3)
    mensagem[0] = req_res | tipo  # Primeiro byte combina req/res e operação
    mensagem[1] = (identificador >> 8) & 0xFF  # Primeiro byte do identificador
    mensagem[2] = identificador & 0xFF         # Segundo byte do identificador
    
    return bytes(mensagem), identificador

def enviar_req(tipo):
    # Envia a mensagem e retorna a resposta do servidor
    payload, identificador = montar_req(tipo)
    ip = IP(dst=IP_SERV)
    udp = UDP(sport=random.randint(49152, 65535), dport=PORTA_SERV)
    pacote = ip / udp / Raw(load=payload)
    resposta = sr1(pacote, timeout=2)

    # Exibe o status da resposta recebida
    if resposta:
        print(f"Requisição enviada (ID: {identificador})")
        return resposta
    else:
        print("Nenhuma resposta do servidor.")
        return None

def receber_resp(resposta, tipo):
    # Processa a resposta recebida com base na opção
    if resposta and Raw in resposta:
        conteudo = resposta[Raw].load
        if tipo == 3:
            resposta_formatada = int.from_bytes(conteudo[4:], byteorder='big')
            print(f"Quantidade de respostas do servidor: {resposta_formatada}")
        else:
            resposta_formatada = conteudo[4:].decode('utf-8')
            print(f"Resposta do servidor: {resposta_formatada}")
    else:
        print("Nenhuma resposta recebida.")

# Loop principal do cliente para exibir o menu e processar as requisições
resposta = ""
while True:
    menu()
    op = opcoes()
    match op:
        case 1:
            resposta = enviar_req(0x00)  # Data e hora
        case 2:
            resposta = enviar_req(0x01)  # Mensagem motivacional
        case 3:
            resposta = enviar_req(0x02)  # Quantidade de respostas
        case 4:
            print("Encerrando o cliente.")
            break
        case _:
            print("Escolha inválida, tente novamente.")
    
    if resposta:
        receber_resp(resposta, op)
        