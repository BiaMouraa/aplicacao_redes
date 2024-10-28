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


def pseudo_cabec_ip(ip_origem, ip_destino, tam):
    # Faz a conversão para bbytes, para que seja possivel concatenar
    ip_origem = socket.inet_aton(ip_origem)
    ip_destino = socket.inet_aton(ip_destino)
    
    # Pseudocabecalho 
    pseudocabecalho = (ip_origem + ip_destino # Os endereços possuem 4 bytes cada
                       + struct.pack('!BBH', # Especifica a formatação e o tipo para cada campo da struct
                                        0, # Byte reservado - 1 byte
                                        17, # Protocolo UDP - 1 byte
                                        tam)) # Comprimento UDP - 2 bytes
    return pseudocabecalho

# Função auxiliar que utiliza o nome do localhost para retornar o seu IP
def get_local_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return str(ip_address)

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

def enviar_req(tipo):
    # Envia a mensagem e retorna a resposta do servidor

    payload, identificador = montar_req(tipo)
    ip = IP(dst=IP_SERV)
    # tam = cabeçalho de 8 bytes + tamanho do payload
    tam = 8 + len(payload)
    udp = UDP(sport=random.randint(49152, 65535), dport=PORTA_SERV, len = tam)

    # Junta os cabeçalhos IP e UDP com o payload
    pacote = ip / udp / Raw(load=payload)


    # Calculando o checksum...
    # Cria um pseudocabecalho ip
    cabec_ip = pseudo_cabec_ip(get_local_ip(), IP_SERV, tam)
    # Concatena o pseudo-cabeçalho, o cabeçalho UDP e o payload para calcular o checksum
    checksum = calcular_checksum(cabec_ip + bytes(pacote[UDP]) + bytes(pacote[Raw]))
    print(f"Checksum: {checksum:}")

    # Envia o pacote e recebe a resposta, com timeout de 2seg
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
        # Seleciona o conteudo da resposta
        conteudo = resposta[Raw].load
        if tipo == 3: # Considera a resposta como um inteiro nos últimos 4 bytes
            resposta_formatada = int.from_bytes(conteudo[4:], byteorder='big')
            print(f"Quantidade de respostas do servidor: {resposta_formatada}")
        else: # Considera a resposta como uma string decodificada usando utf-8
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
