import React from 'react';

function SpecialConditionsSection({ conditions }) {
  if (!conditions || conditions.length === 0) return null;
  return (
    <div className="editor-section">
      <h4>SPECIAL CONDITIONS</h4>
      <ul className="conditions-list">
        {conditions.map((c, i) => <li key={i}>{c}</li>)}
      </ul>
    </div>
  );
}
export default SpecialConditionsSection;
