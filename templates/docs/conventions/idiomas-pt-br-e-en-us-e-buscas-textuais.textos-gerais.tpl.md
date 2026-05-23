# Textos Gerais do Repositório

<!-- AGENT-CARD START -->
Leia este documento ao escrever ou revisar documentação, comentários, docstrings, mensagens de erro ou CLI, templates, fixtures, exemplos e textos gerados fora de `openspec/**`.
Use este documento para decidir quando manter `pt-BR` e quando preservar `en-US` por contrato ou interoperabilidade.
<!-- AGENT-CARD END -->

Esta subconvention define o idioma do texto natural mantido no repositório fora de OpenSpec.

## Regra central

- Use `pt-BR` como idioma padrão do texto natural fora de `openspec/**`.
- Use `pt-BR` em `AGENTS.md`, `docs/`, templates de conventions, comentários, docstrings, mensagens de erro ou CLI, fixtures, exemplos e textos gerados, salvo exceção explícita.
- Use `en-US` quando o conteúdo precisar permanecer em inglês por contrato, convenção externa, interoperabilidade ou fidelidade terminológica.
- Comentários seguem a mesma política de idioma do arquivo ou seção em que aparecem.

## Literais técnicos

- Identificadores técnicos, nomes de arquivos, caminhos, chaves de configuração, marcadores, nomes de campos, comandos, flags, nomes de protocolos, schemas e outros literais contratuais devem manter sua grafia técnica original.
- Não traduza literais técnicos para `pt-BR` apenas para uniformizar a frase.
- Não misture idiomas no mesmo texto natural sem necessidade. Quando a frase estiver em português, mantenha em inglês apenas literais técnicos ou trechos explicitamente intencionais.

## Exemplos

- Evite: `Este repositorio define rules para o agente.`
- Prefira: `Este repositório define regras para o agente.`
- Evite: `Use a chave \`repositorio\` no arquivo de configuracao.`
- Prefira: `Use a chave \`repository\` no arquivo de configuração.`
- Evite: `Misture o texto em portugues with English sem necessidade.`
- Prefira: `Escolha um idioma principal para o texto e mantenha apenas os literais técnicos no outro idioma.`
