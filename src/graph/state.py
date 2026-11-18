from typing import TypedDict
from langchain_core.documents import Document


class RAGState(TypedDict, total=False):
    """Armazena as informações compartilhadas pelos nós do RAG."""

    pergunta: str
    consulta_busca: str
    tentativas_busca: int

    documentos: list[Document]
    contextos: list[Document]

    expandido: bool
    decisao: str

    resposta: str
    fontes: list[str]
    avaliacao: str
    motivo_avaliacao: str
