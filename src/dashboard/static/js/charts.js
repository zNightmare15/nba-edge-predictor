/**
 * NBA Betting Dashboard — Chart.js Utilities
 * 
 * Dark-themed charts for sparklines, player performance, 
 * cumulative profit, and stat distribution.
 */

// ============================================================
// Global Defaults
// ============================================================
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.06)';
Chart.defaults.font.family = "'Inter', system-ui, -apple-system, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyleWidth = 8;
Chart.defaults.animation.duration = 600;

// ============================================================
// Color Palette
// ============================================================
const CHART_COLORS = {
    orange: '#f97316',
    orangeAlpha: 'rgba(249, 115, 22, 0.15)',
    blue: '#3b82f6',
    blueAlpha: 'rgba(59, 130, 246, 0.15)',
    green: '#4ade80',
    greenAlpha: 'rgba(74, 222, 128, 0.15)',
    red: '#f87171',
    redAlpha: 'rgba(248, 113, 113, 0.15)',
    gold: '#fbbf24',
    goldAlpha: 'rgba(251, 191, 36, 0.15)',
    purple: '#a78bfa',
    purpleAlpha: 'rgba(167, 139, 250, 0.15)',
    gray: '#64748b',
    surface: '#1e293b',
    gridLine: 'rgba(255, 255, 255, 0.04)',
};

// ============================================================
// Sparkline — Tiny inline chart for last N games
// ============================================================
function createSparkline(canvasId, dataPoints, color = CHART_COLORS.orange) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');

    // Gradient fill
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, color.replace(')', ', 0.3)').replace('rgb', 'rgba'));
    gradient.addColorStop(1, color.replace(')', ', 0.0)').replace('rgb', 'rgba'));

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: dataPoints.map((_, i) => i + 1),
            datasets: [{
                data: dataPoints,
                borderColor: color,
                backgroundColor: gradient,
                borderWidth: 1.5,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHitRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    enabled: true,
                    backgroundColor: '#1e293b',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    titleFont: { size: 10 },
                    bodyFont: { size: 11 },
                    padding: 6,
                    displayColors: false,
                    callbacks: {
                        title: (items) => `Game ${items[0].label}`,
                        label: (item) => item.formattedValue,
                    }
                }
            },
            scales: {
                x: { display: false },
                y: { display: false }
            },
            interaction: {
                intersect: false,
                mode: 'nearest'
            }
        }
    });
}

// ============================================================
// Batch-create sparklines from data attributes
// ============================================================
function initSparklines() {
    document.querySelectorAll('[data-sparkline]').forEach(el => {
        const data = JSON.parse(el.getAttribute('data-sparkline'));
        const color = el.getAttribute('data-sparkline-color') || CHART_COLORS.orange;
        const canvas = el.querySelector('canvas');
        if (canvas && data.length > 0) {
            createSparkline(canvas.id, data, color);
        }
    });
}

// ============================================================
// Player Performance Line Chart (last 20 games)
// ============================================================
function createPlayerChart(canvasId, gamesData, statTypes = ['PTS', 'REB', 'AST']) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');
    const colors = [CHART_COLORS.orange, CHART_COLORS.blue, CHART_COLORS.green, CHART_COLORS.gold, CHART_COLORS.purple];

    const datasets = statTypes.map((stat, i) => {
        const color = colors[i % colors.length];
        return {
            label: stat,
            data: gamesData.map(g => g[stat.toLowerCase()]),
            borderColor: color,
            backgroundColor: 'transparent',
            borderWidth: 2,
            tension: 0.3,
            pointRadius: 3,
            pointBackgroundColor: color,
            pointBorderColor: color,
            pointHoverRadius: 5,
            hidden: i > 0  // Only show first stat by default
        };
    });

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: gamesData.map(g => g.date || g.game_date),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: {
                        padding: 16,
                        font: { size: 11, weight: '500' },
                    }
                },
                tooltip: {
                    backgroundColor: '#0f172a',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 12,
                    titleFont: { size: 12, weight: '600' },
                    bodyFont: { size: 12 },
                    bodySpacing: 6,
                }
            },
            scales: {
                x: {
                    grid: { color: CHART_COLORS.gridLine },
                    ticks: {
                        maxRotation: 45,
                        font: { size: 10 },
                        maxTicksLimit: 10,
                    }
                },
                y: {
                    grid: { color: CHART_COLORS.gridLine },
                    ticks: { font: { size: 11 } },
                    beginAtZero: true,
                }
            },
            interaction: {
                intersect: false,
                mode: 'index',
            }
        }
    });
}

// ============================================================
// Cumulative Profit Chart
// ============================================================
function createProfitChart(canvasId, dates, profits) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');

    // Gradient fill — green above zero, red below
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, CHART_COLORS.greenAlpha);
    gradient.addColorStop(0.5, 'rgba(74, 222, 128, 0.02)');
    gradient.addColorStop(1, CHART_COLORS.redAlpha);

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Cumulative Profit (€)',
                data: profits,
                borderColor: CHART_COLORS.green,
                backgroundColor: gradient,
                borderWidth: 2,
                fill: true,
                tension: 0.3,
                pointRadius: 2,
                pointBackgroundColor: CHART_COLORS.green,
                pointHoverRadius: 5,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    align: 'end',
                    labels: { font: { size: 11, weight: '500' } }
                },
                tooltip: {
                    backgroundColor: '#0f172a',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: (item) => `€${item.formattedValue}`,
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: CHART_COLORS.gridLine },
                    ticks: {
                        maxRotation: 45,
                        font: { size: 10 },
                        maxTicksLimit: 12,
                    }
                },
                y: {
                    grid: { color: CHART_COLORS.gridLine },
                    ticks: {
                        font: { size: 11 },
                        callback: (val) => '€' + val,
                    },
                }
            },
            interaction: {
                intersect: false,
                mode: 'index',
            }
        }
    });
}

// ============================================================
// Bar Chart — Hit Rate by Category
// ============================================================
function createBarChart(canvasId, labels, values, color = CHART_COLORS.orange, yLabel = 'Hit Rate %') {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: yLabel,
                data: values,
                backgroundColor: labels.map((_, i) => {
                    const palette = [CHART_COLORS.green, CHART_COLORS.gold, CHART_COLORS.red, CHART_COLORS.blue, CHART_COLORS.orange, CHART_COLORS.purple];
                    return palette[i % palette.length] + '88';
                }),
                borderColor: labels.map((_, i) => {
                    const palette = [CHART_COLORS.green, CHART_COLORS.gold, CHART_COLORS.red, CHART_COLORS.blue, CHART_COLORS.orange, CHART_COLORS.purple];
                    return palette[i % palette.length];
                }),
                borderWidth: 1,
                borderRadius: 4,
                maxBarThickness: 50,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0f172a',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 10,
                    callbacks: {
                        label: (item) => `${item.formattedValue}%`,
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 11, weight: '500' } }
                },
                y: {
                    grid: { color: CHART_COLORS.gridLine },
                    ticks: {
                        font: { size: 11 },
                        callback: (val) => val + '%',
                    },
                    beginAtZero: true,
                    max: 100,
                }
            }
        }
    });
}

// ============================================================
// Doughnut Chart — Distribution
// ============================================================
function createDoughnutChart(canvasId, labels, values, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    return new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors || [CHART_COLORS.green + '99', CHART_COLORS.gold + '99', CHART_COLORS.red + '99'],
                borderColor: colors ? colors.map(c => c) : [CHART_COLORS.green, CHART_COLORS.gold, CHART_COLORS.red],
                borderWidth: 1,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 12,
                        font: { size: 11 },
                    }
                },
                tooltip: {
                    backgroundColor: '#0f172a',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 10,
                }
            }
        }
    });
}

// ============================================================
// Init on DOM load
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initSparklines();
});
