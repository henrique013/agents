# Integração em Repositório Consumidor

Este guia é para quem quer aplicar a base `agents` em outro repositório.

Use o guia de manutenção quando o objetivo for trabalhar no próprio repositório base: [manutencao-do-repositorio-agents.md](manutencao-do-repositorio-agents.md).

## Visão geral

```text
repositório consumidor
├── agents-compose.yml
├── templates/docs/conventions-local/**
├── templates/skills-local/**
└── artefatos publicados
    ├── AGENTS.md
    ├── docs/conventions/**
    └── .codex/skills/**
```

O consumidor declara quais fontes locais e remotas quer publicar. As fontes remotas vêm da versão pinada da base `agents`.

## Pré-requisitos

| Ferramenta | Uso |
|---|---|
| Python `>=3.10` como `python3` | executar `bin/agents-bootstrap.py` e `update-docs` |
| Git | clonar a base pinada |
| Acesso ao repositório `agents` | ler a tag declarada em `agents.source.ref` |

## 1. Crie o manifesto

Crie `agents-compose.yml` no repositório consumidor:

```yaml
agents:
  root: false
  source:
    repository: git@github.com:henrique013/agents.git
    ref: v1.1.0
  bootstrap:
    skill: update-docs

outputs:
  AGENTS.md:
    include:
      conventions:
        out_dir: docs/conventions
        local:
          tpl_dir: templates/docs/conventions-local
        remote:
          tpl_dir: templates/docs/conventions
        entries:
          - origin: local
            from: contexto-do-projeto.tpl.md
          - origin: remote
            from: padrao-de-mensagem-de-commit.tpl.md
          - origin: remote
            from: composicao-de-instrucoes-para-repositorios-consumidores.tpl.md
```

Regras principais:

- `agents.root` deve ser `false` no consumidor.
- `agents.source.repository` aponta para a base.
- `agents.source.ref` deve apontar para uma tag ou ref estável.
- `agents.bootstrap.skill` deve ser `update-docs`.
- `entries[].from` é relativo ao `tpl_dir` da origem declarada.
- Convention aponta para arquivo `.tpl.md` pai.
- Skill normal em `outputs.skills.entries` aponta para diretório com `SKILL.md` na raiz.
- Não declare `update-docs` em `outputs.skills.entries`; ela é provisionada pelo bootstrap.

## 2. Crie as fontes locais

Exemplo mínimo:

```text
templates/docs/conventions-local/
└── contexto-do-projeto.tpl.md
```

O arquivo de convention precisa ter:

- exatamente um heading Markdown de nível 1
- exatamente um bloco `AGENT-CARD`
- corpo normativo fora do `AGENT-CARD`

## 3. Instale o launcher inicial

Antes da primeira execução, o consumidor ainda não tem a skill `update-docs` publicada localmente. Por isso, declare `agents.bootstrap.skill: update-docs` e obtenha `bin/agents-bootstrap.py` da mesma versão declarada em `agents.source.ref`.

Exemplo usando uma cópia temporária da base:

```sh
tmp_dir="$(mktemp -d)"
git clone --depth 1 --branch v1.1.0 git@github.com:henrique013/agents.git "$tmp_dir"
mkdir -p bin
cp "$tmp_dir/bin/agents-bootstrap.py" bin/agents-bootstrap.py
rm -rf "$tmp_dir"
```

Depois rode, na raiz do consumidor:

```sh
python3 bin/agents-bootstrap.py
```

O bootstrap instala `.codex/skills/update-docs/` a partir da versão pinada. Esse caminho é reservado ao bootstrap e à autoatualização da própria skill. Depois disso, o fluxo normal passa a ser a skill `update-docs`.

## 4. Sincronize os artefatos publicados

Use a skill `update-docs`.

O fluxo recorrente fica assim:

```text
editar fontes ou agents-compose.yml
  |
  +-> update-docs
        |
        +-> AGENTS.md
        +-> docs/conventions/**
        +-> .codex/skills/**
```

## 5. OpenSpec opcional

Para adotar o fluxo OpenSpec enxuto, inclua a convention remota:

```yaml
- origin: remote
  from: fluxo-openspec-enxuto.tpl.md
```

Para fechar uma change descartável sem arquivar, remova diretamente o diretório ativo correspondente em `openspec/changes/<change-id>/` pela árvore de arquivos do projeto.

Não declare `update-docs` em `outputs.skills.entries`, porque ela já é a skill de bootstrap declarada em `agents.bootstrap.skill`.

As skills OpenSpec padrão, como `openspec-explore`, `openspec-propose`, `openspec-apply-change` e `openspec-archive-change`, devem vir do ambiente OpenSpec/Codex disponível para o agente. Este repositório não as publica como fonte compartilhável por padrão.

## 6. Atualização da versão da base

Para atualizar um consumidor para uma nova versão da base:

1. Altere `agents.source.ref` para a nova tag.
2. Rode `update-docs`.
3. Revise o diff de `AGENTS.md`, `docs/conventions/**` e `.codex/skills/**`.
4. Faça commit das mudanças no consumidor.
