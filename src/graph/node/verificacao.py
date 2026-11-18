
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from graph.state import RAGState


class AvaliacaoContexto(BaseModel):
    """Define o formato da avaliação produzida pelo LLM."""

    avaliacao: Literal[
        "suficiente", "insuficiente", "conflito"
    ] = Field(description="Classificação das evidências.")

    justificativa: str = Field(
        description="Motivo da classificação."
    )


def verificacao(state: RAGState) -> dict:
    """Verifica a suficiência e a consistência dos documentos recuperados."""

    documentos = state.get("contextos", [])

    if not documentos:
        return {
            "avaliacao": "insuficiente",
            "motivo_avaliacao": "Nenhum documento recuperado."
        }

    contexto = "\n\n".join(
        f"Seção: {doc.metadata['secao']}\n{doc.page_content}"
        for doc in documentos
    )

    load_dotenv(
        Path(__file__).resolve().parents[3] / ".env"
    )

    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "openai/gpt-4o-mini"),
        api_key=os.environ["API_KEY"],
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
        max_tokens=400
    )

    avaliador = llm.with_structured_output(
        AvaliacaoContexto,
        method="function_calling"
    )

    resultado = avaliador.invoke([
        (
            "system",
            """
            Você verifica evidências de um manual operacional.

            Classifique como:
            suficiente: o contexto permite responder à pergunta.
            insuficiente: faltam informações necessárias.
            conflito: existem regras incompatíveis para a mesma condição.

            Considere somente o contexto recebido.
            Não utilize conhecimento externo.
            Regras para situações diferentes não são conflitos.
            Não confunda velocidade normal com velocidade em tempestade.
            Na dúvida sobre a suficiência, classifique como insuficiente.
            Explique brevemente sua classificação.
            """
        ),
        (
            "human",
            f"Pergunta: {state['pergunta']}\n\nContexto:\n{contexto}"
        )
    ])

    return {
        "avaliacao": resultado.avaliacao,
        "motivo_avaliacao": resultado.justificativa
    }
