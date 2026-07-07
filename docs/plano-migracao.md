# Plano inicial de migracao Eletron

## Objetivo

Migrar o sistema atual de Reservas/Pedidos do HFSQL para PostgreSQL e reconstruir a aplicacao com backend FastAPI e frontend web desacoplado, preservando o historico e criando uma base tecnica evolutiva.

## Ponto de partida encontrado

O diretorio `ExportHFSQL` contem CSVs exportados do sistema atual. Os arquivos estao em UTF-16LE e devem ser lidos/importados com essa codificacao.

Maiores tabelas identificadas:

| Arquivo | Registros | Papel provavel |
| --- | ---: | --- |
| `T021_ItesReserva.csv` | 71.755 | Itens das reservas |
| `T020_ReservaProdutos.csv` | 35.807 | Cabecalho das reservas/PDV |
| `T030_Titulo.csv` | 33.095 | Titulos/pagamentos |
| `T066_PedidoItens.csv` | 6.852 | Itens de pedidos tipo revista |
| `T061_Produtos.csv` | 4.122 | Produtos sincronizados/consultados |
| `T030_Caixa.csv` | 2.094 | Abertura/fechamento de caixa |
| `T080_BaseComissao.csv` | 1.974 | Base de comissao |
| `T050_Fornecedor.csv` | 1.057 | Fornecedores |
| `T065_Pedidos.csv` | 308 | Pedidos corporativos/revista |

## Estrategia de dados

1. Criar um banco PostgreSQL novo.
2. Criar schema `legacy` com tabelas espelho dos CSVs.
3. Importar os dados brutos mantendo nomes e valores originais.
4. Criar schema principal normalizado por dominio.
5. Criar tabelas de de-para para preservar IDs legados:
   - `legacy_entity_map`
   - `legacy_table_map`
   - campos `legacy_*_id` nas tabelas novas quando fizer sentido.
6. Validar totais entre legado e novo antes de liberar qualquer modulo.

## Dominios iniciais

- Empresas e grupos
- Usuarios, perfis, permissoes e empresas permitidas
- Vendedores e vinculo com filiais
- Produtos, cores, colecoes, fornecedores e grupos de mercadoria
- Reservas/PDV, itens, descontos, trocas e pagamentos
- Caixa
- Pedidos tipo revista/porta a porta, itens, prazos e emails
- Clientes Proton e condicoes de venda
- Comissoes, metas, corridas/pontos e relatorios
- Integracoes externas: Oracle/Proton, TecnoSpeed, PagBank, WhatsApp

## Stack recomendada

Backend:

- Python 3.12+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- PostgreSQL
- `python-oracledb` para consultar Oracle/Proton
- JWT com refresh token, perfis e permissoes por modulo/acao

Frontend:

- TypeScript
- Vue 3 + Vite
- Bootstrap 5
- Pinia para estado
- Vue Router
- Axios ou TanStack Query para HTTP/cache

Recomendacao: Vue 3 e uma boa escolha para este projeto porque tende a ser rapido para telas administrativas, cadastros, dashboards e fluxos de PDV, com curva menor que React em times pequenos. React tambem serviria, mas Vue combina melhor com evolucao incremental e produtividade em CRUDs.

## Arquitetura backend proposta

Estrutura por modulos, mantendo separacao parecida com MVC:

```text
backend/
  app/
    core/
      config.py
      security.py
      database.py
    modules/
      auth/
        controller.py
        service.py
        repository.py
        models.py
        schemas.py
      reservas/
      pedidos/
      produtos/
      caixas/
      comissoes/
      proton/
    main.py
  alembic/
  tests/
```

No FastAPI, o "controller" normalmente e chamado de router. Podemos usar `controller.py` se isso deixar a arquitetura mais familiar.

## Primeira entrega tecnica sugerida

1. Criar projeto base `backend` com FastAPI, SQLAlchemy, Alembic e testes. [feito]
2. Criar projeto base `frontend` com Vue 3, TypeScript e Bootstrap. [feito]
3. Criar `docker-compose.yml` com PostgreSQL. [feito]
4. Criar schema `legacy` e importador dos CSVs. [feito]
5. Criar primeiro modelo novo. [iniciado]
   - empresas
   - formas de pagamento
   - reservas
   - itens de reserva
   - titulos/pagamentos [pendente]
6. Criar endpoints autenticados de consulta de reservas.
7. Criar tela inicial de listagem de reservas. [feito]

## Regras importantes de migracao

- Nunca substituir diretamente o historico por uma interpretacao do modelo novo.
- Primeiro importar bruto, depois transformar.
- Todo registro migrado deve permitir rastrear o arquivo/tabela e ID original.
- Campos financeiros devem virar `numeric(14,2)` ou `numeric(14,4)`, nunca `float`.
- Datas como `20230401` devem virar `date`; horas como `141959` devem virar `time`.
- Senhas antigas devem ser consideradas inseguras: usuarios devem redefinir senha no novo sistema.
- Tokens e credenciais exportadas devem ser rotacionados antes de producao.

## Perguntas pendentes

- O PostgreSQL sera local, servidor interno ou cloud?
- A integracao com Oracle/Proton sera leitura direta em tempo real ou sincronizacao periodica?
- O PDV precisa funcionar offline?
- Quais telas sao obrigatorias no primeiro MVP?
- Quem usa o sistema: loja, backoffice, vendedor externo, cliente corporativo?
