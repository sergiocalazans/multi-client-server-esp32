# Multi-Client Server ESP32

Este repositório contém um sistema de comunicação em rede que integra clientes **ESP32** e scripts **Python** utilizando os protocolos **TCP** e **UDP**. O projeto demonstra a diferença entre protocolos de transporte, implementando um chat multi-cliente e um sistema de monitoramento de sensores em tempo real.

## 📂 Estrutura do Projeto

O projeto está dividido em três pilares principais:

### 1. `tcp/` (Protocolo de Fluxo Confiável)

Implementa um servidor de chat e telemetria onde a entrega dos dados é garantida.

- **`server_tcp.py`**: Gerencia múltiplos clientes simultâneos usando _threads_. Possui um sistema de _Lock_ para evitar condições de corrida na lista de conexões.
- **`client_tcp.py`**: Cliente interativo com suporte a comandos como `/bench` para medir a performance da rede.

### 2. `udp/` (Protocolo de Datagramas Rápidos)

Focado em velocidade e baixa latência, ideal para transmissões rápidas onde a perda ocasional de um pacote não é crítica.

- **`server_udp.py`**: Mantém um registro manual de clientes (já que o UDP não é orientado à conexão) e realiza o _broadcast_ de mensagens.
- **`client_udp.py`**: Permite o envio de mensagens e testes de carga pesada na rede.

### 3. `esp32/` (Integração com Hardware)

- **`esp32_client.ino`**: Código para o microcontrolador ESP32 que:
  - Se conecta à rede Wi-Fi.
  - Envia dados de sensores (Simulados: Temperatura e Umidade) para o servidor TCP.
  - Exibe o status da conexão e dados enviados em um **Display OLED SSD1306**.

## 🚀 Como Executar

### Pré-requisitos

- Python 3.x instalado.
- Arduino IDE com as bibliotecas `Adafruit_SSD1306` e `Adafruit_GFX` (para o ESP32).

### Passo a Passo

1.  **Inicie o Servidor (TCP ou UDP):**
    ```bash
    python tcp/server_tcp.py
    # ou
    python udp/server_udp.py
    ```
2.  **Conecte os Clientes Python:**
    ```bash
    python tcp/client_tcp.py
    ```
3.  **Configure o ESP32:**
    - No arquivo `.ino`, atualize as variáveis `ssid`, `password` e `host` (IP do seu computador).
    - Carregue o código para a placa.

## 🛠️ Funcionalidades Avançadas

- **Broadcast de Mensagens:** O servidor replica a mensagem de um cliente para todos os outros conectados.
- **Comando de Benchmark:** Use `/bench <tamanho_em_mb>` nos clientes Python para testar a vazão da sua rede e ver o tempo de transferência.
- **Interface no Hardware:** O ESP32 utiliza um display OLED para mostrar o IP local e confirmar se a comunicação com o servidor foi bem-sucedida.

## 📊 Comparativo de Implementação

| Recurso            | TCP                      | UDP                         |
| :----------------- | :----------------------- | :-------------------------- |
| **Conexão**        | Orientado (Handshake)    | Sem conexão (Best-effort)   |
| **Garantia**       | Reenvia pacotes perdidos | Não garante entrega         |
| **Uso no Projeto** | Telemetria do ESP32      | Chat de alta velocidade     |
| **Escalabilidade** | Threads por cliente      | Loop único de processamento |

## Desenvolvimento

Esse projeto foi desenvolvido para a disciplina 'Conectividade de Sistemas Ciberfísicos', cursada no 2° Período do curso de Bacharelado em Ciência da Computação. O tema abordado é Redes de Computadores e Internet das Coisas.
