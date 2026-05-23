# Padrão de Mensagem de Commit

<!-- AGENT-CARD START -->
Leia este documento ao criar, sugerir ou revisar commits neste repositório.
Consulte este documento ao decidir formato, escopo e agrupamento de mudanças.
<!-- AGENT-CARD END -->

Este repositório adota o padrão Conventional Commits com convenções locais para idioma, escopo e uso de corpo e footer.

Use este padrão ao criar, sugerir ou revisar mensagens de commit neste repositório.

## Regras da mensagem

- formato: `tipo(escopo): descrição`
- idioma da descrição: `pt-br`
- use ortografia, gramática e acentuação corretas em português brasileiro
- tudo minúsculo
- header com no máximo 72 caracteres
- tipos permitidos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`, `perf`
- por padrão, não use corpo ou footer
- use corpo e footer quando o usuário pedir explicitamente
- corpo e footer também podem ser usados quando forem necessários para representar semântica obrigatória do padrão, como `BREAKING CHANGE`, ou metadados exigidos pelo usuário
- quando existirem, corpo e footer também devem respeitar 72 caracteres por linha
- não use `Co-Authored-By`

## Antes de commitar

- rode `git status` para validar o conjunto de mudanças antes de criar, sugerir ou revisar commits
- agrupe arquivos por propósito e escopo de mudança
- não misture mudanças não relacionadas no mesmo commit
- se houver grupos independentes de arquivos, proponha commits separados, cada um com sua própria mensagem
- o agente deve mostrar a mensagem exata de commit antes de criar o commit
- o agente deve mostrar os arquivos agrupados naquele commit
- o commit só pode ser executado após aprovação explícita do usuário para aquela mensagem e para aquele agrupamento

## Exemplo de agrupamento

Se houver mudanças em 3 escopos diferentes, proponha 3 commits.

Exemplo:

- mudanças em documentação: um commit
- mudanças em configuração do repositório: outro commit
- mudanças em código ou comportamento da aplicação: outro commit separado

## Exemplos de mensagens

Exemplos válidos:

- `docs(repo): esclarece convenção de mensagens de commit`
- `docs(agents): adiciona links para docs de convenções`
- `chore(repo): adiciona configuração de editor e eol`
- `feat(sync): adiciona suporte a fontes locais na configuração de composição`
- `fix(docs): corrige exemplo de composição do AGENTS.md`

Exemplos inválidos:

- `Update docs`
- `Feat(repo): Ajusta AGENTS`
- `docs: atualizações diversas`
- `fix(repo): corrige agents, templates e editorconfig`
