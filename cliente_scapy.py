from scapy.all import *
import random
import struct
from ipaddress import IPv4Address

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

def calcular_checksum(dados):
    # Se o comprimento dos dados for ímpar, adiciona um byte extra
    if len(dados) % 2 == 1:
        dados += b'\x00'

    checksum = 0
    # Soma os dados em blocos de 2 bytes
    for i in range(0, len(dados), 2):
        palavra = int.from_bytes(dados[i:i+2], 'big')
        checksum += palavra
        # Realiza o wraparound
        checksum = (checksum & 0xFFFF) + (checksum >> 16)

    # Retorna o complemento de 1 do que foi calculado
    return ~checksum & 0xFFFF

def montar_cabecalho(porta_origem, porta_destino, ip_origem, ip_destino, payload):
    # Campos do cabeçalho UDP de 8 bytes total
    cabecalho = bytearray(8)
    cabecalho[0:2] = porta_origem.to_bytes(2, 'big')       # Porta de origem - 2 bytes
    cabecalho[2:4] = porta_destino.to_bytes(2, 'big')      # Porta de destino - 2 bytes
    tam = 8 + len(payload)                       # Comprimento do cabeçalho + dados
    cabecalho[4:6] = tam.to_bytes(2, 'big')     # Comprimento total
    cabecalho[6:8] = (0).to_bytes(2, 'big')            # Checksum configurado como 0 - 2 bytes

    # Construção do pseudo-cabeçalho IP para o cálculo do checksum
    cabecalho_ip = struct.pack('!4s4sBBH', # Faz a formatação de cada campo da struct, definindo o seu tamanho e tipo
                                ip_origem.packed,       # IP de origem - 4 bytes
                                ip_destino.packed,      # IP de destino - 4 bytes
                                0,                   # Byte reservado - 1 byte
                                17,                  # Protocolo UDP - 1 byte
                                tam)          # Comprimento UDP - 2 bytes

    # Concatena o pseudo-cabeçalho, o cabeçalho UDP e o payload para calcular o checksum
    dados = cabecalho_ip + cabecalho + payload
    checksum = calcular_checksum(dados)
    cabecalho[6:8] = checksum.to_bytes(2, 'big')

    return cabecalho + payload

def enviar_req(tipo):
    # # Envia a mensagem e retorna a resposta do servidor
    # payload, identificador = montar_req(tipo)
    # ip = IP(dst=IP_SERV)
    # udp = UDP(sport=random.randint(49152, 65535), dport=PORTA_SERV)
    # pacote = ip / udp / Raw(load=payload)
    # resposta = sr1(pacote, timeout=2)

    ip_origem = IPv4Address("192.168.1.105")
    ip_destino = IPv4Address(IP_SERV)

    # Monta o payload e o cabeçalho UDP com checksum calculado
    payload, identificador = montar_req(tipo)
    porta_origem = random.randint(49152, 65535)
    pacote_udp = montar_cabecalho(porta_origem, PORTA_SERV, ip_origem, ip_destino, payload)

    # Envia o pacote UDP usando Scapy
    ip = IP(src=str(ip_origem), dst=IP_SERV)
    pacote = ip / Raw(load=pacote_udp)
    resposta = sr1(pacote, timeout=5)

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
        