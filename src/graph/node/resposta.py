
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from graph.state import RAGState


def resposta(state: RAGState) -> dict:
    """Gera uma resposta fundamentada no manual ou informa a impossibilidade."""

    destino = state.get("decisao", "nao_encontrado")

    if destino == "revisao_humana":
        return {
            "resposta": "Foram identificadas informações conflitantes. É necessária revisão humana.",
            "fontes": []
        }

    if destino != "responder":
        return {
            "resposta": "Não encontrado no manual de operações.",
            "fontes": []
        }

    documentos = state.get("contextos", [])

    if not documentos:
        return {
            "resposta": "Não encontrado no manual de operações.",
            "fontes": []
        }

    contexto = "\n\n".join(
        f"Fonte: {doc.metadata['doc']}\n"
        f"Seção: {doc.metadata['secao']}\n"
        f"Conteúdo: {doc.page_content}"
        for doc in documentos
    )

    load_dotenv(Path(__file__).resolve().parents[3] / ".env")

    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "openai/gpt-4o-mini"),
        api_key=os.environ["API_KEY"],
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
        max_tokens=400
    )

    resultado = llm.invoke([
        (
            "system",
            """
            Você responde perguntas sobre um manual operacional.

            Utilize exclusivamente as informações do contexto.
            Não invente informações ou regras.
            Não utilize conhecimento externo.
            Responda de forma clara e objetiva.
            Indique a seção que fundamenta sua resposta.
            Se o contexto não permitir responder, diga:
            Não encontrado no manual de operações.
            """
        ),
        (
            "human",
            f"Pergunta: {state['pergunta']}\n\nContexto:\n{contexto}"
        )
    ])

    fontes = list(dict.fromkeys(
        doc.metadata["secao"]
        for doc in documentos
    ))

    return {
        "resposta": resultado.content,
        "fontes": fontes
    }
