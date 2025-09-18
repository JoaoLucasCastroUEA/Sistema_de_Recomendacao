import streamlit as st
import pandas as pd
import time

# --- Configuração da Página ---
st.set_page_config(
    page_title="Sistema de Recomendação de Filmes",
    page_icon="🎬",
    layout="wide"
)

# --- Carregamento dos Dados ---
# O frontend precisa de um catálogo de itens para mostrar ao usuário o que pode ser avaliado.
try:
    catalogo_df = pd.read_csv('dataset/movie.csv')
    # Renomeia as colunas do seu dataset para as colunas que o app espera ('ID' e 'Nome')
    catalogo_df.rename(columns={'movieId': 'ID', 'title': 'Nome'}, inplace=True)
except FileNotFoundError:
    st.warning("Arquivo 'movie.csv' não encontrado. Usando um catálogo de exemplo.")
    catalogo_df = pd.DataFrame({
    'ID': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
           111, 112, 113, 114, 115],
    'Nome': [
        'O Poderoso Chefão', 'O Senhor dos Anéis: A Sociedade do Anel', 'Interestelar',
        'A Origem', 'Pulp Fiction', 'Batman: O Cavaleiro das Trevas',
        'Clube da Luta', 'Forrest Gump', 'Matrix', 'Gladiador',
        'A Lista de Schindler', 'Cidade de Deus', 'Os Infiltrados',
        'O Silêncio dos Inocentes', 'Django Livre'
    ]
})

# --- Inicialização do Estado da Sessão ---
# Usamos o session_state para guardar as avaliações do usuário na sessão atual.
if 'avaliacoes_usuario' not in st.session_state:
    st.session_state.avaliacoes_usuario = {}

# --- Título e Descrição ---
st.title("🎬 Sistema de Recomendação de Filmes")
st.markdown("Adicione os filmes que você já assistiu e dê uma nota para receber recomendações personalizadas.")

# --- Layout em Colunas ---
col1, col2 = st.columns([1, 1])

# Coluna da Esquerda: Entrada de Dados
with col1:
    st.header("1. Avalie os Filmes")
    usuario_id = st.text_input("Digite seu ID de Usuário (ex: 'user101'):", "user101")
    st.markdown("---")

    # --- Nova Interface de Avaliação ---
    
    # Filtra o catálogo para não mostrar filmes que já foram avaliados
    filmes_disponiveis = catalogo_df[~catalogo_df['Nome'].isin(st.session_state.avaliacoes_usuario.keys())]
    
    # Campo de seleção com autocomplete
    filme_selecionado = st.selectbox(
        "Digite e selecione o nome do filme:",
        options=filmes_disponiveis['Nome'],
        index=None, # Garante que nada esteja pré-selecionado
        placeholder="Busque por um filme..."
    )

    if filme_selecionado:
        nota = st.slider(f"Sua nota para '{filme_selecionado}'", 1, 5, 3)

        if st.button(f"Adicionar Avaliação para '{filme_selecionado}'"):
            # Adiciona a avaliação ao estado da sessão
            st.session_state.avaliacoes_usuario[filme_selecionado] = nota
            st.success(f"'{filme_selecionado}' avaliado com nota {nota}!")
            # Força o rerender para atualizar a lista de filmes
            st.rerun()
    
    # --- Exibição das avaliações já feitas ---
    if st.session_state.avaliacoes_usuario:
        st.markdown("---")
        st.subheader("Suas Avaliações:")
        for filme, nota in st.session_state.avaliacoes_usuario.items():
            st.markdown(f"- **{filme}**: `{nota} estrelas`")

# Coluna da Direita: Geração e Exibição dos Resultados
with col2:
    st.header("2. Gere suas Recomendações")
    st.markdown("Quando terminar de avaliar, clique no botão para obter suas recomendações.")

    if st.button("Obter Recomendações", type="primary"):
        if not usuario_id:
            st.warning("Por favor, insira um ID de usuário.")
        elif not st.session_state.avaliacoes_usuario:
            st.warning("Você precisa avaliar pelo menos um filme para gerar recomendações.")
        else:
            with st.spinner('Gerando recomendações...'):
                time.sleep(2)

            st.subheader("🎉 Itens Recomendados para Você:")

            recomendacoes_falsas = ["A Viagem de Chihiro", "Psicose", "O Iluminado"]
            for filme in recomendacoes_falsas:
                st.success(f"✔️ **{filme}**")
            
            st.info("Nota: Esta é uma lista de exemplo. A lógica de backend não está conectada.")

