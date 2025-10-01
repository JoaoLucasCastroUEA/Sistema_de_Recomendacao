from flask import Flask, request, jsonify
import pandas as pd
import json
import os
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)

# --- Carregar catálogo ---
movies_df = pd.read_csv("dataset/movie.csv")  # movieId, title, genres

# Pré-processamento: transformar gêneros em vetores
all_genres = set()
for g_list in movies_df['genres'].str.split('|'):
    all_genres.update(g_list)
all_genres = sorted(all_genres)

def encode_genres(genres):
    vec = [1 if g in genres.split('|') else 0 for g in all_genres]
    return vec

movies_df["genre_vector"] = movies_df["genres"].apply(encode_genres)
genre_matrix = list(movies_df["genre_vector"].values)

# Similaridade cosseno entre filmes
similarity_matrix = cosine_similarity(genre_matrix)

# --- Banco simples de avaliações ---
DATA_FILE = "ratings.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/filmes", methods=["GET"])
def filmes():
    return jsonify(movies_df[["movieId", "title", "genres"]].to_dict(orient="records"))

@app.route("/avaliar", methods=["POST"])
def avaliar():
    data = request.json
    usuario_id = data.get("usuario_id")
    filme_id = data.get("movieId")
    nota = data.get("nota")

    if not usuario_id or not filme_id or nota is None:
        return jsonify({"error": "Dados incompletos"}), 400

    db = load_data()
    if usuario_id not in db:
        db[usuario_id] = {"avaliacoes": {}, "feedback": {}}
    if "avaliacoes" not in db[usuario_id]:
        db[usuario_id]["avaliacoes"] = {}
    db[usuario_id]["avaliacoes"][str(filme_id)] = nota
    save_data(db)

    return jsonify({"message": f"Avaliação salva: {filme_id} -> {nota}"})

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.json
    usuario_id = data.get("usuario_id")
    filme_id = data.get("movieId")
    liked = data.get("liked")  # True ou False

    if not usuario_id or not filme_id or liked is None:
        return jsonify({"error": "Dados incompletos"}), 400

    db = load_data()
    if usuario_id not in db:
        db[usuario_id] = {"avaliacoes": {}, "feedback": {}}
    if "feedback" not in db[usuario_id]:
        db[usuario_id]["feedback"] = {}

    db[usuario_id]["feedback"][str(filme_id)] = liked
    save_data(db)

    return jsonify({"message": f"Feedback salvo: {filme_id} -> {'Like' if liked else 'Dislike'}"})


@app.route("/feedback/<usuario_id>", methods=["GET"])
def get_feedback(usuario_id):
    """Retorna todos os feedbacks de um usuário"""
    db = load_data()
    user_data = db.get(usuario_id, {})
    feedbacks = user_data.get("feedback", {})

    return jsonify({
        "usuario_id": usuario_id,
        "feedbacks": feedbacks,
        "total_feedbacks": len(feedbacks)
    })

@app.route("/recomendacoes/<usuario_id>", methods=["GET"])
def recomendacoes(usuario_id):
    db = load_data()
    avaliacoes = db.get(usuario_id, {}).get("avaliacoes", {})
    feedbacks = db.get(usuario_id, {}).get("feedback", {})

    if not avaliacoes:
        return jsonify({"error": "Usuário não possui avaliações"}), 400

    avaliados_ids = [int(fid) for fid in avaliacoes.keys()]
    avaliados_notas = avaliacoes

    scores = {}
    for filme_id, nota in avaliados_notas.items():
        idx_filme = movies_df.index[movies_df["movieId"] == int(filme_id)][0]
        similares = list(enumerate(similarity_matrix[idx_filme]))

        for idx, sim in similares:
            candidato_id = int(movies_df.iloc[idx]["movieId"])
            # Pular se já foi avaliado OU se já recebeu feedback
            if str(candidato_id) in avaliacoes or str(candidato_id) in feedbacks:
                continue
            scores[candidato_id] = scores.get(candidato_id, 0) + sim * nota

    recomendados_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    recomendados = movies_df[movies_df["movieId"].isin([fid for fid, _ in recomendados_ids])]

    return jsonify(recomendados[["movieId", "title", "genres"]].to_dict(orient="records"))


@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    """Retorna lista de todos os usuários cadastrados"""
    db = load_data()
    usuarios = list(db.keys())
    return jsonify({"usuarios": usuarios})


@app.route("/similaridade/<usuario_id>", methods=["GET"])
def similaridade_usuarios(usuario_id):
    """Calcula similaridade entre usuários baseado nas avaliações por gênero"""
    db = load_data()

    if usuario_id not in db:
        return jsonify({"error": "Usuário não encontrado"}), 404

    # Coletar todas as avaliações de todos os usuários
    usuarios_avaliacoes = {}
    todos_generos = set()

    for uid, dados in db.items():
        if "avaliacoes" in dados and dados["avaliacoes"]:
            usuarios_avaliacoes[uid] = dados["avaliacoes"]
            # Coletar gêneros dos filmes avaliados
            for filme_id in dados["avaliacoes"].keys():
                filme_info = movies_df[movies_df["movieId"] == int(filme_id)]
                if not filme_info.empty:
                    generos_filme = filme_info.iloc[0]["genres"].split('|')
                    todos_generos.update(generos_filme)

    if len(usuarios_avaliacoes) < 2:
        return jsonify({"error": "Não há usuários suficientes para comparação"}), 400

    # Criar matriz de avaliações por gênero
    todos_generos = sorted(todos_generos)
    matriz_generos = []
    usuarios_ids = []

    for uid, avaliacoes in usuarios_avaliacoes.items():
        vetor_generos = []

        for genero in todos_generos:
            notas_genero = []
            for filme_id, nota in avaliacoes.items():
                filme_info = movies_df[movies_df["movieId"] == int(filme_id)]
                if not filme_info.empty:
                    generos_filme = filme_info.iloc[0]["genres"].split('|')
                    if genero in generos_filme:
                        notas_genero.append(float(nota))

            # Calcular nota média para o gênero
            if notas_genero:
                nota_media_genero = sum(notas_genero) / len(notas_genero)
            else:
                nota_media_genero = 0

            vetor_generos.append(nota_media_genero)

        matriz_generos.append(vetor_generos)
        usuarios_ids.append(uid)

    # Calcular similaridade cosseno baseada em gêneros
    matriz_generos = np.array(matriz_generos)
    similaridades = cosine_similarity(matriz_generos)

    # Encontrar índice do usuário alvo
    try:
        idx_usuario = usuarios_ids.index(usuario_id)
    except ValueError:
        return jsonify({"error": "Usuário não encontrado na matriz"}), 404

    # Calcular estatísticas do usuário alvo
    avaliacoes_alvo = usuarios_avaliacoes[usuario_id]
    generos_preferidos_alvo = {}

    for filme_id, nota in avaliacoes_alvo.items():
        filme_info = movies_df[movies_df["movieId"] == int(filme_id)]
        if not filme_info.empty:
            generos_filme = filme_info.iloc[0]["genres"].split('|')
            for genero in generos_filme:
                if genero not in generos_preferidos_alvo:
                    generos_preferidos_alvo[genero] = []
                generos_preferidos_alvo[genero].append(float(nota))

    # Calcular nota média por gênero para o usuário alvo
    generos_alvo_com_media = {}
    for genero, notas in generos_preferidos_alvo.items():
        generos_alvo_com_media[genero] = sum(notas) / len(notas)

    # Ordenar gêneros por preferência
    generos_ordenados = sorted(generos_alvo_com_media.items(), key=lambda x: x[1], reverse=True)

    # Calcular similaridades para o usuário alvo
    similaridades_usuario = []
    for i, uid in enumerate(usuarios_ids):
        if uid != usuario_id:  # Não incluir o próprio usuário
            similaridade = similaridades[idx_usuario][i]

            # Calcular gêneros em comum com notas similares
            generos_comuns = 0
            avaliacoes_similar = usuarios_avaliacoes[uid]
            generos_preferidos_similar = {}

            for filme_id, nota in avaliacoes_similar.items():
                filme_info = movies_df[movies_df["movieId"] == int(filme_id)]
                if not filme_info.empty:
                    generos_filme = filme_info.iloc[0]["genres"].split('|')
                    for genero in generos_filme:
                        if genero not in generos_preferidos_similar:
                            generos_preferidos_similar[genero] = []
                        generos_preferidos_similar[genero].append(float(nota))

            # Calcular nota média por gênero para o usuário similar
            generos_similar_com_media = {}
            for genero, notas in generos_preferidos_similar.items():
                generos_similar_com_media[genero] = sum(notas) / len(notas)

            # Contar gêneros em comum com diferença de nota menor que 1.0
            for genero, nota_alvo in generos_alvo_com_media.items():
                if genero in generos_similar_com_media:
                    nota_similar = generos_similar_com_media[genero]
                    if abs(nota_alvo - nota_similar) <= 1.0:
                        generos_comuns += 1

            # Calcular filmes em comum (para referência)
            filmes_comuns = len(set(avaliacoes_alvo.keys()) & set(avaliacoes_similar.keys()))

            similaridades_usuario.append({
                "usuario_id": uid,
                "similaridade": float(similaridade),
                "generos_comuns": generos_comuns,
                "filmes_comuns": filmes_comuns,
                "total_avaliacoes": len(avaliacoes_similar),
                "generos_preferidos": list(generos_similar_com_media.keys())[:3]  # Top 3 gêneros
            })

    # Ordenar por similaridade (mais similar primeiro)
    similaridades_usuario.sort(key=lambda x: x["similaridade"], reverse=True)

    return jsonify({
        "usuario_alvo": usuario_id,
        "total_usuarios_comparados": len(similaridades_usuario),
        "generos_preferidos_usuario": [g[0] for g in generos_ordenados[:5]],  # Top 5 gêneros
        "notas_por_genero": {g: round(v, 2) for g, v in generos_ordenados[:5]},
        "similaridades": similaridades_usuario[:10]  # Top 10 mais similares
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)