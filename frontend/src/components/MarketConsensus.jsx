import React, { useState, useEffect } from 'react';
import { DollarSign, TrendingUp, ShieldAlert, BarChart3, Users, Flame, RefreshCw, Info } from 'lucide-react';

export default function MarketConsensus() {
  const [sharpData, setSharpData] = useState([]);
  const [dvpData, setDvpData] = useState([]);
  const [activeSubTab, setActiveSubTab] = useState('sharp'); // 'sharp' | 'dvp'
  const [isLoading, setIsLoading] = useState(false);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [resSharp, resDvp] = await Promise.all([
        fetch('/api/sharp-money'),
        fetch('/api/dvp'),
      ]);

      if (resSharp.ok) {
        const dSharp = await resSharp.json();
        setSharpData(dSharp);
      }
      if (resDvp.ok) {
        const dDvp = await resDvp.json();
        setDvpData(dDvp);
      }
    } catch (err) {
      console.warn('Error fetching free sources data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Sub-navigation & Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className={`filter-btn ${activeSubTab === 'sharp' ? 'active' : ''}`}
            onClick={() => setActiveSubTab('sharp')}
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.55rem 1rem' }}
          >
            <DollarSign size={16} />
            <span>Dinero Inteligente & Consenso (Action Network)</span>
          </button>

          <button
            className={`filter-btn ${activeSubTab === 'dvp' ? 'active' : ''}`}
            onClick={() => setActiveSubTab('dvp')}
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.55rem 1rem' }}
          >
            <BarChart3 size={16} />
            <span>Defensa vs Posición (Hashtag Basketball)</span>
          </button>
        </div>

        <button
          className="filter-btn"
          onClick={fetchData}
          disabled={isLoading}
          style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
        >
          <RefreshCw size={14} className={isLoading ? 'spin' : ''} />
          <span>{isLoading ? 'Actualizando...' : 'Refrescar Mercado'}</span>
        </button>
      </div>

      {/* VIEW 1: SHARP MONEY & PUBLIC CONSENSUS */}
      {activeSubTab === 'sharp' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="glass-panel" style={{ padding: '1rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'rgba(59, 130, 246, 0.08)', borderColor: 'rgba(59, 130, 246, 0.3)' }}>
            <Info size={20} color="#38bdf8" style={{ flexShrink: 0 }} />
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              <strong>¿Cómo interpretar el Dinero Inteligente (Sharp Money)?</strong> Si el público masivo apuesta a un equipo (muchos boletos / <i>% Tickets</i>), pero el volumen real de dinero (<i>% Cash</i>) entra con fuerza en el rival, indica que los apostadores profesionales están tomando la postura contraria al público.
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '1.25rem' }}>
            {sharpData.map((item) => (
              <div key={item.game_id} className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {/* Match Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#ffffff' }}>
                      {item.away_name} @ {item.home_name}
                    </h3>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                      Spread: <strong style={{ color: '#ffffff' }}>{item.spread > 0 ? `+${item.spread}` : item.spread}</strong> • Total O/U: <strong style={{ color: '#ffffff' }}>{item.total}</strong>
                    </div>
                  </div>

                  {item.is_sharp_action && (
                    <span className="risk-badge LOW" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.75rem' }}>
                      <Flame size={13} color="#10b981" />
                      <span>SHARP: {item.sharp_side}</span>
                    </span>
                  )}
                </div>

                {/* Moneyline Probabilities */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', background: 'var(--bg-secondary)', padding: '0.75rem', borderRadius: '8px' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.away_team} (Visitante)</div>
                    <div className="mono" style={{ fontSize: '1.05rem', fontWeight: '700', color: '#38bdf8' }}>
                      @{item.ml_away_decimal || '2.00'} <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>({item.ml_away_win_prob}%)</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Total: {item.away_team_total || '-'} pts</div>
                  </div>

                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.home_team} (Local)</div>
                    <div className="mono" style={{ fontSize: '1.05rem', fontWeight: '700', color: '#10b981' }}>
                      @{item.ml_home_decimal || '1.80'} <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>({item.ml_home_win_prob}%)</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Total: {item.home_team_total || '-'} pts</div>
                  </div>
                </div>

                {/* Public Tickets vs Real Cash Visual Bars */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Distribución del Hándicap (Spread):</span>
                    <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>{item.split_status}</span>
                  </div>

                  {/* Spread Comparison Bar */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '0.2rem' }}>
                      <span>% Boletos Público ({item.home_team}): <strong>{item.spread_home_tickets_pct}%</strong></span>
                      <span>% Dinero Real ({item.home_team}): <strong style={{ color: '#10b981' }}>{item.spread_home_money_pct}%</strong></span>
                    </div>
                    <div style={{ height: '8px', background: '#1e293b', borderRadius: '4px', overflow: 'hidden', display: 'flex' }}>
                      <div style={{ width: `${item.spread_home_money_pct}%`, background: item.is_sharp_action ? '#10b981' : '#38bdf8' }}></div>
                    </div>
                  </div>

                  {/* Over/Under Total Comparison Bar */}
                  <div style={{ marginTop: '0.4rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '0.2rem' }}>
                      <span>Total OVER % Boletos: <strong>{item.total_over_tickets_pct}%</strong></span>
                      <span>Total OVER % Dinero: <strong style={{ color: '#38bdf8' }}>{item.total_over_money_pct}%</strong></span>
                    </div>
                    <div style={{ height: '8px', background: '#1e293b', borderRadius: '4px', overflow: 'hidden', display: 'flex' }}>
                      <div style={{ width: `${item.total_over_money_pct}%`, background: '#38bdf8' }}></div>
                    </div>
                  </div>
                </div>

                {/* Footer with Bet Volume */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-color)', paddingTop: '0.6rem', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Users size={13} />
                    <span>Volumen: {item.num_bets} apuestas registradas</span>
                  </div>
                  <div>Fuente: Action Network (API Gratuita)</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* VIEW 2: DEFENSE VS POSITION (HASHTAG BASKETBALL) */}
      {activeSubTab === 'dvp' && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#ffffff' }}>
              Defensa vs Posición (Hashtag Basketball DvP)
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Cuántos puntos, rebotes, asistencias y triples permite cada equipo a las diferentes posiciones en cancha
            </p>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textTransform: 'uppercase', fontSize: '0.75rem' }}>
                  <th style={{ padding: '0.65rem 0.85rem' }}>Posición</th>
                  <th style={{ padding: '0.65rem 0.85rem' }}>Equipo</th>
                  <th style={{ padding: '0.65rem 0.85rem' }}>PTS Concedidos</th>
                  <th style={{ padding: '0.65rem 0.85rem' }}>FG% Rival</th>
                  <th style={{ padding: '0.65rem 0.85rem' }}>3PM Concedidos</th>
                  <th style={{ padding: '0.65rem 0.85rem' }}>REB Concedidos</th>
                  <th style={{ padding: '0.65rem 0.85rem' }}>AST Concedidos</th>
                </tr>
              </thead>
              <tbody>
                {dvpData.length > 0 ? (
                  dvpData.map((row, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)', background: idx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.01)' }}>
                      <td style={{ padding: '0.75rem 0.85rem', fontWeight: '700', color: '#38bdf8' }}>{row.Position}</td>
                      <td style={{ padding: '0.75rem 0.85rem', fontWeight: '600', color: '#ffffff' }}>{row.Team}</td>
                      <td style={{ padding: '0.75rem 0.85rem', color: '#f59e0b', fontWeight: '700' }} className="mono">{row.PTS}</td>
                      <td style={{ padding: '0.75rem 0.85rem' }} className="mono">{row['FG%']}</td>
                      <td style={{ padding: '0.75rem 0.85rem', color: '#10b981' }} className="mono">{row['3PM']}</td>
                      <td style={{ padding: '0.75rem 0.85rem' }} className="mono">{row.REB}</td>
                      <td style={{ padding: '0.75rem 0.85rem' }} className="mono">{row.AST}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-dim)' }}>
                      Cargando métricas de Defensa vs Posición...
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

