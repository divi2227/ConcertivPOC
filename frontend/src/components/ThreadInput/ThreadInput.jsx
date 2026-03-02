import React, { useState, useEffect, useCallback } from 'react';
import useStore from '../../store/useStore';
import * as api from '../../services/api';
import RecentThreadsList from './RecentThreadsList';
import './ThreadInput.css';

function ThreadInput() {
  const [selectedVendor, setSelectedVendor] = useState('');
  const [selectedClient, setSelectedClient] = useState('');
  const {
    vendors, setVendors, clients, setClients,
    threads, setThreads, fetchedThread, setFetchedThread,
    setCurrentThread, setCurrentProposal, setScreen,
    isFetching, setIsFetching, isAnalyzing, setIsAnalyzing,
    setError, clearError,
  } = useStore();

  useEffect(() => {
    api.getVendors().then(res => setVendors(res.data.vendors || res.data)).catch(() => {});
    api.getClients().then(res => setClients(res.data.clients || res.data)).catch(() => {});
    api.listThreads().then(res => setThreads(res.data)).catch(() => {});
  }, [setVendors, setClients, setThreads]);

  const handleFetch = useCallback(async () => {
    if (!selectedVendor || !selectedClient) {
      setError('Please select both a vendor and a client.');
      return;
    }
    try {
      clearError();
      setIsFetching(true);
      setFetchedThread(null);
      const res = await api.fetchOutlookThread(selectedVendor, selectedClient);
      setFetchedThread(res.data);
      setCurrentThread(res.data);
      setIsFetching(false);
    } catch (err) {
      setIsFetching(false);
      setFetchedThread(null);
      const errorMsg = err.response?.data?.error || err.message || 'Failed to fetch conversation';
      setError(errorMsg);
    }
  }, [selectedVendor, selectedClient, setIsFetching, setFetchedThread, setCurrentThread, setError, clearError]);

  const handleAnalyze = useCallback(async () => {
    if (!fetchedThread) return;
    try {
      clearError();
      setIsAnalyzing(true);
      const analyzeRes = await api.analyzeThread(fetchedThread.id);
      setCurrentProposal(analyzeRes.data.extraction);
      setIsAnalyzing(false);
      setScreen('review');
    } catch (err) {
      setIsAnalyzing(false);
      setError(err.response?.data?.error || err.message || 'Analysis failed');
    }
  }, [fetchedThread, setCurrentProposal, setScreen, setIsAnalyzing, setError, clearError]);

  const handleSelectThread = useCallback(async (thread) => {
    try {
      clearError();
      const res = await api.getThread(thread.id);
      setCurrentThread(res.data);
      setIsAnalyzing(true);
      const analyzeRes = await api.analyzeThread(thread.id);
      setCurrentProposal(analyzeRes.data.extraction);
      setIsAnalyzing(false);
      setScreen('review');
    } catch (err) {
      setIsAnalyzing(false);
      setError(err.response?.data?.error || err.message);
    }
  }, [setCurrentThread, setCurrentProposal, setScreen, setIsAnalyzing, setError, clearError]);

  return (
    <div className="thread-input">
      <h2>Fetch Email Thread</h2>
      <p className="subtitle">
        Select a vendor and client to fetch their negotiation thread from Outlook
      </p>

      <div className="filter-panel">
        <div className="filter-row">
          <div className="filter-group">
            <label htmlFor="vendor-select">Vendor</label>
            <select
              id="vendor-select"
              value={selectedVendor}
              onChange={(e) => setSelectedVendor(e.target.value)}
              disabled={isFetching || isAnalyzing}
            >
              <option value="">Select vendor...</option>
              {vendors.map((v) => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
          </div>
          <div className="filter-group">
            <label htmlFor="client-select">Client</label>
            <select
              id="client-select"
              value={selectedClient}
              onChange={(e) => setSelectedClient(e.target.value)}
              disabled={isFetching || isAnalyzing}
            >
              <option value="">Select client...</option>
              {clients.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>
        <button
          className="btn-primary fetch-btn"
          onClick={handleFetch}
          disabled={isFetching || isAnalyzing || !selectedVendor || !selectedClient}
        >
          {isFetching ? 'Fetching from Outlook...' : 'Fetch Conversation'}
        </button>
      </div>

      {isFetching && (
        <div className="status-indicator">
          <div className="spinner"></div>
          <p>Fetching email thread from Outlook...</p>
        </div>
      )}

      {fetchedThread && !isFetching && (
        <div className="fetched-thread">
          <h3>
            Fetched Email Thread ({fetchedThread.messages?.length || 0} messages)
          </h3>
          <div className="email-list">
            {(fetchedThread.messages || []).map((msg, idx) => (
              <div key={msg.id || idx} className="email-item">
                <div className="email-header">
                  <span className="email-sender">
                    {msg.sender_name || msg.from?.name || 'Unknown'}
                  </span>
                  <span className="email-date">
                    {new Date(msg.timestamp).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      hour: 'numeric',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
                <div className="email-subject">
                  {msg.subject || fetchedThread.subject}
                </div>
                <div className="email-body">
                  {(msg.clean_body || msg.raw_body || msg.body || '').substring(0, 200)}
                  {(msg.clean_body || msg.raw_body || msg.body || '').length > 200 ? '...' : ''}
                </div>
              </div>
            ))}
          </div>
          <button
            className="btn-primary analyze-btn"
            onClick={handleAnalyze}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? 'Analyzing with Claude...' : 'Analyze with Claude'}
          </button>
        </div>
      )}

      {isAnalyzing && (
        <div className="status-indicator">
          <div className="spinner"></div>
          <p>Claude is extracting commercial terms...</p>
        </div>
      )}

      {threads.length > 0 && (
        <RecentThreadsList threads={threads} onSelect={handleSelectThread} />
      )}
    </div>
  );
}

export default ThreadInput;
