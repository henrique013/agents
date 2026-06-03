# Handoff Log

## Convenção Append-Only

Acrescente novos eventos no fim de `## Entradas`. Não reescreva eventos anteriores, salvo correção explícita de erro material registrada em um novo evento.

## Tipos de Evento

- `initialization`: criação inicial dos artefatos de handoff.
- `plan-change`: mudança de plano, escopo, versão ou critério de aceite.
- `blocker`: bloqueio que impede continuação segura.
- `evidence`: evidência coletada para cumprir `dod.md`.
- `handoff`: transferência para outro agente ou pessoa.
- `completion`: conclusão do handoff.

## Entradas

### `<YYYY-MM-DD HH:MM TZ>` - initialization

- Plano: `<v1>`
- Resumo da fonte: `<decisões e contexto usados para criar o handoff, sem copiar o chat>`
- Destino: `.tmp/prompts/<slug-topic>/`
- Artefatos gerados:
  - `prompt.md`
  - `dod.md`
  - `log.md`
