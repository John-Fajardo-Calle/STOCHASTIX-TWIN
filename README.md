# STOCHASTIX-TWIN

[![CI](https://github.com/John-Fajardo-Calle/STOCHASTIX-TWIN/actions/workflows/ci.yml/badge.svg)](https://github.com/John-Fajardo-Calle/STOCHASTIX-TWIN/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/github/license/John-Fajardo-Calle/STOCHASTIX-TWIN)](LICENSE)

## English

### 1) Title & Badges

**STOCHASTIX-TWIN** — a stochastic supply-chain digital twin (DES + Monte Carlo).

### 2) Project Description

STOCHASTIX-TWIN is a lightweight digital twin for a two-echelon inventory system (Distribution Center → Store). It runs a discrete-event simulation (SimPy) and supports Monte Carlo replications to quantify KPI uncertainty (service level, fill rate, stockouts, inventory averages). A minimal FastAPI backend exposes simulations as pollable jobs, and a Vite+React frontend provides an interactive dashboard.

### 3) Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2
- **Simulation**: SimPy (DES), NumPy (randomness & aggregation)
- **Frontend**: Vite, React
- **Dev / Ops**: Docker + Docker Compose, Dev Container for Codespaces
- **Testing**: pytest, httpx (ASGITransport), anyio

### 4) Prerequisites

Install the following on your machine:

- Python 3.10+ (recommended 3.11)
- Node.js 20+ and npm
- Docker Desktop (optional, for one-command startup)

### 5) Installation

Clone the repository:

```bash
git clone https://github.com/John-Fajardo-Calle/STOCHASTIX-TWIN.git
cd STOCHASTIX-TWIN
```

#### Configure environment files

Frontend (Vite):

```bash
cp frontend/.env.example frontend/.env.local
```

Backend (optional, for future configuration):

```bash
cp backend/.env.example backend/.env
```

#### Local installation (no Docker)

Create and activate a virtual environment, then install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

#### Docker installation (recommended for quick start)

```bash
docker compose build
```

### 6) Usage

#### Option A: Run with Docker Compose (one command)

```bash
docker compose up
```

- Backend health check: `http://localhost:8000/api/health`
- Frontend dashboard: `http://localhost:5173`

#### Option B: Run locally (no Docker)

Terminal 1 (backend):

```bash
source .venv/bin/activate
python -m uvicorn backend.api.app:app --reload --port 8000
```

Terminal 2 (frontend):

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

#### API examples

Health check:

```bash
curl http://localhost:8000/api/health
```

Start a simulation job (single run):

```bash
curl -X POST "http://localhost:8000/api/simulations" \
	-H "Content-Type: application/json" \
	-d '{
		"config": {
			"days": 30,
			"demand_lambda_per_day": 15,
			"demand_peaks": [],
			"s_store": 80,
			"S_store": 160,
			"s_dc": 200,
			"S_dc": 400,
			"initial_on_hand_store": 120,
			"initial_on_hand_dc": 300,
			"lead_time_mean_days": 7,
			"lead_time_std_days": 2,
			"disruption_probability_per_shipment": 0,
			"disruption_delay_days": 0,
			"seed": 123
		},
		"replications": 1
	}'
```

Poll job status until `status` is `complete` (replace `JOB_ID`):

```bash
curl "http://localhost:8000/api/simulations/JOB_ID"
```

Run tests:

```bash
source .venv/bin/activate
pytest -q
```

Build the frontend:

```bash
cd frontend
npm run build
```

### 7) Roadmap / Features

Current features:
- Discrete-event simulation of a two-echelon system (DC → Store)
- (s, S) inventory policy at Store and DC
- Lognormal lead times + optional disruption delay
- Single-run KPI output + time-series for plotting
- Monte Carlo summary (mean/std of KPIs)
- FastAPI job API with progress polling
- Minimal React dashboard with a lightweight SVG line chart

Future goals:
- Persistence for jobs/results (DB or object storage)
- More realistic order/fulfillment flows (lost sales vs backorders, partial shipments rules)
- Multi-item / multi-store networks
- Scenario templates + parameter sweeps
- Richer visualization (KPI dashboards, percentile bands, export)

### 8) Contributing

Contributions are welcome.

```bash
git checkout -b feature/my-change
git commit -am "Describe your change"
git push origin feature/my-change
```

Then open a Pull Request and include:
- What problem you’re solving
- How to reproduce / validate
- Any screenshots (for frontend changes)

### 9) License & Contact

- License: MIT — see `LICENSE`
- Author: John Fajardo
- Contact: john.fajardo.calle@gmail.com

---

## Español

### 1) Título & Badges

**STOCHASTIX-TWIN** — gemelo digital estocástico de cadena de suministro (DES + Monte Carlo).

Badges:
- CI: [![CI](https://github.com/John-Fajardo-Calle/STOCHASTIX-TWIN/actions/workflows/ci.yml/badge.svg)](https://github.com/John-Fajardo-Calle/STOCHASTIX-TWIN/actions/workflows/ci.yml)
- Licencia (MIT): [![License: MIT](https://img.shields.io/github/license/John-Fajardo-Calle/STOCHASTIX-TWIN)](LICENSE)

### 2) Descripción del Proyecto

STOCHASTIX-TWIN es un gemelo digital liviano para un sistema de inventario de dos niveles (Centro de Distribución → Tienda). Ejecuta una simulación de eventos discretos (SimPy) y permite replicaciones Monte Carlo para cuantificar la incertidumbre de KPIs (nivel de servicio, fill rate, quiebres de stock y promedios de inventario). Un backend mínimo con FastAPI expone simulaciones como “jobs” consultables por polling, y un frontend Vite+React ofrece un dashboard interactivo.

### 3) Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2
- **Simulación**: SimPy (DES), NumPy (aleatoriedad y agregación)
- **Frontend**: Vite, React
- **Dev / Ops**: Docker + Docker Compose, Dev Container para Codespaces
- **Testing**: pytest, httpx (ASGITransport), anyio

### 4) Prerrequisitos

Instala lo siguiente en tu máquina:

- Python 3.10+ (recomendado 3.11)
- Node.js 20+ y npm
- Docker Desktop (opcional, para iniciar con un comando)

### 5) Instalación

Clonar el repositorio:

```bash
git clone https://github.com/John-Fajardo-Calle/STOCHASTIX-TWIN.git
cd STOCHASTIX-TWIN
```

#### Configurar archivos de entorno

Frontend (Vite):

```bash
cp frontend/.env.example frontend/.env.local
```

Backend (opcional, para futura configuración):

```bash
cp backend/.env.example backend/.env
```

#### Instalación local (sin Docker)

Crear y activar un entorno virtual, luego instalar dependencias Python:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Instalar dependencias del frontend:

```bash
cd frontend
npm install
cd ..
```

#### Instalación con Docker (recomendado para quick start)

```bash
docker compose build
```

### 6) Uso

#### Opción A: Ejecutar con Docker Compose (un comando)

```bash
docker compose up
```

- Health check del backend: `http://localhost:8000/api/health`
- Dashboard del frontend: `http://localhost:5173`

#### Opción B: Ejecutar local (sin Docker)

Terminal 1 (backend):

```bash
source .venv/bin/activate
python -m uvicorn backend.api.app:app --reload --port 8000
```

Terminal 2 (frontend):

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

#### Ejemplos de API

Health check:

```bash
curl http://localhost:8000/api/health
```

Iniciar un job (single run):

```bash
curl -X POST "http://localhost:8000/api/simulations" \
	-H "Content-Type: application/json" \
	-d '{
		"config": {
			"days": 30,
			"demand_lambda_per_day": 15,
			"demand_peaks": [],
			"s_store": 80,
			"S_store": 160,
			"s_dc": 200,
			"S_dc": 400,
			"initial_on_hand_store": 120,
			"initial_on_hand_dc": 300,
			"lead_time_mean_days": 7,
			"lead_time_std_days": 2,
			"disruption_probability_per_shipment": 0,
			"disruption_delay_days": 0,
			"seed": 123
		},
		"replications": 1
	}'
```

Consultar el estado hasta que `status` sea `complete` (reemplaza `JOB_ID`):

```bash
curl "http://localhost:8000/api/simulations/JOB_ID"
```

Ejecutar tests:

```bash
source .venv/bin/activate
pytest -q
```

Compilar frontend:

```bash
cd frontend
npm run build
```

### 7) Roadmap / Features

Features actuales:
- Simulación de eventos discretos de un sistema de dos niveles (CD → Tienda)
- Política de inventario (s, S) en Tienda y CD
- Lead time lognormal + delay opcional por disrupción
- KPIs y serie temporal para graficar
- Resumen Monte Carlo (media/desvío de KPIs)
- API FastAPI con jobs y polling de progreso
- Dashboard React mínimo con gráfico SVG liviano

Objetivos futuros:
- Persistencia de jobs/resultados (DB u object storage)
- Flujos más realistas (ventas perdidas vs backorders, reglas de parciales)
- Redes multi-item / multi-tienda
- Plantillas de escenarios + barridos de parámetros
- Visualizaciones más ricas (bandas percentiles, export)

### 8) Contribuir

Las contribuciones son bienvenidas.

```bash
git checkout -b feature/mi-cambio
git commit -am "Describe tu cambio"
git push origin feature/mi-cambio
```

Luego abre un Pull Request e incluye:
- Qué problema resuelve
- Cómo reproducir / validar
- Capturas (si cambia el frontend)

### 9) Licencia & Contacto

- Licencia: MIT — ver `LICENSE`
- Autor: John Fajardo
- Contacto: john.fajardo.calle@gmail.com
