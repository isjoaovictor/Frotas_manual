def buscar_lexical(pergunta, chunks, k=3):
    """Realiza uma busca lexical utilizando o algoritmo BM25."""

    
    tokens = word_tokenize(pergunta.lower(), language='portuguese')
    chunk_token = [word_tokenize(chunk.page_content.lower(), language='portuguese') for chunk in chunks]

    bm25 = BM25Okapi(chunk_token)
    pontuacoes = bm25.get_scores(tokens)

    resultados = sorted(zip(chunks, pontuacoes), key=lambda x: x[1], reverse=True)[:k]

    return resultados