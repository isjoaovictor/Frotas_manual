"""Interface Low-Ship. Execute com streamlit run src/app/main.py."""

import logging
import sys
from base64 import b64encode
from html import escape
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


APP_DIR = Path(__file__).resolve().parent
SRC_DIR = APP_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

ERRO_INTERNO = "Houve um problema interno no servidor da Vale. Tente novamente."
CAMPO_AUSENTE = "Não informado pelo fluxo."


def enviar_pergunta():
    """Agenda uma única execução e invalida o resultado da consulta anterior."""
    if st.session_state.processando:
        return
    pergunta = st.session_state.pergunta.strip()
    st.session_state.resultado = None
    st.session_state.erro = ""
    st.session_state.vazia = not pergunta
    if pergunta:
        st.session_state.pergunta_preservada = st.session_state.pergunta
        st.session_state.pergunta_enviada = pergunta
        st.session_state.processando = True


def mostrar_trecho(documento, rotulo):
    metadata = documento.metadata
    posicao = metadata.get("posicao")
    posicao_html = ""
    if posicao is not None:
        posicao_html = f'<p class="source-meta">Posição {escape(str(posicao))}</p>'
    st.html(
        '<article class="source">'
        f'<p class="source-label">{escape(rotulo)}</p>'
        f'<h3>{escape(str(metadata.get("doc", CAMPO_AUSENTE)))}</h3>'
        f'<p class="source-meta">Seção {escape(str(metadata.get("secao", CAMPO_AUSENTE)))}</p>'
        f'{posicao_html}'
        f'<blockquote>{escape(documento.page_content)}</blockquote>'
        '</article>'
    )


def mostrar_resultado(resultado):
    st.subheader("Resposta")
    with st.container(key="resposta_texto"):
        st.markdown(resultado.get("resposta") or "O fluxo retornou uma resposta vazia.")
    st.subheader("Evidências")
    fontes = resultado.get("fontes", [])
    if fontes:
        st.caption("Seções informadas pelo fluxo como fontes")
        for fonte in fontes:
            st.text(str(fonte))
    else:
        st.caption("O fluxo retornou nenhuma fonte." if "fontes" in resultado else CAMPO_AUSENTE)

    st.caption(
        "O fluxo informa seções e trechos de contexto. A identificação dos trechos "
        "efetivamente utilizados em cada afirmação está indisponível."
    )
    contextos = resultado.get("contextos", [])
    documentos = resultado.get("documentos", [])
    # Contextos e documentos podem compartilhar os mesmos chunks. Exiba cada um uma vez.
    exibidos = set()
    for conjunto, rotulo in (
        (contextos, "Trecho de contexto retornado pelo fluxo"),
        (documentos, "Trecho recuperado na busca"),
    ):
        for documento in conjunto:
            chave = (str(documento.metadata), documento.page_content)
            if chave in exibidos:
                continue
            exibidos.add(chave)
            mostrar_trecho(documento, rotulo)
    if not exibidos:
        st.caption("Nenhum trecho disponível no resultado.")

    with st.expander("Detalhes da busca"):
        st.markdown("**Quantidade de buscas**")
        st.text(str(resultado.get("tentativas_busca", CAMPO_AUSENTE)))
        st.markdown("**Pergunta original**")
        st.text(st.session_state.pergunta_enviada)
        st.markdown("**Consulta final**")
        st.text(resultado.get("consulta_busca") or CAMPO_AUSENTE)
        st.markdown("**Expansão de contexto**")
        expandido = resultado.get("expandido")
        st.text({True: "Sim", False: "Não"}.get(expandido, CAMPO_AUSENTE))
        if resultado.get("avaliacao"):
            st.markdown("**Avaliação do contexto**")
            st.text(resultado["avaliacao"])
        if resultado.get("motivo_avaliacao"):
            st.text(resultado["motivo_avaliacao"])


def main():
    st.set_page_config(page_title="Low-Ship", page_icon=str(APP_DIR / "logo-dark.png"), layout="centered")
    st.html(APP_DIR / "style.css")
    imagem_navio = b64encode((APP_DIR / "ship.svg").read_bytes()).decode("ascii")
    navio = f'<img src="data:image/svg+xml;base64,{imagem_navio}" alt="" width="64" height="32">'
    imagem_logo = b64encode((APP_DIR / "logo-dark.png").read_bytes()).decode("ascii")
    for chave, valor in {
        "pergunta": "", "pergunta_enviada": "", "resultado": None,
        "processando": False, "erro": "", "vazia": False,
        "exibir_resultados": st.session_state.get("resultado") is not None,
    }.items():
        st.session_state.setdefault(chave, valor)

    layout = "results" if st.session_state.exibir_resultados else "initial"
    animar = "true" if st.session_state.pop("animar_resultado", False) else "false"
    st.html(
        f'<header class="site-header" data-layout="{layout}" data-animate="{animar}">'
        f'<img class="site-logo" src="data:image/png;base64,{imagem_logo}" alt="GenAI Deloitte">'
        f'<div class="brand">{navio}<span>Low-Ship</span></div>'
        '</header>'
    )
    if st.session_state.pop("restaurar_pergunta", False):
        st.session_state.pergunta = st.session_state.pergunta_preservada

    # A estrutura permanece estável entre envios para preservar os widgets.
    # O CSS expande a página e revela a segunda coluna ao receber um resultado.
    with st.container(key="consulta_layout"):
        pergunta_coluna, resultado_coluna = st.columns([1, 2], gap="large")
        with pergunta_coluna:
            with st.container(key="painel_pergunta"):
                st.title("Redução de custos da frota da Vale")
                st.caption("Consulta ao manual de operações do Porto Alfa")
                with st.form("consulta", clear_on_submit=False):
                    st.text_area("Sua pergunta", key="pergunta", height=120,
                                 disabled=st.session_state.processando)
                    st.form_submit_button("Consultar manual", type="primary",
                                          disabled=st.session_state.processando,
                                          on_click=enviar_pergunta)

                if st.session_state.vazia:
                    st.error("Digite uma pergunta para consultar o manual")
                    # O formulário nativo não oferece foco após validação.
                    components.html("""<script>
                        const campo = window.parent.document.querySelector('textarea');
                        if (campo) {
                            campo.focus();
                            campo.setAttribute('aria-invalid', 'true');
                        }
                    </script>""", height=0)
                if st.session_state.erro:
                    st.error(st.session_state.erro)

        with resultado_coluna:
            with st.container(key="painel_resultado"):
                if st.session_state.resultado is not None:
                    mostrar_resultado(st.session_state.resultado)

    if st.session_state.processando:
        modal = st.empty()
        modal.markdown(
            '<div class="loading-overlay"><div class="loading-dialog" '
            'role="dialog" aria-modal="true" aria-labelledby="loading-title">'
            f'<div class="orbit" aria-hidden="true"><div class="orbit-ship">{navio}</div></div>'
            '<p id="loading-title" role="status">Gerando resposta</p>'
            '</div></div>', unsafe_allow_html=True,
        )
        try:
            # Carregamento tardio permite apresentar também falhas de importação.
            from graph.builder import graph

            pergunta = st.session_state.pergunta_enviada
            st.session_state.resultado = graph.invoke({"pergunta": pergunta})
            st.session_state.animar_resultado = not st.session_state.exibir_resultados
            st.session_state.exibir_resultados = True
        except Exception:
            logging.getLogger(__name__).exception("Falha na consulta Low-Ship")
            st.session_state.resultado = None
            st.session_state.erro = ERRO_INTERNO
        finally:
            st.session_state.processando = False
            st.session_state.restaurar_pergunta = True
            modal.empty()
        st.rerun()

if __name__ == "__main__":
    main()
