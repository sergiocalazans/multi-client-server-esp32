// trabalho_final/esp32/esp32_client/esp32_client.ino

// --- INCLUSÃO DE BIBLIOTECAS ---
#include <WiFi.h>              // Biblioteca nativa do ESP32 para gerenciar conexão WiFi
#include <Wire.h>              // Biblioteca para comunicação I2C (usada pelo display OLED)
#include <Adafruit_GFX.h>      // Biblioteca gráfica base da Adafruit (fontes, linhas, formas)
#include <Adafruit_SSD1306.h>  // Driver específico para controlar o display OLED SSD1306

// --- CONFIGURAÇÕES DA REDE E SERVIDOR ---
// Define o nome da rede WiFi (SSID)
const char* ssid = "NOME DA REDE";
// Define a senha da rede WiFi
const char* password = "SENHA DA REDE";
// Define o endereço IP do servidor (computador) que receberá os dados
const char* host = "10.86.70.245";
// Define a porta de comunicação TCP do servidor (deve ser a mesma configurada no servidor python)
const int port = 5000;

// --- CONFIGURAÇÕES DE HARDWARE ---
// Define o pino do LED interno
#define LED_PIN 2 

// Configurações da tela OLED para a placa HW-724
#define SCREEN_WIDTH 128  // Largura do display em pixels
#define SCREEN_HEIGHT 64  // Altura do display em pixels
#define OLED_SDA 5        // Pino de dados I2C (SDA)
#define OLED_SCL 4        // Pino de clock I2C (SCL)

// --- OBJETOS GLOBAIS ---
// Cria um objeto cliente WiFi para gerenciar a conexão TCP
WiFiClient client;
// Cria o objeto de controle do display OLED, passando largura, altura, referência do I2C e pino de reset (-1 se não houver)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// --- FUNÇÃO DE SETUP (Executada uma vez ao iniciar) ---
void setup() {
  Serial.begin(115200);       // Inicia a comunicação serial para debug no PC (velocidade 115200)
  pinMode(LED_PIN, OUTPUT);   // Configura o pino do LED como saída digital
  digitalWrite(LED_PIN, LOW); // Garante que o LED comece apagado

  // Inicia o barramento I2C definindo manualmente os pinos SDA e SCL
  Wire.begin(OLED_SDA, OLED_SCL);

  // Tenta iniciar o display no endereço I2C 0x3C
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
    Serial.println(F("Falha ao iniciar a tela SSD1306")); // Mensagem de erro na serial se falhar
    for(;;); // Loop infinito para travar o programa caso o display não funcione
  }

  // --- Inicialização da Interface Visual ---
  display.clearDisplay();           // Limpa o buffer da tela (apaga tudo)
  display.setTextSize(1);           // Define o tamanho da fonte (1 é o padrão pequeno)
  display.setTextColor(SSD1306_WHITE); // Define a cor do texto (Branco, já que o display é monocromático)
  display.setCursor(0, 0);          // Posiciona o cursor de escrita no canto superior esquerdo (X=0, Y=0)
  display.println("Conectando ao WiFi..."); // Escreve o texto no buffer
  display.display();                // Envia o buffer para o hardware da tela (atualiza a imagem)

  // --- Conexão WiFi ---
  WiFi.begin(ssid, password);       // Inicia a tentativa de conexão com a rede configurada
  // Loop que roda enquanto o status não for "Conectado"
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);         // Espera meio segundo entre checagens
    Serial.print(".");  // Imprime um ponto na serial para feedback
    display.print("."); // Imprime um ponto no OLED para feedback visual
    display.display();  // Atualiza a tela
  }
  
  // Após conectar, atualiza a tela mostrando o IP obtido
  updateDisplayInfo("WiFi Sergio: Connect!","IP: " + WiFi.localIP().toString());
}

// --- LOOP PRINCIPAL (Executado repetidamente) ---
void loop() {
  // Verifica se a conexão TCP com o servidor caiu ou não existe
  if (!client.connected()) {
    connectToServer(); // Chama a função para tentar reconectar
  }

  // Variável estática para controlar o tempo (não bloqueante)
  static unsigned long lastSendTime = 0;
  
  // Verifica se passaram 2000ms (2 segundos) desde o último envio
  if (millis() - lastSendTime > 2000) {
    // Valores simulados de sensores
    float temp = 25.3;
    int hum = 60;
    
    // Cria uma string no formato JSON manualmente para enviar ao servidor
    // Exemplo: {"type": "data", "from": "esp32", "payload": {"temp": 25.3, "hum": 60}}
    String jsonData = "{\"type\": \"data\", \"from\": \"esp32\", \"payload\": {\"temp\": " + String(temp) + ", \"hum\": " + String(hum) + "}}";
    
    client.println(jsonData); // Envia o JSON via TCP para o servidor
    
    updateDisplayData(temp, hum); // Atualiza a parte da tela que mostra os dados dos sensores
    lastSendTime = millis();      // Atualiza o contador de tempo
  }

  // Verifica se há dados chegando do servidor
  if (client.available()) {
    String command = client.readStringUntil('\n'); // Lê a mensagem recebida até encontrar uma quebra de linha
    command.trim(); // Remove espaços em branco ou quebras de linha no início/fim
    
    // Verifica se a mensagem tem o formato "chave:valor" procurando por ':'
    int colonIndex = command.indexOf(':');
    if (colonIndex != -1) {
      // Se tiver ':', pega apenas a parte depois do ':' (o comando real)
      command = command.substring(colonIndex + 1);
      command.trim(); // Limpa espaços novamente
    }
    
    // --- LÓGICA DE COMANDOS RECEBIDOS ---
    // Comandos que controlam a tela OLED >>>
    
    if (command == "led_on") {
      // Se o comando for "led_on", liga o hardware do display
      display.ssd1306_command(SSD1306_DISPLAYON); 
      updateDisplayStatus("Tela: LIGADA"); // Mostra status na tela
      
    } else if (command == "led_off") {
      // Se o comando for "led_off", prepara para desligar
      updateDisplayStatus("Tela: DESLIGADA"); // Avisa o usuário antes de apagar
      delay(500); // Pequeno delay para o usuário conseguir ler a mensagem "DESLIGADA"
      
      // Envia comando de baixo nível para desligar a alimentação do painel OLED (economia de energia)
      display.ssd1306_command(SSD1306_DISPLAYOFF); 
    }
  }
}

// --- FUNÇÕES AUXILIARES ---

// Função para gerenciar a conexão com o servidor TCP
void connectToServer() {
  updateDisplayStatus("Conectando Servidor..."); // Atualiza status na tela
  
  // Tenta conectar ao IP e Porta definidos. Retorna true se sucesso.
  while (!client.connect(host, port)) {
    Serial.println("Falha na conexão. Tentando novamente em 5 segundos...");
    delay(5000); // Espera 5 segundos antes de tentar de novo (bloqueante)
  }
  
  Serial.println("Conectado ao servidor");
  updateDisplayStatus("Servidor: OK"); // Atualiza status na tela confirmando conexão
}

// Função para limpar a tela e escrever o cabeçalho (WiFi e IP)
void updateDisplayInfo(String line1, String line2) {
  display.clearDisplay();   // Limpa tudo
  display.setCursor(0, 0);  // Linha 1
  display.println(line1);
  display.setCursor(0, 10); // Linha 2 (aprox 10px abaixo)
  display.println(line2);
  display.display();        // Atualiza
}

// Função otimizada para atualizar apenas a linha de status (evita piscar a tela toda)
void updateDisplayStatus(String status) {
  // Desenha um retângulo preto para "apagar" apenas a área antiga do status
  // Parâmetros: (x, y, largura, altura, cor)
  display.fillRect(0, 25, SCREEN_WIDTH, 10, SSD1306_BLACK); 
  
  display.setCursor(0, 25); // Posiciona cursor na área limpa
  display.println(status);  // Escreve o novo status
  display.display();        // Atualiza
}

// Função otimizada para atualizar apenas os dados numéricos (Temperatura/Umidade)
void updateDisplayData(float temp, int hum) {
  // Limpa apenas a área inferior onde ficam os dados
  display.fillRect(0, 40, SCREEN_WIDTH, 24, SSD1306_BLACK);
  
  display.setCursor(0, 40);
  display.print("Temp: ");
  display.print(temp);
  display.println(" C"); // Adiciona unidade
  
  display.setCursor(0, 50);
  display.print("Hum:  ");
  display.print(hum);
  display.println(" %"); // Adiciona unidade
  
  display.display(); // Atualiza a tela
}