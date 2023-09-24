# Linkedin BOT

Procura ofertas de trabalho no linkedin por uma entrada (keywords) e tenta localizar algumas keywords, vindas de um banco de dados, no texto.
Há duas variações: uma que usa uma tabela com keywords que serão as únicas aceitas (se um post conter outra ele é descartado) e outra que usa um dataset de posts com suas keywords e a
sua nota, de 1 (muito ruim) a 5 (muito bom), baseada somente nessas keywords.

## Requisitos

- biblioteca [linkedin-api](https://github.com/tomquirk/linkedin-api)
- biblioteca [unidecode](https://pypi.org/project/Unidecode/)
- biblioteca [pandas](https://pandas.pydata.org/)
- biblioteca [scikit-learn](https://scikit-learn.org/stable/)
- [docker](https://www.docker.com/)

## Uso

1. abra o terminal e insira: docker compose up
2. edite o arquivo params.json
    ```
    {
        "username" : "thiago.com",
        "password" : "1234",
        "keywords" : ["c++", "python", "javascript"],
        "function" : [],
        "sortBy" : "R",
        "locationUnion" : 103658898,
        "populatedPlace" : [106701406, 100177287, 101236820, 102872198, 105272189],
        "experience" : [2, 3],
        "limit" : [10, 10, 10],
        "companies" : [],
        "workplaceType" : [1, 2, 3],
        "count" : 7,
        "distance" : 25,
        "listed_at" : 31536000,
        "output" : "jobs",
        "cutoff" : 4,
        "search" : "simple"
    }
    ```

    Sendo:

- username: o email do seu usuário (melhor que use um novo)
- password: a senha do seu usuário
- keywords: lista com as entradas da busca (o que vai ser colocado na barra de pesquisa)
- limit: limite no número de posts da entrada que está na mesma posição em keywords (caso seja -1 não é limitado)
- function: id's das funções que serão selecionadas. Para encontrar uma específica: pesquise uma vaga, clique em Todos os filtros, selecione uma função e copie o valor do atributo f_F na caixa de url
- sortBy: R é para posts relevantes e DD para recentes
- locationUnion: id da região para encontrar a vaga (país, cidade, estado, etc). Para encontrar o valor: pesquise a vaga usando o local e copie o valor do parâmetro geoId na caixa de url.
- populatedPlace: lista com os id's das sub-regiões. Para encontrar uma sub-região: pesquise uma vaga com a região escolhida, clique em todos os filtros, selecione uma das sub-regiões em Localidade e copie o valor do parâmetro f_PP na caixa de url.
- experience: 1 (estágio), 2 (assistente), 3 (júnior), 4 (pleno/senior), 5 (diretor) e 6 (executivo)
- discardCompanies: lista com os id's das empresas que devem ser descartadas. Para encontrar de uma empresa espacífica: vá na página da empresa, pesquise uma vaga e copie o valor do atributo f_C na caixa de url.
- companies: lista com os id's da empresas alvos. Para encontrar de uma empresa espacífica: vá na página da empresa, pesquise uma vaga e copie o valor do atributo f_C na caixa de url.
- workplaceType: 1 (Presencial), 2 (Remoto), 3 (Híbrido)
- count: não precisa modificar (é o limite de posts por página na requisição)
- distance: raio da busca (default é 25)
- listed_at: número de segundos desde a publicação
- output: arquivo csv com os dados dos posts
- search: simple se usa a tabela skills.csv ou se usa o dataset de exemplos
- cutoff: se search é simple, então só aceita se a soma dos pesos das keywords truncado para inteiro presente no texto não é menor que cutoff, senão se é ml todos os posts com peso maior ou igual a cutoff são os únicos exemplos que podem ser aceitos (todos os outros não são aceitos)

3. abra o terminal e insira: python3 bot.py

4. espere terminar e abra o arquivo de saída (output). Ele contém algumas informações do post:
- urn_id: id do post
- jobtitle: título do post
- url: url do post
- score: score do post (baseado nas keywords)
- skills: lista com as skills encontradas
- company: nome da empresa
- company_urn_id: id da empresa
- location: localização
- listedAt: tempo em segundos desde a publicação
- company_url: url da página da empresa no linkedin
- workPlaceType: lista com os modos de trabalho

## Editar o banco de dados
Para construir o arquivo linkedin.sql: vá em tmp, abra o terminal e digite python3 sql_builder.py

Na pasta tmp há alguns arquivos .json com dados para o banco de dados:
- keywords.json: com as keywords e suas variações aceitas (que serão usadas para identificar a keyword) com o seguinte formato:
```
"javascript" : ["javascript", "js", "java script"]
```
- correlations.json: com as keywords e os conhecimentos necessários para possuí-la:
```
"pyspark" : ["spark", "python"]
```
- posts.json: com as informações de algum post:
```
{
    "title" : "PontoTel - Desenvolvedor Back End Jr (Remoto)",
    "weight" : 3,
    "keywords" : [
        "backend",
        "jr",
        "javascript",
        "vuejs",
        "html",
        "css",
        "git"   
    ]
}
```

## Todo

- Pegar as exigências do post
- Colocar mais exemplos
- Colocar mais keywords
- Conseguir ver se alguns atributos são desejáveis
