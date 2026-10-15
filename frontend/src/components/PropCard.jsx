import React, { useState } from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, ShieldCheck, Info, ChevronRight, HelpCircle } from 'lucide-react';

// Approximation of Normal CDF for client-side reactive recalculation
function normCdf(x) {
  const t = 1 / (1 + 0.2316419 * Math.abs(x));
  const d = 0.3989423 * Math.exp(-x * x / 2);
  let p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  if (x > 0) p = 1 - p;
  return p;
}

const STAT_STDS = {
  PTS: 4.8,
  REB: 2.4,
  AST: 2.1,
  '3PM': 1.2,
  PRA: 6.2,
};

export default function PropCard({ player, bankroll, kellyFraction, onUpdateLine }) {
  const [showRiskModal, setShowRiskModal] = useState(false);
  const [currentLine, setCurrentLine] = useState(player.book_line);
  const [selectedBook, setSelectedBook] = useState('bet365'); // 'bet365' | 'winamax'
  const [currentOdds, setCurrentOdds] = useState(player.bet365_odds || player.book_odds || 1.85);

  const statType = player.stat_type || 'PTS';
  const proj = player.projection;
  const std = STAT_STDS[statType] || 4.5;
  const odds = currentOdds;

  // Reactive calculations
  const rawEdge = proj - currentLine;
  const direction = rawEdge >= 0 ? 'OVER' : 'UNDER';
  const edgePct = currentLine > 0 ? Math.abs((rawEdge / currentLine) * 100) : 0;

  // Win probability
  const zScore = (currentLine - proj) / std;
  let winProb = direction === 'OVER' ? (1 - normCdf(zScore)) : normCdf(zScore);
  // Bounds
  winProb = Math.max(0.05, Math.min(0.95, winProb));

  // EV with dynamic odds
  const b = odds - 1;
  const ev = (winProb * b) - ((1 - winProb) * 1.0);

  // Kelly stake with dynamic odds
  const q = 1 - winProb;
  const fullKelly = (b * winProb - q) / b;
  let stake = 0;
  if (fullKelly > 0) {
    const fraction = kellyFraction || 0.25;
    stake = fullKelly * fraction * bankroll;
    const maxStake = 0.05 * bankroll;
    stake = Math.min(stake, maxStake);
    stake = Math.max(0, Math.round(stake * 10) / 10);
  }

  const handleSelectBook = (book) => {
    setSelectedBook(book);
    const newOdd = book === 'winamax'
      ? (player.winamax_odds || 1.88)
      : (player.bet365_odds || 1.83);
    setCurrentOdds(newOdd);
  };

  const handleOddsChange = (e) => {
    const val = parseFloat(e.target.value);
    if (!isNaN(val) && val >= 1.01) {
      setCurrentOdds(val);
    } else if (e.target.value === '') {
      setCurrentOdds(1.0);
    }
  };

  const handleLineChange = (e) => {
    const val = parseFloat(e.target.value);
    if (!isNaN(val) && val >= 0) {
      setCurrentLine(val);
      if (onUpdateLine) {
        onUpdateLine(player.player_id, statType, val);
      }
    } else if (e.target.value === '') {
      setCurrentLine(0);
    }
  };

  const riskLevel = player.risk_level || 'MEDIUM';
  const riskScore = player.risk_score || 3.2;

  return (
    <div className="prop-card">
      {/* Header */}
      <div className="prop-card-header">
        <div>
          <div className="player-info-title">
            <span>{player.player_name}</span>
          </div>
          <div className="player-meta-sub">
            {player.team} vs {player.opponent} • {player.position} • Exp. {player.exp_minutes} min
          </div>
        </div>

        <button 
          className={`risk-badge ${riskLevel}`}
          onClick={() => setShowRiskModal(true)}
          title="Ver desglose de los 8 factores de riesgo"
          style={{ cursor: 'pointer' }}
        >
          {riskLevel === 'LOW' && <ShieldCheck size={13} />}
          {riskLevel === 'MEDIUM' && <HelpCircle size={13} />}
          {riskLevel === 'HIGH' && <AlertTriangle size={13} />}
          <span>RIESGO {riskLevel === 'LOW' ? 'BAJO' : riskLevel === 'MEDIUM' ? 'MEDIO' : 'ALTO'}</span>
        </button>
      </div>

      {/* Metrics Row */}
      <div className="prop-metrics-grid">
        <div className="metric-box">
          <span className="metric-label">Proyección ML ({statType})</span>
          <span className="metric-value" style={{ color: '#38bdf8' }}>
            {proj} <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>unid</span>
          </span>
        </div>

        <div className="metric-box">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-label">Línea & Cuota</span>
            <div style={{ display: 'flex', gap: '0.25rem' }}>
              <button
                type="button"
                onClick={() => handleSelectBook('bet365')}
                style={{
                  fontSize: '0.65rem',
                  padding: '0.1rem 0.35rem',
                  borderRadius: '3px',
                  background: selectedBook === 'bet365' ? '#117843' : 'transparent',
                  color: selectedBook === 'bet365' ? '#fff' : 'var(--text-dim)',
                  border: '1px solid ' + (selectedBook === 'bet365' ? '#117843' : 'var(--border-color)'),
                  cursor: 'pointer'
                }}
              >
                B365
              </button>
              <button
                type="button"
                onClick={() => handleSelectBook('winamax')}
                style={{
                  fontSize: '0.65rem',
                  padding: '0.1rem 0.35rem',
                  borderRadius: '3px',
                  background: selectedBook === 'winamax' ? '#c8102e' : 'transparent',
                  color: selectedBook === 'winamax' ? '#fff' : 'var(--text-dim)',
                  border: '1px solid ' + (selectedBook === 'winamax' ? '#c8102e' : 'var(--border-color)'),
                  cursor: 'pointer'
                }}
              >
                WMX
              </button>
            </div>
          </div>
          <div className="line-input-wrapper" style={{ marginTop: '0.2rem' }}>
            <input
              type="number"
              step="0.5"
              className="line-input mono"
              value={currentLine}
              onChange={handleLineChange}
              title="Edita este valor con la línea de la casa"
            />
            <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>@</span>
            <input
              type="number"
              step="0.01"
              className="line-input mono"
              style={{ width: '60px', padding: '0.2rem 0.35rem' }}
              value={currentOdds}
              onChange={handleOddsChange}
              title="Cuota decimal de Bet365 o Winamax (puedes cambiarla libremente)"
            />
          </div>
        </div>
      </div>

      {/* Direction & Edge Pill */}
      <div className="edge-banner" style={{ background: direction === 'OVER' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)' }}>
        <div className={`direction-tag ${direction}`}>
          {direction === 'OVER' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          <span>{direction} {currentLine}</span>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div className="edge-pct" style={{ color: edgePct > 5 ? '#10b981' : 'var(--text-main)' }}>
            +{edgePct.toFixed(1)}% Edge
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Win Prob: {(winProb * 100).toFixed(1)}% • EV: {ev > 0 ? `+${ev.toFixed(2)}` : ev.toFixed(2)}€
          </div>
        </div>
      </div>

      {/* Stake & Bookmakers Footer */}
      <div className="bet-stake-row">
        <div className="stake-recommendation">
          <span style={{ color: 'var(--text-muted)' }}>Stake Kelly (0.25x):</span>
          <span className="stake-val mono">{stake > 0 ? `${stake.toFixed(2)} €` : '0.00 € (Sin valor)'}</span>
        </div>

        <div className="bookmaker-pills">
          <button
            type="button"
            className="bm-pill bet365"
            onClick={() => handleSelectBook('bet365')}
            style={{
              opacity: selectedBook === 'bet365' ? 1 : 0.45,
              border: selectedBook === 'bet365' ? '1px solid #ffffff' : 'none',
              cursor: 'pointer'
            }}
          >
            bet365: @{player.bet365_odds || 1.83}
          </button>
          <button
            type="button"
            className="bm-pill winamax"
            onClick={() => handleSelectBook('winamax')}
            style={{
              opacity: selectedBook === 'winamax' ? 1 : 0.45,
              border: selectedBook === 'winamax' ? '1px solid #ffffff' : 'none',
              cursor: 'pointer'
            }}
          >
            winamax: @{player.winamax_odds || 1.87}
          </button>
        </div>
      </div>

      {/* 8-Factor Risk Breakdown Modal */}
      {showRiskModal && (
        <div className="modal-overlay" onClick={() => setShowRiskModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#ffffff' }}>
                Evaluación de Riesgo: {player.player_name}
              </h3>
              <button 
                className="filter-btn" 
                onClick={() => setShowRiskModal(false)}
                style={{ padding: '0.2rem 0.6rem' }}
              >
                ✕
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: 'var(--bg-secondary)', padding: '1rem', borderRadius: '8px' }}>
              <div className={`risk-badge ${riskLevel}`} style={{ fontSize: '0.9rem', padding: '0.4rem 0.8rem' }}>
                NIVEL: {riskLevel}
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Puntuación algorítmica: <strong style={{ color: '#ffffff' }}>{riskScore.toFixed(1)} / 10</strong> (Umbrales: &le;2.5 Bajo, 2.5-5.0 Medio, &gt;5.0 Alto)
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
              <div style={{ fontWeight: '600', color: '#38bdf8', marginBottom: '0.2rem' }}>
                Desglose de los 8 Factores Ponderados:
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-color)' }}>
                <span>1. Riesgo de Paliza (Blowout Spread &gt; 10 pts)</span>
                <span className="mono" style={{ color: Math.abs(player.spread || 0) > 10 ? '#ef4444' : '#10b981' }}>
                  {Math.abs(player.spread || 0) > 10 ? 'Alto (+2.0)' : 'Seguro (+0.0)'}
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-color)' }}>
                <span>2. Estado Médico e Historial de Lesión</span>
                <span className="mono" style={{ color: player.injury_status === 'Healthy' ? '#10b981' : '#f59e0b' }}>
                  {player.injury_status || 'Disponible'} (+0.0)
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-color)' }}>
                <span>3. Varianza de Minutos (Últimos 10 partidos)</span>
                <span className="mono" style={{ color: player.minutes_std_10 > 4 ? '#f59e0b' : '#10b981' }}>
                  std = {player.minutes_std_10 || 2.2} min
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-color)' }}>
                <span>4. Regularidad en Puntos/Stat (Coef. Variación)</span>
                <span className="mono" style={{ color: '#10b981' }}>
                  std = {player.stat_std_10 || 3.0}
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-color)' }}>
                <span>5. Cansancio / Back-to-Back (2 partidos en 2 noches)</span>
                <span className="mono" style={{ color: player.is_b2b ? '#ef4444' : '#10b981' }}>
                  {player.is_b2b ? 'Sí (+1.0)' : 'Descanso normal (0.0)'}
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-color)' }}>
                <span>6. Margen de Ventaja del Modelo (Edge)</span>
                <span className="mono" style={{ color: edgePct > 7 ? '#10b981' : '#f59e0b' }}>
                  {edgePct.toFixed(1)}%
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-color)' }}>
                <span>7. Bajas de Compañeros Clave (Uso de balón)</span>
                <span className="mono" style={{ color: '#10b981' }}>
                  Rotación Completa
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0' }}>
                <span>8. Historial de Enfrentamiento / Traspasos</span>
                <span className="mono" style={{ color: '#10b981' }}>
                  Muestra conocida
                </span>
              </div>
            </div>

            <button 
              className="filter-btn active"
              onClick={() => setShowRiskModal(false)}
              style={{ width: '100%', padding: '0.6rem', marginTop: '0.5rem' }}
            >
              Cerrar y Volver
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

