# Idiomas PT-BR e EN-US, UTF-8 e Buscas Textuais

<!-- AGENT-CARD START -->
Leia este documento ao escrever, revisar ou buscar texto natural neste repositório.
Use este documento como referência para decidir quando usar `pt-BR` ou `en-US`, como preservar UTF-8 e como executar buscas textuais nos dois idiomas.
<!-- AGENT-CARD END -->

Este documento é o ponto de entrada para a política de idioma, codificação e busca textual do repositório. Leia a subconvention específica quando a dúvida envolver chat do agente, artefatos OpenSpec, textos gerais do repositório ou busca textual.

## Escopo

- Esta família define quando usar `pt-BR` e `en-US`, como preservar UTF-8 e como buscar conceitos textuais que possam aparecer em mais de um idioma.
- A regra padrão do repositório continua sendo `pt-BR` para texto natural fora de OpenSpec.
- Artefatos OpenSpec usam `en-US` por contrato local.
- Literais técnicos e contratuais preservam a grafia própria, mesmo quando isso mistura idiomas ao redor de comandos, caminhos, chaves ou valores exatos.

## Regras gerais

- Use `pt-BR` como idioma padrão para comunicação do agente e texto natural fora de OpenSpec.
- Use `en-US` em `openspec/**`, incluindo nomes de changes, capabilities, specs e conteúdo dos artefatos.
- Use `en-US` fora de OpenSpec apenas quando o conteúdo precisar permanecer em inglês por contrato, convenção externa, interoperabilidade ou fidelidade terminológica.
- Identificadores técnicos, nomes de arquivos, caminhos, chaves de configuração, marcadores, nomes de campos, comandos, flags, nomes de protocolos, schemas e outros literais contratuais devem manter sua grafia técnica original, mesmo quando isso resultar em `en-US`.
- Não misture idiomas no mesmo texto natural sem necessidade. Quando a frase estiver em português, mantenha em inglês apenas os literais técnicos ou trechos explicitamente intencionais.
- Ao criar conteúdo novo, decida o idioma principal antes de escrever e preserve essa escolha de forma consistente no documento, na seção ou na mensagem.
