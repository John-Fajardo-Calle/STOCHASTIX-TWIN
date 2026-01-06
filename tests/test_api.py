"""API integration tests.

I use ASGITransport to run the FastAPI app in-process, which keeps tests fast
and avoids any dependence on ports or external services.
"""

import time

import httpx
import pytest

from backend.api.app import app


@pytest.mark.anyio
async def test_api_health():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"


@pytest.mark.anyio
async def test_api_simulation_single_completes():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
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
                "seed": 123,
            },
            "replications": 1,
        }

        start = await client.post("/api/simulations", json=payload)
        assert start.status_code == 200
        job = start.json()
        job_id = job["job_id"]

        deadline = time.time() + 3.0
        last = None
        while time.time() < deadline:
            res = await client.get(f"/api/simulations/{job_id}")
            assert res.status_code == 200
            last = res.json()
            if last["status"] in ("complete", "error"):
                break
            await _sleep(0.02)

        assert last is not None
        assert last["status"] == "complete"
        assert last["result"]["type"] == "single"
        assert "kpis" in last["result"]


async def _sleep(seconds: float) -> None:
    """Yield control to the event loop between polls."""

    import anyio

    await anyio.sleep(seconds)
