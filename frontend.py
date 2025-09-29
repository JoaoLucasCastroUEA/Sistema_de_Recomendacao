import streamlit as st
import pandas as pd
import time
import requests

API_URL = "http://localhost:5000"

st.set_page_config(
    page_title="Sistema de Recomendação de Filmes",
    page_icon="🎬",
    layout="wide"
)

# --- Carregar catálogo do backend ---
try:
    res = requests.get(f"{API_URL}/filmes")
    catalogo_df = pd.DataFrame(res.json())
    catalogo_df.rename(columns={'movieId': 'ID', 'title': 'Nome'}, inplace=True)
except Exception:
    st.warning("Não foi possível carregar filmes do backend.")
    catalogo_df = pd.DataFrame([])

if 'avaliacoes_usuario' not in st.session_state:
    st.session_state.avaliacoes_usuario = {}

st.title("🎬 Sistema de Recomendação de Filmes")
st.markdown("Avalie filmes e receba recomendações personalizadas.")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Avalie os Filmes")
    usuario_id = st.text_input("Digite seu ID de Usuário:", "HokageDaParaiba69")
    st.markdown("---")

    filmes_disponiveis = catalogo_df[~catalogo_df['Nome'].isin(st.session_state.avaliacoes_usuario.keys())]

    filme_selecionado = st.selectbox(
        "Selecione um filme:",
        options=filmes_disponiveis['Nome'] if not filmes_disponiveis.empty else [],
        index=None,
        placeholder="Busque por um filme..."
    )

    if filme_selecionado:
        nota = st.slider(f"Sua nota para '{filme_selecionado}'", 1, 5, 3)

        if st.button(f"Adicionar Avaliação"):
            res = requests.post(f"{API_URL}/avaliar", json={
                "usuario_id": usuario_id,
                "filme": filme_selecionado,
                "nota": nota
            })
            if res.status_code == 200:
                st.session_state.avaliacoes_usuario[filme_selecionado] = nota
                st.success(f"'{filme_selecionado}' avaliado com nota {nota}!")
                st.rerun()
            else:
                st.error("Erro ao salvar avaliação.")

    if st.session_state.avaliacoes_usuario:
        st.markdown("---")
        st.subheader("Suas Avaliações:")
        for filme, nota in st.session_state.avaliacoes_usuario.items():
            st.markdown(f"- **{filme}**: `{nota} estrelas`")

with col2:
    st.header("2. Gere suas Recomendações")

    if st.button("Obter Recomendações", type="primary"):
        if not usuario_id:
            st.warning("Por favor, insira um ID de usuário.")
        else:
            with st.spinner('Gerando recomendações...'):
                res = requests.get(f"{API_URL}/recomendacoes/{usuario_id}")
                if res.status_code == 200:
                    recomendacoes = res.json()
                    st.subheader("🎉 Recomendados para você:")
                    for r in recomendacoes:
                        st.success(f"✔️ **{r['title']}**")
                else:
                    st.error("Erro ao gerar recomendações.")
