import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

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
        # A. AUTENTICAÇÃO SEGURA USANDO STREAMLIT SECRETS
        # st.secrets carrega as chaves do seu arquivo de configuração seguro (secrets.toml)
        
        # Certifique-se de que o nome da chave (gcp_service_account) corresponde ao seu secrets.toml
        creds_json = dict(st.secrets["gcp_service_account"])
        
        scope = ['https://www.googleapis.com/auth/spreadsheets', 
                 'https://www.googleapis.com/auth/drive']
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
        client = gspread.authorize(creds)

        # B. ACESSO E LEITURA DA PLANILHA
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        data = worksheet.get_all_values()
        
        # Criação do DataFrame
        headers = data[0]
        data_rows = data[1:]
        df = pd.DataFrame(data_rows, columns=headers)
        
        # O Streamlit armazena os dados em strings, precisamos convertê-los, se necessário
        # Exemplo simples de limpeza/conversão:
        # df['Preço'] = pd.to_numeric(df['Preço'].str.replace('R$', '').str.replace(',', '.'), errors='coerce')
        
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
    # Usaremos uma tabela simples como visualização inicial
    st.dataframe(df.head(10)) 
    
    st.success(f"Dados carregados com sucesso. Total de {len(df)} linhas.")

    # Se você quiser permitir que os usuários atualizem os dados manualmente, use:
    if st.button("Puxar Dados Mais Recentes"):
        st.cache_data.clear()
        st.experimental_rerun()
        
else:
    st.warning("Não foi possível carregar os dados. Verifique as credenciais ou o compartilhamento da planilha.")