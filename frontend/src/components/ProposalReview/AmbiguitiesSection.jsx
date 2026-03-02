import React from 'react';

function AmbiguitiesSection({ ambiguities }) {
  if (!ambiguities || ambiguities.length === 0) return null;
  return (
    <div className="editor-section ambiguities">
      <h4>&#9888; AMBIGUITIES</h4>
      <ul className="ambiguities-list">
        {ambiguities.map((a, i) => <li key={i}>{a}</li>)}
      </ul>
    </div>
  );
}
export default AmbiguitiesSection;
