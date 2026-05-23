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

| Diretório | Papel |
|---|---|
| `templates/skills/` | fonte compartilhada de pacotes de `skill` vindos do repositório base |
| `templates/skills-local/` | fonte local de pacotes de `skill` mantidos pelo repositório consumidor |
| `.codex/skills/update-docs/` | saída reservada da skill de bootstrap declarada em `agents.bootstrap.skill` |
| `.codex/skills/<skill>/` | saída publicada para skills normais declaradas em `outputs.skills` |

- Edite `templates/skills/` ou `templates/skills-local/` quando a mudança for autoral em uma skill compartilhável.
- Trate `.codex/skills/` como saída publicada, não como fonte de verdade.
- Neste repositório, `update-docs` é fonte remota em `templates/skills/update-docs/` e saída reservada em `.codex/skills/update-docs/`.
- Neste repositório, `update-version` é fonte local em `templates/skills-local/update-version/` e saída publicada em `.codex/skills/update-version/`.
- `update-docs` é a skill de bootstrap e o fluxo de materialização de `AGENTS.md`, `docs/conventions/**` e skills normais declaradas.
- `update-version` é o fluxo de release Git do repositório: ele pode preparar a release com `update-docs`, sincronizar artefatos gerados, sincronizar `package.json.version` e `package-lock.json`, e publicar `main` junto com a tag.
- `update-version` não atualiza `agents-compose.yml` nem `agents.ref`.
- Não trate `.agents/skills/` como casa normal das skills operacionais publicadas por este repositório.
- Não declare `update-docs` em `outputs.skills.entries`; use `agents.bootstrap.skill: update-docs`.
- Pacotes publicados em `.codex/skills/` devem ser copiados como diretórios inteiros, sem aviso de arquivo gerado, renderização Markdown ou normalização textual.

## Checkpoints de confirmação

- A `skill` é responsável pelos próprios checkpoints de confirmação, coleta adicional de contexto e pausas deliberadas previstos no seu workflow.
- Quando uma `skill` fizer parte de uma exceção explícita à política global de confirmação, isso remove apenas o gate externo genérico; não elimina checkpoints internos definidos pela própria `skill`.
- Esta regra vale para `skills` do OpenSpec e para qualquer outra `skill` publicada pelos repositórios consumidores.

## Quando ler as subconventions

### Semântica e Determinismo em Skills

Arquivo: `docs/conventions/convencoes-para-skills.semantica-e-determinismo.md`

- Leia este documento ao projetar, implementar, revisar ou refatorar `skills` neste repositório.
- Use este documento para decidir o que deve ficar com o agente e o que pode ser automatizado de forma determinística.
