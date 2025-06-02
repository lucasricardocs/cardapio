import streamlit as st
import requests
from bs4 import BeautifulSoup
import hashlib
import pandas as pd
from datetime import datetime
import time

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
            # Adiciona timestamp para evitar cache
            timestamp = int(time.time())
            url_com_cache = f"{url}?v={timestamp}"
            
            response = requests.get(url_com_cache, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Parse do HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove scripts e estilos
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Obtém o texto limpo
                conteudo = soup.get_text()
                
                # Gera hash MD5 do conteúdo
                hash_conteudo = hashlib.md5(conteudo.encode('utf-8')).hexdigest()
                
                return hash_conteudo, True, "OK", conteudo[:200]
            else:
                return None, False, f"Erro HTTP {response.status_code}", ""
                
        except requests.exceptions.RequestException as e:
            return None, False, f"Erro de conexão: {str(e)}", ""
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
            'Detalhes': detalhes[:100] + "..." if len(detalhes) > 100 else detalhes
        })
        
        # Manter apenas os últimos 50 registros
        if len(st.session_state.historico) > 50:
            st.session_state.historico = st.session_state.historico[-50:]

def enviar_notificacao(url, timestamp):
    """Envia notificação compatível com Streamlit Cloud"""
    # Notificação visual no Streamlit
    st.success(f"🚨 **SITE ATUALIZADO!**")
    st.write(f"**URL:** {url}")
    st.write(f"**Horário:** {timestamp}")
    
    # Efeito visual
    st.balloons()
    
    # Toast notification
    st.toast("Site atualizado!", icon="🚨")

def main():
    st.title("🔍 Monitor de Sites em Tempo Real")
    st.markdown("Sistema de monitoramento que verifica atualizações em sites a cada 60 segundos")
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
        
        # Intervalo de verificação
        intervalo = st.selectbox(
            "Intervalo de verificação:",
            [30, 60, 120, 300, 600],
            index=1,
            format_func=lambda x: f"{x//60} minutos" if x >= 60 else f"{x} segundos"
        )
        
        st.info(f"🕐 Verificação a cada {intervalo} segundos")
        
        # Botões de controle
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ Iniciar", type="primary", use_container_width=True):
                st.session_state.monitoramento_ativo = True
                st.session_state.hash_anterior = None  # Reset para nova baseline
                st.success("✅ Monitoramento iniciado!")
        
        with col2:
            if st.button("⏹️ Parar", use_container_width=True):
                st.session_state.monitoramento_ativo = False
                st.info("⏸️ Monitoramento pausado")
        
        # Verificação manual
        if st.button("🔄 Verificação Manual", use_container_width=True):
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
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Status do Monitoramento")
        status_container = st.empty()
        
    with col2:
        st.subheader("📈 Estatísticas")
        
        # Métricas
        if st.session_state.historico:
            df_historico = pd.DataFrame(st.session_state.historico)
            total_verificacoes = len(df_historico)
            atualizacoes_detectadas = len(df_historico[df_historico['Status'] == 'ATUALIZAÇÃO DETECTADA'])
            erros = len(df_historico[df_historico['Status'].str.contains('Erro', na=False)])
            
            st.metric("Total de Verificações", total_verificacoes)
            st.metric("Atualizações Detectadas", atualizacoes_detectadas)
            st.metric("Erros", erros)
            
            if st.session_state.ultima_atualizacao:
                st.metric("Última Atualização", st.session_state.ultima_atualizacao.strftime("%H:%M:%S"))
        else:
            st.metric("Total de Verificações", 0)
            st.metric("Atualizações Detectadas", 0)
            st.metric("Erros", 0)
    
    # Fragment para monitoramento automático
    if st.session_state.monitoramento_ativo:
        run_every = intervalo
    else:
        run_every = None
    
    @st.fragment(run_every=run_every)
    def monitorar_site():
        if not st.session_state.monitoramento_ativo:
            return
        
        url = st.session_state.url_monitorar
        hash_atual, sucesso, mensagem, preview = monitor.verificar_site(url)
        timestamp = datetime.now()
        
        st.session_state.contador_verificacoes += 1
        
        if sucesso:
            if st.session_state.hash_anterior is None:
                # Primeira verificação - estabelecer baseline
                st.session_state.hash_anterior = hash_atual
                status = "Baseline Estabelecido"
                
                with status_container:
                    st.info(f"📝 **Baseline estabelecido**")
                    st.write(f"**Horário:** {timestamp.strftime('%d/%m/%Y às %H:%M:%S')}")
                    st.write(f"**URL:** {url}")
                    st.write(f"**Verificações:** {st.session_state.contador_verificacoes}")
                
                monitor.salvar_historico(url, status, "Primeira verificação realizada")
            
            elif hash_atual != st.session_state.hash_anterior:
                # ATUALIZAÇÃO DETECTADA!
                st.session_state.hash_anterior = hash_atual
                st.session_state.ultima_atualizacao = timestamp
                status = "ATUALIZAÇÃO DETECTADA"
                
                with status_container:
                    enviar_notificacao(url, timestamp.strftime('%d/%m/%Y às %H:%M:%S'))
                    st.write(f"**Verificações:** {st.session_state.contador_verificacoes}")
                
                monitor.salvar_historico(url, status, preview)
            
            else:
                # Sem mudanças
                status = "Sem Alterações"
                
                with status_container:
                    st.success(f"✅ **Monitoramento Ativo**")
                    st.write(f"**Última verificação:** {timestamp.strftime('%H:%M:%S')}")
                    st.write(f"**URL:** {url}")
                    st.write(f"**Status:** Sem alterações detectadas")
                    st.write(f"**Verificações:** {st.session_state.contador_verificacoes}")
                
                monitor.salvar_historico(url, status, "")
        
        else:
            # Erro na verificação
            status = f"Erro: {mensagem}"
            
            with status_container:
                st.error(f"❌ **Erro na Verificação**")
                st.write(f"**Horário:** {timestamp.strftime('%H:%M:%S')}")
                st.write(f"**Erro:** {mensagem}")
                st.write(f"**Verificações:** {st.session_state.contador_verificacoes}")
            
            monitor.salvar_historico(url, status, mensagem)
    
    # Executar o fragment
    monitorar_site()
    
    # Histórico de verificações
    st.markdown("---")
    st.subheader("📋 Histórico de Verificações")
    
    if st.session_state.historico:
        df_historico = pd.DataFrame(st.session_state.historico)
        
        # Filtros
        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            status_filtro = st.selectbox(
                "Filtrar por status:",
                ["Todos"] + list(df_historico['Status'].unique())
            )
        
        with col_filtro2:
            quantidade = st.selectbox(
                "Mostrar últimos:",
                [10, 20, 50],
                index=1
            )
        
        # Aplicar filtros
        if status_filtro != "Todos":
            df_filtrado = df_historico[df_historico['Status'] == status_filtro]
        else:
            df_filtrado = df_historico
        
        # Limitar quantidade e ordenar
        df_final = df_filtrado.tail(quantidade).sort_values('Timestamp', ascending=False)
        
        # Exibir tabela
        st.dataframe(
            df_final,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Timestamp": st.column_config.DatetimeColumn(
                    "Data/Hora",
                    format="DD/MM/YYYY HH:mm:ss"
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
        
        # Download do histórico
        if st.button("📥 Baixar Histórico CSV"):
            csv = df_historico.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"historico_monitoramento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    else:
        st.info("Nenhuma verificação realizada ainda. Clique em 'Iniciar' para começar o monitoramento.")
    
    # Footer
    st.markdown("---")
    st.markdown("**💡 Dica:** Deixe esta aba aberta para manter o monitoramento ativo.")

if __name__ == "__main__":
    main()
