# Log De Execução: `<slug-topic>`

## Versão

- Versão: `<vN>`
- Motivo da versão: `<criação inicial ou mudança de plano>`
- Regra de conteúdo: eventos deste arquivo pertencem somente a esta pasta de versão.

## Convenção Append-Only

Acrescente novos eventos no fim de `## Entradas` desta versão. Não reescreva eventos anteriores, salvo correção explícita registrada em novo evento.

Mudanças de plano, escopo, bloqueio ou evidência que alterem a versão ativa criam uma nova pasta `vN+1/` com novo `log.md`.

## Tipos de Evento

- `initialization`: criação inicial dos artefatos de handoff.
- `preflight`: inspeção inicial antes de editar.
- `evidence`: evidência coletada para cumprir `dod.md`.
- `plan-change`: mudança de plano, escopo, versão ou critério de aceite.
- `blocker`: bloqueio que impede continuação segura.
- `handoff`: transferência para outro agente ou pessoa.
- `completion`: conclusão do handoff.

## Entradas

### LOG-001

- Timestamp: `<YYYY-MM-DD HH:MM TZ>`
- Plano vigente: `<vN>`
- Tipo: initialization
- Ação: Handoff criado em `.tmp/prompts/<slug-topic>/<vN>/`.
- Comando: n/a
- CWD: `<diretório em que o handoff foi criado>`
- Destino: `.tmp/prompts/<slug-topic>/<vN>/`
- Arquivos/recursos afetados:
  - `.tmp/prompts/<slug-topic>/<vN>/prompt.md`
  - `.tmp/prompts/<slug-topic>/<vN>/dod.md`
  - `.tmp/prompts/<slug-topic>/<vN>/log.md`
- Resultado: `<resumo operacional dos artefatos criados nesta versão>`
- Evidência: `<como a criação foi verificada>`
- DOD relacionado: `<vN>/DOD-001 a <vN>/DOD-N ainda pendentes ou status inicial`
- Risco ou bloqueio: `<risco inicial ou n/a>`
- Próximo estado retomável: `<primeira ação concreta para quem continuar>`
