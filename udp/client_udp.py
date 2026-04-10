# trabalho_final/udp/client_udp.py

# Importa a biblioteca socket para comunicação de rede
import socket
# Importa a biblioteca threading para enviar e receber dados ao mesmo tempo
import threading
# Importa a biblioteca time para medir o tempo (usado no benchmark)
import time

# Define o apelido padrão do usuário
nickname = "user"

# --- FUNÇÃO PARA RECEBER MENSAGENS (Executada em thread separada) ---
def receive_messages(client_socket):
    while True: # Loop infinito ouvindo a rede
        try:
            # recvfrom é específico do UDP.
            # Ele retorna (dados, (ip_remoto, porta_remota)). 
            # Como só queremos os dados, usamos '_' para ignorar o endereço por enquanto.
            # 1024 é o tamanho do buffer (máximo de bytes por pacote lido de uma vez).
            message, _ = client_socket.recvfrom(1024)
            
            # Decodifica os bytes para texto e imprime na tela
            print(message.decode('utf-8'))
        except:
            # Se der erro (ex: socket fechado), encerra o loop
            break

# --- FUNÇÃO PARA ENVIAR MENSAGENS (Executada na thread principal) ---
def send_messages(client_socket):
    global nickname # Permite alterar a variável global
    
    # --- "LOGIN" NO UDP ---
    # Como UDP não tem "connect", o servidor não sabe que existimos até enviarmos algo.
    # Enviamos essa mensagem inicial apenas para o servidor registrar nosso IP e Porta na lista dele.
    # sendto exige (dados_em_bytes, (ip_destino, porta_destino)).
    client_socket.sendto(f"{nickname}: entrou no chat.".encode('utf-8'), ('127.0.0.1', 5001))

    while True: # Loop aguardando digitação
        message = input() # Bloqueia até o usuário digitar e dar Enter
        
        # Comando para trocar o apelido localmente
        if message.startswith('/nick '):
            nickname = message.split(' ', 1)[1]
            print(f"Nickname alterado para: {nickname}")
        
        # Comando para sair
        elif message == '/sair':
            # No UDP, não precisamos avisar o servidor que fechamos a conexão formalmente (pois não há conexão),
            # mas o loop é quebrado para encerrar o programa.
            break
        
        # Comando de teste de velocidade (Benchmark)
        elif message.startswith('/bench '):
            try:
                # Lê o tamanho em MB digitado
                size_mb = int(message.split(' ')[1])
                # Cria um pacote gigante de dados (pode ser fragmentado pelo SO)
                data = b'a' * (size_mb * 1024 * 1024)
                
                start_time = time.time() # Marca o início
                
                # Envia o pacote gigante via UDP. 
                # Nota: O UDP não garante entrega. Se o pacote for muito grande, pode ser descartado pelo roteador.
                client_socket.sendto(data, ('127.0.0.1', 5001))
                
                end_time = time.time() # Marca o fim
                
                print(f"Tempo de envio (UDP): {end_time - start_time:.4f} segundos")
            except (ValueError, IndexError):
                print("Uso: /bench <tamanho_em_mb>")
        
        # Mensagem de chat normal
        else:
            full_message = f"{nickname}: {message}"
            # Envia a mensagem para o servidor (localhost:5001).
            # Se o servidor estiver em outro PC, mude '127.0.0.1' para o IP dele.
            client_socket.sendto(full_message.encode('utf-8'), ('127.0.0.1', 5001))

# --- CONFIGURAÇÃO INICIAL DO CLIENTE ---
def start_client():
    # Cria o socket.
    # AF_INET = IPv4
    # SOCK_DGRAM = Datagramas (Protocolo UDP)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Inicia a thread que fica escutando mensagens chegando
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    # Inicia a thread (ou executa direto) o envio de mensagens
    send_thread = threading.Thread(target=send_messages, args=(client,))
    send_thread.start()

# Ponto de entrada do script
if __name__ == "__main__":
    start_client()
    