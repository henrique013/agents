# Contrato dos artefatos de handoff

Use este contrato para revisar se um handoff permite continuar o trabalho sem depender do chat original.

## Layout

O handoff é uma raiz com pastas versionadas:

```text
.tmp/prompts/<slug-topic>/
├── v1/
│   ├── prompt.md
│   ├── dod.md
│   └── log.md
└── vN/
    ├── prompt.md
    ├── dod.md
    └── log.md
```

A raiz deve conter somente diretórios `v1/`, `v2/`, etc. Não use `INDEX.md`, `current`, symlink, cópia `latest` ou arquivos `prompt.md`, `dod.md` e `log.md` na raiz.

A versão ativa é a maior pasta `vN` contígua. Se houver `v1/` e `v3/` sem `v2/`, o handoff está inválido.

## Responsabilidades

| Artefato | Responsabilidade | Evite |
|---|---|---|
| `vN/prompt.md` | Contexto, diagnóstico, decisões, escopo, plano, critérios, riscos e resultado visual da versão. | Resumo cronológico do chat, plano genérico, conteúdo de outra versão ou `## Plano vN` dentro do arquivo. |
| `vN/dod.md` | Checklist vivo da versão, com IDs, status, evidência mínima, evidência atual e vínculo com `vN/log.md`. | Misturar versões, repetir todo o prompt ou marcar item sem evidência. |
| `vN/log.md` | Eventos numerados da versão, plano vigente, ação, evidência e próximo estado retomável. | Narrativa solta, reescrita de histórico ou eventos de outra versão. |

IDs `DOD-*` e `LOG-*` reiniciam em cada pasta. Referências entre arquivos devem incluir a versão, como `v3/DOD-001` ou `v3/LOG-001`.

## Conteúdo por versão

Em `v1`, escreva o contrato inicial completo.

Em `v2+`, repita a estrutura visual completa, mas escreva somente o delta em relação à versão anterior. Se uma categoria não mudou, registre `Sem mudança nesta versão.`.

Isso mantém cada versão pequena, executável e independente do chat, sem copiar integralmente versões anteriores.

## Contexto suficiente

Há contexto suficiente quando o agente consegue definir objetivo, diagnóstico, decisões, fatos, assunções, restrições, escopo, plano, critérios, riscos, evidências e pontos em aberto da versão.

Pause quando faltar decisão fechada, objetivo concreto, diagnóstico mínimo, escopo autorizado, evidência para fatos, próximos passos verificáveis ou decisão sobre destino existente.

## Exemplos

Exemplo aceitável de raiz:

```text
.tmp/prompts/refatorar-skill/v1/prompt.md
.tmp/prompts/refatorar-skill/v1/dod.md
.tmp/prompts/refatorar-skill/v1/log.md
.tmp/prompts/refatorar-skill/v2/prompt.md
.tmp/prompts/refatorar-skill/v2/dod.md
.tmp/prompts/refatorar-skill/v2/log.md
```

Exemplo inaceitável de raiz:

```text
.tmp/prompts/refatorar-skill/prompt.md
.tmp/prompts/refatorar-skill/dod.md
.tmp/prompts/refatorar-skill/log.md
.tmp/prompts/refatorar-skill/v2/prompt.md
```

Exemplo aceitável de DOD:

```text
| DOD-001 | Template de log versionado por pasta. | passa | Inspeção do template. | `assets/log.template.md` usa destino em `v2/`. | v2/LOG-001 |
```

Exemplo inaceitável de `prompt.md`:

```text
## Plano v2 - Ajuste de escopo

### Objetivo

Como falamos antes, continuar a mudança.
```

## Separação das categorias

| Categoria | Definição | Sinal prático |
|---|---|---|
| Decisão | Escolha confirmada que orienta execução. | Gera consequência operacional. |
| Fato | Informação verificável. | Tem evidência concreta. |
| Assunção | Hipótese provisória. | Tem forma de validação e ação se for falsa. |
| Restrição | Limite que reduz opções válidas. | Proíbe ou obriga comportamento. |
| Risco | Possibilidade de falha com impacto. | Tem mitigação e condição de pausa. |
| Pendência | Algo ainda não decidido ou não executado. | Deve aparecer em pontos em aberto. |
