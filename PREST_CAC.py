import streamlit as st
import pandas as pd
from urllib.error import URLError

# -------------------- CONFIGURAÇÕES INICIAIS --------------------
st.set_page_config(page_title="📂 Dashboard Documental", layout="wide")

st.title("📂 DASHBOARD DOCUMENTAL")
st.markdown("**Sistema de Classificação Documental com Filtros Dinâmicos e Visualização Fuzzy**")

# -------------------- CONFIGURAÇÕES FUZZY --------------------
DICIONARIO_LOGICO = {
    'pertinencia_alta': 0.9,
    'pertinencia_media': 0.75,
    'pertinencia_baixa': 0.6
}

# -------------------- CARREGAMENTO DE DADOS --------------------
@st.cache_data(show_spinner="Carregando dados...")
def load_data():
    try:
        sheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQMXKjpKX5zUTvnv1609z3cnmU3FtTmDy4Y0NHYgEMFc78ZjC0ZesQoNeYafZqWtSl_deKwwBI1W0AB/pub?output=csv'
        df = pd.read_csv(sheet_url)
        df['Ano'] = df['Nome'].str.extract(r'(\d{4})')
        df['Municipio'] = df['Nome'].str.extract(r'(BENEDITO LEITE|[A-Z ]{3,})')
        df['Artefato'] = df['Subclasse_Funcional']
        return df
    except URLError:
        st.error("Erro ao acessar os dados online. Verifique a conexão ou a URL da planilha.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # -------------------- FILTROS DINÂMICOS --------------------
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        ano_filter = st.multiselect('Ano:', options=sorted(df['Ano'].dropna().unique()), default=sorted(df['Ano'].dropna().unique()))
    with col2:
        municipio_filter = st.multiselect('Município:', options=df['Municipio'].dropna().unique(), default=df['Municipio'].dropna().unique())
    with col3:
        classe_filter = st.multiselect('Classe:', options=df['Classe_Final_V2'].unique(), default=df['Classe_Final_V2'].unique())
    with col4:
        artefato_filter = st.multiselect('Artefato:', options=df['Artefato'].unique(), default=df['Artefato'].unique())

    filtered_df = df[
        (df['Ano'].isin(ano_filter)) &
        (df['Municipio'].isin(municipio_filter)) &
        (df['Classe_Final_V2'].isin(classe_filter)) &
        (df['Artefato'].isin(artefato_filter))
    ]

    # -------------------- ABA NAVEGAÇÃO --------------------
    menu = st.sidebar.selectbox("Navegar", ["📊 Resumo Fuzzy", "📑 Estatísticas", "📂 Documentos Classificados"])

    if menu == "📊 Resumo Fuzzy":
        st.subheader('Resumo Fuzzy por Ano e Classe')
        resumo = filtered_df.groupby(['Ano', 'Classe_Final_V2']).size().reset_index(name='Contagem')
        resumo['Pertinência'] = resumo['Contagem'].apply(lambda x: DICIONARIO_LOGICO['pertinencia_alta'] if x >= 10 else (DICIONARIO_LOGICO['pertinencia_media'] if x >= 5 else DICIONARIO_LOGICO['pertinencia_baixa']))
        st.dataframe(resumo, use_container_width=True)

    elif menu == "📑 Estatísticas":
        st.subheader('Resumo Estatístico Detalhado')
        count_table = filtered_df.groupby(['Ano', 'Classe_Final_V2']).size().reset_index(name='Contagem')
        st.dataframe(count_table)

    elif menu == "📂 Documentos Classificados":
        st.subheader('Documentos Classificados por Tipologia')
        table_links = filtered_df[['Nome', 'Ano', 'Municipio', 'Classe_Final_V2', 'Artefato', 'Link']]
        def make_clickable(link):
            return f'<a href="{link}" target="_blank">Abrir Documento</a>'
        table_links['Link'] = table_links['Link'].apply(lambda x: make_clickable(x) if pd.notnull(x) else '')
        st.write(table_links.to_html(escape=False, index=False), unsafe_allow_html=True)

    # -------------------- RODAPÉ --------------------
    st.markdown("---")
    st.caption('Dashboard Documental | Classificação & Visualização Fuzzy | Powered by Streamlit')
else:
    st.warning("Não foi possível carregar os dados. Verifique a URL ou sua conexão.")
