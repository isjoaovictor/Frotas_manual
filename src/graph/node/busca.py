
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from graph.state import RAGState
from utils.vector_store import buscar_hibrida


def busca(state: RAGState) -> dict:
    """Executa a busca híbrida e reformula a consulta na segunda tentativa."""

    tentativas = state.get("tentativas_busca", 0)
    consulta = state.get("consulta_busca") or state["pergunta"]

    if tentativas >= 1:
        load_dotenv(Path(__file__).resolve().parents[3] / ".env")

        llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "openai/gpt-4o-mini"),
            api_key=os.environ["API_KEY"],
            base_url="https://openrouter.ai/api/v1",
            temperature=0,
            max_tokens=100
        )

        resultado = llm.invoke([
            (
                "system",
                """
                Reformule a pergunta para melhorar a recuperação
                de informações em um manual de operações marítimas.

                Utilize sinônimos e termos operacionais relacionados.
                Preserve o significado da pergunta original.
                Não invente informações.
                Retorne somente a consulta reformulada.
                """
            ),
            (
                "human",
                f"Pergunta original: {state['pergunta']}\n"
                f"Consulta anterior: {consulta}\n"
                f"Motivo da insuficiência: "
                f"{state.get('motivo_avaliacao', '')}"
            )
        ])

        if isinstance(resultado.content, str) and resultado.content.strip():
            consulta = resultado.content.strip()

    documentos = buscar_hibrida(consulta, k=3)

    return {
        "consulta_busca": consulta,
        "documentos": documentos,
        "contextos": documentos,
        "tentativas_busca": tentativas + 1,
        "expandido": False,
        "decisao": ""
    }
