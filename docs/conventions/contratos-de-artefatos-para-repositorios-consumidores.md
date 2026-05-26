> Arquivo gerado. Não edite manualmente.
> Altere a fonte e o manifesto aplicáveis e use o fluxo público de publicação do repositório.

# Contratos de Artefatos para Repositórios Consumidores

Este documento é o ponto de entrada para o tema de contratos de artefatos em repositórios consumidores.

## Propósito e escopo

- Esta `convention` reúne orientações públicas sobre os artefatos locais que entram na composição das instruções compartilhadas.
- Use este documento quando a dúvida for como criar ou revisar `agents-compose.yml`, `conventions`-fonte, `subconventions`-fonte ou pacotes de `skill` válidos.
- Use este documento para separar o contrato autoral público dos detalhes internos do fluxo de publicação.
- Quando a dúvida for sobre qual arquivo editar, fonte de verdade ou artefato final publicado, leia primeiro a `convention` de composição das instruções para repositórios consumidores.

## Papel desta família

```text
artefatos locais de composição
├── agents-compose.yml
├── convention-fonte
├── subconvention-fonte
└── skill-fonte
     |
     +-> entram no fluxo de composição/publicação
```

- A `convention` de composição explica como interpretar fonte, manifesto e artefatos publicados.
- Esta família explica como estruturar os artefatos locais que participam desse fluxo.
- As subconventions publicadas a partir deste documento detalham o manifesto, a estrutura mínima dos arquivos-fonte e a relação entre `convention` pai e `subconvention` filha.
- Pacotes de `skill` declarados no manifesto usam diretórios fonte próprios e são publicados como pacotes inteiros, sem renderização Markdown.

## Quando ler as subconventions

### Manifesto `agents-compose.yml`

Arquivo: `docs/conventions/contratos-de-artefatos-para-repositorios-consumidores.agents-compose.md`

- Leia este documento ao criar, revisar ou ajustar `agents-compose.yml` em um repositório consumidor.
- Use este documento para definir os blocos públicos mínimos do manifesto e as entradas que participam da composição.

### Estrutura de Arquivos-Fonte `.tpl.md`

Arquivo: `docs/conventions/contratos-de-artefatos-para-repositorios-consumidores.arquivos-fonte.md`

- Leia este documento ao criar, revisar ou ajustar uma `convention`-fonte ou `subconvention`-fonte em um repositório consumidor.
- Use este documento para definir a estrutura mínima pública dos arquivos `.tpl.md` que entram na publicação e classificar valores literais antes de tratá-los como contratos.

### Relação entre Convention Pai e Subconvention Filha

Arquivo: `docs/conventions/contratos-de-artefatos-para-repositorios-consumidores.relacao-pai-filha.md`

- Leia este documento ao organizar uma família de `convention` com subconventions em um repositório consumidor.
- Use este documento para nomear arquivos, manter o vínculo pai e filha, prever os artefatos publicados e descobrir subconventions acionadas.
