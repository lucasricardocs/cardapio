import streamlit as st
import requests
from bs4 import BeautifulSoup
import hashlib
import pandas as pd
from datetime import datetime
import time
import re

# Configuração da página
st.set_page_config(
    page_title="Monitor de Sites",
    page_icon="🔍",
    layout="wide"
)

class MonitorSite:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
    
    def verificar_site(self, url):
        """Verifica o site e retorna hash do conteúdo"""
        try:
            # Cache busting - evita cache do navegador/CDN
            timestamp = int(time.time())
            url_com_cache = f"{url}?v={timestamp}"
            
            response = requests.get(url_com_cache, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                # Parse do HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove elementos que mudam sem afetar conteúdo principal
                for elemento in soup(["script", "style", "noscript", "meta"]):
                    elemento.decompose()
                
                # Remove comentários HTML
                for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
                    comment.extract()
                
                # Obtém o texto limpo
                conteudo = soup.get_text()
                
                # Remove timestamps automáticos comuns
                conteudo = re.sub(r'\d{2}:\d{2}:\d{2}', '', conteudo)  # Remove horários
                conteudo = re.sub(r'\d{2}/\d{2}/\d{4}', '', conteudo)  # Remove datas
                conteudo = re.sub(r'\d{4}-\d{2}-\d{2}', '', conteudo)  # Remove datas ISO
                
                # Remove espaços extras e quebras de linha
                conteudo = ' '.join(conteudo.split())
                
                # Gera hash MD5 do conteúdo limpo
                hash_conteudo = hashlib.md5(conteudo.encode('utf-8')).hexdigest()
                
                return hash_conteudo, True, "OK", conteudo[:300]
            else:
                return None, False, f"Erro HTTP {response.status_code}", ""
                
        except requests.exceptions.Timeout:
            return None, False, "Timeout - Site demorou para responder", ""
        except requests.exceptions.ConnectionError:
            return None, False, "Erro de conexão - Site inacessível", ""
        except requests.exceptions.RequestException as e:
            return None, False, f"Erro de requisição: {str(e)}", ""
        except Exception as e:
            return None, False, f"Erro inesperado: {str(e)}", ""
    
    def salvar_historico(self, url, status, detalhes=""):
        """Salva o histórico de verificações"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if 'historico' not in st.session_state:
            st.session_state.historico = []
        
        st.session_state.historico.append({
            'Timestamp': timestamp,
            'URL': url,
            'Status': status,
            'Detalhes': detalhes[:150] + "..." if len(detalhes) > 150 else detalhes
        })
        
        # Manter apenas os últimos 100 registros
        if len(st.session_state.historico) > 100:
            st.session_state.historico = st.session_state.historico[-100:]

def enviar_notificacao(url, timestamp):
    """Envia notificação quando site é atualizado"""
    st.success(f"🚨 **SITE ATUALIZADO!**")
    st.write(f"**URL:** {url}")
    st.write(f"**Horário:** {timestamp}")
    
    # Efeitos visuais
    st.balloons()
    
    # Toast notification
    st.toast("🚨 Site atualizado!", icon="🔥")

def forcar_atualizacao():
    """Força atualização caso o fragment falhe"""
    if 'ultima_execucao' not in st.session_state:
        st.session_state.ultima_execucao = time.time()
    
    tempo_atual = time.time()
    if st.session_state.monitoramento_ativo and tempo_atual - st.session_state.ultima_execucao >= 60:
        st.session_state.ultima_execucao = tempo_atual
        st.rerun()

def main():
    st.title("🔍 Monitor de Sites em Tempo Real")
    st.markdown("Sistema que detecta atualizações em sites verificando a cada 1 minuto")
    st.markdown("---")
    
    monitor = MonitorSite()
    
    # Inicializar session state
    if "monitoramento_ativo" not in st.session_state:
        st.session_state.monitoramento_ativo = False
    if "url_monitorar" not in st.session_state:
        st.session_state.url_monitorar = "https://example.com"
    if "hash_anterior" not in st.session_state:
        st.session_state.hash_anterior = None
    if "historico" not in st.session_state:
        st.session_state.historico = []
    if "contador_verificacoes" not in st.session_state:
        st.session_state.contador_verificacoes = 0
    if "ultima_atualizacao" not in st.session_state:
        st.session_state.ultima_atualizacao = None
    if "proxima_verificacao" not in st.session_state:
        st.session_state.proxima_verificacao = None
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # URL para monitorar
        url_input = st.text_input(
            "URL para monitorar:",
            value=st.session_state.url_monitorar,
            help="Digite a URL completa do site que deseja monitorar"
        )
        st.session_state.url_monitorar = url_input
        
        # Intervalo fixo de 60 segundos
        st.info("🕐 **Intervalo fixo: 60 segundos (1 minuto)**")
        
        # Status do monitoramento
        if st.session_state.monitoramento_ativo:
            st.success("✅ Monitoramento ATIVO")
            if st.session_state.proxima_verificacao:
                tempo_restante = max(0, int(st.session_state.proxima_verificacao - time.time()))
                st.write(f"⏱️ Próxima verificação em: {tempo_restante}s")
        else:
            st.error("⏹️ Monitoramento PAUSADO")
        
        # Botões de controle
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ Iniciar", type="primary", use_container_width=True):
                st.session_state.monitoramento_ativo = True
                st.session_state.hash_anterior = None  # Reset baseline
                st.session_state.proxima_verificacao = time.time() + 60
                st.success("✅ Monitoramento iniciado!")
                st.rerun()
        
        with col2:
            if st.button("⏹️ Parar", use_container_width=True):
                st.session_state.monitoramento_ativo = False
                st.session_state.proxima_verificacao = None
                st.info("⏸️ Monitoramento pausado")
                st.rerun()
        
        # Verificação manual
        if st.button("🔄 Verificação Manual", use_container_width=True):
            with st.spinner("Verificando..."):
                hash_atual, sucesso, mensagem, preview = monitor.verificar_site(st.session_state.url_monitorar)
                if sucesso:
                    st.success("✅ Verificação manual concluída")
                    monitor.salvar_historico(st.session_state.url_monitorar, "Verificação Manual", preview)
                else:
                    st.error(f"❌ {mensagem}")
        
        # Botão para limpar histórico
        if st.button("🗑️ Limpar Histórico"):
            st.session_state.historico = []
            st.session_state.contador_verificacoes = 0
            st.success("Histórico limpo!")
            st.rerun()
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Status do Monitoramento")
        status_container = st.empty()
        
    with col2:
        st.subheader("📈 Estatísticas")
        
        # Métricas em tempo real
        if st.session_state.historico:
            df_historico = pd.DataFrame(st.session_state.historico)
            total_verificacoes = len(df_historico)
            atualizacoes_detectadas = len(df_historico[df_historico['Status'] == 'ATUALIZAÇÃO DETECTADA'])
            erros = len(df_historico[df_historico['Status'].str.contains('Erro', na=False)])
            
            st.metric("Total de Verificações", total_verificacoes)
            st.metric("Atualizações Detectadas", atualizacoes_detectadas, delta=None)
            st.metric("Taxa de Sucesso", f"{((total_verificacoes-erros)/total_verificacoes*100):.1f}%" if total_verificacoes > 0 else "0%")
            
            if st.session_state.ultima_atualizacao:
                st.metric("Última Atualização", st.session_state.ultima_atualizacao.strftime("%H:%M:%S"))
        else:
            st.metric("Total de Verificações", 0)
            st.metric("Atualizações Detectadas", 0)
            st.metric("Taxa de Sucesso", "0%")
    
    # Sistema de monitoramento com fragment + fallback
    if st.session_state.monitoramento_ativo:
        
        @st.fragment(run_every=60)
        def monitorar_site():
            if not st.session_state.monitoramento_ativo:
                return
            
            # Força atualização como backup
            forcar_atualizacao()
            
            url = st.session_state.url_monitorar
            
            with st.spinner("Verificando site..."):
                hash_atual, sucesso, mensagem, preview = monitor.verificar_site(url)
            
            timestamp = datetime.now()
            st.session_state.contador_verificacoes += 1
            st.session_state.proxima_verificacao = time.time() + 60
            
            if sucesso:
                if st.session_state.hash_anterior is None:
                    # Primeira verificação - estabelecer baseline
                    st.session_state.hash_anterior = hash_atual
                    status = "Baseline Estabelecido"
                    
                    with status_container:
                        st.info(f"📝 **Baseline estabelecido com sucesso**")
                        st.write(f"**Horário:** {timestamp.strftime('%d/%m/%Y às %H:%M:%S')}")
                        st.write(f"**URL:** {url}")
                        st.write(f"**Verificação:** #{st.session_state.contador_verificacoes}")
                        st.write(f"**Hash:** `{hash_atual[:16]}...`")
                    
                    monitor.salvar_historico(url, status, f"Hash inicial: {hash_atual[:16]}...")
                
                elif hash_atual != st.session_state.hash_anterior:
                    # ATUALIZAÇÃO DETECTADA!
                    hash_antigo = st.session_state.hash_anterior
                    st.session_state.hash_anterior = hash_atual
                    st.session_state.ultima_atualizacao = timestamp
                    status = "ATUALIZAÇÃO DETECTADA"
                    
                    with status_container:
                        enviar_notificacao(url, timestamp.strftime('%d/%m/%Y às %H:%M:%S'))
                        st.write(f"**Verificação:** #{st.session_state.contador_verificacoes}")
                        st.write(f"**Hash anterior:** `{hash_antigo[:16]}...`")
                        st.write(f"**Hash atual:** `{hash_atual[:16]}...`")
                    
                    monitor.salvar_historico(url, status, f"Mudança detectada: {hash_antigo[:8]}... → {hash_atual[:8]}...")
                
                else:
                    # Sem mudanças
                    status = "Sem Alterações"
                    
                    with status_container:
                        st.success(f"✅ **Monitoramento Ativo - Sem Alterações**")
                        st.write(f"**Última verificação:** {timestamp.strftime('%H:%M:%S')}")
                        st.write(f"**URL:** {url}")
                        st.write(f"**Verificação:** #{st.session_state.contador_verificacoes}")
                        st.write(f"**Hash atual:** `{hash_atual[:16]}...`")
                        
                        # Countdown para próxima verificação
                        tempo_restante = max(0, int(st.session_state.proxima_verificacao - time.time()))
                        st.write(f"**Próxima verificação em:** {tempo_restante} segundos")
                    
                    monitor.salvar_historico(url, status, f"Hash: {hash_atual[:16]}...")
            
            else:
                # Erro na verificação
                status = f"Erro: {mensagem}"
                
                with status_container:
                    st.error(f"❌ **Erro na Verificação**")
                    st.write(f"**Horário:** {timestamp.strftime('%H:%M:%S')}")
                    st.write(f"**Erro:** {mensagem}")
                    st.write(f"**Verificação:** #{st.session_state.contador_verificacoes}")
                    st.write("**Tentativa automática em 60 segundos...**")
                
                monitor.salvar_historico(url, status, mensagem)
        
        # Executar o fragment
        monitorar_site()
    
    else:
        # Monitoramento pausado
        with status_container:
            st.info("⏸️ **Monitoramento Pausado**")
            st.write("Clique em 'Iniciar' na barra lateral para começar o monitoramento.")
            st.write(f"**URL configurada:** {st.session_state.url_monitorar}")
    
    # Histórico de verificações
    st.markdown("---")
    st.subheader("📋 Histórico de Verificações")
    
    if st.session_state.historico:
        df_historico = pd.DataFrame(st.session_state.historico)
        
        # Filtros
        col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
        
        with col_filtro1:
            status_filtro = st.selectbox(
                "Filtrar por status:",
                ["Todos"] + sorted(list(df_historico['Status'].unique()))
            )
        
        with col_filtro2:
            quantidade = st.selectbox(
                "Mostrar últimos:",
                [10, 20, 50, 100],
                index=1
            )
        
        with col_filtro3:
            ordenacao = st.selectbox(
                "Ordenar por:",
                ["Mais recente primeiro", "Mais antigo primeiro"]
            )
        
        # Aplicar filtros
        if status_filtro != "Todos":
            df_filtrado = df_historico[df_historico['Status'] == status_filtro]
        else:
            df_filtrado = df_historico
        
        # Limitar quantidade e ordenar
        df_final = df_filtrado.tail(quantidade)
        if ordenacao == "Mais recente primeiro":
            df_final = df_final.sort_values('Timestamp', ascending=False)
        else:
            df_final = df_final.sort_values('Timestamp', ascending=True)
        
        # Exibir tabela com configuração personalizada
        st.dataframe(
            df_final,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Timestamp": st.column_config.TextColumn(
                    "Data/Hora",
                    width="medium"
                ),
                "Status": st.column_config.TextColumn(
                    "Status",
                    width="medium"
                ),
                "URL": st.column_config.LinkColumn(
                    "URL",
                    display_text="Link"
                ),
                "Detalhes": st.column_config.TextColumn(
                    "Detalhes",
                    width="large"
                )
            }
        )
        
        # Estatísticas do histórico
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            st.metric("Total de Registros", len(df_historico))
        with col_stat2:
            atualizacoes = len(df_historico[df_historico['Status'] == 'ATUALIZAÇÃO DETECTADA'])
            st.metric("Atualizações", atualizacoes)
        with col_stat3:
            erros = len(df_historico[df_historico['Status'].str.contains('Erro', na=False)])
            st.metric("Erros", erros)
        with col_stat4:
            if len(df_historico) > 0:
                taxa_sucesso = ((len(df_historico) - erros) / len(df_historico)) * 100
                st.metric("Taxa de Sucesso", f"{taxa_sucesso:.1f}%")
        
        # Download do histórico
        if st.button("📥 Baixar Histórico Completo"):
            csv = df_historico.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"historico_monitoramento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    else:
        st.info("📝 Nenhuma verificação realizada ainda.")
        st.write("**Para começar:**")
        st.write("1. Configure a URL na barra lateral")
        st.write("2. Clique em 'Iniciar' para começar o monitoramento")
        st.write("3. O sistema verificará o site a cada 60 segundos")
    
    # Footer com informações importantes
    st.markdown("---")
    st.markdown("### 💡 Informações Importantes")
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.info("""
        **Como funciona a detecção:**
        - Gera hash MD5 do conteúdo da página
        - Remove elementos que mudam automaticamente
        - Compara com hash anterior
        - Detecta qualquer mudança no texto
        """)
    
    with col_info2:
        st.warning("""
        **Para manter ativo:**
        - Mantenha esta aba aberta no navegador
        - Evite colocar o computador em modo sleep
        - Conexão com internet estável é necessária
        """)

if __name__ == "__main__":
    main()
