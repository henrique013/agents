> Arquivo gerado. Não edite manualmente.
> Altere a fonte e o manifesto aplicáveis e use o fluxo público de publicação do repositório.

# UUID em Novas Implementações

Use `UUIDv7` como padrão para novas implementações que precisem gerar UUID quando o usuário não pedir uma versão específica e quando não houver restrição técnica contrária.

## Regra principal

- Prefira `UUIDv7` em código novo que gere UUID.
- Trate `UUIDv7` como identificador ordenável por tempo, composto por timestamp Unix em milissegundos e aleatoriedade.
- Para UUID persistido em banco, especialmente em coluna indexada, chave primária ou índice com alta escrita, prefira `UUIDv7` quando não houver exceção explícita.
- Explique a escolha por localidade de índice melhor que UUIDs totalmente randômicos, sem prometer ganho de performance universal.
- Não descreva `UUIDv7` como sequência incremental simples.

## Exceções

Não aplique o padrão `UUIDv7` quando:

- o usuário pedir explicitamente `UUIDv4`, `UUIDv5` ou outra versão suportada pelo contexto
- contrato externo exigir outra versão ou outro formato de identificador
- schema existente, API pública, framework, banco, biblioteca ou integração exigir versão ou formato específico
- o trabalho tocar código, schema ou dado existente que já use `UUIDv4` ou outra versão

Usos existentes de `UUIDv4` ou de outras versões não devem ser refatorados nem migrados para `UUIDv7` sem pedido explícito do usuário.

## Opacidade e segurança

- Trate UUID como identificador opaco no código de negócio.
- Não extraia timestamp, ordem ou semântica de negócio a partir de um `UUIDv7`; modele esses dados em campos próprios.
- Não use UUID como segredo, token de autenticação, credencial ou mecanismo de autorização.

## Geração

- Use suporte nativo da linguagem, runtime, banco ou framework quando ele atender ao requisito.
- Se o projeto já tiver uma biblioteca instalada capaz de gerar a versão necessária, prefira essa biblioteca.
- Se não houver suporte nativo nem biblioteca instalada para gerar `UUIDv7`, sugira uma biblioteca comum e mantida para a stack de trabalho.
- Não implemente gerador local manual de UUID como substituto de suporte mantido pela stack.
- Antes de instalar nova dependência, respeite a política de confirmação e instalação de dependências do repositório.
