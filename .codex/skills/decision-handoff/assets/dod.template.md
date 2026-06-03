# Definition Of Done: `<slug-topic>`

## Versão

- Versão: `<vN>`
- Atualizado em: `<YYYY-MM-DD>`
- Motivo da versão: `<criação inicial ou mudança de plano>`
- Regra de conteúdo: este DOD vale somente para esta pasta de versão.

## Estado

- Status geral: `<pendente|em-andamento|passa|falha|n/a|dispensado>`

## Checklist de Status

| ID | Item | Status | Evidência mínima | Evidência atual | Último log |
|---|---|---|---|---|---|
| DOD-001 | `<critério ou marco rastreável desta versão>` | pendente | `<comando, inspeção, teste, diff ou arquivo que comprova o item>` | - | `<vN>/LOG-001` |

## Critérios de Aceite

- [ ] `<critério verificável para considerar esta versão concluída>`

## Evidências Mínimas

- `<comando, inspeção, teste, diff, revisão ou arquivo que comprova o critério>`

## Responsável

- Papel responsável: `<agente executor, revisor, pessoa usuária ou outro papel>`

## Regras De Status

| Status | Uso |
|---|---|
| pendente | Item ainda não iniciado. |
| em-andamento | Item em execução ou validação. |
| passa | Critério satisfeito com evidência registrada. |
| falha | Critério testado e não satisfeito. |
| n/a | Item não aplicável por motivo registrado. |
| dispensado | Dispensado por decisão explícita registrada. |

## Regra De Mudança De Plano

- Uma nova versão do plano deve ser criada como nova pasta `vN+1/`.
- A raiz `.tmp/prompts/<slug-topic>/` deve conter somente pastas `v1/`, `v2/`, etc.
- Não misture conteúdo de versões diferentes na mesma pasta.
- Em versões posteriores, escreva apenas o que mudou em relação à versão anterior.
- Para categorias sem mudança, registre `Sem mudança nesta versão.`.

## Vínculo com log.md

- Registre em `log.md` da mesma pasta todo início, bloqueio, mudança de plano, evidência coletada e conclusão.
- Use `Último log` com referência completa, como `<vN>/LOG-001`.
