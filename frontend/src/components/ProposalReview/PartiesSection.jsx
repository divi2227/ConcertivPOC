import React from 'react';

function EditableField({ label, value, onChange }) {
  return (
    <div className="editable-field">
      <label>{label}</label>
      <div className="field-input">
        <input type="text" value={value || ''} onChange={(e) => onChange(e.target.value)} />
        <span className="edit-icon">&#9998;</span>
      </div>
    </div>
  );
}

function PartiesSection({ parties, onChange }) {
  const client = parties.client_contact || {};
  const vendor = parties.vendor_contact || {};
  const concertiv = parties.concertiv_contact || {};

  return (
    <div className="editor-section">
      <h4>PARTIES</h4>
      <EditableField label="Client" value={parties.client_name}
        onChange={(v) => onChange('parties', 'client_name', v)} />
      <EditableField label="Client Contact" value={client.name}
        onChange={(v) => onChange('parties', 'client_contact', { ...client, name: v })} />
      <EditableField label="Vendor" value={parties.vendor_name}
        onChange={(v) => onChange('parties', 'vendor_name', v)} />
      <EditableField label="Vendor Contact" value={vendor.name}
        onChange={(v) => onChange('parties', 'vendor_contact', { ...vendor, name: v })} />
      <EditableField label="Concertiv" value={concertiv.name}
        onChange={(v) => onChange('parties', 'concertiv_contact', { ...concertiv, name: v })} />
    </div>
  );
}
export default PartiesSection;
