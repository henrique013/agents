# Handoff Prompt

## Objetivo

`<descreva o resultado concreto que o próximo agente deve alcançar>`

## Escopo

### Dentro do escopo

- `<item dentro do escopo>`

### Fora do escopo

- `<item fora do escopo>`

## Decisões Confirmadas

- `<decisão tomada e consequência operacional>`

## Fatos Relevantes

- `<fato verificável que o próximo agente pode usar como base>`

## Assunções

- `<assunção explícita que ainda pode precisar de validação>`

## Restrições

- `<restrição técnica, operacional, de prazo, política ou repositório>`

## Riscos

- `<risco concreto, impacto esperado e mitigação inicial>`

## Próximos Passos

1. `<próxima ação executável>`

## Artefatos Esperados

- `<arquivo, diff, relatório, comando validado ou outro entregável esperado>`

## Instruções Para Execução

- Comece lendo este `prompt.md`, depois confira `dod.md` e `log.md`.
- Não dependa do histórico original do chat para executar o trabalho.
- Trate decisões, fatos, assunções, restrições e riscos como categorias diferentes.
- Valide assunções antes de usá-las como fatos.
- Se encontrar conflito entre este handoff e instruções ativas do repositório, siga a hierarquia de instruções do ambiente e registre o conflito em `log.md`.

## Manutenção de dod.md e log.md

- `dod.md` contém a versão ativa do plano, critérios de aceite e evidências mínimas.
- Antes de continuar após qualquer mudança de plano ou escopo, atualize `dod.md` para a nova versão do plano.
- Depois de alterar plano, escopo, bloqueio ou evidência, acrescente um evento correspondente em `log.md`.
- Preserve `log.md` como append-only, exceto por correção explícita de erro material registrada em novo evento.
