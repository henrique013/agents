---
name: update-version
description: Gera a próxima versão semver deste repositório com prévia isolada, um gate final de publicação e tag anotada no commit versionado.
---

# Versionamento da release

Use a skill `update-version` quando a pessoa quiser publicar uma nova versão semver do repositório `agents`.
Trate a própria skill como a interface pública do fluxo.

## Escopo

- Esta skill publica `main` e uma tag anotada `vX.Y.Z` no `HEAD` versionado da release.
- A fonte autoral fica em `templates/skills-local/update-version/`.
- A saída publicada fica em `.codex/skills/update-version/` e deve ser materializada pelo fluxo público `update-docs`, não por edição manual.
- Antes do gate final, a worktree principal não deve receber alterações de arquivos, commits, tags ou push.
- A preparação necessária para decidir a versão deve acontecer em uma prévia isolada.
- A confirmação final autoriza somente os efeitos apresentados no resumo de publicação.

## Responsabilidades

- O agente decide `major`, `minor` ou `patch`.
- A decisão deve considerar o range preparado da release, incluindo alterações válidas que `update-docs` produziria.
- O helper interno só executa e valida passos mecânicos: estado Git, versão de pacote, prévia isolada, caminhos gerados e sincronização de metadados.
- Não empurre a classificação semântica para o helper.

## Critérios do bump

- Use `major` quando a mudança quebrar contrato, compatibilidade ou comportamento esperado por consumidores.
- Use `minor` quando a mudança adicionar capacidade sem quebrar compatibilidade.
- Use `patch` quando a mudança corrigir, refatorar ou documentar sem mudar contrato nem comportamento observável.
- Em caso de dúvida, escolha o menor bump que preserve compatibilidade real.
- Se a classificação continuar ambígua, explique a ambiguidade no gate final.

## Fluxo

### 1. Inspeção inicial

Faça apenas inspeção local e read-only:

- confirme que a branch é `main`
- confirme que a worktree está limpa
- capture o `HEAD` inicial
- capture `origin/main`
- descubra a última tag semver local
- valide que `package.json.version` corresponde à última tag semver local sem `v`

Se qualquer premissa falhar, pare e diga exatamente o que precisa ser corrigido.

### 2. Prévia isolada

Crie uma prévia isolada a partir do `HEAD` inicial validado.

Na prévia:

- use a skill `update-docs`
- valide que eventuais alterações ficaram restritas aos artefatos gerados permitidos
- crie um commit local de prévia para artefatos gerados, se houver alterações, com a mensagem:
  `chore(repo): sincroniza artefatos gerados da release`
- inspecione o range `<ultima-tag-semver>..HEAD` preparado
- decida o bump e calcule a próxima versão

A prévia serve para decisão e resumo. Ela não deve criar tag, push nem substituir a execução real na worktree principal.
Limpe a prévia quando ela não for mais necessária.

### 3. Gate final único

Antes de alterar a worktree principal, criar tag ou fazer push, apresente um único resumo de publicação com:

- versão proposta, como `v3.9.0`
- bump escolhido e motivo curto
- última tag semver local usada como base
- resumo do range preparado
- resultado da prévia de `update-docs`, incluindo se haverá commit de artefatos gerados
- exemplos documentados de consumidores que serão sincronizados com a versão proposta
- commits que serão criados na worktree principal
- tag anotada que será criada
- push que será feito
- recursos externos afetados: branch `main` e tag Git em `origin`

Não despeje a lista completa de comandos internos no fluxo normal.
Mostre comandos internos somente se a pessoa pedir ou se forem necessários para explicar um erro.

Sem confirmação explícita do gate final, não altere a worktree principal, não crie commit, não crie tag e não faça push.

### 4. Publicação confirmada

Depois da confirmação:

- atualize a visão local de `origin`
- revalide branch, worktree limpa, `HEAD`, última tag semver local, `origin/main` e `package.json.version` contra as premissas confirmadas
- use a skill `update-docs` na worktree principal
- valide os caminhos gerados, se houver alterações
- crie o commit de artefatos gerados quando necessário:
  `chore(repo): sincroniza artefatos gerados da release`
- se a preparação real divergir materialmente da prévia, pare e apresente um novo gate final
- sincronize `package.json.version` e `package-lock.json` com a versão confirmada
- sincronize os exemplos documentados de consumidores com a versão confirmada
- crie o commit de metadado de versão:
  `chore(repo): atualiza versão para vA.B.C`
- valide o estado final antes da tag
- crie a tag anotada `vA.B.C` no `HEAD` versionado
- publique `main` e `vA.B.C` juntos

## Limites

- Não modifique `agents-compose.yml`.
- Não atualize `agents.ref`.
- Não crie tag antes de rodar `update-docs` na publicação confirmada.
- Não faça push antes de sincronizar metadados de versão e criar a tag local.
- Não publique tag que aponte para um commit anterior às alterações válidas geradas por `update-docs`.
- Não publique tag que aponte para um commit anterior ao commit `chore(repo): atualiza versão para vA.B.C`.
- Não execute o script interno da `update-docs` como interface pública normal.
