> Arquivo gerado. Não edite manualmente.
> Altere a fonte e o manifesto aplicáveis e use o fluxo público de publicação do repositório.

# Python no Host para Artefatos Estruturados

Use este documento quando a tarefa envolver automação local com Python no host e artefatos estruturados.

## Manutenção

Mantenha este documento curto, direto e prático.

Registre aqui apenas critérios de escolha de ferramenta no host para automação e manipulação de artefatos estruturados. Não misture com estilo de código do projeto, apresentação visual de documentos ou regras gerais de confirmação.

## Escopo

Esta convenção vale quando o agente precisar ler, extrair, transformar, consolidar ou inspecionar artefatos estruturados no host.

Ela cobre, por exemplo:
- planilhas
- CSV
- JSON
- XML
- ZIP
- arquivos tabulares ou hierárquicos
- automações locais de baixo atrito para consolidar dados

Ela não obriga uso de Python quando a tarefa for read-only simples e ficar mais clara com leitura direta ou busca textual.

## 1. Prefira `python3` no host quando ele for solução viável e rápida

Sempre que `python3` no host resolver a tarefa de forma simples e rápida, prefira essa abordagem.

## 2. Use a biblioteca já disponível mais adequada ao artefato

Ao usar `python3`, escolha a biblioteca já disponível no host mais adequada ao tipo de artefato e à operação desejada.

Não substitua essa escolha por shell, parsing manual, utilitário genérico ou acesso ao formato interno do arquivo só por hábito ou conveniência.

## 3. Não desça de nível sem necessidade real

Se uma biblioteca adequada resolver o problema com menos fragilidade e menor complexidade, prefira a biblioteca.

Só recorra a uma abordagem mais manual quando a tarefa exigir esse controle ou quando houver limitação técnica concreta.

## 4. Se faltar biblioteca, explicite isso objetivamente

Se a biblioteca mais adequada não estiver disponível, informe qual pacote falta, por que ele é o mais apropriado e só proponha instalação mediante autorização explícita, conforme o `AGENTS.md`.

## 5. Entre opções viáveis em Python, escolha a mais simples

Se houver mais de uma solução viável em `python3`, escolha a de menor complexidade estrutural entre as que usam a biblioteca mais adequada.
