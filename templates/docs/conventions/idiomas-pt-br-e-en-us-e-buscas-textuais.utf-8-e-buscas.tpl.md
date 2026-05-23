# UTF-8 e Buscas Textuais

<!-- AGENT-CARD START -->
Leia este documento ao preservar codificação textual ou procurar termos naturais em `pt-BR` e `en-US`.
Use este documento para evitar perda de acentos, falso negativo em buscas e conclusões baseadas em apenas uma variante de idioma.
<!-- AGENT-CARD END -->

Esta subconvention define regras de codificação textual e busca para conteúdo natural em `pt-BR` e `en-US`.

## Regras de codificação

- Arquivos textuais deste repositório devem preservar codificação UTF-8.
- Não converta texto natural para ASCII puro para "padronizar", "facilitar busca" ou "evitar incompatibilidade".
- Caracteres próprios do `pt-BR`, como acentos e cedilha, devem ser preservados.
- Texto natural em `en-US` também não deve ser rebaixado artificialmente para ASCII quando o arquivo já suporta UTF-8.
- ASCII puro só é aceitável quando o conteúdo for um literal técnico restrito por contrato, ferramenta ou protocolo.

## Regras de busca

- Ao procurar texto natural em `pt-BR`, consulte variantes com e sem acentuação para evitar falso positivo e falso negativo.
- Ao procurar um conceito que possa aparecer em `pt-BR` ou `en-US`, consulte os termos relevantes nos dois idiomas.
- Quando a ferramenta permitir, combine variantes na mesma expressão. Quando não permitir, execute buscas separadas.
- Em revisões e refatorações textuais, confirme a forma preferida e as formas legadas antes de concluir que um termo não existe mais no repositório.
- Não trate a ausência de uma variante ortográfica, acentuada ou em outro idioma como prova de ausência do conceito.

## Exemplos de busca

- `rg -n 'repositório|repositorio'`
- `rg -n 'instrução|instrucao|instruction'`
- `rg -n 'idioma|language'`
- `rg -n 'mensagem|message'`
- `rg -n 'ação|acao|action'`
