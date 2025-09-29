from flask import Flask, request, jsonify
import pandas as pd
import json
import os
from sklearn.metrics.pairwise import cosine_similarity

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

@app.route("/feedback", methods=["GET"])

@app.route("/recomendacoes/<usuario_id>", methods=["GET"])
def recomendacoes(usuario_id):
    db = load_data()
    avaliacoes = db.get(usuario_id, {}).get("avaliacoes", {})

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
            if str(candidato_id) in avaliacoes:  # já avaliado
                continue
            scores[candidato_id] = scores.get(candidato_id, 0) + sim * nota

    recomendados_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    recomendados = movies_df[movies_df["movieId"].isin([fid for fid, _ in recomendados_ids])]

    return jsonify(recomendados[["movieId", "title", "genres"]].to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
