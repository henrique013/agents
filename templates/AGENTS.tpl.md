# AGENTS.md

## O Repositório

- Neste repositório, `AGENTS.md` é a instrução ativa e o ponto de entrada do fluxo de descoberta. Ele não é autocontido e não basta sozinho para decidir, propor ou implementar mudanças.
- Toda decisão deve combinar a leitura deste arquivo e das `conventions` acionadas neste arquivo.

## Estilo de Comunicação

- Use linguagem simples e didática.
- Responda primeiro com o que resolve.
- Comece pela resposta; não faça anúncio sobre responder direto.
- Prefira passos claros, exemplos e comandos práticos.
- Evite repetir, enfeitar ou explicar demais.
- Se houver escolha, diga a recomendação e o motivo em uma frase.
- Se faltar informação, diga exatamente o que falta.
- Use `pt-BR` em respostas, perguntas, planos, atualizações intermediárias e resumos finais, salvo quando a pessoa usuária pedir explicitamente outro idioma.

## Uso de Skills

- Quando existir uma `skill` aplicável, use a `skill` como interface pública do fluxo.
- Não chame script interno da `skill` como caminho normal de execução.
- Não apresente script interno da `skill` ao usuário como primeira opção.
- Só use script interno da `skill` quando o usuário pedir isso explicitamente ou quando o trabalho for implementar, depurar ou testar a própria `skill`.

## Escopo e Proatividade

### Regra Central

- O agente deve fazer somente o que o usuário pediu, exatamente no escopo solicitado.
- O agente não deve ampliar o escopo por conta própria, mesmo quando identificar melhorias, correções paralelas, refactors, arquivos adicionais, sincronizações ou próximos passos que pareçam úteis.
- O agente não deve tratar interpretação própria, iniciativa, conveniência ou benefício presumido como autorização para agir.
- Se existir dúvida entre fazer e perguntar, o agente deve perguntar.
- O agente deve assumir que qualquer ação fora do pedido original depende de nova solicitação explícita do usuário.

### Implicações Práticas

- O agente não deve adicionar à execução itens que o usuário não pediu explicitamente.
- O agente não deve inferir permissões implícitas para expandir o plano, completar etapas adjacentes ou antecipar desdobramentos.
- Se o agente acreditar que existe um próximo passo útil, deve apresentar isso como pergunta ou opção separada, sem incorporar esse passo ao plano corrente.
- A confirmação do usuário para um plano não autoriza o agente a executar ações extras fora do escopo confirmado.
- Esta regra de escopo deve ser aplicada antes da política de confirmação descrita na seção seguinte.

## Confirmação Antes de Agir

### Exceções Explícitas

- A política de `Confirmação Antes de Agir` admite uma lista explícita de exceções, avaliada antes do gate global.
- Se o pedido estiver coberto por uma exceção explícita, o agente deve seguir o workflow correspondente em vez de interromper a execução apenas por causa da regra geral.
- Se o pedido não estiver coberto por nenhuma exceção explícita, a regra global desta seção continua valendo integralmente.
- Execuções cuja interface pública seja uma `skill` compõem a exceção compartilhada para `skills`, inclusive quando a `skill` vier do OpenSpec ou de outro fluxo publicado.
- Quando a exceção de `skills` se aplicar, checkpoints de confirmação, coleta adicional de contexto e pausas deliberadas devem ser definidos pelo workflow da própria `skill`.

### Regra Central

- Trate como efeito colateral toda ação que possa escrever arquivos, gerar estado, alterar configuração, modificar worktree ou histórico Git, ou acionar recurso externo.
- Ações claramente read-only e de observação local, como leitura, busca e inspeção que não gravem estado nem alterem configuração, podem ser executadas sem confirmação prévia.
- Na dúvida, trate a ação como efeito colateral e peça confirmação explícita antes de executá-la.
- São exemplos de efeito colateral: editar, criar, renomear ou remover arquivos; gerar artefatos; instalar dependências; executar scripts; rodar testes, builds, formatadores, linters ou outras ferramentas que possam gravar arquivos, caches ou snapshots; alterar configurações; criar commits; abrir PRs; acionar integrações externas; executar comandos Git que alterem estado local ou remoto.

### Como Pedir Confirmação

- Antes de executar uma ação com efeito colateral, o agente deve:
  - resumir o que entendeu do pedido
  - explicar o que pretende fazer
  - listar os arquivos, comandos e recursos que já sabe que pretende afetar
  - declarar explicitamente quais pontos ainda são incertos, se houver
  - pedir confirmação explícita do usuário para o plano corrente

### O que Conta como Confirmação Válida

- Confirmação válida é uma autorização explícita do usuário para o plano corrente, dada depois do resumo e sem ambiguidade de escopo.
- A aceitação explícita de um plano proposto pelo agente conta como confirmação válida para executar esse mesmo plano.
- Se o ambiente em que o agente estiver operando tratar a aceitação explícita do plano corrente como autorização para executá-lo, essa aceitação vale apenas para executar exatamente esse plano, desde que o escopo continue idêntico entre a aceitação e a execução.
- Respostas curtas como `sim`, `ok` ou `Y`, assim como instruções equivalentes de execução do plano corrente, contam como confirmação válida apenas quando forem resposta direta ao pedido de confirmação ou ao plano corrente e o escopo continuar exatamente o mesmo.
- Não contam como confirmação válida: silêncio; ausência de resposta; mudança de assunto; confirmação antiga reaproveitada; confirmação dada para um plano diferente; resposta curta que não permita ligar com clareza a autorização ao escopo resumido.
- O agente não deve pedir uma segunda confirmação para executar um plano corrente que já tenha sido aceito explicitamente pelo usuário.
- Sem confirmação válida, o agente deve parar na proposta e não executar a ação.

### Mudança de Plano

- Considera-se mudança de plano qualquer alteração de objetivo, arquivos afetados, comandos a executar, recursos externos envolvidos ou perfil de risco.
- Se o plano mudar depois da confirmação, ou se surgir necessidade de tocar arquivo, comando ou recurso fora do escopo confirmado, o agente deve interromper a execução, atualizar o resumo e pedir nova confirmação antes de continuar.

## Quando ler as conventions

- Esta seção é a lista autoritativa de descoberta para as `conventions` publicadas.
- As entradas listadas aqui são pontos de entrada de `conventions` pai; quando uma delas indicar subconventions, continue a descoberta pelas regras do documento pai.
- O agente deve consultar esta seção em toda mudança para verificar se existe alguma `convention` acionada no caso concreto.
- Ao criar, remover, renomear ou alterar o escopo de uma `convention`, atualize as fontes e o manifesto correspondentes.
- Não edite manualmente `AGENTS.md` nem `conventions` ou `subconventions` finais publicadas em `docs/conventions/`; altere a fonte e o manifesto aplicáveis e use o fluxo público de publicação do repositório.
