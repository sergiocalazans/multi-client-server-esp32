# trabalho_final/tcp/server_tcp.py

# Importa a biblioteca socket para comunicação de rede
import socket
# Importa a biblioteca threading para lidar com múltiplos clientes simultaneamente
import threading

# Lista global para armazenar as conexões dos clientes ativos (ESP32, Chat Python, etc.)
clients = []
# Cria um "cadeado" (Lock) para garantir que duas threads não modifiquem a lista 'clients' ao mesmo tempo
lock = threading.Lock()

# --- FUNÇÃO QUE GERENCIA CADA CLIENTE INDIVIDUALMENTE ---
def handle_client(conn, addr):
    print(f"Nova conexão de {addr}") # Exibe no log do servidor quem acabou de entrar
    
    # Bloqueia o acesso à lista para adicionar o novo cliente com segurança
    with lock:
        clients.append(conn)

    try:
        # Loop infinito para escutar as mensagens desse cliente específico
        while True:
            # Tenta ler até 1024 bytes e decodifica para string (texto)
            message = conn.recv(1024).decode('utf-8')
            
            # Se a mensagem estiver vazia, significa que o cliente desconectou
            if not message:
                break
            
            # Mostra no terminal do servidor o que chegou (útil para debug)
            print(f"Mensagem de {addr}: {message}")

            # Tenta separar o conteúdo da mensagem.
            # O formato esperado geralmente é "Nickname: Conteúdo"
            try:
                # Divide no primeiro ':' e pega a segunda parte (o comando/texto real)
                # .strip() remove espaços extras no começo e fim
                content = message.split(':', 1)[1].strip()
            except IndexError:
                # Se não houver ':', assume que o conteúdo é vazio ou formato desconhecido
                content = ""

            # --- LÓGICA DE COMANDOS ESPECÍFICOS ---
            # Verifica se o conteúdo é um comando para o LED/Tela
            if content in ["led_on", "led_off"]:
                # 1. Feedback para quem enviou (ex: usuário do chat):
                # Avisa que o comando foi entendido.
                feedback = f"Servidor: Comando '{content}' recebido e enviado ao ESP32."
                conn.send(feedback.encode('utf-8'))
                
                # 2. Retransmite a mensagem original para TODOS os outros (Broadcast)
                # É aqui que a mensagem chega ao ESP32 para ele acender/apagar a tela
                broadcast(message, conn)
            else:
                # --- LÓGICA PADRÃO DE CHAT ---
                # Se não for comando de LED, apenas repassa a mensagem para todos (chat normal)
                broadcast(message, conn)
                
    except:
        pass # Se houver erro de conexão, apenas segue para o bloco 'finally'
    finally:
        # Bloco executado sempre que a conexão encerra (erro ou desconexão voluntária)
        with lock:
            if conn in clients:
                clients.remove(conn) # Remove o cliente da lista de ativos
        
        conn.close() # Fecha o socket para liberar recursos
        print(f"Conexão de {addr} encerrada")

# --- FUNÇÃO PARA ESPALHAR MENSAGENS (BROADCAST) ---
def broadcast(message, source_conn):
    # Bloqueia a lista para evitar erros enquanto percorremos ela
    with lock:
        for client in clients:
            # Envia a mensagem para todos, EXCETO para quem enviou (evita eco)
            if client != source_conn:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    # Se falhar ao enviar (cliente caiu), fecha e remove da lista
                    client.close()
                    if client in clients:
                        clients.remove(client)

# --- FUNÇÃO PRINCIPAL DO SERVIDOR ---
def start_server():
    # Cria o socket TCP/IP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Vincula o servidor a todos os IPs da máquina ('0.0.0.0') na porta 5000
    # Isso permite receber conexões da rede WiFi e do localhost
    server.bind(('0.0.0.0', 5000))
    
    # Coloca o socket em modo de escuta (aguardando chamadas)
    server.listen()

    print("Servidor TCP aguardando conexões na porta 5000...")

    # Loop principal que aceita novos clientes indefinidamente
    while True:
        # Quando alguém conecta, aceita e retorna o objeto de conexão (conn) e endereço (addr)
        conn, addr = server.accept()
        
        # Cria uma nova thread (processo paralelo) dedicada a esse cliente
        # Isso permite que o servidor atenda vários clientes ao mesmo tempo sem travar
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start() # Inicia a thread

# --- PONTO DE ENTRADA DO SCRIPT ---
if __name__ == "__main__":
    start_server()
    