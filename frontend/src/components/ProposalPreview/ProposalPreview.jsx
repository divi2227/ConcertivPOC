import React from 'react';
import useStore from '../../store/useStore';
import HtmlRenderer from './HtmlRenderer';
import DownloadButton from './DownloadButton';
import './ProposalPreview.css';

function ProposalPreview() {
  const { generatedHtml, currentProposal, setScreen } = useStore();
  return (
    <div className="proposal-preview">
      <div className="preview-header">
        <button className="btn-secondary" onClick={() => setScreen('review')}>
          &larr; Back to Review
        </button>
        <DownloadButton proposalId={currentProposal?.id} />
      </div>
      <div className="preview-content">
        <HtmlRenderer html={generatedHtml} />
      </div>
    </div>
  );
}
export default ProposalPreview;
