> Arquivo gerado. Não edite manualmente.
> Altere a fonte e o manifesto aplicáveis e use o fluxo público de publicação do repositório.

# Relação entre Convention Pai e Subconvention Filha

Este documento explica como a relação entre `convention` pai e `subconvention` filha funciona na autoria e na publicação.

## Propósito e escopo

- Esta `convention` vale para criação, revisão, renomeação e reorganização de `conventions` com subconventions relacionadas.
- Use este documento quando precisar decidir nomes de arquivos, vínculo entre pai e filha ou destino publicado esperado.
- Este documento cobre apenas a relação estrutural entre arquivos-fonte relacionados.
- Este documento não substitui a `convention` de composição, que continua explicando a diferença entre fonte, manifesto e artefato final publicado.

## Padrão de nomeação

```text
<raiz>.tpl.md
<raiz>.<subtema>.tpl.md
```

- Use `<raiz>.tpl.md` para a `convention` pai.
- Use `<raiz>.<subtema>.tpl.md` para cada `subconvention` filha da mesma família.
- Use apenas um nível adicional depois da raiz para arquivos filhos.
- Mantenha o arquivo pai e os arquivos filhos no mesmo diretório de origem.

## Vínculo entre pai e filha

- Toda `subconvention` filha deve compartilhar a mesma raiz nominal do arquivo pai.
- Toda `subconvention` filha depende da existência do arquivo pai correspondente.
- Não trate um arquivo filho como válido de forma isolada, sem o pai da mesma raiz.
- Registre no manifesto apenas o arquivo pai da família.

## Correspondência com os artefatos publicados

```text
fontes
├── politica.tpl.md
├── politica.excecoes.tpl.md
└── politica.detalhes.tpl.md

publicados
├── politica.md
├── politica.excecoes.md
└── politica.detalhes.md
```

- O artefato publicado preserva o nome relativo do arquivo-fonte.
- A publicação troca apenas o sufixo `.tpl.md` por `.md`.
- O nome publicado da `subconvention` continua ligado ao nome publicado do pai pela mesma raiz.

## O que evitar

- criar arquivo filho com mais de um nível adicional no nome
- criar `subconvention` filha sem o arquivo pai correspondente
- registrar diretamente no manifesto um arquivo-fonte filho
- usar nomes que quebrem a raiz compartilhada entre pai e filha
