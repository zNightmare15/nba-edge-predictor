import React, { useState } from 'react';
import { Sliders, Euro, ShieldAlert, Check } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose, settings, onSaveSettings }) {
  if (!isOpen) return null;

  const [bankroll, setBankroll] = useState(settings.bankroll || 1000);
  const [kellyFraction, setKellyFraction] = useState(settings.kelly_fraction || 0.25);
  const [minEdge, setMinEdge] = useState(settings.min_edge_pct || 3.0);
  const [maxRisk, setMaxRisk] = useState(settings.max_risk_level || 'HIGH');

  const handleSave = () => {
    onSaveSettings({
      bankroll: parseFloat(bankroll),
      kelly_fraction: parseFloat(kellyFraction),
      min_edge_pct: parseFloat(minEdge),
      max_risk_level: maxRisk,
    });
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Sliders size={20} color="#38bdf8" />
            <h3 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#ffffff' }}>
              Configuración del Algoritmo & Bankroll
            </h3>
          </div>
          <button className="filter-btn" onClick={onClose} style={{ padding: '0.2rem 0.6rem' }}>
            ✕
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Bankroll */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.4rem', fontWeight: '600' }}>
              Bankroll Total en Euros (€)
            </label>
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
              <input
                type="number"
                className="line-input mono"
                style={{ width: '100%', padding: '0.55rem 0.75rem', fontSize: '1.05rem', textAlign: 'left' }}
                value={bankroll}
                onChange={(e) => setBankroll(e.target.value)}
              />
              <span style={{ position: 'absolute', right: '1rem', color: '#10b981', fontWeight: '700' }}>€</span>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.25rem', display: 'block' }}>
              El algoritmo calculará los stakes de cada apuesta en proporción a este capital.
            </span>
          </div>

          {/* Kelly Fraction */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: '600' }}>
                Fracción del Criterio de Kelly
              </label>
              <span className="mono" style={{ color: '#38bdf8', fontWeight: '700' }}>
                {kellyFraction}x ({kellyFraction === 0.25 ? 'Cuarto de Kelly - Recomendado' : kellyFraction < 0.25 ? 'Conservador' : 'Agresivo'})
              </span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.50"
              step="0.05"
              value={kellyFraction}
              onChange={(e) => setKellyFraction(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: '#38bdf8', cursor: 'pointer' }}
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.25rem', display: 'block' }}>
              Un Kelly fraccional del 0.25x amortigua las rachas de varianza negativa y previene la quiebra.
            </span>
          </div>

          {/* Min Edge Threshold */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.4rem', fontWeight: '600' }}>
              Umbral Mínimo de Ventaja (Min Edge %)
            </label>
            <input
              type="number"
              step="0.5"
              className="line-input mono"
              style={{ width: '100%', padding: '0.55rem 0.75rem', fontSize: '1.05rem', textAlign: 'left' }}
              value={minEdge}
              onChange={(e) => setMinEdge(e.target.value)}
            />
          </div>

          {/* The Odds API Key Integration */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.4rem', fontWeight: '600' }}>
              Clave Gratuita de The Odds API (Opcional - Cuotas en Vivo Bet365 / Winamax)
            </label>
            <input
              type="text"
              placeholder="Ej: a1b2c3d4e5f6... (500 llamadas/mes gratis)"
              className="line-input mono"
              style={{ width: '100%', padding: '0.55rem 0.75rem', fontSize: '0.85rem', textAlign: 'left' }}
              value={settings.odds_api_key || ''}
              onChange={(e) => onSaveSettings({ ...settings, odds_api_key: e.target.value })}
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.25rem', display: 'block' }}>
              Puedes obtener una clave gratuita en <a href="https://the-odds-api.com" target="_blank" rel="noopener noreferrer" style={{ color: '#38bdf8' }}>the-odds-api.com</a> para sincronizar automáticamente cuotas europeas en vivo. Si no tienes clave, puedes editar las cuotas manualmente en cada tarjeta con un solo clic.
            </span>
          </div>

          {/* Legal Compliance Notice */}
          <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', padding: '0.85rem', borderRadius: '8px', display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
            <ShieldAlert size={18} color="#f59e0b" style={{ flexShrink: 0, marginTop: '0.1rem' }} />
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
              <strong style={{ color: '#ffffff' }}>Cumplimiento Legal en España (DGOJ):</strong> Las apuestas en casas con licencia española (Bet365.es y Winamax.es) deben ser ejecutadas exclusivamente de forma manual por el usuario. Juega con responsabilidad (+18).
            </div>
          </div>
        </div>

        {/* Action buttons */}
        <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
          <button className="filter-btn" onClick={onClose} style={{ flex: 1, padding: '0.65rem' }}>
            Cancelar
          </button>
          <button className="filter-btn active" onClick={handleSave} style={{ flex: 2, padding: '0.65rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}>
            <Check size={16} />
            <span>Guardar Ajustes</span>
          </button>
        </div>
      </div>
    </div>
  );
}

