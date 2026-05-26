> Arquivo gerado. Não edite manualmente.
> Altere a fonte e o manifesto aplicáveis e use o fluxo público de publicação do repositório.

# Estrutura de Arquivos-Fonte `.tpl.md`

Este documento explica a estrutura mínima que um arquivo-fonte `.tpl.md` deve seguir para participar da composição das instruções compartilhadas.

## Propósito e escopo

- Esta `convention` vale para qualquer arquivo-fonte `.tpl.md` usado como `convention` pai ou `subconvention` filha.
- Use este documento quando precisar criar uma fonte nova, revisar uma fonte existente ou confirmar se a estrutura do arquivo continua válida.
- Este documento cobre a estrutura mínima pública do arquivo-fonte e a classificação de valores literais usados como orientação normativa.
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

## Classificação de valores literais

Antes de escrever caminho, diretório, nome de arquivo, nome de skill, raiz de fonte, destino publicado ou outro valor literal como regra direta, classifique esse valor.

Use estas categorias:

| Categoria | Como escrever |
|---|---|
| fixo por contrato | cite o literal e diga que ele é exigido pelo contrato |
| configurado no manifesto | cite o campo de `agents-compose.yml` como fonte normativa |
| derivado de outro campo | descreva a regra de derivação e cite o campo de origem |
| exemplo | deixe claro que o literal é apenas exemplo |
| valor atual do repositório | diga que o literal é o valor atual declarado no manifesto do repositório |
| saída de ferramenta externa | identifique a ferramenta ou workflow responsável |

Quando o valor vier de `agents-compose.yml`, não trate o valor atual como diretório fixo.
Use o campo do manifesto como regra, como `outputs.AGENTS.md.include.conventions.out_dir`, `outputs.AGENTS.md.include.conventions.local.tpl_dir`, `outputs.AGENTS.md.include.conventions.remote.tpl_dir`, `outputs.skills.out_dir`, `outputs.skills.local.tpl_dir`, `outputs.skills.remote.tpl_dir` ou `entries[].from`.

Valores literais podem aparecer em exemplos, diagnósticos, contexto local ou casos fixos por contrato, desde que essa classificação esteja clara no texto.

## Papel do `AGENT-CARD`

- O `AGENT-CARD` resume quando o documento deve ser lido e como ele deve ser usado.
- O `AGENT-CARD` faz parte da fonte, não do corpo normativo principal do documento.
- Escreva o `AGENT-CARD` com instruções curtas, operacionais e legíveis para agentes.

## O que evitar

- criar mais de um título principal no mesmo arquivo
- duplicar o bloco `AGENT-CARD`
- deixar o bloco `AGENT-CARD` vazio
- misturar dentro do `AGENT-CARD` o conteúdo normativo principal do documento
- transformar valor configurável do manifesto em caminho fixo apenas porque esse é o valor atual do repositório
