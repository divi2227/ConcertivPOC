import React from 'react';

function ConfidenceBadge({ confidence }) {
  const colors = { high: 'var(--success)', medium: 'var(--warning)', low: 'var(--danger)' };
  const icons = { high: '\u2713', medium: '\u26A0', low: '\u2717' };
  const bg = { high: '#d4edda', medium: '#fff3cd', low: '#f8d7da' };
  return (
    <span className="confidence-badge" style={{ background: bg[confidence] || bg.low, color: colors[confidence] || colors.low, padding: '6px 14px', borderRadius: '20px', fontWeight: 700, fontSize: '13px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
      <span>{icons[confidence] || icons.low}</span>
      {(confidence || 'low').toUpperCase()}
    </span>
  );
}
export default ConfidenceBadge;
