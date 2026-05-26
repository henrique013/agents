> Arquivo gerado. Não edite manualmente.
> Altere a fonte e o manifesto aplicáveis e use o fluxo público de publicação do repositório.

# Convenções para Skills

Este documento é o ponto de entrada para o tema `skills` neste repositório.

## Propósito e escopo

- Esta `convention` reúne orientações gerais sobre `skills`.
- Use este documento quando estiver criando, revisando ou ajustando uma `skill`.
- Use este documento para decidir o que pertence ao workflow público da `skill`, incluindo checkpoints internos de confirmação quando eles forem necessários.
- Quando a decisão exigir separar responsabilidade entre agente e automação determinística, leia a subconvention de semântica e determinismo.

## Diretórios de skills

Classifique cada caminho de skill antes de tratá-lo como diretório fixo.
Skills normais declaradas são controladas pelo manifesto; bootstrap e pacotes externos têm contratos próprios.

| Categoria | Fonte de verdade |
|---|---|
| fonte compartilhada de skill normal | pacote resolvido por `outputs.skills.remote.tpl_dir` e `outputs.skills.entries[].from` |
| fonte local de skill normal | pacote resolvido por `outputs.skills.local.tpl_dir` e `outputs.skills.entries[].from` |
| saída publicada de skill normal | pacote resolvido por `outputs.skills.out_dir` e `outputs.skills.entries[].from` |
| bootstrap reservado | `agents.bootstrap.skill: update-docs`, fixo por contrato, com fonte de bootstrap no repositório base e saída operacional reservada |
| skill externa gerada | pacote materializado pelo gerador ou ferramenta correspondente, fora de `agents-compose.yml` e de `outputs.skills.entries` |

No manifesto atual deste repositório, `outputs.skills.remote.tpl_dir` vale `templates/skills`, `outputs.skills.local.tpl_dir` vale `templates/skills-local` e `outputs.skills.out_dir` vale `.codex/skills`.
Esses valores atuais não devem ser usados como regra fixa em repositórios consumidores.

- Edite o pacote fonte resolvido por `outputs.skills.local.tpl_dir`, `outputs.skills.remote.tpl_dir` e `entries[].from` quando a mudança for autoral em uma skill normal compartilhável.
- Trate o diretório operacional de skills como diretório de pacotes materializados ou gerados, não como fonte de verdade única.
- `update-docs` é a skill fixa de bootstrap declarada em `agents.bootstrap.skill`; ela não é uma skill normal declarada em `outputs.skills.entries`.
- Skills normais locais declaradas em `outputs.skills.entries` usam fonte em `outputs.skills.local.tpl_dir/<entries[].from>` e saída publicada em `outputs.skills.out_dir/<entries[].from>`.
- Skills normais remotas declaradas em `outputs.skills.entries` usam fonte em `outputs.skills.remote.tpl_dir/<entries[].from>` no repositório base e saída publicada em `outputs.skills.out_dir/<entries[].from>`.
- Skills externas geradas, incluindo o valor de saída comum `.codex/skills/openspec-*/` produzido pelo OpenSpec, não são declaradas em `outputs.skills.entries` e não devem ser adicionadas ao manifesto apenas para espelhar a saída da ferramenta.
- Para alterar uma skill externa gerada, use o workflow público do gerador ou da ferramenta correspondente, como o fluxo do OpenSpec para `openspec-*`, em vez de editar diretamente o pacote operacional gerado.
- `update-docs` é a skill de bootstrap e o fluxo de materialização de `AGENTS.md`, das `conventions` no diretório configurado em `outputs.AGENTS.md.include.conventions.out_dir` e das skills normais declaradas.
- Workflows próprios de release ou publicação Git pertencem a conventions locais ou à skill local correspondente; não são inferidos desta convention compartilhada.
- Não assuma `.agents/skills/` como casa normal das skills operacionais publicadas; use `outputs.skills.out_dir` para skills normais declaradas.
- Não declare `update-docs` em `outputs.skills.entries`; use `agents.bootstrap.skill: update-docs`, fixo por contrato.
- Pacotes de skills normais publicados em `outputs.skills.out_dir` devem ser copiados como diretórios inteiros, sem aviso de arquivo gerado, renderização Markdown ou normalização textual.

## Checkpoints de confirmação

- A `skill` é responsável pelos próprios checkpoints de confirmação, coleta adicional de contexto e pausas deliberadas previstos no seu workflow.
- Quando uma `skill` fizer parte de uma exceção explícita à política global de confirmação, isso remove apenas o gate externo genérico; não elimina checkpoints internos definidos pela própria `skill`.
- Esta regra vale para `skills` do OpenSpec e para qualquer outra `skill` publicada pelos repositórios consumidores.

## Quando ler as subconventions

### Semântica e Determinismo em Skills

Arquivo: `docs/conventions/convencoes-para-skills.semantica-e-determinismo.md`

- Leia este documento ao projetar, implementar, revisar ou refatorar `skills` neste repositório.
- Use este documento para decidir o que deve ficar com o agente e o que pode ser automatizado de forma determinística.
