import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

API_URL = "http://localhost:5000"

if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

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
if 'feedback_pendentes' not in st.session_state:
    st.session_state.feedback_pendentes = {}
if 'recomendacoes_atuais' not in st.session_state:
    st.session_state.recomendacoes_atuais = []
if 'historico_recomendacoes' not in st.session_state:
    st.session_state.historico_recomendacoes = []


def main():
    def navigate_to(page_name):
        st.session_state.current_page = page_name

    with st.sidebar:
        st.header("⚡ Menu rápido")
        st.subheader("Qual vai ser seu próximo passo?")

        # Botões para navegação
        if st.button("Avaliar filmes.", use_container_width=True,
                     type='primary' if st.session_state.current_page == "home" else 'secondary'):
            navigate_to("home")

        if st.button("Feedback das recomendações", use_container_width=True,
                     type='primary' if st.session_state.current_page == "feedback" else 'secondary'):
            navigate_to("feedback")

    if st.session_state.current_page == "home":
        st.title("🎬 Sistema de Recomendação de Filmes")
        st.markdown("Avalie filmes e receba recomendações personalizadas.")

        with st.expander("👨‍🏫 **Sobre o programa**", expanded=False):
            st.write("- 🎬 Avalie filmes.")
            st.write("- 👥 Encontre conexões com gostos parecidos com os seus.")
            st.write("- 🎯 Receba recomendações de Filmes")

        col1, col2 = st.columns(2)

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

        with col2:
            st.header("Gere suas Recomendações")

            if st.button("Obter Novas Recomendações", type="primary"):
                if not usuario_id:
                    st.warning("Por favor, insira um ID de usuário.")
                else:
                    with st.spinner('Gerando recomendações...'):
                        res = requests.get(f"{API_URL}/recomendacoes/{usuario_id}")
                        if res.status_code == 200:
                            recomendacoes = res.json()
                            st.session_state.recomendacoes_atuais = recomendacoes
                            st.session_state.feedback_pendentes = {}

                            # Adicionar ao histórico de recomendações feitas
                            for rec in recomendacoes:
                                if rec['movieId'] not in st.session_state.historico_recomendacoes:
                                    st.session_state.historico_recomendacoes.append(rec['movieId'])

                            st.balloons()
                        else:
                            st.error("Erro ao gerar recomendações.")

            # Mostrar recomendações se existirem
            if st.session_state.recomendacoes_atuais:
                st.subheader("🎉 Recomendados para você:")

                # Filtrar recomendações que ainda não foram curtidas
                recomendacoes_nao_curtidas = []
                for r in st.session_state.recomendacoes_atuais:
                    # Verificar se não está nos feedbacks pendentes nem nos feedbacks salvos
                    if (str(r['movieId']) not in st.session_state.feedback_pendentes and
                            str(r['movieId']) not in st.session_state.feedback):
                        recomendacoes_nao_curtidas.append(r)

                if recomendacoes_nao_curtidas:
                    for r in recomendacoes_nao_curtidas:
                        colA, colB = st.columns([3, 1])
                        with colA:
                            st.info(f"🎬 **{r['title']}**")

                        with colB:
                            if st.button("👍 Curtir", key=f"like_{r['movieId']}"):
                                st.session_state.feedback_pendentes[str(r['movieId'])] = True
                                st.rerun()
                else:
                    st.info(
                        "🎊 Todas as recomendações atuais já foram avaliadas! Clique em 'Obter Novas Recomendações' para mais sugestões.")

                # Botão para enviar todos os feedbacks pendentes
                if st.session_state.feedback_pendentes:
                    st.markdown("---")
                    st.subheader("📤 Enviar Feedbacks")
                    st.write(f"**Curtidas pendentes:** {len(st.session_state.feedback_pendentes)}")

                    if st.button("💾 Salvar Todas as Curtidas", type="primary"):
                        with st.spinner('Salvando curtidas...'):
                            todos_salvos = True
                            for filme_id, liked in st.session_state.feedback_pendentes.items():
                                res_fb = requests.post(f"{API_URL}/feedback", json={
                                    "usuario_id": usuario_id,
                                    "movieId": int(filme_id),
                                    "liked": liked
                                })
                                if res_fb.status_code != 200:
                                    todos_salvos = False
                                    st.error(f"Erro ao salvar curtida para filme ID {filme_id}")

                            if todos_salvos:
                                # Atualizar feedbacks permanentes
                                st.session_state.feedback.update(st.session_state.feedback_pendentes)

                                # Remover as recomendações curtidas da lista atual
                                st.session_state.recomendacoes_atuais = [
                                    r for r in st.session_state.recomendacoes_atuais
                                    if str(r['movieId']) not in st.session_state.feedback_pendentes
                                ]

                                # Limpar feedbacks pendentes
                                st.session_state.feedback_pendentes = {}

                                st.success(
                                    "✅ Todas as curtidas foram salvas com sucesso! As recomendações curtidas foram removidas da lista.")
                                st.rerun()

                # Mostrar recomendações que já foram curtidas (apenas para informação)
                recomendacoes_curtidas = [
                    r for r in st.session_state.recomendacoes_atuais
                    if str(r['movieId']) in st.session_state.feedback
                ]

                if recomendacoes_curtidas:
                    st.markdown("---")
                    st.subheader("✅ Já Curtidos:")
                    for r in recomendacoes_curtidas:
                        st.success(f"🎬 **{r['title']}** - ✅ Curtiu")

            elif not st.session_state.recomendacoes_atuais and st.session_state.historico_recomendacoes:
                st.info(
                    "📝 Você já avaliou todas as recomendações atuais. Clique em 'Obter Novas Recomendações' para receber mais sugestões!")

    if st.session_state.current_page == "feedback":
        st.header("Acurácia do sistema de recomendação")

        usuario_id = st.text_input("Digite seu ID de Usuário para ver feedbacks:", "HokageDaParaiba69",
                                   key="feedback_user_id")

        if st.button("Carregar Estatísticas"):
            res = requests.get(f"{API_URL}/feedback/{usuario_id}")
            if res.status_code == 200:
                feedback_data = res.json()
                feedbacks = feedback_data.get("feedbacks", {})

                if feedbacks or st.session_state.historico_recomendacoes:
                    st.subheader("📊 Desempenho das Recomendações")

                    # Dados para comparação
                    total_recomendacoes_feitas = len(st.session_state.historico_recomendacoes)
                    total_recomendacoes_curtidas = sum(1 for v in feedbacks.values() if v)

                    # Atualizar session state
                    st.session_state.feedback = feedbacks

                    # Gráfico de comparação
                    fig, ax = plt.subplots(figsize=(10, 6))

                    # Preparar dados para o gráfico
                    categorias = ['Total de Recomendações\nFeitas', 'Recomendações\nCurtidas']
                    valores = [total_recomendacoes_feitas, total_recomendacoes_curtidas]
                    cores = ['#2196F3', '#4CAF50']  # Azul para total, Verde para curtidas

                    # Criar gráfico de barras
                    barras = ax.bar(categorias, valores, color=cores, alpha=0.8)

                    # Configurações do gráfico
                    ax.set_ylabel('Quantidade', fontsize=12)
                    ax.set_title('Comparação: Total de Recomendações vs Recomendações Curtidas',
                                 fontsize=14, fontweight='bold', pad=20)

                    # Adicionar valores nas barras
                    for barra, valor in zip(barras, valores):
                        height = barra.get_height()
                        ax.text(barra.get_x() + barra.get_width() / 2., height + 0.1,
                                f'{valor}', ha='center', va='bottom', fontsize=12, fontweight='bold')

                    # Adicionar linha de porcentagem
                    if total_recomendacoes_feitas > 0:
                        porcentagem = (total_recomendacoes_curtidas / total_recomendacoes_feitas) * 100
                        ax.axhline(y=total_recomendacoes_feitas, color='red', linestyle='--', alpha=0.7,
                                   label=f'Meta: 100% ({total_recomendacoes_feitas})')
                        ax.legend()

                    # Ajustar layout
                    plt.tight_layout()
                    st.pyplot(fig)

                    # Métricas em colunas
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Total de Recomendações Feitas",
                            total_recomendacoes_feitas
                        )

                    with col2:
                        st.metric(
                            "Recomendações Curtidas",
                            total_recomendacoes_curtidas
                        )

                    with col3:
                        if total_recomendacoes_feitas > 0:
                            taxa_acerto = (total_recomendacoes_curtidas / total_recomendacoes_feitas) * 100
                            st.metric(
                                "Taxa de Acerto",
                                f"{taxa_acerto:.1f}%",
                                delta=f"{taxa_acerto:.1f}%"
                            )
                        else:
                            st.metric("Taxa de Acerto", "0%")

                    # Estatísticas adicionais
                    st.subheader("📈 Estatísticas Detalhadas")

                    col_a, col_b = st.columns(2)

                    with col_a:
                        st.info(f"**📤 Recomendações Enviadas:** {total_recomendacoes_feitas}")
                        st.info(f"**✅ Curtidas Recebidas:** {total_recomendacoes_curtidas}")

                    with col_b:
                        if total_recomendacoes_feitas > 0:
                            st.warning(f"**📊 Eficiência do Sistema:** {taxa_acerto:.1f}%")
                            st.warning(f"**🎯 Potencial de Melhoria:** {100 - taxa_acerto:.1f}%")

                    # Mostrar detalhes das curtidas
                    if feedbacks:
                        st.subheader("📝 Detalhes das Curtidas")
                        for filme_id, liked in feedbacks.items():
                            if liked:  # Mostrar apenas os que foram curtidos
                                filme_info = catalogo_df[catalogo_df['ID'] == int(filme_id)]
                                if not filme_info.empty:
                                    filme_nome = filme_info['Nome'].iloc[0]
                                    st.write(f"- **{filme_nome}** ✅")
                else:
                    st.info("Nenhum dado de recomendação encontrado para este usuário.")
            else:
                st.error("Erro ao carregar feedbacks do servidor.")


if __name__ == "__main__":
    main()