
from graph.state import RAGState
from utils.vector_store import carregar_chunks, expandir_contexto


def expansao(state: RAGState) -> dict:
    """Amplia o contexto recuperando os chunks vizinhos dos documentos."""

    documentos = state.get("documentos", [])

    chunks = carregar_chunks()

    contextos_expandidos = expandir_contexto(
        documentos,
        chunks
    )

    return {
        "contextos": contextos_expandidos,
        "expandido": True
    }
