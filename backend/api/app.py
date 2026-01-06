"""FastAPI app exposing simulation runs as pollable jobs.

This API uses a simple job model because browsers are happiest with plain
request/response. I run the simulation in a background thread, store
progress/results in memory, and let the frontend poll at a comfortable cadence.

This service is deliberately non-persistent: a process restart clears jobs.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.simulation.models import DemandPeak, MonteCarloResult, SimulationConfig
from backend.simulation.runner import monte_carlo, run_single


class DemandPeakIn(BaseModel):
    """API-facing representation of a demand peak."""

    start_day: int = Field(ge=0)
    end_day: int = Field(ge=0)
    multiplier: float = Field(gt=0)


class SimulationConfigIn(BaseModel):
    """Validated input schema for `SimulationConfig` used by the API."""

    days: int = Field(ge=1, le=3650)
    demand_lambda_per_day: float = Field(ge=0)
    demand_peaks: list[DemandPeakIn] = []

    s_store: int = Field(ge=0)
    S_store: int = Field(ge=0)
    s_dc: int = Field(ge=0)
    S_dc: int = Field(ge=0)

    initial_on_hand_store: int = Field(ge=0)
    initial_on_hand_dc: int = Field(ge=0)

    lead_time_mean_days: float = Field(gt=0)
    lead_time_std_days: float = Field(ge=0)

    disruption_probability_per_shipment: float = Field(ge=0, le=1)
    disruption_delay_days: float = Field(ge=0)

    seed: Optional[int] = None


class SimulationRequest(BaseModel):
    """Request payload for starting a simulation job."""

    config: SimulationConfigIn
    replications: int = Field(default=1, ge=1, le=2000)


class JobStatus(BaseModel):
    """Job metadata returned to the frontend for polling."""

    job_id: str
    status: str
    progress: float
    created_at: str
    finished_at: Optional[str] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None


def _cfg_from_in(data: SimulationConfigIn) -> SimulationConfig:
    """Convert validated API config into the internal dataclass."""

    peaks = tuple(
        DemandPeak(start_day=p.start_day, end_day=p.end_day, multiplier=p.multiplier)
        for p in data.demand_peaks
    )
    return SimulationConfig(
        days=data.days,
        demand_lambda_per_day=data.demand_lambda_per_day,
        demand_peaks=peaks,
        s_store=data.s_store,
        S_store=data.S_store,
        s_dc=data.s_dc,
        S_dc=data.S_dc,
        initial_on_hand_store=data.initial_on_hand_store,
        initial_on_hand_dc=data.initial_on_hand_dc,
        lead_time_mean_days=data.lead_time_mean_days,
        lead_time_std_days=data.lead_time_std_days,
        disruption_probability_per_shipment=data.disruption_probability_per_shipment,
        disruption_delay_days=data.disruption_delay_days,
        seed=data.seed,
    )


app = FastAPI(title="STOCHASTIX-TWIN API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


_jobs_by_id: dict[str, dict[str, Any]] = {}
_jobs_lock = threading.Lock()


def _utc_now_iso() -> str:
    """UTC timestamp formatted for JSON."""

    return datetime.now(tz=timezone.utc).isoformat()


def _set_job_fields(job_id: str, **fields: Any) -> None:
    """Update job state atomically.

    The lock keeps reads and writes consistent under background execution.
    """

    with _jobs_lock:
        if job_id in _jobs_by_id:
            _jobs_by_id[job_id].update(fields)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Health check used by local dev and Docker smoke tests."""

    return {"status": "ok"}


@app.post("/api/simulations", response_model=JobStatus)
def start_simulation(request: SimulationRequest) -> JobStatus:
    """Start a background simulation job and return its initial status."""

    config = _cfg_from_in(request.config)
    job_id = str(uuid.uuid4())
    created_at = _utc_now_iso()

    with _jobs_lock:
        _jobs_by_id[job_id] = {
            "job_id": job_id,
            "status": "running",
            "progress": 0.0,
            "created_at": created_at,
            "finished_at": None,
            "result": None,
            "error": None,
        }

    def run_job() -> None:
        try:
            if request.replications == 1:
                result = run_single(config)
                payload = {
                    "type": "single",
                    "kpis": asdict(result.kpis),
                    "timeseries": result.timeseries,
                    "config": asdict(result.config),
                }
                _set_job_fields(job_id, progress=1.0)
            else:
                def progress_callback(progress: float) -> None:
                    _set_job_fields(job_id, progress=float(progress))

                monte_carlo_result: MonteCarloResult = monte_carlo(
                    config,
                    replications=request.replications,
                    progress_cb=progress_callback,
                )
                payload = {
                    "type": "monte_carlo",
                    "summary": asdict(monte_carlo_result.summary),
                    "config": asdict(monte_carlo_result.config),
                }
                _set_job_fields(job_id, progress=1.0)

            _set_job_fields(
                job_id,
                status="complete",
                finished_at=_utc_now_iso(),
                result=payload,
            )
        except Exception as exc:
            # I intentionally surface the message to keep the UI simple.
            # If this grows, I can switch to structured error types.
            _set_job_fields(
                job_id,
                status="error",
                finished_at=_utc_now_iso(),
                error=str(exc),
            )

    threading.Thread(target=run_job, daemon=True).start()

    with _jobs_lock:
        return JobStatus(**_jobs_by_id[job_id])


@app.get("/api/simulations/{job_id}", response_model=JobStatus)
def get_simulation(job_id: str) -> JobStatus:
    """Fetch job status (and result when complete)."""

    with _jobs_lock:
        job = _jobs_by_id.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="job not found")
        return JobStatus(**job)
