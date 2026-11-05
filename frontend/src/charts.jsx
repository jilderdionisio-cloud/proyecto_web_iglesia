const TICKS = 4

function roundedMax(value) {
  if (value <= 0) return TICKS
  const magnitude = 10 ** Math.floor(Math.log10(value / TICKS))
  const step = [1, 2, 2.5, 5, 10].map((factor) => factor * magnitude).find((candidate) => candidate * TICKS >= value)
  return Math.max(step * TICKS, TICKS)
}

// Columnas apiladas sobre una sola línea base. Cada fila es { label, [serie.key]: valor }.
export function ColumnChart({ title, data, series, formatValue = String, formatTick = String }) {
  const totals = data.map((row) => series.reduce((sum, item) => sum + Number(row[item.key]), 0))
  const max = roundedMax(Math.max(...totals, 0))
  const ticks = Array.from({ length: TICKS + 1 }, (_, index) => (max / TICKS) * index)

  return (
    <figure className="chart">
      <figcaption>{title}</figcaption>
      {series.length > 1 && (
        <ul className="chart-legend">
          {series.map((item) => <li key={item.key}><span style={{ background: item.color }} />{item.label}</li>)}
        </ul>
      )}
      <div className="chart-plot">
        <div className="chart-grid" aria-hidden="true">
          {ticks.map((tick) => <span key={tick} style={{ bottom: `${(tick / max) * 100}%` }}><small>{formatTick(tick)}</small></span>)}
        </div>
        <div className="chart-columns">
          {data.map((row, index) => {
            const detail = series.map((item) => `${item.label}: ${formatValue(row[item.key])}`).join(' · ')
            const lastFilled = series.findLastIndex((item) => Number(row[item.key]) > 0)
            return (
              <div className="chart-slot" key={row.label} tabIndex={0} aria-label={`${row.label}. ${detail}`}>
                <div className="chart-bar" style={{ height: `${(totals[index] / max) * 100}%` }}>
                  {series.map((item, seriesIndex) => Number(row[item.key]) > 0 && (
                    <span
                      key={item.key}
                      className={seriesIndex === lastFilled ? 'chart-cap' : ''}
                      style={{ flexGrow: Number(row[item.key]), background: item.color }}
                    />
                  )).reverse()}
                </div>
                <div className="chart-tooltip" role="tooltip">
                  <strong>{row.label}</strong>
                  {series.map((item) => <span key={item.key}>{item.label}: {formatValue(row[item.key])}</span>)}
                </div>
              </div>
            )
          })}
        </div>
      </div>
      <div className="chart-labels" aria-hidden="true">
        {data.map((row) => <span key={row.label}>{row.label}</span>)}
      </div>
      <details className="chart-table">
        <summary>Ver datos</summary>
        <table>
          <thead><tr><th>Periodo</th>{series.map((item) => <th key={item.key}>{item.label}</th>)}</tr></thead>
          <tbody>
            {data.map((row) => <tr key={row.label}><td>{row.label}</td>{series.map((item) => <td key={item.key}>{formatValue(row[item.key])}</td>)}</tr>)}
          </tbody>
        </table>
      </details>
    </figure>
  )
}
