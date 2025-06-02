import requests
from bs4 import BeautifulSoup
import hashlib
import time
import os
from datetime import datetime
from winotify import Notification
from dotenv import load_dotenv

class MonitorSite:
    def __init__(self):
        load_dotenv()
        self.url = os.getenv("URL_MONITORAR", "https://example.com")
        self.intervalo = int(os.getenv("INTERVALO_SEGUNDOS", "300"))  # 5 minutos padrão
        self.hash_anterior = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
        
    def obter_conteudo_site(self):
        """Obtém o conteúdo do site e retorna o hash MD5"""
        try:
            # Adiciona timestamp para evitar cache
            timestamp = int(time.time())
            url_com_cache = f"{self.url}?v={timestamp}"
            
            response = requests.get(url_com_cache, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Parse do HTML para extrair apenas o conteúdo relevante
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove scripts e estilos que podem mudar sem afetar o conteúdo
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Obtém o texto limpo
                conteudo = soup.get_text()
                
                # Gera hash MD5 do conteúdo
                hash_conteudo = hashlib.md5(conteudo.encode('utf-8')).hexdigest()
                return hash_conteudo, True
            else:
                print(f"Erro HTTP {response.status_code} ao acessar {self.url}")
                return None, False
                
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar o site: {e}")
            return None, False
    
    def enviar_notificacao_windows(self, mensagem):
        """Envia notificação do Windows"""
        try:
            notificacao = Notification(
                app_id="Monitor de Site",
                title="Site Atualizado!",
                msg=mensagem,
                duration="long",
                icon=None
            )
            notificacao.show()
            print("Notificação enviada!")
        except Exception as e:
            print(f"Erro ao enviar notificação: {e}")
    
    def enviar_notificacao_telegram(self, mensagem):
        """Envia notificação via Telegram (opcional)"""
        token = os.getenv("TELEGRAM_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if token and chat_id:
            try:
                url_telegram = f"https://api.telegram.org/bot{token}/sendMessage"
                dados = {
                    'chat_id': chat_id,
                    'text': mensagem
                }
                response = requests.post(url_telegram, data=dados)
                if response.status_code == 200:
                    print("Notificação Telegram enviada!")
                else:
                    print("Erro ao enviar notificação Telegram")
            except Exception as e:
                print(f"Erro no Telegram: {e}")
    
    def salvar_log(self, mensagem):
        """Salva log das verificações"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("monitor_log.txt", "a", encoding="utf-8") as arquivo:
            arquivo.write(f"[{timestamp}] {mensagem}\n")
    
    def iniciar_monitoramento(self):
        """Inicia o monitoramento contínuo do site"""
        print(f"Iniciando monitoramento de: {self.url}")
        print(f"Intervalo de verificação: {self.intervalo} segundos")
        
        # Primeira verificação para estabelecer baseline
        hash_atual, sucesso = self.obter_conteudo_site()
        if sucesso:
            self.hash_anterior = hash_atual
            mensagem = f"Monitoramento iniciado para {self.url}"
            print(mensagem)
            self.salvar_log(mensagem)
        else:
            print("Erro na verificação inicial. Tentando novamente...")
        
        while True:
            try:
                time.sleep(self.intervalo)
                
                hash_atual, sucesso = self.obter_conteudo_site()
                
                if sucesso:
                    if self.hash_anterior is None:
                        # Primeira verificação bem-sucedida
                        self.hash_anterior = hash_atual
                        mensagem = f"Baseline estabelecido para {self.url}"
                        print(mensagem)
                        self.salvar_log(mensagem)
                    
                    elif hash_atual != self.hash_anterior:
                        # Detectou mudança!
                        timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
                        mensagem = f"ATUALIZAÇÃO DETECTADA em {self.url} em {timestamp}"
                        
                        print("🚨 " + mensagem)
                        self.salvar_log(mensagem)
                        
                        # Envia notificações
                        self.enviar_notificacao_windows(f"{self.url} foi atualizado!")
                        self.enviar_notificacao_telegram(mensagem)
                        
                        # Atualiza o hash de referência
                        self.hash_anterior = hash_atual
                    
                    else:
                        # Sem mudanças
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        print(f"[{timestamp}] Verificação OK - Sem alterações")
                
                else:
                    print("Falha na verificação. Tentando novamente no próximo ciclo...")
                    
            except KeyboardInterrupt:
                print("\nMonitoramento interrompido pelo usuário.")
                self.salvar_log("Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                print(f"Erro inesperado: {e}")
                self.salvar_log(f"Erro inesperado: {e}")

if __name__ == "__main__":
    monitor = MonitorSite()
    monitor.iniciar_monitoramento()
