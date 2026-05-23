> Arquivo gerado. Não edite manualmente.
> Altere a fonte e o manifesto aplicáveis e use o fluxo público de publicação do repositório.

# Autoria e Publicação de Conventions

Esta `convention` define o fluxo correto para mudanças em `conventions` no repositório `agents`.

## Propósito e escopo

- Esta regra vale para criação, remoção, renomeação e mudança de escopo de `conventions` neste repositório.
- Ela cobre arquivos-fonte, manifesto de composição e artefatos publicados.
- Ela existe para evitar edição manual de saídas geradas.

## 1. Fonte de verdade

Ao criar ou alterar uma `convention`, trate como fonte de verdade apenas:

- o arquivo template correspondente em `templates/docs/conventions-local/` ou `templates/docs/conventions/`
- a entrada correspondente em `outputs.AGENTS.md.include.conventions.entries` dentro de `agents-compose.yml`

Não trate `AGENTS.md` nem `docs/conventions/*.md` como fonte de verdade.

## 2. O que o agente pode fazer na fase de autoria

Quando o pedido for criar ou ajustar uma `convention`, o agente deve limitar a mudança a:

- criar, editar, renomear ou remover o arquivo `.tpl.md` aplicável
- atualizar `agents-compose.yml` para incluir, remover ou ajustar a entrada correspondente

O agente não deve:

- editar manualmente `AGENTS.md`
- criar ou editar manualmente arquivos em `docs/conventions/`
- executar `update-docs` como desdobramento implícito da autoria

## 3. Como a sincronização acontece

A materialização de `AGENTS.md`, de `docs/conventions/` e das skills normais declaradas acontece pelo fluxo público `update-docs`.

Nesse fluxo:

- a pessoa usuária decide executar `update-docs`
- a skill lê `agents-compose.yml`
- em `agents.root: true`, a skill usa os templates locais deste repositório
- em `agents.root: false`, a skill usa o checkout pinado declarado em `agents.source.repository/ref` para entradas `origin: remote`
- a skill regenera os artefatos publicados a partir das fontes e do manifesto

Fora desse fluxo, trate `AGENTS.md` e `docs/conventions/` como saídas derivadas que não devem ser editadas manualmente.

## 4. Como o versionamento acontece

A publicação de versão Git acontece pelo fluxo `update-version`.
Esse fluxo valida o estado do repositório, prepara artefatos derivados quando necessário, sincroniza metadados de versão e cria uma tag anotada no commit versionado.

`update-version` pode chamar o fluxo público `update-docs`, criar commits necessários de preparação da release, publicar `main` e publicar a tag Git correspondente. Ele não atualiza `agents-compose.yml` nem `agents.ref`.

## 5. Regra de interpretação

Se a pessoa pedir para criar uma nova `convention`, interprete esse pedido como autoria da fonte, não como sincronização imediata da publicação.

Se a pessoa também quiser materializar a mudança nos artefatos publicados, isso depende de um pedido separado para executar a skill `update-docs`.
