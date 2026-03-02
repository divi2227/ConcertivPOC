import React from 'react';

function ActionBar({ onSave, onBack, isSaving }) {
  return (
    <div className="action-bar">
      <button className="btn-secondary" onClick={onBack}>&larr; Back</button>
      <button className="btn-primary" onClick={onSave} disabled={isSaving}>
        {isSaving ? 'Saving...' : 'Save Edits'}
      </button>
    </div>
  );
}
export default ActionBar;
