import React from 'react';
import { Activity, Cpu, Table, Sliders, RefreshCw, Euro, ShieldCheck } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, bankroll, onOpenSettings, isRefreshing, onRefresh }) {
  return (
    <header className="navbar">
      <div className="container navbar-inner">
        {/* Brand */}
        <div className="brand-badge">
          <div className="brand-icon">
            <Activity size={20} color="#ffffff" />
          </div>
          <div>
            <div className="brand-title">NBAEdge Predictor</div>
            <div className="brand-sub">ML & Apuestas España • Bet365 & Winamax</div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="nav-tabs">
          <button
            className={`nav-tab-btn ${activeTab === 'matches' ? 'active' : ''}`}
            onClick={() => setActiveTab('matches')}
          >
            <Activity size={16} />
            <span>Partidos En Vivo</span>
            <span className="live-indicator" title="Conexión en vivo con ESPN"></span>
          </button>

          <button
            className={`nav-tab-btn ${activeTab === 'training' ? 'active' : ''}`}
            onClick={() => setActiveTab('training')}
          >
            <Cpu size={16} />
            <span>Lógica ML & Entrenamiento</span>
          </button>

          <button
            className={`nav-tab-btn ${activeTab === 'table' ? 'active' : ''}`}
            onClick={() => setActiveTab('table')}
          >
            <Table size={16} />
            <span>Mesa de Apuestas</span>
          </button>

          <button
            className={`nav-tab-btn ${activeTab === 'market' ? 'active' : ''}`}
            onClick={() => setActiveTab('market')}
          >
            <Activity size={16} color="#38bdf8" />
            <span>Mercado & Dinero Inteligente</span>
          </button>
        </nav>

        {/* Right actions */}
        <div className="nav-actions">
          <button 
            className="filter-btn" 
            onClick={onRefresh} 
            disabled={isRefreshing}
            title="Refrescar partidos y props de ESPN"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer' }}
          >
            <RefreshCw size={14} className={isRefreshing ? 'spin' : ''} />
            <span style={{ fontSize: '0.8rem' }}>{isRefreshing ? 'Actualizando...' : 'Refrescar'}</span>
          </button>

          <div className="bankroll-pill" onClick={onOpenSettings} style={{ cursor: 'pointer' }} title="Configurar Bankroll">
            <Euro size={15} color="#10b981" />
            <span style={{ color: 'var(--text-muted)' }}>Bankroll:</span>
            <span className="bankroll-amount mono">{Number(bankroll).toLocaleString('es-ES', { minimumFractionDigits: 2 })} €</span>
          </div>

          <button 
            className="filter-btn" 
            onClick={onOpenSettings} 
            title="Ajustes de algoritmo y Kelly"
            style={{ padding: '0.45rem' }}
          >
            <Sliders size={16} />
          </button>
        </div>
      </div>
    </header>
  );
}

