import streamlit as st
import pandas as pd
import gspread
# oauth2client e json não são mais necessários com o método moderno do gspread.

# --- Configurações da Planilha ---
# Seu ID da planilha
SPREADSHEET_ID = '1fa4HLFfjIFKHjHBuxW_ymHkahVPzeoB_XlHNJMaNCg8'
# Nome exato da sua aba
WORKSHEET_NAME = 'Chevrolet Preços' 

# 1. FUNÇÃO DE CONEXÃO E CACHE
# O cache (ttl=600) garante que os dados sejam atualizados a cada 10 minutos
@st.cache_data(ttl=600) 
def load_data_from_gsheets():
    try:
        # A. AUTENTICAÇÃO MODERNA E SEGURA USANDO STREAMLIT SECRETS
        # st.secrets carrega as chaves do seu arquivo de configuração seguro (secrets.toml)
        creds_json = dict(st.secrets["gcp_service_account"])
        
        # Método moderno: gspread se autentica diretamente com o dicionário de chaves
        client = gspread.service_account_from_dict(creds_json)

        # B. ACESSO E LEITURA DA PLANILHA
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        data = worksheet.get_all_values()
        
        # Criação do DataFrame
        headers = data[0]
        data_rows = data[1:]
        df = pd.DataFrame(data_rows, columns=headers)
        
        return df

    except Exception as e:
        # Exibe uma mensagem de erro clara no painel
        st.error(f"⚠️ Erro ao carregar os dados. Verifique a chave 'gcp_service_account' no Secrets. Erro: {e}")
        return pd.DataFrame() 

# 2. ESTRUTURA DO PAINEL
st.title("💰 Painel de Preços Chevrolet")

# Carrega os dados
df = load_data_from_gsheets()

if not df.empty:
    st.subheader(f"Dados Carregados da Aba: {WORKSHEET_NAME}")
    
    # 3. EXEMPLO DE VISUALIZAÇÃO
    # Removemos o .head(10) para mostrar todos os dados e definimos uma altura para rolar.
    st.dataframe(df, height=600, use_container_width=True) 
    
    st.success(f"Dados carregados com sucesso. Total de {len(df)} linhas.")

    # 4. BOTÃO DE ATUALIZAÇÃO CORRIGIDO
    if st.button("Puxar Dados Mais Recentes"):
        # Limpa o cache para garantir que novos dados sejam buscados
        st.cache_data.clear()
        # CORREÇÃO CRÍTICA: st.rerun() é o comando moderno e funcional
        st.rerun()
        
else:
    st.warning("Não foi possível carregar os dados. Verifique as credenciais ou o compartilhamento da planilha.")
