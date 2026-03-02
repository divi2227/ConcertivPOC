import React, { useState, useCallback } from 'react';
import useStore from '../../store/useStore';
import * as api from '../../services/api';
import ConfidenceBadge from './ConfidenceBadge';
import AmbiguityWarningBar from './AmbiguityWarningBar';
import ThreadViewer from './ThreadViewer';
import ExtractionEditor from './ExtractionEditor';
import ActionBar from './ActionBar';
import './ProposalReview.css';

function ProposalReview() {
  const { currentThread, currentProposal, setCurrentProposal,
          setGeneratedHtml, setScreen, isGenerating, setIsGenerating, setError } = useStore();
  const [editedProposal, setEditedProposal] = useState(currentProposal);
  const [isSaving, setIsSaving] = useState(false);

  const handleFieldChange = useCallback((section, field, value) => {
    setEditedProposal(prev => ({
      ...prev,
      [section]: typeof prev[section] === 'object' && !Array.isArray(prev[section])
        ? { ...prev[section], [field]: value }
        : value,
    }));
  }, []);

  const handleSave = useCallback(async () => {
    try {
      setIsSaving(true);
      const res = await api.updateProposal(editedProposal.id, editedProposal);
      setCurrentProposal(res.data);
      setEditedProposal(res.data);
      setIsSaving(false);
    } catch (err) {
      setIsSaving(false);
      setError(err.response?.data?.error || 'Failed to save');
    }
  }, [editedProposal, setCurrentProposal, setError]);

  const handleGenerate = useCallback(async () => {
    try {
      setIsGenerating(true);
      await api.updateProposal(editedProposal.id, editedProposal);
      const res = await api.generateProposal(editedProposal.id);
      setGeneratedHtml(res.data.html_content);
      setIsGenerating(false);
      setScreen('preview');
    } catch (err) {
      setIsGenerating(false);
      setError(err.response?.data?.error || 'Failed to generate proposal');
    }
  }, [editedProposal, setGeneratedHtml, setScreen, setIsGenerating, setError]);

  if (!currentThread || !editedProposal) return <div className="loading">Loading...</div>;

  const ambiguities = editedProposal.ambiguities || [];

  return (
    <div className="proposal-review">
      <div className="review-header">
        <div className="review-header-left">
          <ConfidenceBadge confidence={editedProposal.confidence} />
          {editedProposal.acceptance_signal && (
            <span className="acceptance-text">
              Acceptance: &ldquo;{editedProposal.acceptance_signal.substring(0, 60)}...&rdquo;
            </span>
          )}
        </div>
        <div className="review-header-right">
          {ambiguities.length > 0 && <AmbiguityWarningBar count={ambiguities.length} />}
          <button className="btn-primary" onClick={handleGenerate} disabled={isGenerating}>
            {isGenerating ? 'Generating...' : 'Generate PDF'}
          </button>
        </div>
      </div>
      <div className="review-panels">
        <div className="panel-left">
          <ThreadViewer thread={currentThread} proposal={editedProposal} />
        </div>
        <div className="panel-right">
          <ExtractionEditor proposal={editedProposal} onChange={handleFieldChange} />
        </div>
      </div>
      <ActionBar onSave={handleSave} onBack={() => setScreen('input')} isSaving={isSaving} />
    </div>
  );
}
export default ProposalReview;
