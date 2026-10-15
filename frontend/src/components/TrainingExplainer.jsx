import React, { useState } from 'react';
import { Cpu, Database, GitBranch, ShieldCheck, Terminal, Copy, Check, Clock, AlertTriangle, Layers, BookOpen, Download, FileText } from 'lucide-react';

export default function TrainingExplainer() {
  const [copiedStep, setCopiedStep] = useState(null);

  const copyToClipboard = (text, stepIndex) => {
    navigator.clipboard.writeText(text);
    setCopiedStep(stepIndex);
    setTimeout(() => setCopiedStep(null), 2000);
  };

  return (
    <div className="training-container">
      {/* Hero Banner */}
      <div className="training-hero">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
          <span className="live-indicator"></span>
          <span style={{ fontSize: '0.85rem', color: 'var(--accent-cyan)', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Arquitectura de Inteligencia Artificial & Aprendizaje Automático
          </span>
        </div>
        <h2 style={{ fontSize: '1.9rem', fontWeight: '800', color: '#ffffff', letterSpacing: '-0.02em', marginBottom: '0.75rem' }}>
          Lógica de Entrenamiento: Jerarquía en 2 Fases & Modelos Predictivos
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', maxWidth: '900px', lineHeight: '1.6' }}>
          Para predecir con ventaja matemática frente a casas de apuestas como <strong>Bet365</strong> y <strong>Winamax</strong>, no se pueden predecir puntos de manera ingenua. Este sistema utiliza una <strong>descomposición estocástica en dos submodelos</strong>, previniendo fugas de datos temporales (<em>Data Leakage</em>) y ajustando el riesgo ante partidos desiguales (<em>Blowouts</em>).
        </p>

        {/* Download Technical PDF Button */}
        <div style={{ marginTop: '1.25rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <a
            href="/api/download-pdf"
            target="_blank"
            rel="noopener noreferrer"
            className="filter-btn active"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.55rem',
              padding: '0.65rem 1.25rem',
              fontSize: '0.88rem',
              textDecoration: 'none',
              borderRadius: '8px',
              fontWeight: '700',
              background: 'linear-gradient(135deg, #0284c7 0%, #2563eb 100%)',
              border: 'none',
              boxShadow: '0 4px 15px rgba(2, 132, 199, 0.4)'
            }}
          >
            <Download size={17} />
            <span>Descargar Documento Técnico PDF (Especificación de Ingeniería)</span>
          </a>
        </div>
      </div>

      {/* Grid of 4 Key Concepts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        {/* Concept 1 */}
        <div className="flow-step-card">
          <div className="flow-step-number">01</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Layers size={22} color="#38bdf8" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: '700', color: '#ffffff' }}>Jerarquía en 2 Fases</h3>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.5' }}>
            <strong>El 68% del error</strong> en props NBA proviene de no acertar cuántos minutos jugará el jugador.
          </p>
          <div style={{ background: 'var(--bg-secondary)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '0.85rem' }}>
            <div style={{ color: '#38bdf8', fontWeight: '600', marginBottom: '0.3rem' }}>• Submodelo 1 (Minutos):</div>
            <div style={{ color: 'var(--text-dim)' }}>LightGBM Regressor que proyecta el tiempo en pista en función de faltas, rotaciones del entrenador y diferencial del partido (Blowout).</div>
            <div style={{ color: '#c084fc', fontWeight: '600', marginTop: '0.5rem', marginBottom: '0.3rem' }}>• Submodelo 2 (Stats):</div>
            <div style={{ color: 'var(--text-dim)' }}>Ensemble de LightGBM (55%) + XGBoost (45%) por cada estadística (PTS, REB, AST, 3PM, PRA), usando los minutos predichos de la Fase 1 como variable central.</div>
          </div>
        </div>

        {/* Concept 2 */}
        <div className="flow-step-card">
          <div className="flow-step-number">02</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <ShieldCheck size={22} color="#10b981" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: '700', color: '#ffffff' }}>Cero Data Leakage (.shift(1))</h3>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.5' }}>
            El error más letal en ciencia de datos deportiva es incluir estadísticas del partido objetivo en las medias móviles.
          </p>
          <div className="code-box" style={{ fontSize: '0.78rem' }}>
            <span className="code-comment"># En src/features/rolling.py:</span><br />
            df[<span className="code-str">'pts_roll_10'</span>] = (<br />
            &nbsp;&nbsp;df.groupby(<span className="code-str">'player_id'</span>)[<span className="code-str">'pts'</span>]<br />
            &nbsp;&nbsp;&nbsp;&nbsp;.apply(<span className="code-keyword">lambda</span> x: x.<span className="code-func">shift</span>(1).<span className="code-func">rolling</span>(10).mean())<br />
            )
          </div>
          <div style={{ fontSize: '0.8rem', color: '#10b981' }}>
            ✓ Garantiza que el modelo solo ve información disponible <strong>antes</strong> del salto inicial.
          </div>
        </div>

        {/* Concept 3 */}
        <div className="flow-step-card">
          <div className="flow-step-number">03</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <GitBranch size={22} color="#8b5cf6" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: '700', color: '#ffffff' }}>Validación Walk-Forward</h3>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.5' }}>
            No se utiliza K-Fold aleatorio (violaría la flecha del tiempo). Se utiliza <strong>TimeSeriesSplit</strong> estricto:
          </p>
          <div style={{ background: 'var(--bg-secondary)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
              <span>Entrenamiento:</span>
              <strong style={{ color: '#ffffff' }}>2014-15 a 2022-23 (9 temporadas)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
              <span>Validación e Hiperparámetros:</span>
              <strong style={{ color: '#38bdf8' }}>2023-24 (1 temporada)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Test Ciego (Backtesting):</span>
              <strong style={{ color: '#10b981' }}>2024-25 y 2025-26</strong>
            </div>
          </div>
        </div>

        {/* Concept 4 */}
        <div className="flow-step-card">
          <div className="flow-step-number">04</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <AlertTriangle size={22} color="#f59e0b" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: '700', color: '#ffffff' }}>Gestión de Riesgo & Kelly</h3>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.5' }}>
            Tener una proyección con ventaja (Edge &gt; 0) no basta si el partido termina en paliza o el jugador llega tocado.
          </p>
          <ul style={{ color: 'var(--text-muted)', fontSize: '0.85rem', paddingLeft: '1.2rem', lineHeight: '1.5' }}>
            <li><strong>8 Factores Ponderados:</strong> Spreads &gt; 10 puntos (Blowout), B2B, varianza de minutos, etc.</li>
            <li><strong>Criterio de Kelly Fraccional (0.25x):</strong> Protege la banca contra rachas adversas, recomendando exactamente cuánto apostar en euros (€).</li>
          </ul>
        </div>
      </div>

      {/* Dataset & Requirements Deep-Dive */}
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
          <Database size={24} color="#38bdf8" />
          <h3 style={{ fontSize: '1.35rem', fontWeight: '700', color: '#ffffff' }}>
            ¿Qué necesitas exactamente para entrenar el modelo?
          </h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
          <div style={{ background: 'var(--bg-secondary)', padding: '1.25rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div style={{ color: '#38bdf8', fontWeight: '700', fontSize: '0.95rem', marginBottom: '0.5rem' }}>
              1. Datos Históricos de la NBA
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.5' }}>
              Se requieren 10 temporadas completas (2014-15 hasta la fecha). Esto equivale a aproximadamente <strong>250.000 filas de partidos individuales por jugador</strong> con minutos, tiros de campo, rebotes, asistencias, faltas y rating defensivo del rival.
            </p>
          </div>

          <div style={{ background: 'var(--bg-secondary)', padding: '1.25rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div style={{ color: '#10b981', fontWeight: '700', fontSize: '0.95rem', marginBottom: '0.5rem' }}>
              2. nba_api & Respeto al Rate Limiting
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.5' }}>
              El paquete <code style={{ color: '#38bdf8' }}>nba_api</code> se conecta directamente a los endpoints oficiales de <code style={{ color: '#a5d6ff' }}>stats.nba.com</code>. Para evitar que Cloudflare bloquee tu dirección IP, nuestro script implementa una pausa estricta de <strong>1.0 segundo</strong> por petición.
            </p>
          </div>

          <div style={{ background: 'var(--bg-secondary)', padding: '1.25rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
            <div style={{ color: '#c084fc', fontWeight: '700', fontSize: '0.95rem', marginBottom: '0.5rem' }}>
              3. Matriz de Características (62 Features)
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.5' }}>
              Se generan ventanas móviles (3, 5, 10, 20 partidos), medias ponderadas exponenciales (EWMA), tendencia lineal, fatiga por partidos consecutivos (B2B), altitud de Denver y rating defensivo del rival por posición.
            </p>
          </div>
        </div>

        {/* Step by step execution */}
        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
          <h4 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#ffffff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Terminal size={18} color="#38bdf8" />
            Comandos de Terminal para Ejecutar el Entrenamiento
          </h4>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {/* Command 1 */}
            <div style={{ background: '#0d1117', border: '1px solid #21262d', borderRadius: '8px', padding: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#58a6ff' }}>
                  Paso 1: Descargar 10 temporadas de la NBA a SQLite (Una sola vez)
                </span>
                <button
                  className="filter-btn"
                  onClick={() => copyToClipboard('python main.py ingest --seasons 2014-15 2015-16 2016-17 2017-18 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24 2024-25', 1)}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', padding: '0.2rem 0.6rem' }}
                >
                  {copiedStep === 1 ? <Check size={13} color="#10b981" /> : <Copy size={13} />}
                  <span>{copiedStep === 1 ? 'Copiado' : 'Copiar'}</span>
                </button>
              </div>
              <code style={{ color: '#c9d1d9', fontSize: '0.85rem' }}>
                python main.py ingest --seasons 2014-15 2015-16 2016-17 2017-18 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24 2024-25
              </code>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.4rem' }}>
                ⏱ Toma aprox. 25-35 minutos debido al rate limiting seguro. Se almacena localmente en data/nba_stats.db.
              </div>
            </div>

            {/* Command 2 */}
            <div style={{ background: '#0d1117', border: '1px solid #21262d', borderRadius: '8px', padding: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#58a6ff' }}>
                  Paso 2: Calcular la matriz de features sin Data Leakage
                </span>
                <button
                  className="filter-btn"
                  onClick={() => copyToClipboard('python main.py features', 2)}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', padding: '0.2rem 0.6rem' }}
                >
                  {copiedStep === 2 ? <Check size={13} color="#10b981" /> : <Copy size={13} />}
                  <span>{copiedStep === 2 ? 'Copiado' : 'Copiar'}</span>
                </button>
              </div>
              <code style={{ color: '#c9d1d9', fontSize: '0.85rem' }}>
                python main.py features
              </code>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.4rem' }}>
                ⚙️ Procesa todas las ventanas temporales y genera el archivo data/processed/features.parquet.
              </div>
            </div>

            {/* Command 3 */}
            <div style={{ background: '#0d1117', border: '1px solid #21262d', borderRadius: '8px', padding: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#58a6ff' }}>
                  Paso 3: Entrenar el Submodelo de Minutos y los Ensembles LightGBM + XGBoost
                </span>
                <button
                  className="filter-btn"
                  onClick={() => copyToClipboard('python main.py train', 3)}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', padding: '0.2rem 0.6rem' }}
                >
                  {copiedStep === 3 ? <Check size={13} color="#10b981" /> : <Copy size={13} />}
                  <span>{copiedStep === 3 ? 'Copiado' : 'Copiar'}</span>
                </button>
              </div>
              <code style={{ color: '#c9d1d9', fontSize: '0.85rem' }}>
                python main.py train
              </code>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.4rem' }}>
                🔥 Entrena los modelos, valida con TimeSeriesSplit y guarda los artefactos binarios en data/models/.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

