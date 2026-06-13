# Base de instruções para agentes

Este repositório centraliza a base compartilhada de instruções para agentes. Ele existe para evitar cópia manual entre projetos e manter previsível a composição de `AGENTS.md`, `conventions` e `skills`.

A ideia principal é simples: este repositório publica uma versão base, e repositórios consumidores apontam para essa versão para materializar localmente os artefatos que os agentes vão ler.

```text
fontes + agents-compose.yml
  |
  +-> update-docs
        |
        +-> AGENTS.md
        +-> docs/conventions/**
        +-> .codex/skills/update-docs/ (bootstrap)
        +-> .codex/skills/<skill>/ (skills declaradas)
```

## Leituras principais

| Objetivo | Leia |
|---|---|
| Manter este repositório `agents` | [docs/guides/manutencao-do-repositorio-agents.md](docs/guides/manutencao-do-repositorio-agents.md) |
| Integrar um repositório consumidor | [docs/guides/integracao-em-repositorio-consumidor.md](docs/guides/integracao-em-repositorio-consumidor.md) |
| Entender o contrato de composição | [docs/conventions/contratos-de-artefatos-para-repositorios-consumidores.md](docs/conventions/contratos-de-artefatos-para-repositorios-consumidores.md) |
| Entender o fluxo OpenSpec enxuto | [docs/conventions/fluxo-openspec-enxuto.md](docs/conventions/fluxo-openspec-enxuto.md) |

## Modelo

| Modo | Onde acontece | Manifesto | Fonte de `origin: remote` |
|---|---|---|---|
| raiz | neste repositório | `agents.root: true` + `agents.bootstrap.skill` | templates locais deste repositório |
| consumidor | repositório filho | `agents.root: false` + `agents.source.repository/ref` + `agents.bootstrap.skill` | checkout pinado da base |

No modo raiz, tudo que é compartilhável vem dos templates locais deste repositório.

No modo consumidor, o manifesto fixa a versão da base em `agents.source.repository/ref`. Entradas `origin: local` vêm do repositório consumidor; entradas `origin: remote` vêm do checkout pinado da base.

## Estrutura

| Caminho | Papel |
|---|---|
| `templates/AGENTS.tpl.md` | template base de `AGENTS.md` |
| `templates/docs/conventions/` | fontes compartilhadas de `conventions` |
| `templates/docs/conventions-local/` | fontes locais deste repositório |
| `templates/skills/` | fontes compartilhadas de skills |
| `templates/skills-local/` | fontes locais de skills deste repositório |
| `agents-compose.yml` | manifesto que declara o que entra na publicação |
| `AGENTS.md` | saída publicada para instrução ativa |
| `docs/conventions/**` | saídas publicadas de conventions |
| `.codex/skills/**` | saídas publicadas de skills |

Não edite manualmente `AGENTS.md`, `docs/conventions/**` ou `.codex/skills/**` para refletir mudanças de conteúdo. Edite as fontes e use o fluxo público `update-docs`.

## Versão

As versões publicadas usam tags `vX.Y.Z`. Em consumidores, prefira sempre uma tag estável em `agents.source.ref`, por exemplo:

```yaml
agents:
  root: false
  source:
    repository: git@github.com:henrique013/agents.git
    ref: v2.6.0
  bootstrap:
    skill: update-docs
```
