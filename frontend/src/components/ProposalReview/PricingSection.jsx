import React from 'react';

function PricingSection({ pricing, onChange }) {
  const handleChange = (field, value) => onChange('pricing', field, value);
  return (
    <div className="editor-section">
      <h4>PRICING</h4>
      <div className="editable-field">
        <label>Unit</label>
        <div className="field-input">
          <input type="text" value={pricing.unit || ''} onChange={(e) => handleChange('unit', e.target.value)} />
          <span className="edit-icon">&#9998;</span>
        </div>
      </div>
      <div className="editable-field">
        <label>Unit Price</label>
        <div className="field-input">
          <input type="text" value={pricing.unit_price != null ? `$${Number(pricing.unit_price).toLocaleString()}` : ''}
            onChange={(e) => handleChange('unit_price', parseFloat(e.target.value.replace(/[$,]/g, '')) || null)} />
          <span className="edit-icon">&#9998;</span>
        </div>
      </div>
      <div className="editable-field">
        <label>Quantity</label>
        <div className="field-input">
          <input type="text" value={pricing.quantity || ''}
            onChange={(e) => handleChange('quantity', parseInt(e.target.value) || null)} />
          <span className="edit-icon">&#9998;</span>
        </div>
      </div>
      <div className="editable-field">
        <label>Annual Value</label>
        <div className="field-input">
          <input type="text" value={pricing.total_annual_value != null ? `$${Number(pricing.total_annual_value).toLocaleString()}` : ''}
            onChange={(e) => handleChange('total_annual_value', parseFloat(e.target.value.replace(/[$,]/g, '')) || null)} />
          <span className="edit-icon">&#9998;</span>
        </div>
      </div>
      <div className="editable-field">
        <label>Contract Value</label>
        <div className="field-input">
          <input type="text" value={pricing.total_contract_value != null ? `$${Number(pricing.total_contract_value).toLocaleString()}` : ''}
            onChange={(e) => handleChange('total_contract_value', parseFloat(e.target.value.replace(/[$,]/g, '')) || null)} />
          <span className="edit-icon">&#9998;</span>
        </div>
      </div>
      {pricing.price_history && pricing.price_history.length > 0 && (
        <div className="price-history">
          <h5>Price History</h5>
          <table>
            <thead><tr><th>Round</th><th>By</th><th>Price</th><th>Notes</th></tr></thead>
            <tbody>
              {pricing.price_history.map((h, i) => (
                <tr key={i}>
                  <td>{h.round}</td>
                  <td>{h.proposed_by}</td>
                  <td>{h.unit_price != null ? `$${Number(h.unit_price).toLocaleString()}` : '—'}</td>
                  <td>{h.notes || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
export default PricingSection;
