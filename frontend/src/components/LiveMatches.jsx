import React from 'react';
import { Calendar, MapPin, AlertOctagon, TrendingUp, Info } from 'lucide-react';
import PropCard from './PropCard';

export default function LiveMatches({ games, bankroll, kellyFraction, onUpdateLine, onRefresh, isRefreshing }) {
  if (!games || games.length === 0) {
    return (
      <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
          No hay partidos programados o la conexión con el servidor está sincronizándose.
        </p>
        <button className="filter-btn active" onClick={onRefresh} disabled={isRefreshing}>
          {isRefreshing ? 'Consultando ESPN...' : 'Sincronizar Partidos de Hoy'}
        </button>
      </div>
    );
  }

  return (
    <div className="matches-grid">
      {games.map((game) => {
        const isBlowout = Math.abs(game.spread || 0) > 10.0;
        const awayName = game.away_team_name || game.away_team;
        const homeName = game.home_team_name || game.home_team;

        return (
          <div key={game.game_id || `${game.away_team}-${game.home_team}`} className="match-card">
            {/* Match Header */}
            <div className="match-header">
              <div className="teams-display">
                <div className="team-block">
                  <span className="team-badge">{game.away_team}</span>
                  <span className="team-name">{awayName}</span>
                </div>

                <span className="vs-divider">@</span>

                <div className="team-block">
                  <span className="team-badge">{game.home_team}</span>
                  <span className="team-name">{homeName}</span>
                </div>
              </div>

              {/* Match Metadata Badges */}
              <div className="match-meta">
                <div className="meta-pill">
                  <Calendar size={13} />
                  <span>{game.game_time}</span>
                </div>

                <div className="meta-pill">
                  <MapPin size={13} />
                  <span>{game.venue}</span>
                </div>

                <div className="meta-pill mono">
                  <span>Spread: <strong>{game.odds_detail || `${game.spread > 0 ? '+' : ''}${game.spread}`}</strong></span>
                </div>

                <div className="meta-pill mono">
                  <span>Total O/U: <strong>{game.total_line}</strong></span>
                </div>

                {isBlowout && (
                  <div className="meta-pill blowout-warning" title="Diferencia proyectada > 10 puntos: Los titulares podrían descansar en el 4º cuarto">
                    <AlertOctagon size={13} />
                    <span>ALERTA BLOWOUT</span>
                  </div>
                )}
              </div>
            </div>

            {/* Player Props Cards */}
            <div className="props-container">
              {game.players && game.players.length > 0 ? (
                game.players.map((player) => (
                  <PropCard
                    key={`${player.player_id}_${player.stat_type}`}
                    player={player}
                    bankroll={bankroll}
                    kellyFraction={kellyFraction}
                    onUpdateLine={onUpdateLine}
                  />
                ))
              ) : (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', gridColumn: '1 / -1', padding: '1rem' }}>
                  Sincronizando rotaciones y cuotas oficiales de Bet365 / Winamax para este encuentro...
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

