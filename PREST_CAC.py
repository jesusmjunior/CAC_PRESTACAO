import streamlit as st
import pandas as pd
from urllib.error import URLError

# -------------------- CONFIGURAÇÕES INICIAIS --------------------
st.set_page_config(page_title="📂 Dashboard Documental", layout="wide")

st.title("📂 DASHBOARD DOCUMENTAL")
st.markdown("**Gestão Documental Integrada | Aplicação de Teoria de Conjuntos + Lógica Fuzzy**")

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
        file_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQMXKjpKX5zUTvnv1609z3cnmU3FtTmDy4Y0NHYgEMFc78ZjC0ZesQoNeYafZqWtSl_deKwwBI1W0AB/pub?output=csv'
        df = pd.read_csv(file_url)
        return df
    except URLError:
        st.error("Erro ao acessar os dados online. Verifique a conexão ou a URL da planilha.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # -------------------- PRÉ-PROCESSAMENTO --------------------
    df['Ano'] = df['Nome'].str.extract(r'(\d{4})')
    df['Artefato'] = df['Subclasse_Funcional']

    # -------------------- VISÃO GERAL --------------------
    st.markdown("### 📊 Painel Geral de Gestão Documental")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Documentos", len(df))
    with col2:
        st.metric("Total Municípios", df['Municipio'].nunique())
    with col3:
        st.metric("Classes Primárias", df['Classe_Final_V2'].nunique())

    st.bar_chart(df['Classe_Final_V2'].value_counts().head(10))

    # -------------------- FILTROS DINÂMICOS SIMPLIFICADOS --------------------
    with st.sidebar:
        st.subheader("🔎 Filtros Documentais")
        ano_filter = st.multiselect('Ano', sorted(df['Ano'].dropna().unique()), default=sorted(df['Ano'].dropna().unique()))
        municipio_filter = st.multiselect('Município', sorted(df['Municipio'].dropna().unique()), default=sorted(df['Municipio'].dropna().unique()))
        classe_filter = st.multiselect('Classe', sorted(df['Classe_Final_V2'].dropna().unique()), default=sorted(df['Classe_Final_V2'].dropna().unique()))

    filtered_df = df[
        (df['Ano'].isin(ano_filter)) &
        (df['Municipio'].isin(municipio_filter)) &
        (df['Classe_Final_V2'].isin(classe_filter))
    ]

    st.markdown("---")
    st.markdown("### 📄 Documentos Filtrados")
    st.dataframe(filtered_df[['Nome', 'Ano', 'Municipio', 'Classe_Final_V2', 'Subclasse_Funcional', 'Link']], use_container_width=True)

    # -------------------- MÉTRICA DE REGULARIDADE --------------------
    st.markdown("---")
    st.markdown("### 📈 Índice R_i de Regularidade Documental")
    indice_ri = len(filtered_df) / len(df) if len(df) > 0 else 0
    pertinencia = "Alta" if indice_ri >= DICIONARIO_LOGICO['pertinencia_alta'] else ("Média" if indice_ri >= DICIONARIO_LOGICO['pertinencia_media'] else "Baixa")
    st.write(f"**R_i = {indice_ri:.2f} | Pertinência: {pertinencia}**")

    # -------------------- HIERARQUIA CLASSE → SUBCLASSE → ATRIBUTO --------------------
    st.markdown("---")
    st.markdown("### 🔎 Hierarquia Documental")
    agrupado = filtered_df.groupby(['Classe_Final_V2', 'Subclasse_Funcional', 'Atributo_Funcional']).size().reset_index(name='Total')
    st.dataframe(agrupado)

    # -------------------- RODAPÉ --------------------
    st.markdown("---")
    st.caption('Dashboard Documental | Visualização Fuzzy & Teoria de Conjuntos | Powered by Streamlit')
else:
    st.warning("Não foi possível carregar os dados. Verifique a URL ou sua conexão.")
