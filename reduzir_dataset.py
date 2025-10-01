import pandas as pd
import os


def reduzir_dataset():
    """Reduz o dataset original para melhor performance"""
    try:
        # Verificar se os arquivos originais existem
        if not os.path.exists("dataset/rating.csv"):
            print("❌ Arquivo dataset/rating.csv não encontrado")
            return False

        if not os.path.exists("dataset/movie.csv"):
            print("❌ Arquivo dataset/movie.csv não encontrado")
            return False

        # Ler o dataset completo de ratings
        print("📖 Lendo dataset completo...")
        ratings_df = pd.read_csv("dataset/rating.csv")

        # Reduzir para 30% do tamanho original
        print("🔧 Reduzindo dataset...")
        ratings_reduzido = ratings_df.sample(frac=0.001, random_state=42)

        # Manter apenas os filmes que estão no dataset reduzido
        movies_df = pd.read_csv("dataset/movie.csv")
        filmes_relevantes = ratings_reduzido['movieId'].unique()
        movies_reduzido = movies_df[movies_df['movieId'].isin(filmes_relevantes)]

        # Salvar datasets reduzidos
        print("💾 Salvando datasets reduzidos...")
        ratings_reduzido.to_csv("dataset/rating_reduzido.csv", index=False)
        movies_reduzido.to_csv("dataset/movie_reduzido.csv", index=False)

        print(f"✅ Dataset reduzido criado com sucesso!")
        print(f"📊 Ratings: {len(ratings_reduzido)} avaliações (original: {len(ratings_df)})")
        print(f"🎬 Filmes: {len(movies_reduzido)} filmes (original: {len(movies_df)})")

        return True

    except Exception as e:
        print(f"❌ Erro ao reduzir dataset: {e}")
        return False


if __name__ == "__main__":
    reduzir_dataset()