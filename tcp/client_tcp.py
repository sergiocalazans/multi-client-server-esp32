# trabalho_final/tcp/client_tcp.py

# Importa a biblioteca de sockets para comunicação de rede (TCP/IP)
import socket
# Importa a biblioteca threading para permitir executar envio e recebimento ao mesmo tempo
import threading
# Importa a biblioteca time para medir o tempo (usado na função de benchmark)
import time

# Define uma variável global para o apelido do usuário (começa como "user")
nickname = "user"

# --- FUNÇÃO PARA RECEBER MENSAGENS ---
# Esta função roda em uma thread separada para não travar o input do usuário
def receive_messages(client_socket):
    while True: # Loop infinito para ficar escutando constantemente
        try:
            # Tenta receber dados do servidor. O buffer é de 1024 bytes.
            # .decode('utf-8') converte os bytes recebidos de volta para texto (string)
            message = client_socket.recv(1024).decode('utf-8')
            
            # Imprime a mensagem recebida no terminal
            print(message)
        except:
            # Se ocorrer qualquer erro (ex: servidor fechou a conexão), entra aqui
            print("Conexão com o servidor perdida.")
            # Sai do loop infinito, encerrando esta thread
            break

# --- FUNÇÃO PARA ENVIAR MENSAGENS ---
# Esta função roda na thread principal (ou secundária) e gerencia o input do teclado
def send_messages(client_socket):
    global nickname # Indica que vamos usar/modificar a variável global 'nickname'
    while True: # Loop infinito para aguardar digitação do usuário
        message = input() # Trava a execução até o usuário digitar algo e dar Enter

        # Verifica se a mensagem é um comando para mudar o nick
        if message.startswith('/nick '):
            # Divide a string no primeiro espaço e pega a segunda parte (o novo nome)
            nickname = message.split(' ', 1)[1]
            print(f"Nickname alterado para: {nickname}")
        
        # Verifica se a mensagem é um comando para sair
        elif message == '/sair':
            client_socket.close() # Fecha a conexão de rede corretamente
            break # Sai do loop, encerrando a thread de envio
        
        # Verifica se é o comando de benchmark (teste de velocidade)
        elif message.startswith('/bench '):
            try:
                # Pega o número digitado após o comando (tamanho em MB)
                size_mb = int(message.split(' ')[1])
                
                # Cria um pacote de dados "fictícios" (letra 'a' repetida muitas vezes)
                # 1024 * 1024 converte MB para Bytes
                data = b'a' * (size_mb * 1024 * 1024)
                
                # Marca o tempo inicial antes do envio
                start_time = time.time()
                
                # Envia todos os dados criados. 'sendall' garante que tudo seja enviado,
                # diferente de 'send' que pode enviar apenas uma parte se o buffer encher.
                client_socket.sendall(data)
                
                # Marca o tempo final após o envio completar
                end_time = time.time()
                
                # Calcula e exibe a diferença de tempo
                print(f"Tempo de envio (TCP): {end_time - start_time:.4f} segundos")
            except (ValueError, IndexError):
                # Tratamento de erro caso o usuário digite errado (ex: /bench abc)
                print("Uso: /bench <tamanho_em_mb>")
        
        # Se não for nenhum comando especial, envia como mensagem de chat normal
        else:
            # Formata a mensagem com o apelido atual
            full_message = f"{nickname}: {message}"
            # Converte a string para bytes (encode) e envia para o servidor
            client_socket.send(full_message.encode('utf-8'))

# --- FUNÇÃO PRINCIPAL DE INICIALIZAÇÃO ---
def start_client():
    # Cria o objeto socket
    # AF_INET = Família de endereços IPv4
    # SOCK_STREAM = Protocolo TCP (garante entrega e ordem dos pacotes)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Conecta ao servidor no IP local (localhost) e porta 5000
    client.connect(('127.0.0.1', 5000))

    # Cria uma thread (processo paralelo) para a função receive_messages
    # args=(client,) passa o objeto socket como argumento para a função
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start() # Inicia a execução da thread de recebimento

    # Cria uma thread para a função send_messages
    send_thread = threading.Thread(target=send_messages, args=(client,))
    send_thread.start() # Inicia a execução da thread de envio

# --- VERIFICAÇÃO DE EXECUÇÃO ---
# Garante que o código só rode se for executado diretamente (não importado)
if __name__ == "__main__":
    start_client()
