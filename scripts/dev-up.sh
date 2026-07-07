#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
EXPORT_DIR="$ROOT_DIR/ExportHFSQL"

RUN_INSTALL=1
RUN_IMPORT=1
RUN_BACKEND=1
RUN_FRONTEND=1

usage() {
  cat <<'EOF'
Uso:
  ./scripts/dev-up.sh [opcoes]

Opcoes:
  --skip-import    Nao importa/transforma os CSVs HFSQL.
  --no-install     Nao instala dependencias Python/Node.
  --backend-only   Sobe apenas PostgreSQL + backend.
  --frontend-only  Sobe apenas frontend.
  -h, --help       Mostra esta ajuda.

Servicos:
  Backend:  http://127.0.0.1:8000
  Frontend: http://127.0.0.1:5173
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-import)
      RUN_IMPORT=0
      shift
      ;;
    --no-install)
      RUN_INSTALL=0
      shift
      ;;
    --backend-only)
      RUN_FRONTEND=0
      shift
      ;;
    --frontend-only)
      RUN_BACKEND=0
      RUN_IMPORT=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Opcao desconhecida: $1"
      usage
      exit 1
      ;;
  esac
done

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Comando obrigatorio nao encontrado: $1"
    exit 1
  fi
}

backend_python() {
  if [[ -x "$BACKEND_DIR/.venv/Scripts/python.exe" ]]; then
    echo "$BACKEND_DIR/.venv/Scripts/python.exe"
  elif [[ -x "$BACKEND_DIR/.venv/bin/python" ]]; then
    echo "$BACKEND_DIR/.venv/bin/python"
  else
    echo ""
  fi
}

run_backend_setup() {
  require_command python

  if [[ ! -d "$BACKEND_DIR/.venv" ]]; then
    echo "Criando ambiente virtual do backend..."
    python -m venv "$BACKEND_DIR/.venv"
  fi

  PYTHON_BIN="$(backend_python)"
  if [[ -z "$PYTHON_BIN" ]]; then
    echo "Nao encontrei o Python do ambiente virtual em backend/.venv."
    exit 1
  fi

  if [[ "$RUN_INSTALL" -eq 1 ]]; then
    echo "Instalando dependencias do backend..."
    "$PYTHON_BIN" -m pip install -e "${BACKEND_DIR}[dev]"
  fi

  echo "Aplicando migrations..."
  (cd "$BACKEND_DIR" && "$PYTHON_BIN" -m alembic upgrade head)

  if [[ "$RUN_IMPORT" -eq 1 ]]; then
    if find "$EXPORT_DIR" -maxdepth 1 -name '*.csv' -print -quit | grep -q .; then
      echo "Importando CSVs HFSQL para legacy..."
      (cd "$BACKEND_DIR" && "$PYTHON_BIN" scripts/import_legacy_csvs.py --input "$EXPORT_DIR")

      echo "Transformando dados iniciais..."
      (cd "$BACKEND_DIR" && "$PYTHON_BIN" scripts/transform_reservas.py)
    else
      echo "Nenhum CSV encontrado em $EXPORT_DIR. Pulando importacao."
    fi
  fi
}

run_frontend_setup() {
  if command -v npm.cmd >/dev/null 2>&1; then
    NPM_BIN="npm.cmd"
  else
    require_command npm
    NPM_BIN="npm"
  fi

  if [[ "$RUN_INSTALL" -eq 1 ]]; then
    echo "Instalando dependencias do frontend..."
    (cd "$FRONTEND_DIR" && "$NPM_BIN" install)
  fi
}

start_processes() {
  PIDS=()

  if [[ "$RUN_BACKEND" -eq 1 ]]; then
    PYTHON_BIN="$(backend_python)"
    echo "Subindo backend em http://127.0.0.1:8000 ..."
    (cd "$BACKEND_DIR" && "$PYTHON_BIN" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000) &
    PIDS+=("$!")
  fi

  if [[ "$RUN_FRONTEND" -eq 1 ]]; then
    if command -v npm.cmd >/dev/null 2>&1; then
      NPM_BIN="npm.cmd"
    else
      NPM_BIN="npm"
    fi
    echo "Subindo frontend em http://127.0.0.1:5173 ..."
    (cd "$FRONTEND_DIR" && "$NPM_BIN" run dev) &
    PIDS+=("$!")
  fi

  if [[ "${#PIDS[@]}" -eq 0 ]]; then
    echo "Nenhum processo para subir."
    exit 0
  fi

  trap 'echo "Encerrando servicos..."; kill "${PIDS[@]}" 2>/dev/null || true' INT TERM EXIT
  wait "${PIDS[@]}"
}

cd "$ROOT_DIR"

if [[ ! -f "$ROOT_DIR/.env" ]]; then
  echo "Criando .env a partir de .env.example..."
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
fi

if [[ "$RUN_BACKEND" -eq 1 ]]; then
  require_command docker
  echo "Subindo PostgreSQL..."
  docker compose up -d postgres
  run_backend_setup
fi

if [[ "$RUN_FRONTEND" -eq 1 ]]; then
  run_frontend_setup
fi

start_processes
