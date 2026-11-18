
from graph.state import RAGState


def entrada(state: RAGState) -> dict:
    """Valida a pergunta e inicializa o estado da execução do RAG."""

    pergunta = state["pergunta"].strip()

    if not pergunta:
        raise ValueError("A pergunta não pode estar vazia.")

    return {
        "pergunta": pergunta,
        "consulta_busca": pergunta,
        "tentativas_busca": 0,
        "documentos": [],
        "contextos": [],
        "expandido": False,
        "avaliacao": "",
        "motivo_avaliacao": "",
        "decisao": "",
        "resposta": "",
        "fontes": []
    }
