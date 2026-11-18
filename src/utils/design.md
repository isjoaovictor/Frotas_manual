# Low-Ship | Design da interface Streamlit

## Escopo de implementação

Implemente a interface de consulta ao manual didático do Porto Alfa. Restrinja o diff à nova interface Streamlit, aos seus recursos visuais e à configuração visual necessária. Preserve integralmente o backend, a entrada existente em src/app/main.py e o README. Localize por leitura a função pública que recebe uma pergunta e devolve o resultado do RAG. Crie uma entrada Streamlit separada em src/app/ e informe ao final o comando para executá-la a partir da raiz.

Encaminhe a pergunta uma vez por envio. O backend controla recuperação, reformulação da consulta, número de buscas, expansão de contexto e geração da resposta. Apresente os valores que ele devolver. Se algum campo não estiver disponível, indique essa limitação na entrega. Não crie fontes, métricas ou decisões para preencher a tela.

## Identidade e composição

Aplique a identidade pessoal de João em toda a experiência, inclusive no formulário, no modal, nas evidências e nas mensagens de estado. A base é preta, com superfícies grafite, tipografia clara e detalhes geométricos em verde e vermelho. Use o verde na ação principal e no foco de teclado. Reserve o vermelho para um pequeno detalhe da marca e para sinalizar falhas acompanhadas de texto.

Como proposta de implementação, use fundo #0C0E0E, superfície #191C1B, texto #F4F5F3, texto secundário #BCC5BF, verde #91DB80 e vermelho #F07878. Use Inter ou uma sans serif do sistema. Preserve contraste e espaço livre. Evite barra lateral, slogans, indicadores de economia fictícios e elementos decorativos repetidos.

No cabeçalho, alinhe o nome Low-Ship a uma silhueta lateral de navio cargueiro. Desenhe casco longo, proa angulada e ponte de comando com poucos traços. O símbolo precisa continuar reconhecível a 32 px. Reutilize o desenho no carregamento.

## Tela de consulta

Use uma coluna central com largura máxima aproximada de 800 px. No celular, mantenha 16 px de margem lateral. A ordem de leitura é marca, título, pergunta, resposta e evidências.

Título principal sugerido: **Redução de custos da frota da Vale**. Abaixo, identifique a fonte com a linha curta “Consulta ao manual de operações do Porto Alfa”. O título dá contexto ao projeto. A aplicação entrega respostas documentais.

Mostre o rótulo “Sua pergunta”, um campo de texto e a ação “Consultar manual”. Envio vazio deve manter o foco na pergunta e exibir “Digite uma pergunta para consultar o manual”. Na abertura, deixe a área de resultado vazia.

## Durante a consulta

Ao enviar uma pergunta válida, abra um modal centralizado sobre o conteúdo escurecido. Exiba “Gerando resposta” e a silhueta do cargueiro percorrendo uma trajetória circular contínua. Mantenha o texto parado e o navio reconhecível. Respeite a preferência de movimento reduzido exibindo a silhueta estática e o mesmo texto. Mostre o modal antes de aguardar o RAG e feche-o tanto ao receber o resultado quanto em caso de falha.

Use o estado da sessão da interface para preservar a pergunta e seu último resultado. Abrir evidências ou redesenhar a página não deve reenviar a pergunta. Bloqueie envios duplicados durante o processamento.

## Resposta e evidências

Exiba primeiro a resposta recebida, preservando números, unidades e ressalvas. Logo abaixo, mantenha o título “Evidências” visível. Para cada fonte disponível, apresente o documento, a seção e o trecho literal em que a resposta se apoia. Use a posição do trecho quando fornecida. Distinga trechos apenas recuperados daqueles identificados pelo backend como evidência. Use rótulos textuais e uma linha lateral discreta para facilitar a leitura.

Em “Detalhes da busca”, uma área expansível, apresente a quantidade de buscas, a consulta final e a expansão de contexto informadas pelo fluxo. Quando a consulta final diferir da pergunta original, preserve as duas. A leitura desses dados deve ser possível também no celular.

Quando o fluxo concluir que o manual não contém a informação, apresente “Não encontrado no manual de operações.” Preserve os detalhes da busca. Uma falha técnica deve fechar o modal e apresentar “Houve um problema interno no servidor da Vale. Tente novamente.” Preserve a pergunta para um novo envio manual e evite mostrar dados da resposta anterior como se pertencessem à pergunta atual.

## Verificação da entrega

1. Uma pergunta respondida apresenta a resposta e permite conferir o trecho de origem.
2. No cenário de nevoeiro, se o RAG devolver duas buscas e ausência de evidência, a interface apresenta exatamente esse resultado e a consulta final recebida.
3. Uma falha simulada pelo lado da interface encerra o carregamento e mostra a mensagem de problema interno. Um novo envio funciona.
4. Expandir fontes ou detalhes não provoca nova chamada ao RAG.
5. Em tela estreita, a pergunta, o botão, a resposta e as evidências permanecem legíveis por teclado e sem rolagem horizontal.
6. Confira o diff final e informe arquivos alterados, comando de execução e cenários efetivamente verificados.
