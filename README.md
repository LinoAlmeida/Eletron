# Eletron Reservas

Reconstrucao do sistema de reservas/PDV/pedidos a partir da base atual HFSQL, com PostgreSQL, FastAPI e Vue.

## Estrutura

```text
backend/          API FastAPI, SQLAlchemy, Alembic e scripts de migracao
frontend/         Vue 3, TypeScript, Bootstrap e consumo HTTP da API
ExportHFSQL/      CSVs exportados da base HFSQL atual
docs/             Inventario e plano de migracao
scripts/          Ferramentas auxiliares do workspace
```

## Subir tudo com script

No Git Bash ou WSL:

```bash
./scripts/dev-up.sh
```

Opcoes uteis:

```bash
./scripts/dev-up.sh --skip-import
./scripts/dev-up.sh --no-install --skip-import
./scripts/dev-up.sh --backend-only
./scripts/dev-up.sh --frontend-only
```

O script sobe PostgreSQL, aplica migrations, importa/transforma os CSVs quando existirem, instala dependencias e inicia backend e frontend.

No PowerShell, caso `npm install` seja bloqueado por policy, use `npm.cmd install` ou rode o script pelo Git Bash.

## Banco local

Subir PostgreSQL:

```powershell
docker compose up -d postgres
```

O PostgreSQL do Docker publica a porta local `5433` para evitar conflito com instalacoes locais na porta `5432`.

Copiar variaveis de ambiente:

```powershell
Copy-Item .env.example .env
```

## Backend

Criar ambiente virtual e instalar dependencias:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Aplicar migrations:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Importar CSVs HFSQL para o schema `legacy`:

```powershell
.\.venv\Scripts\python.exe .\scripts\import_legacy_csvs.py --input ..\ExportHFSQL
```

Transformar o primeiro bloco de dados para o modelo novo:

```powershell
.\.venv\Scripts\python.exe .\scripts\transform_reservas.py
```

Rodar API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Endpoints iniciais:

- `GET http://127.0.0.1:8000/api/v1/health`
- `POST http://127.0.0.1:8000/api/v1/auth/login`
- `GET http://127.0.0.1:8000/api/v1/auth/me`
- `GET http://127.0.0.1:8000/api/v1/reservas`

Usuario legado para teste apos importar/transformar os CSVs:

```text
Login: Master User
Senha: 11463402000149
```

Para redefinir uma senha local:

```powershell
cd backend
.\.venv\Scripts\python.exe .\scripts\set_user_password.py lino.almeida 123456
```

## Frontend

Instalar dependencias e rodar:

```powershell
cd frontend
npm install
npm run dev
```

Acessar:

```text
http://127.0.0.1:5173
```

## Fluxo de migracao

1. Importar os CSVs para `legacy` sem alterar nomes ou valores.
2. Transformar para tabelas novas por dominio.
3. Validar contagens e totais financeiros entre legado e novo.
4. Evoluir telas e endpoints por modulo.

Primeiro modulo em andamento:

- `empresas`
- `formas_pagamento`
- `reservas`
- `reserva_itens`

## Observacoes

- Os CSVs HFSQL estao em UTF-16LE sem BOM.
- Campos financeiros usam `numeric`, nao `float`.
- Datas como `20230401` viram `date`.
- Horas como `141959` viram `time`.
- IDs legados sao mantidos em campos `legacy_*`.
