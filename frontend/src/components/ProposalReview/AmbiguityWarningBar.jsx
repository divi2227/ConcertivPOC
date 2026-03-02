import React from 'react';

function AmbiguityWarningBar({ count }) {
  return (
    <span style={{ background: '#fff3cd', color: '#856404', padding: '6px 14px', borderRadius: '20px', fontSize: '13px', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '6px', marginRight: '12px' }}>
      &#9888; {count} ambiguit{count === 1 ? 'y' : 'ies'} flagged
    </span>
  );
}
export default AmbiguityWarningBar;
