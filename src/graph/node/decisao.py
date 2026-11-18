
from graph.state import RAGState


def decisao(state: RAGState) -> dict:
    """Define o próximo caminho do grafo com base na verificação."""

    avaliacao = state.get("avaliacao", "insuficiente")
    expandido = state.get("expandido", False)
    tentativas = state.get("tentativas_busca", 0)

    if avaliacao == "conflito":
        destino = "revisao_humana"

    elif avaliacao == "suficiente":
        destino = "responder"

    elif not expandido:
        destino = "expandir"

    elif tentativas < 2:
        destino = "rebuscar"

    else:
        destino = "nao_encontrado"

    return {"decisao": destino}
