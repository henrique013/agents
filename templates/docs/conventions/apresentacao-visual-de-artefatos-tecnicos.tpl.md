# Apresentação Visual de Artefatos Técnicos

<!-- AGENT-CARD START -->
Leia este documento ao criar, revisar ou reorganizar specs, RFCs, instruções operacionais, documentação técnica ou qualquer artefato cujo entendimento dependa de fluxo, estrutura, hierarquia, mapeamento, comparação ou decomposição.
Use este documento para decidir quando preferir parágrafo curto, lista estruturada, tabela, árvore ASCII ou fluxograma ASCII.
<!-- AGENT-CARD END -->

Use este documento para padronizar a apresentação visual de artefatos técnicos voltados à leitura humana.

## Manutenção

Mantenha este documento curto, direto e prático.

Registre aqui apenas critérios de apresentação visual de artefatos técnicos. Não misture com regras gerais de escrita, confirmação, estilo de código ou arquitetura local.

## Escopo

- Esta `convention` vale para artefatos técnicos legíveis por humanos cujo entendimento dependa de fluxo, estrutura, hierarquia, mapeamento, comparação ou decomposição.
- Ela cobre, por exemplo, specs, RFCs, instruções operacionais, documentação técnica, descrições de pipeline e mapeamentos de dados.
- Ela não se destina a notas curtas, respostas rápidas, changelogs, mensagens de commit ou textos que não dependam de relação estrutural para serem entendidos.
- Ela não obriga uso de representação visual quando um parágrafo curto comunicar melhor com menos esforço cognitivo.

## 1. Prefira forma visual ao explicar relações técnicas

Sempre que uma informação técnica puder ser entendida mais rápido em formato visual do que em prosa corrida, prefira o formato visual.

Não use texto corrido como default para explicar fluxo, pipeline, hierarquia, composição, mapeamento ou comparação.

## 2. Escolha a forma pelo tipo de entendimento necessário

Use fluxograma ASCII para:
- fluxo principal
- pipeline
- sequência operacional
- transição de estado
- tratamento de erro

Use árvore ASCII para:
- hierarquia
- composição estrutural
- organização de arquivos
- decomposição de partes

Use tabela para:
- comparação
- mapeamento `campo -> origem -> destino`
- contrato de dados
- responsabilidades por item

Use lista estruturada para:
- regras
- critérios
- restrições
- decisões
- checkpoints

Use parágrafo curto para:
- contexto
- conclusão
- observações simples que não ganhem clareza com estrutura visual

## 3. Trate o fluxo principal como caso obrigatório por padrão

Em specs e documentos técnicos semelhantes, apresente o fluxo principal em formato visual quando houver múltiplas etapas, ramificações, dependências ou tratamento de erro.

Só deixe de usar formato visual quando ele claramente piorar a clareza do conteúdo.

## 4. Exemplo canônico de fluxo principal

Prefira:

```text
processar_lote(entradas)
  |
  +-> validar entradas
  |     - origem obrigatória
  |     - formato suportado
  |
  +-> carregar configuração
  |
  +-> para cada item
        |
        +-> transformar dados
        +-> validar resultado
        +-> salvar saída
        |
        +-> em caso de erro
              - registrar contexto do item
              - seguir para o próximo item
```

Evite:

```md
O processo valida as entradas, carrega a configuração e percorre os itens. Para cada item, transforma os dados, valida o resultado e salva a saída. Se ocorrer erro, registra o contexto e segue para o próximo item.
```

## 5. Exemplo canônico de mapeamento

Prefira:

| Campo destino | Origem | Regra |
|---|---|---|
| `id` | `registro.codigo` | manter valor original |
| `nome` | `registro.titulo` | aplicar `trim` |
| `criado_em` | `metadata.created_at` | formatar em ISO-8601 |

Evite descrever esse tipo de relação em parágrafo corrido.

## 6. Exemplo canônico de estrutura

Prefira:

```text
Pipeline de Importação
├── Main
├── LerFonte
├── TransformarDados
└── PersistirResultado
```

## 7. Regra de qualidade

- A forma visual deve ser escaneável.
- Não complique o diagrama para parecer completo.
- Prefira o menor formato que preserve clareza.
- Não repita em parágrafo corrido o que o diagrama, a tabela ou a árvore já comunicam com clareza.
- Se um exemplo visual comunicar melhor do que uma regra abstrata, inclua o exemplo.
