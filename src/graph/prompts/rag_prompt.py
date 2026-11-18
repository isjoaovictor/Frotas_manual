from langchain_core.prompts import ChatPromptTemplate

RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        ""
    ),
    (
        "human",
        "{pergunta}\n\n{contextos}"
    )
])
