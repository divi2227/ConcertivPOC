import React from 'react';

function LicenseTermsSection({ terms, onChange }) {
  const handleChange = (field, value) => onChange('license_terms', field, value);
  return (
    <div className="editor-section">
      <h4>LICENSE TERMS</h4>
      <div className="editable-field">
        <label>Term</label>
        <div className="field-input">
          <input type="text" value={terms.term_years ? `${terms.term_years} years` : ''}
            onChange={(e) => handleChange('term_years', parseInt(e.target.value) || null)} />
          <span className="edit-icon">&#9998;</span>
        </div>
      </div>
      <div className="editable-field">
        <label>Start Date</label>
        <div className="field-input">
          <input type="text" value={terms.start_date || ''}
            onChange={(e) => handleChange('start_date', e.target.value)} />
          <span className="edit-icon">&#9998;</span>
        </div>
      </div>
      <div className="editable-field">
        <label>End Date</label>
        <div className="field-input">
          <input type="text" value={terms.end_date || ''}
            onChange={(e) => handleChange('end_date', e.target.value)} />
          <span className="edit-icon">&#9998;</span>
        </div>
      </div>
      <div className="editable-field">
        <label>Seats</label>
        <div className="field-input">
          <input type="text" value={terms.seat_count || ''}
            onChange={(e) => handleChange('seat_count', parseInt(e.target.value) || null)} />
          <span className="edit-icon">&#9998;</span>
        </div>
      </div>
      <div className="editable-field">
        <label>Renewal</label>
        <div className="field-input">
          <input type="text" value={terms.renewal_type || ''}
            onChange={(e) => handleChange('renewal_type', e.target.value)} />
          {!terms.renewal_type && <span className="warning-icon">&#9888;</span>}
          <span className="edit-icon">&#9998;</span>
        </div>
      </div>
    </div>
  );
}
export default LicenseTermsSection;
