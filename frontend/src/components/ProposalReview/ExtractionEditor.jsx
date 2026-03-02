import React from 'react';
import PartiesSection from './PartiesSection';
import PricingSection from './PricingSection';
import LicenseTermsSection from './LicenseTermsSection';
import SpecialConditionsSection from './SpecialConditionsSection';
import AmbiguitiesSection from './AmbiguitiesSection';

function ExtractionEditor({ proposal, onChange }) {
  return (
    <div className="extraction-editor">
      <h3>EXTRACTED PROPOSAL</h3>
      <PartiesSection parties={proposal.parties || {}} onChange={onChange} />
      <PricingSection pricing={proposal.pricing || {}} onChange={onChange} />
      <LicenseTermsSection terms={proposal.license_terms || {}} onChange={onChange} />
      <SpecialConditionsSection conditions={proposal.special_conditions || []} onChange={onChange} />
      {(proposal.ambiguities || []).length > 0 && (
        <AmbiguitiesSection ambiguities={proposal.ambiguities} />
      )}
    </div>
  );
}
export default ExtractionEditor;
