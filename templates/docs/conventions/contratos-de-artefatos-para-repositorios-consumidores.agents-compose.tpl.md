# Manifesto `agents-compose.yml`

<!-- AGENT-CARD START -->
Leia este documento ao criar, revisar ou ajustar `agents-compose.yml` em um repositório consumidor.
Use este documento para definir os blocos públicos mínimos do manifesto e as entradas que participam da composição.
<!-- AGENT-CARD END -->

Este documento explica o contrato público de `agents-compose.yml` para composição de instruções compartilhadas e publicação de skills declaradas.

## Propósito e escopo

- Esta `convention` define a estrutura pública mínima do manifesto usada para compor `AGENTS.md`, `conventions` publicadas e skills compartilháveis.
- Use este documento quando precisar criar um manifesto novo, completar um manifesto incompleto ou revisar uma mudança estrutural no arquivo.
- Este documento cobre apenas os blocos e campos públicos necessários para a composição das instruções.
- Este documento não substitui a política local de versionamento, publicação ou atualização do repositório consumidor.

## Estrutura pública

```text
agents-compose.yml
├── agents
│   ├── root
│   ├── bootstrap
│   │   └── skill
│   └── source (somente consumidores)
│       ├── repository
│       └── ref
└── outputs
    ├── AGENTS.md
    │   └── include
    │       └── conventions
    │           ├── out_dir
    │           ├── local.tpl_dir
    │           ├── remote.tpl_dir
    │           └── entries[]
    └── skills (opcional)
        ├── out_dir
        ├── local.tpl_dir
        ├── remote.tpl_dir
        └── entries[]
```

## Campos públicos

| Campo | Papel |
|---|---|
| `agents.root` | seleciona explicitamente se o repositório é a raiz das instruções compartilhadas |
| `agents.bootstrap.skill` | declara a skill reservada de bootstrap que provisiona o fluxo público `update-docs` |
| `agents.source.repository` | em consumidores, identifica o repositório base de instruções compartilhadas |
| `agents.source.ref` | em consumidores, fixa a versão, tag ou ref usada como base da composição |
| `outputs.AGENTS.md.include.conventions.out_dir` | define o diretório dos artefatos publicados |
| `outputs.AGENTS.md.include.conventions.local.tpl_dir` | define a raiz das fontes mantidas no repositório consumidor |
| `outputs.AGENTS.md.include.conventions.remote.tpl_dir` | define a raiz das fontes vindas da base compartilhada |
| `outputs.AGENTS.md.include.conventions.entries` | lista quais arquivos-fonte pai participam da publicação |
| `outputs.skills.out_dir` | define o diretório dos pacotes de `skill` publicados |
| `outputs.skills.local.tpl_dir` | define a raiz dos pacotes de `skill` mantidos no repositório consumidor |
| `outputs.skills.remote.tpl_dir` | define a raiz dos pacotes de `skill` vindos da base compartilhada |
| `outputs.skills.entries` | lista quais pacotes de `skill` normais participam da publicação |

## Estrutura de `conventions.entries`

Cada item de `outputs.AGENTS.md.include.conventions.entries` representa uma `convention` pai incluída na publicação.

| Campo | Regra pública |
|---|---|
| `origin` | use `local` para fonte mantida no repositório consumidor ou `remote` para fonte vinda da base compartilhada |
| `from` | use o caminho do arquivo `.tpl.md` relativo ao `tpl_dir` da origem escolhida |

## Estrutura de `skills.entries`

Cada item de `outputs.skills.entries` representa um pacote de `skill` normal incluído na publicação.
Não use `outputs.skills.entries` para declarar a skill reservada `update-docs`.

| Campo | Regra pública |
|---|---|
| `origin` | use `local` para pacote mantido no repositório consumidor ou `remote` para pacote vindo da base compartilhada |
| `from` | use o caminho do diretório de pacote relativo ao `tpl_dir` da origem escolhida |

Neste repositório, `update-docs` é declarado em `agents.bootstrap.skill`; `update-version` é declarado como `origin: local` e `from: update-version`.

## Exemplos de `agents`

No repositório raiz das instruções compartilhadas:

```yaml
agents:
  root: true
  bootstrap:
    skill: update-docs
```

Em repositórios consumidores:

```yaml
agents:
  root: false
  source:
    repository: git@github.com:henrique013/agents.git
    ref: v2.1.0
  bootstrap:
    skill: update-docs
```

## Regras operacionais

- Use apenas os blocos públicos esperados em `outputs.AGENTS.md.include.conventions`: `out_dir`, `local`, `remote` e `entries`.
- Declare `agents.root` como booleano.
- Declare `agents.bootstrap.skill` como `update-docs`.
- Não declare `agents.source` quando `agents.root` for `true`.
- Declare `agents.source.repository` e `agents.source.ref` quando `agents.root` for `false`.
- Não use os campos legados `agents.repository` e `agents.ref`.
- `outputs.skills` é opcional. Quando existir, use apenas os blocos públicos esperados: `out_dir`, `local`, `remote` e `entries`.
- Use apenas `tpl_dir` dentro dos blocos `local` e `remote` de `conventions` e `skills`.
- Use apenas `origin` e `from` em cada item de `entries`.
- Faça cada item de `conventions.entries` apontar para um arquivo-fonte pai, não para uma `subconvention` filha.
- Faça cada item de `skills.entries` apontar para um diretório de pacote que contenha `SKILL.md` na raiz.
- Use em `conventions.entries[].from` apenas um arquivo `.tpl.md` que pertença à origem declarada pelo campo `origin`.
- Use em `skills.entries[].from` apenas um caminho relativo seguro para um diretório de skill que pertença à origem declarada pelo campo `origin`.
- Não declare `update-docs` em `outputs.skills.entries`, porque `.codex/skills/update-docs/` é reservado ao bootstrap e à autoatualização da própria skill.

## O que esta convention não decide

- o conteúdo normativo de cada `convention`
- o conteúdo autoral de cada `skill`
- a ordem interna das etapas de publicação
- mensagens de erro, validações auxiliares ou detalhes internos da automação
