from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
import os
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
import nltk
from nltk.tokenize import word_tokenize



DADOS = Path(__file__).resolve().parents[1] / "dados" / "manual_operacoes.txt"
    
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

def carregar_chunks():
    """Carrega os chunks de texto a partir do arquivo de dados."""
    
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("##", "secao")],
        strip_headers=False
    )

    chunks = splitter.split_text(DADOS.read_text(encoding="utf-8"))

    for posicao, dado in enumerate(chunks, start=1):
        dado.metadata["doc"] = DADOS.stem
        dado.metadata["posicao"] = posicao
        print(posicao, dado)

    return chunks




def get_vector_store():
    """Cria e retorna um InMemoryVectorStore com os chunks carregados."""
    

    embeddings = OpenAIEmbeddings(
        model="openai/text-embedding-3-small",
        api_key=os.environ["API_KEY"],
        base_url="https://openrouter.ai/api/v1",
    )
    
    chunks = carregar_chunks()
    vector_store = InMemoryVectorStore.from_documents(chunks, embeddings)
    
    return vector_store


def buscar_lexical(pergunta, chunks, k=3):
    """Realiza uma busca lexical utilizando o algoritmo BM25."""

    
    tokens = word_tokenize(pergunta.lower(), language='portuguese')
    chunk_token = [word_tokenize(chunk.page_content.lower(), language='portuguese') for chunk in chunks]

    bm25 = BM25Okapi(chunk_token)
    pontuacoes = bm25.get_scores(tokens)

    resultados = sorted(zip(chunks, pontuacoes), key=lambda x: x[1], reverse=True)[:k]

    return resultados


def buscar_hibrida(pergunta, k=3):
    """Combina buscas semântica e lexical utilizando RRF."""

    vector_store = get_vector_store()

    ranking_semantico = vector_store.similarity_search(
        pergunta, k=k
    )

    chunks = carregar_chunks()
    ranking_lexical = buscar_lexical(pergunta, chunks, k=k)

    pontuacoes_rrf = {}
    documentos = {}

    # Pontuação da busca semântica
    for posicao, documento in enumerate(ranking_semantico, start=1):
        identificador = (
            documento.metadata["doc"],
            documento.metadata["posicao"]
        )

        pontuacoes_rrf[identificador] = 1 / (60 + posicao)
        documentos[identificador] = documento

    # Pontuação da busca lexical
    for posicao, (documento, pontuacao_bm25) in enumerate(
        ranking_lexical, start=1
    ):
        identificador = (
            documento.metadata["doc"],
            documento.metadata["posicao"]
        )

        if pontuacao_bm25 <= 0:
            continue

        pontuacao_atual = pontuacoes_rrf.get(identificador, 0)

        pontuacoes_rrf[identificador] = (
            pontuacao_atual + 1 / (60 + posicao)
        )

        documentos[identificador] = documento

    # Ordenação final pela pontuação RRF
    ranking_final = sorted(
        pontuacoes_rrf.items(),
        key=lambda item: item[1],
        reverse=True
    )[:k]

    return [
        documentos[identificador]
        for identificador, pontuacao in ranking_final
    ]


def expandir_contexto(documentos, chunks, raio=1):
    """Recupera os chunks vizinhos dos documentos selecionados."""

    indice = {
        (chunk.metadata["doc"], chunk.metadata["posicao"]): chunk
        for chunk in chunks
    }

    selecionados = {}

    for documento in documentos:
        origem = documento.metadata["doc"]
        posicao = documento.metadata["posicao"]

        for vizinho in range(posicao - raio, posicao + raio + 1):
            chave = (origem, vizinho)

            if chave in indice:
                selecionados[chave] = indice[chave]

    return sorted(
        selecionados.values(),
        key=lambda doc: (
            doc.metadata["doc"],
            doc.metadata["posicao"]
        )
    )

