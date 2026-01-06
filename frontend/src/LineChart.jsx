import React, { useMemo } from 'react'

/**
 * Lightweight SVG line chart.
 *
 * Why SVG + custom code: for this project I only need simple time-series
 * visualization, and avoiding a charting dependency reduces bundle size and
 * dependency churn.
 */
export default function LineChart({ title, series, width = 900, height = 220 }) {
  const { minX, maxX, minY, maxY } = useMemo(() => {
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
    for (const s of series) {
      for (const p of s.points) {
        minX = Math.min(minX, p.x)
        maxX = Math.max(maxX, p.x)
        minY = Math.min(minY, p.y)
        maxY = Math.max(maxY, p.y)
      }
    }
    if (!Number.isFinite(minX)) return { minX: 0, maxX: 1, minY: 0, maxY: 1 }
    if (minY === maxY) maxY = minY + 1
    if (minX === maxX) maxX = minX + 1
    return { minX, maxX, minY, maxY }
  }, [series])

  const padding = 24
  const innerWidth = width - padding * 2
  const innerHeight = height - padding * 2

  function toSvgX(x) {
    return padding + ((x - minX) / (maxX - minX)) * innerWidth
  }

  function toSvgY(y) {
    return padding + (1 - (y - minY) / (maxY - minY)) * innerHeight
  }

  function pathFor(points) {
    if (!points.length) return ''
    const d = points
      .map((p, i) => `${i === 0 ? 'M' : 'L'} ${toSvgX(p.x).toFixed(2)} ${toSvgY(p.y).toFixed(2)}`)
      .join(' ')
    return d
  }

  return (
    <div className="chart">
      <div className="chartTitle">{title}</div>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
        <rect x="0" y="0" width={width} height={height} fill="white" stroke="#e5e7eb" />
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#9ca3af" />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#9ca3af" />

        {series.map((s) => (
          <path key={s.name} d={pathFor(s.points)} fill="none" stroke={s.color} strokeWidth="2" />
        ))}
      </svg>
      <div className="legend">
        {series.map((s) => (
          <div key={s.name} className="legendItem">
            <span className="swatch" style={{ background: s.color }} />
            <span>{s.name}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
