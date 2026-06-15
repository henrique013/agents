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
        +-> <outputs.AGENTS.md.include.conventions.out_dir>/<convention>.md
        +-> <outputs.AGENTS.md.include.conventions.out_dir>/<convention>.<subconvention>.md
        +-> <outputs.skills.out_dir>/<skill>/ para skills normais declaradas
```

`agents.bootstrap.skill` deve declarar `update-docs`, que é a skill fixa de bootstrap.
A saída operacional `.codex/skills/update-docs/` é reservada ao bootstrap e à autoatualização dessa skill, não a uma entrada normal de `outputs.skills.entries`.
O diretório operacional de skills também pode conter pacotes externos gerados por ferramentas, como `.codex/skills/openspec-*/`, que ficam fora de `agents-compose.yml` e de `outputs.skills.entries`.

## Papéis de cada camada

| Camada | Papel | Edição manual |
|---|---|---|
| arquivos-fonte | definem o conteúdo autoral em arquivos `.tpl.md` de documentação ou em pacotes de `skill` mantidos pelo repositório | permitida quando o pedido for alterar o conteúdo autoral |
| manifesto de composição | declara quais entradas participam da publicação final | permitida quando o pedido exigir incluir, remover, renomear, reordenar ou trocar a origem de entradas |
| `AGENTS.md` publicado | instrução ativa derivada da composição | proibida |
| `conventions` e `subconventions` finais publicadas | documentação normativa derivada da composição | proibida |
| diretório operacional de skills | pacotes de `skill` com origens distintas, incluindo bootstrap reservado, skills normais declaradas em `outputs.skills.entries` e pacotes externos gerados por ferramentas | proibida |

## Regra central

- Comece toda mudança em `conventions` ou `skills` compartilháveis identificando se o alvo é fonte, manifesto ou artefato final publicado.
- Faça alterações autorais nos arquivos-fonte `.tpl.md` ou nos pacotes de `skill` aplicáveis.
- Faça mudanças de inclusão, remoção, renomeação, reordenação ou origem no manifesto de composição aplicável.
- Trate `AGENTS.md`, `conventions` finais, `subconventions` finais e pacotes de skills publicados ou gerados como artefatos materializados.
- Não edite manualmente esses artefatos publicados para refletir mudanças em `conventions` ou `skills`, mesmo quando a mudança parecer pequena ou localizada.
- Se o usuário pedir alteração em um arquivo final publicado, interprete esse pedido como mudança na fonte ou no manifesto aplicáveis.
- Quando a dúvida for sobre qual arquivo mexer, descubra primeiro se o pedido altera conteúdo autoral ou a composição da publicação.

## Como aplicar uma mudança

1. Identifique se o alvo citado pelo usuário é fonte, manifesto ou artefato final publicado.
2. Se o alvo for um artefato final publicado, localize a fonte correspondente e o manifesto que o inclui na publicação.
3. Edite apenas a fonte e o manifesto que realmente precisam mudar.
4. Se for necessário materializar artefatos publicados, use o fluxo público de sincronização/publicação configurado no repositório.
5. Se o pedido cobrir apenas autoria e a política local separar autoria de publicação, conclua a autoria e informe qual fluxo público deve publicar ou sincronizar os artefatos depois. Não execute publicação ou sincronização fora do escopo autorizado.

## Fluxo público de sincronização/publicação

- A materialização de `AGENTS.md`, das `conventions` no diretório configurado em `outputs.AGENTS.md.include.conventions.out_dir` e das skills normais declaradas deve usar o fluxo público configurado no repositório.
- A skill fixa `update-docs` deve ser declarada em `agents.bootstrap.skill` e materializada como bootstrap reservado pelo bootstrap ou pela autoatualização da própria skill.
- Quando a skill `update-docs` for esse fluxo público no consumidor, use a skill `update-docs`.
- Não chame, documente nem apresente o script interno da skill `update-docs` como fluxo normal.
- Se uma política local definir outro fluxo público, a política local prevalece.
- A sincronização ou publicação de artefatos derivados é independente da política local de release Git; quando um repositório tiver skill ou fluxo de release próprio, documente esse comportamento em conventions locais ou na skill local correspondente.
- `update-docs` não é hook automático universal para toda alteração em `conventions`.

## Sinais de interpretação correta

- Pedido para alterar texto normativo de uma `convention` publicada: muda a fonte correspondente, não o arquivo final.
- Pedido para adicionar, remover, renomear ou reordenar uma `convention` publicada: muda o manifesto de composição aplicável.
- Pedido para alterar uma `skill` normal publicada por `outputs.skills.entries`: muda o pacote fonte resolvido por `outputs.skills.local.tpl_dir`, `outputs.skills.remote.tpl_dir` e `entries[].from`, não a saída publicada.
- Pedido para adicionar, remover, renomear ou reordenar uma `skill` publicada normal: muda `outputs.skills.entries` no manifesto aplicável.
- Pedido para alterar `update-docs`: muda a fonte fixa da skill de bootstrap no repositório base; a saída operacional `.codex/skills/update-docs/` é reservada ao bootstrap e à autoatualização.
- Pedido para alterar uma skill externa gerada, como `.codex/skills/openspec-*/`: usa o workflow público do gerador ou da ferramenta correspondente, não `outputs.skills.entries`.
- Pedido para alterar workflow específico de uma `skill` local: muda a fonte local dessa skill e mantém a orientação pública em convention local ou no próprio pacote da skill.
- Pedido para publicar uma versão Git de um repositório: segue o fluxo local documentado pelo próprio repositório, sem herdar comportamento de release da base compartilhada.
- Pedido para corrigir `AGENTS.md` publicado: verifica se a correção nasce em template-base, em fonte publicada ou no manifesto que controla a lista de `conventions`.
- Pedido para publicar ou sincronizar artefatos derivados: usa o fluxo público local, não edição manual dos arquivos finais.

## O que evitar

- Tratar arquivo publicado como fonte de verdade só porque ele é o arquivo aberto no editor.
- Corrigir `AGENTS.md` final diretamente para "ganhar tempo".
- Alterar `subconventions` finais publicadas como se fossem independentes da `convention` pai.
- Alterar pacote operacional de skill como se fosse fonte autoral de `skill` compartilhável.
- Pular o fluxo público de sincronização/publicação depois de ajustar a fonte ou o manifesto.
- Executar `update-docs` implicitamente quando a política local exigir outro fluxo público.
- Chamar script interno de skill como caminho normal de publicação.
