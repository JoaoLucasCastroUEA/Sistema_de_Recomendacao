import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

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
if 'feedback' not in st.session_state:
    st.session_state.feedback = {}

st.title("🎬 Sistema de Recomendação de Filmes")
st.markdown("Avalie filmes e receba recomendações personalizadas.")

col1, col2 = st.columns([1, 1])

# --- Coluna Esquerda (Avaliação) ---
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
            filme_id = int(catalogo_df[catalogo_df['Nome'] == filme_selecionado]['ID'].iloc[0])
            res = requests.post(f"{API_URL}/avaliar", json={
                "usuario_id": usuario_id,
                "movieId": filme_id,
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

# --- Coluna Direita (Recomendações + Feedback) ---
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
                        colA, colB = st.columns([3,1])
                        with colA:
                            st.info(f"🎬 **{r['title']}**")
                        with colB:
                            if st.button("👍 Curtir", key=f"like_{r['movieId']}"):
                                res_fb = requests.post(f"{API_URL}/feedback", json={
                                    "usuario_id": usuario_id,
                                    "movieId": r["movieId"],
                                    "liked": True
                                })
                                if res_fb.status_code == 200:
                                    st.session_state.feedback[r['title']] = True
                                    st.success(f"Você curtiu **{r['title']}**!")
                                    st.rerun()
                else:
                    st.error("Erro ao gerar recomendações.")

    if st.button("Obter feeddback", type="primary"):
        with st.spinner('Gerando recomendações...'):
            res = requests.get(f"{API_URL}/feedback/")
            if res.status_code == 200:
                if st.session_state.feedback:
                    st.subheader("📊 Desempenho das Recomendações")

                    total_recs = len(st.session_state.feedback)
                    curtidas = sum(1 for v in st.session_state.feedback.values() if v)

                    fig, ax = plt.subplots()
                    ax.bar(["Curtidas", "Total"], [curtidas, total_recs])
                    ax.set_ylabel("Quantidade")
                    ax.set_title("Proporção de Recomendações Validadas")
                    st.pyplot(fig)

                    st.markdown(f"✅ {curtidas} curtidas de {total_recs} recomendações recebidas.")
