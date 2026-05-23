# Composição de Instruções para Repositórios Consumidores

<!-- AGENT-CARD START -->
Leia este documento ao alterar instruções compartilhadas em um repositório consumidor.
Use este documento para distinguir fonte de verdade, manifesto de composição e artefatos finais publicados.
<!-- AGENT-CARD END -->

Este documento explica como um repositório consumidor deve interpretar a composição entre arquivos-fonte, manifesto de composição e artefatos finais publicados. Antes de alterar uma `convention`, `subconvention` ou `skill` compartilhável, identifique se o alvo citado é fonte, manifesto ou artefato publicado.

## Modelo de composição

```text
arquivos-fonte + manifesto de composição
  |
  +-> fluxo público de sincronização/publicação
        |
        +-> AGENTS.md
        +-> docs/conventions/<convention>.md
        +-> docs/conventions/<convention>.<subconvention>.md
        +-> .codex/skills/<skill>/ para skills normais declaradas
```

`.codex/skills/update-docs/` é reservado à skill de bootstrap declarada em `agents.bootstrap.skill`, não a uma entrada normal de `outputs.skills.entries`.

## Papéis de cada camada

| Camada | Papel | Edição manual |
|---|---|---|
| arquivos-fonte | definem o conteúdo autoral em arquivos `.tpl.md` de documentação ou em pacotes de `skill` mantidos pelo repositório | permitida quando o pedido for alterar o conteúdo autoral |
| manifesto de composição | declara quais entradas participam da publicação final | permitida quando o pedido exigir incluir, remover, renomear, reordenar ou trocar a origem de entradas |
| `AGENTS.md` publicado | instrução ativa derivada da composição | proibida |
| `conventions` e `subconventions` finais publicadas | documentação normativa derivada da composição | proibida |
| `.codex/skills` publicado | pacotes de `skill` derivados das fontes declaradas e a skill reservada de bootstrap | proibida |

## Regra central

- Comece toda mudança em `conventions` ou `skills` compartilháveis identificando se o alvo é fonte, manifesto ou artefato final publicado.
- Faça alterações autorais nos arquivos-fonte `.tpl.md` ou nos pacotes de `skill` aplicáveis.
- Faça mudanças de inclusão, remoção, renomeação, reordenação ou origem no manifesto de composição aplicável.
- Trate `AGENTS.md`, `conventions` finais, `subconventions` finais e `.codex/skills` como saídas derivadas.
- Não edite manualmente esses artefatos publicados para refletir mudanças em `conventions` ou `skills`, mesmo quando a mudança parecer pequena ou localizada.
- Se a pessoa pedir alteração em um arquivo final publicado, interprete esse pedido como mudança na fonte ou no manifesto aplicáveis.
- Quando a dúvida for sobre qual arquivo mexer, descubra primeiro se o pedido altera conteúdo autoral ou a composição da publicação.

## Como aplicar uma mudança

1. Identifique se o alvo citado pela pessoa é fonte, manifesto ou artefato final publicado.
2. Se o alvo for um artefato final publicado, localize a fonte correspondente e o manifesto que o inclui na publicação.
3. Edite apenas a fonte e o manifesto que realmente precisam mudar.
4. Se for necessário materializar artefatos publicados, use o fluxo público de sincronização/publicação configurado no repositório.
5. Se o pedido cobrir apenas autoria e a política local separar autoria de publicação, conclua a autoria e informe qual fluxo público deve publicar ou sincronizar os artefatos depois. Não execute publicação ou sincronização fora do escopo autorizado.

## Fluxo público de sincronização/publicação

- A materialização de `AGENTS.md`, `docs/conventions/**` e skills normais declaradas deve usar o fluxo público configurado no repositório.
- A skill `update-docs` deve ser declarada em `agents.bootstrap.skill` e publicada em `.codex/skills/update-docs/` pelo bootstrap ou pela autoatualização da própria skill.
- Quando a skill `update-docs` for esse fluxo público no consumidor, use a skill `update-docs`.
- Não chame, documente nem apresente o script interno da skill `update-docs` como fluxo normal.
- Se uma política local definir outro fluxo público, a política local prevalece.
- No repositório `agents`, `update-docs` materializa artefatos derivados; `update-version` é o fluxo de release Git que pode preparar artefatos gerados, sincronizar metadados de versão e publicar `main` com a tag.
- `update-docs` não é hook automático universal para toda alteração em `conventions`.

## Sinais de interpretação correta

- Pedido para alterar texto normativo de uma `convention` publicada: muda a fonte correspondente, não o arquivo final.
- Pedido para adicionar, remover, renomear ou reordenar uma `convention` publicada: muda o manifesto de composição aplicável.
- Pedido para alterar uma `skill` publicada em `.codex/skills`: muda o pacote fonte em `templates/skills-local` ou `templates/skills`, não a saída publicada.
- Pedido para adicionar, remover, renomear ou reordenar uma `skill` publicada normal: muda `outputs.skills.entries` no manifesto aplicável.
- Pedido para alterar `update-docs`: muda `templates/skills/update-docs/`; `.codex/skills/update-docs/` é a saída reservada do bootstrap e da autoatualização.
- Pedido para alterar `update-version`: muda `templates/skills-local/update-version/`, que publica `.codex/skills/update-version/` neste repositório.
- Pedido para publicar uma versão Git deste repositório: usa `update-version`, que executa a preparação de release com o fluxo público `update-docs` quando houver artefatos derivados a sincronizar.
- Pedido para corrigir `AGENTS.md` publicado: verifica se a correção nasce em template-base, em fonte publicada ou no manifesto que controla a lista de `conventions`.
- Pedido para publicar ou sincronizar artefatos derivados: usa o fluxo público local, não edição manual dos arquivos finais.

## O que evitar

- Tratar arquivo publicado como fonte de verdade só porque ele é o arquivo aberto no editor.
- Corrigir `AGENTS.md` final diretamente para "ganhar tempo".
- Alterar `subconventions` finais publicadas como se fossem independentes da `convention` pai.
- Alterar `.codex/skills` como se fosse fonte autoral de `skill` compartilhável.
- Pular o fluxo público de sincronização/publicação depois de ajustar a fonte ou o manifesto.
- Executar `update-docs` implicitamente quando a política local exigir outro fluxo público.
- Chamar script interno de skill como caminho normal de publicação.
