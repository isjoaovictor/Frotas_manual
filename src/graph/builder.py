
from langgraph.graph import StateGraph, START, END

from graph.state import RAGState
from graph.node.entrada import entrada
from graph.node.busca import busca
from graph.node.verificacao import verificacao
from graph.node.decisao import decisao
from graph.node.expansao import expansao
from graph.node.resposta import resposta



builder = StateGraph(RAGState)


builder.add_node("entrada", entrada)
builder.add_node("busca", busca)
builder.add_node("verificacao", verificacao)
builder.add_node("decisao", decisao)
builder.add_node("expansao", expansao)
builder.add_node("resposta", resposta)


builder.add_edge(START, "entrada")
builder.add_edge("entrada", "busca")
builder.add_edge("busca", "verificacao")
builder.add_edge("verificacao", "decisao")

# Caminhos escolhidos pelo nó de decisão
builder.add_conditional_edges(
    "decisao",
    lambda state: state["decisao"],
    {
        "responder": "resposta",
        "expandir": "expansao",
        "rebuscar": "busca",
        "revisao_humana": "resposta",
        "nao_encontrado": "resposta"
    }
)

# Após expandir, verificamos novamente
builder.add_edge("expansao", "verificacao")
builder.add_edge("resposta", END)

graph = builder.compile()


