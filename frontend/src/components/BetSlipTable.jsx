import React, { useState } from 'react';
import { Filter, TrendingUp, TrendingDown, ShieldCheck, AlertTriangle, HelpCircle, Download } from 'lucide-react';

export default function BetSlipTable({ games, bankroll, kellyFraction }) {
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [statFilter, setStatFilter] = useState('ALL');
  const [minEdge, setMinEdge] = useState(3.0);

  // Flatten all players from games
  const allProps = [];
  if (games) {
    games.forEach((game) => {
      if (game.players) {
        game.players.forEach((p) => {
          allProps.push({
            ...p,
            game_time: game.game_time,
            venue: game.venue,
          });
        });
      }
    });
  }

  // Filter props
  const filtered = allProps.filter((p) => {
    if (riskFilter !== 'ALL' && p.risk_level !== riskFilter) return false;
    if (statFilter !== 'ALL' && p.stat_type !== statFilter) return false;
    if (p.edge_pct < minEdge) return false;
    return true;
  });

  // Calculate summary metrics
  const totalStake = filtered.reduce((acc, curr) => acc + (curr.suggested_stake || 0), 0);
  const avgEdge = filtered.length > 0
    ? filtered.reduce((acc, curr) => acc + (curr.edge_pct || 0), 0) / filtered.length
    : 0;

  return (
    <div className="glass-panel" style={{ padding: '1.75rem' }}>
      {/* Table Header & Filters */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: '700', color: '#ffffff' }}>
            Mesa de Apuestas Recomendadas (Bet365 / Winamax)
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            Filtra según tu perfil de tolerancia al riesgo y estadísticas de interés
          </p>
        </div>

        {/* Top Summary Bar */}
        <div style={{ display: 'flex', gap: '1rem' }}>
          <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', padding: '0.5rem 1rem', borderRadius: '8px', fontSize: '0.85rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>Apuestas Detectadas: </span>
            <strong style={{ color: '#38bdf8' }}>{filtered.length}</strong>
          </div>
          <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', padding: '0.5rem 1rem', borderRadius: '8px', fontSize: '0.85rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>Exposición Total: </span>
            <strong style={{ color: '#10b981' }}>{totalStake.toFixed(2)} €</strong>
          </div>
          <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', padding: '0.5rem 1rem', borderRadius: '8px', fontSize: '0.85rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>Edge Promedio: </span>
            <strong style={{ color: '#c084fc' }}>+{avgEdge.toFixed(1)}%</strong>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        {/* Risk Filter */}
        <div className="filter-group">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: '600' }}>Riesgo:</span>
          {['ALL', 'LOW', 'MEDIUM', 'HIGH'].map((level) => (
            <button
              key={level}
              className={`filter-btn ${riskFilter === level ? 'active' : ''}`}
              onClick={() => setRiskFilter(level)}
            >
              {level === 'ALL' ? 'Todos' : level === 'LOW' ? 'Bajo' : level === 'MEDIUM' ? 'Medio' : 'Alto'}
            </button>
          ))}
        </div>

        {/* Stat Filter */}
        <div className="filter-group">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: '600' }}>Mercado:</span>
          {['ALL', 'PTS', 'REB', 'AST', '3PM', 'PRA'].map((s) => (
            <button
              key={s}
              className={`filter-btn ${statFilter === s ? 'active' : ''}`}
              onClick={() => setStatFilter(s)}
            >
              {s === 'ALL' ? 'Todos' : s}
            </button>
          ))}
        </div>

        {/* Min Edge filter */}
        <div className="filter-group">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: '600' }}>Min Edge:</span>
          {[0, 3, 5, 8].map((val) => (
            <button
              key={val}
              className={`filter-btn ${minEdge === val ? 'active' : ''}`}
              onClick={() => setMinEdge(val)}
            >
              +{val}%
            </button>
          ))}
        </div>
      </div>

      {/* Responsive Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em' }}>
              <th style={{ padding: '0.75rem 1rem' }}>Jugador</th>
              <th style={{ padding: '0.75rem 1rem' }}>Partido</th>
              <th style={{ padding: '0.75rem 1rem' }}>Mercado</th>
              <th style={{ padding: '0.75rem 1rem' }}>Proyección</th>
              <th style={{ padding: '0.75rem 1rem' }}>Línea</th>
              <th style={{ padding: '0.75rem 1rem' }}>Edge</th>
              <th style={{ padding: '0.75rem 1rem' }}>Win Prob</th>
              <th style={{ padding: '0.75rem 1rem' }}>Riesgo</th>
              <th style={{ padding: '0.75rem 1rem' }}>Stake (€)</th>
              <th style={{ padding: '0.75rem 1rem' }}>Casas</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length > 0 ? (
              filtered.map((item, idx) => (
                <tr
                  key={`${item.player_id}_${item.stat_type}_${idx}`}
                  style={{
                    borderBottom: '1px solid var(--border-color)',
                    background: idx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.01)',
                  }}
                >
                  <td style={{ padding: '0.85rem 1rem', fontWeight: '600', color: '#ffffff' }}>
                    {item.player_name}
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: '400' }}>
                      {item.team} • {item.position}
                    </div>
                  </td>

                  <td style={{ padding: '0.85rem 1rem', color: 'var(--text-muted)' }}>
                    {item.team} vs {item.opponent}
                  </td>

                  <td style={{ padding: '0.85rem 1rem' }}>
                    <span className={`direction-tag ${item.direction}`} style={{ display: 'inline-flex', padding: '0.15rem 0.45rem', fontSize: '0.75rem' }}>
                      {item.direction === 'OVER' ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                      <span>{item.direction} {item.stat_type}</span>
                    </span>
                  </td>

                  <td style={{ padding: '0.85rem 1rem', color: '#38bdf8', fontWeight: '700' }} className="mono">
                    {item.projection}
                  </td>

                  <td style={{ padding: '0.85rem 1rem', color: '#ffffff' }} className="mono">
                    {item.book_line} <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>@{item.book_odds}</span>
                  </td>

                  <td style={{ padding: '0.85rem 1rem', color: '#10b981', fontWeight: '700' }} className="mono">
                    +{item.edge_pct}%
                  </td>

                  <td style={{ padding: '0.85rem 1rem' }} className="mono">
                    {item.win_prob}%
                  </td>

                  <td style={{ padding: '0.85rem 1rem' }}>
                    <span className={`risk-badge ${item.risk_level}`} style={{ display: 'inline-flex', padding: '0.2rem 0.5rem', fontSize: '0.7rem' }}>
                      {item.risk_level}
                    </span>
                  </td>

                  <td style={{ padding: '0.85rem 1rem', color: '#10b981', fontWeight: '700' }} className="mono">
                    {item.suggested_stake ? `${item.suggested_stake.toFixed(2)} €` : '0.00 €'}
                  </td>

                  <td style={{ padding: '0.85rem 1rem' }}>
                    <div style={{ display: 'flex', gap: '0.3rem' }}>
                      <span className="bm-pill bet365">B365</span>
                      <span className="bm-pill winamax">WMX</span>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={10} style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-dim)' }}>
                  No se encontraron apuestas con los filtros seleccionados.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

