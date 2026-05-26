# Manutenção do Repositório `agents`

Este guia é para quem clona e mantém este repositório base.

Use o guia de integração quando o objetivo for aplicar esta base em outro repositório: [integracao-em-repositorio-consumidor.md](integracao-em-repositorio-consumidor.md).

## Pré-requisitos

| Ferramenta | Versão |
|---|---|
| Python | `>=3.10`, disponível como `python3` |
| Node | `>=22` |
| npm | compatível com o Node instalado |

## Setup local

Depois de clonar este repositório, rode:

```sh
make setup
```

Esse comando valida o ambiente, executa `npm ci` a partir de `package-lock.json` e instala os hooks Git via Lefthook local.

O setup atual não instala Python, Node, npm, curl ou Lefthook globalmente. Se o clone ainda tiver o Lefthook global legado instalado por fluxo antigo, remova essa instalação antes de confiar no setup local.

## Testes

Para validar o repositório:

```sh
make tests
```

O hook `pre-push` também executa `make tests`.

## O que editar

| Tipo de mudança | Edite |
|---|---|
| Template base de instruções | `templates/AGENTS.tpl.md` |
| Convention compartilhável | `templates/docs/conventions/**` |
| Convention local deste repositório | `templates/docs/conventions-local/**` |
| Skill compartilhável | `templates/skills/**` |
| Skill local deste repositório | `templates/skills-local/**` |
| Inclusão, remoção ou ordem de publicação | `agents-compose.yml` |

Não edite manualmente:

- `AGENTS.md`
- `docs/conventions/**`
- `.codex/skills/**`

Esses caminhos são artefatos publicados.

## Publicação de artefatos

Use a skill `update-docs` quando precisar materializar `AGENTS.md`, `docs/conventions/**` e skills normais publicadas em `.codex/skills/**` a partir das fontes e do manifesto.
O caminho `.codex/skills/update-docs/` é reservado ao bootstrap e à autoatualização da própria skill.

```text
templates/** + agents-compose.yml
  |
  +-> update-docs
        |
        +-> AGENTS.md
        +-> docs/conventions/**
        +-> .codex/skills/update-docs/ (bootstrap/self-update)
        +-> .codex/skills/<skill>/ (outputs.skills)
```

No repositório raiz, entradas `origin: remote` também são resolvidas a partir dos templates locais deste próprio repositório.

## Versionamento

Use a skill `update-version` para publicar uma nova versão semver.

Esse fluxo:

- prepara uma prévia isolada
- roda `update-docs`
- valida caminhos gerados
- sincroniza `package.json.version` e `package-lock.json`
- cria o commit de versão
- cria a tag anotada `vX.Y.Z`
- publica `main` e a tag no `origin`

`update-version` não atualiza `agents-compose.yml` nem refs de consumidores.

## OpenSpec

Este repositório mantém `openspec/config.yaml` e seleciona a convention `fluxo-openspec-com-remocao-direta.tpl.md`. Para fechar uma change descartável sem arquivar, remova diretamente somente o diretório ativo correspondente em `openspec/changes/<change-id>/` pela árvore de arquivos do projeto.

As skills OpenSpec padrão, como `openspec-explore`, `openspec-propose`, `openspec-apply-change` e `openspec-archive-change`, são esperadas como parte do ambiente OpenSpec/Codex usado pelo agente. Elas não são fonte compartilhável deste repositório por padrão.
