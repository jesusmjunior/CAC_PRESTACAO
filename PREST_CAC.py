import streamlit as st
import pandas as pd

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
    file_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQMXKjpKX5zUTvnv1609z3cnmU3FtTmDy4Y0NHYgEMFc78ZjC0ZesQoNeYafZqWtSl_deKwwBI1W0AB/pub?output=csv'
    df = pd.read_csv(file_url)
    return df

df = load_data()

if not df.empty:
    # -------------------- PRÉ-PROCESSAMENTO --------------------
    df.columns = df.columns.str.strip()  # Sanitização de espaços nos nomes das colunas
    df['Ano'] = df['Nome'].str.extract(r'(\d{4})')
    df['Artefato'] = df['Subclasse_Funcional']

    municipios = df['Municipio'].dropna().unique() if 'Municipio' in df.columns else []

    # -------------------- VISÃO GERAL --------------------
    st.markdown("### 📊 Painel Geral de Gestão Documental")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Documentos", len(df))
    with col2:
        st.metric("Total Municípios", len(municipios))
    with col3:
        st.metric("Classes Primárias", df['Classe_Final_V2'].nunique() if 'Classe_Final_V2' in df.columns else 0)

    if 'Classe_Final_V2' in df.columns:
        st.bar_chart(df['Classe_Final_V2'].value_counts().head(10))

    # -------------------- FILTROS DINÂMICOS SIMPLIFICADOS --------------------
    with st.sidebar:
        st.subheader("🔎 Filtros Documentais")
        ano_filter = st.multiselect('Ano', sorted(df['Ano'].dropna().unique()), default=sorted(df['Ano'].dropna().unique()))
        municipio_filter = st.multiselect('Município', sorted(municipios), default=sorted(municipios))
        classe_filter = st.multiselect('Classe', sorted(df['Classe_Final_V2'].dropna().unique()) if 'Classe_Final_V2' in df.columns else [], default=sorted(df['Classe_Final_V2'].dropna().unique()) if 'Classe_Final_V2' in df.columns else [])

    filtered_df = df[
        (df['Ano'].isin(ano_filter)) &
        (df['Municipio'].isin(municipio_filter) if 'Municipio' in df.columns else True) &
        (df['Classe_Final_V2'].isin(classe_filter) if 'Classe_Final_V2' in df.columns else True)
    ]

    st.markdown("---")
    st.markdown("### 📄 Documentos Filtrados")
    display_columns = ['Nome', 'Ano', 'Municipio', 'Classe_Final_V2', 'Subclasse_Funcional', 'Link']
    available_columns = [col for col in display_columns if col in df.columns]
    st.dataframe(filtered_df[available_columns], use_container_width=True)

    # -------------------- MÉTRICA DE REGULARIDADE --------------------
    st.markdown("---")
    st.markdown("### 📈 Índice R_i de Regularidade Documental")
    indice_ri = len(filtered_df) / len(df) if len(df) > 0 else 0
    pertinencia = "Alta" if indice_ri >= DICIONARIO_LOGICO['pertinencia_alta'] else ("Média" if indice_ri >= DICIONARIO_LOGICO['pertinencia_media'] else "Baixa")
    st.write(f"**R_i = {indice_ri:.2f} | Pertinência: {pertinencia}**")

    # -------------------- HIERARQUIA CLASSE → SUBCLASSE → ATRIBUTO --------------------
    st.markdown("---")
    st.markdown("### 🔎 Hierarquia Documental")
    if 'Classe_Final_V2' in df.columns and 'Subclasse_Funcional' in df.columns and 'Atributo_Funcional' in df.columns:
        agrupado = filtered_df.groupby(['Classe_Final_V2', 'Subclasse_Funcional', 'Atributo_Funcional']).size().reset_index(name='Total')
        st.dataframe(agrupado)

    # -------------------- RODAPÉ --------------------
    st.markdown("---")
    st.caption('Dashboard Documental | Visualização Fuzzy & Teoria de Conjuntos | Powered by Streamlit')
else:
    st.warning("Não foi possível carregar os dados. Verifique a URL ou sua conexão.")
