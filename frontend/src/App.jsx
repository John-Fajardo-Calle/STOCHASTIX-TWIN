import React, { useMemo, useRef, useState } from 'react'
import { getSimulation, startSimulation, getApiBaseUrl } from './api.js'
import LineChart from './LineChart.jsx'

/**
 * Parse a user-provided value into a number.
 *
 * Why this exists: HTML inputs return strings and I want the payload to be
 * numeric without making the UI brittle when users temporarily clear a field.
 */
function toNumberOr(value, fallback) {
  const n = Number(value)
  return Number.isFinite(n) ? n : fallback
}

export default function App() {
  const [days, setDays] = useState(365)
  const [lambda, setLambda] = useState(20)

  const [storeReorderPoint, setStoreReorderPoint] = useState(80)
  const [storeOrderUpTo, setStoreOrderUpTo] = useState(160)
  const [dcReorderPoint, setDcReorderPoint] = useState(300)
  const [dcOrderUpTo, setDcOrderUpTo] = useState(600)

  const [initialStoreOnHand, setInitialStoreOnHand] = useState(120)
  const [initialDcOnHand, setInitialDcOnHand] = useState(500)

  const [leadTimeMeanDays, setLeadTimeMeanDays] = useState(7)
  const [leadTimeStdDays, setLeadTimeStdDays] = useState(2)

  const [disruptionProbabilityPerShipment, setDisruptionProbabilityPerShipment] = useState(0)
  const [disruptionDelayDays, setDisruptionDelayDays] = useState(0)

  const [seed, setSeed] = useState(123)
  const [replications, setReplications] = useState(1)

  const [job, setJob] = useState(null)
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)

  const pollIntervalId = useRef(null)

  async function onRun() {
    setError(null)
    setStatus(null)
    setJob(null)

    // Payload keys intentionally match the backend schema.
    // This avoids a separate mapping layer and keeps the API contract explicit.
    const payload = {
      config: {
        days: toNumberOr(days, 365),
        demand_lambda_per_day: toNumberOr(lambda, 20),
        demand_peaks: [],

        s_store: toNumberOr(storeReorderPoint, 80),
        S_store: toNumberOr(storeOrderUpTo, 160),
        s_dc: toNumberOr(dcReorderPoint, 300),
        S_dc: toNumberOr(dcOrderUpTo, 600),

        initial_on_hand_store: toNumberOr(initialStoreOnHand, 120),
        initial_on_hand_dc: toNumberOr(initialDcOnHand, 500),

        lead_time_mean_days: toNumberOr(leadTimeMeanDays, 7),
        lead_time_std_days: toNumberOr(leadTimeStdDays, 2),

        disruption_probability_per_shipment: toNumberOr(disruptionProbabilityPerShipment, 0),
        disruption_delay_days: toNumberOr(disruptionDelayDays, 0),

        seed: seed === '' ? null : toNumberOr(seed, 123)
      },
      replications: toNumberOr(replications, 1)
    }

    const started = await startSimulation(payload)
    setJob(started)

    async function poll() {
      try {
        const s = await getSimulation(started.job_id)
        setStatus(s)
        if (s.status === 'complete' || s.status === 'error') {
          if (pollIntervalId.current) {
            clearInterval(pollIntervalId.current)
            pollIntervalId.current = null
          }
        }
      } catch (e) {
        setError(String(e?.message || e))
        if (pollIntervalId.current) {
          clearInterval(pollIntervalId.current)
          pollIntervalId.current = null
        }
      }
    }

    await poll()
    // 750ms keeps the UI responsive without hammering the backend.
    pollIntervalId.current = setInterval(poll, 750)
  }

  const result = status?.result || null
  const singleTimeseries = result?.type === 'single' ? result.timeseries : null

  const chartSeries = useMemo(() => {
    if (!singleTimeseries?.length) return null
    const points = (key) => singleTimeseries.map((p) => ({ x: p.day, y: p[key] }))
    return [
      { name: 'Store on-hand', color: '#2563eb', points: points('store_on_hand') },
      { name: 'Store backorder', color: '#dc2626', points: points('store_backorder') },
      { name: 'DC on-hand', color: '#059669', points: points('dc_on_hand') }
    ]
  }, [singleTimeseries])

  return (
    <div className="page">
      <header className="header">
        <div>
          <div className="title">STOCHASTIX-TWIN</div>
          <div className="subtitle">Gemelo digital estocástico (DES + Monte Carlo)</div>
        </div>
        <div className="apiBase">API: {getApiBaseUrl()}</div>
      </header>

      <section className="card">
        <div className="cardTitle">Parámetros</div>
        <div className="grid">
          <Field label="Days" value={days} onChange={setDays} type="number" />
          <Field label="Demand λ/day" value={lambda} onChange={setLambda} type="number" />
          <Field label="Replications" value={replications} onChange={setReplications} type="number" />
          <Field label="Seed (optional)" value={seed} onChange={setSeed} type="number" />

          <Field label="s (Store)" value={storeReorderPoint} onChange={setStoreReorderPoint} type="number" />
          <Field label="S (Store)" value={storeOrderUpTo} onChange={setStoreOrderUpTo} type="number" />
          <Field label="s (DC)" value={dcReorderPoint} onChange={setDcReorderPoint} type="number" />
          <Field label="S (DC)" value={dcOrderUpTo} onChange={setDcOrderUpTo} type="number" />

          <Field label="Init store" value={initialStoreOnHand} onChange={setInitialStoreOnHand} type="number" />
          <Field label="Init DC" value={initialDcOnHand} onChange={setInitialDcOnHand} type="number" />

          <Field label="Lead time mean (days)" value={leadTimeMeanDays} onChange={setLeadTimeMeanDays} type="number" />
          <Field label="Lead time std (days)" value={leadTimeStdDays} onChange={setLeadTimeStdDays} type="number" />

          <Field label="Disruption P/shipment" value={disruptionProbabilityPerShipment} onChange={setDisruptionProbabilityPerShipment} type="number" step="0.01" />
          <Field label="Disruption delay (days)" value={disruptionDelayDays} onChange={setDisruptionDelayDays} type="number" step="0.1" />
        </div>

        <div className="actions">
          <button className="btn" onClick={onRun}>Run simulation</button>
        </div>

        {error ? <div className="error">{error}</div> : null}
      </section>

      <section className="card">
        <div className="cardTitle">Ejecución</div>
        <div className="row">
          <div><b>Job:</b> {job?.job_id || '—'}</div>
          <div><b>Status:</b> {status?.status || '—'}</div>
          <div><b>Progress:</b> {status ? `${Math.round((status.progress || 0) * 100)}%` : '—'}</div>
        </div>
      </section>

      {result?.type === 'single' ? (
        <section className="card">
          <div className="cardTitle">KPIs (single run)</div>
          <JsonGrid data={result.kpis} />
          {chartSeries ? <LineChart title="Inventory evolution" series={chartSeries} /> : null}
        </section>
      ) : null}

      {result?.type === 'monte_carlo' ? (
        <section className="card">
          <div className="cardTitle">Monte Carlo summary</div>
          <div className="row"><b>Replications:</b> {result.summary.replications}</div>
          <div className="twoCol">
            <div>
              <div className="miniTitle">Mean</div>
              <JsonGrid data={result.summary.kpi_mean} />
            </div>
            <div>
              <div className="miniTitle">Std</div>
              <JsonGrid data={result.summary.kpi_std} />
            </div>
          </div>
        </section>
      ) : null}
    </div>
  )
}

function Field({ label, value, onChange, type = 'text', step }) {
  return (
    <label className="field">
      <div className="label">{label}</div>
      <input
        className="input"
        type={type}
        value={value}
        step={step}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  )
}

function JsonGrid({ data }) {
  if (!data) return null
  const entries = Object.entries(data)
  return (
    <div className="kv">
      {entries.map(([k, v]) => (
        <div key={k} className="kvRow">
          <div className="kvKey">{k}</div>
          <div className="kvVal">{typeof v === 'number' ? v.toFixed(4) : String(v)}</div>
        </div>
      ))}
    </div>
  )
}
