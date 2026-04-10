# trabalho_final/udp/server_udp.py

# Importa a biblioteca socket para comunicação de rede
import socket

# Dicionário para armazenar os clientes conhecidos.
# O UDP não mantém conexão aberta, então precisamos salvar manualmente quem falou conosco.
# Estrutura: { ('IP', Porta): 'Nickname' }
clients = {}

# --- FUNÇÃO PRINCIPAL DO SERVIDOR ---
def start_server():
    # Cria o socket.
    # AF_INET = IPv4
    # SOCK_DGRAM = Datagramas (Protocolo UDP)
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Vincula o servidor a todos os IPs da máquina ('0.0.0.0') na porta 5001.
    # O bind é necessário para o sistema operacional saber para onde direcionar os pacotes UDP que chegam.
    server.bind(('0.0.0.0', 5001))
    
    print("Servidor UDP aguardando mensagens na porta 5001...")

    # Loop infinito para processar pacotes chegando
    while True:
        # recvfrom espera receber um pacote UDP.
        # Retorna dois valores:
        # message_bytes: o conteúdo da mensagem em bytes.
        # addr: uma tupla contendo o endereço de quem enviou (IP, Porta).
        message_bytes, addr = server.recvfrom(1024)
        
        # Decodifica os bytes para string (texto)
        message = message_bytes.decode('utf-8')

        # --- LÓGICA DE REGISTRO DE CLIENTES ---
        # Verifica se o endereço (IP, Porta) já está na nossa lista de clientes conhecidos
        if addr not in clients:
            # Se não estiver, é um "novo usuário". Tentamos descobrir o nome dele.
            # O cliente envia no formato "Nickname: mensagem".
            parts = message.split(':', 1)
            
            # Se a mensagem tiver o formato correto (tiver dois pontos)
            if len(parts) > 1:
                # Salva no dicionário: Chave = Endereço, Valor = Nickname (primeira parte da msg)
                clients[addr] = parts[0]
                print(f"Novo cliente conectado: {clients[addr]} de {addr}")

        # Exibe no terminal do servidor a mensagem recebida.
        # clients.get(addr, addr) tenta pegar o Nickname; se não achar, mostra o IP bruto.
        print(f"Mensagem de {clients.get(addr, addr)}: {message}")
        
        # --- LÓGICA DE BROADCAST (Espalhar a mensagem) ---
        # Como não existe "conexão", percorremos nossa lista de endereços salvos
        for client_addr in clients:
            # Enviamos a mensagem para todos, EXCETO para quem enviou (addr)
            if client_addr != addr:
                # sendto envia o pacote UDP para o endereço específico recuperado do dicionário
                server.sendto(message.encode('utf-8'), client_addr)

# Ponto de entrada do script
if __name__ == "__main__":
    start_server()
    