# Estrutura de Arquivos-Fonte `.tpl.md`

<!-- AGENT-CARD START -->
Leia este documento ao criar, revisar ou ajustar uma `convention`-fonte ou `subconvention`-fonte em um repositório consumidor.
Use este documento para definir a estrutura mínima pública dos arquivos `.tpl.md` que entram na publicação.
<!-- AGENT-CARD END -->

Este documento explica a estrutura mínima que um arquivo-fonte `.tpl.md` deve seguir para participar da composição das instruções compartilhadas.

## Propósito e escopo

- Esta `convention` vale para qualquer arquivo-fonte `.tpl.md` usado como `convention` pai ou `subconvention` filha.
- Use este documento quando precisar criar uma fonte nova, revisar uma fonte existente ou confirmar se a estrutura do arquivo continua válida.
- Este documento cobre apenas a estrutura mínima pública do arquivo-fonte.
- Este documento não substitui outras `conventions` do repositório sobre idioma, apresentação visual ou conteúdo normativo.

## Estrutura mínima

Prefira esta forma:

```text
Título H1 do documento

AGENT-CARD START
  Leia este documento ao...
  Use este documento para...
AGENT-CARD END

Texto introdutório e seções do corpo
```

## Regras públicas

- Cada arquivo-fonte deve conter exatamente um heading Markdown de nível 1.
- Cada arquivo-fonte deve conter exatamente um bloco `AGENT-CARD`.
- O bloco `AGENT-CARD` deve conter ao menos uma linha não vazia.
- O corpo do documento deve ficar fora do bloco `AGENT-CARD`.
- O texto natural do arquivo continua sendo o conteúdo autoral mantido pelo repositório.

## Papel do `AGENT-CARD`

- O `AGENT-CARD` resume quando o documento deve ser lido e como ele deve ser usado.
- O `AGENT-CARD` faz parte da fonte, não do corpo normativo principal do documento.
- Escreva o `AGENT-CARD` com instruções curtas, operacionais e legíveis para agentes.

## O que evitar

- criar mais de um título principal no mesmo arquivo
- duplicar o bloco `AGENT-CARD`
- deixar o bloco `AGENT-CARD` vazio
- misturar dentro do `AGENT-CARD` o conteúdo normativo principal do documento
