# Sistema de Recomendação de Filmes

Este é um sistema de recomendação de filmes desenvolvido em Python. O objetivo deste projeto é fornecer recomendações personalizadas de filmes aos usuários com base em seus gostos e similaridades com outros usuários. O sistema utiliza o [MovieLens 20M Dataset](https://www.kaggle.com/datasets/grouplens/movielens-20m-dataset) para alimentar suas recomendações.

## 🚀 Funcionalidades

-   **Recomendações Personalizadas:** Receba sugestões de filmes com base nos gêneros que você mais gosta.
-   **Curta suas Recomendações:** Demonstre seu interesse em um filme recomendado, ajudando a aprimorar futuras sugestões.
-   **Análise de Similaridade:** Descubra o quão parecido o seu gosto para filmes é com o de outros usuários do sistema.
-   **Visualização de Dados:** Explore gráficos interativos que apresentam insights sobre os dados de filmes e as preferências dos usuários.

## ⚙️ Como o Sistema Funciona

O núcleo do nosso sistema de recomendação se baseia no gênero dos filmes. Ao analisar os filmes que um usuário avaliou positivamente, o sistema identifica os gêneros preferidos. Em seguida, ele busca no nosso vasto conjunto de dados por outros filmes que correspondam a esses gêneros, apresentando ao usuário uma lista de recomendações relevantes.

Além disso, a plataforma calcula um score de similaridade entre os usuários. Isso é feito comparando os padrões de gostos e os gêneros de filmes que diferentes usuários apreciam. Isso permite que você não apenas receba recomendações de filmes, mas também descubra outras pessoas com um gosto cinematográfico parecido com o seu.

## 🏁 Começando

Siga as instruções abaixo para configurar e executar o projeto em sua máquina local.

### Pré-requisitos

-   Python 3.x
-   Pip (gerenciador de pacotes do Python)
-   Node.js e npm (para o front-end, se aplicável)

### Instalação

1.  **Instale as dependências do back-end:**
    Crie e ative um ambiente virtual (recomendado):
    ```bash
    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Para Windows
    python -m venv venv
    .\\venv\\Scripts\\activate
    ```
    Em seguida, instale os pacotes necessários:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Instale as dependências do front-end:**
    Navegue até a pasta do front-end e instale os pacotes:
    ```bash
    cd frontend
    npm install
    ```

### Executando a Aplicação

1.  **Inicie o back-end:**
    A partir da pasta raiz do projeto, execute:
    ```bash
    # Certifique-se que seu ambiente virtual está ativado
    python app.py 
    ```
    O servidor back-end estará em execução em `http://localhost:5000`.

2.  **Inicie o front-end:**
    Em um **novo terminal**, a partir da pasta `frontend`, execute:
    ```bash
    npm start
    ```
    A aplicação estará acessível em `http://localhost:3000`.

## 📊 O Conjunto de Dados

Este projeto utiliza o **MovieLens 20M Dataset**, um dos mais populares e bem conceituados conjuntos de dados para sistemas de recomendação. Ele contém 20 milhões de avaliações de mais de 27.000 filmes, fornecidas por aproximadamente 138.000 usuários. O arquivo principal que utilizamos para a análise de gêneros é o `movie.csv`.
