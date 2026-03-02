import React from 'react';
import './styles/variables.css';
import './App.css';
import useStore from './store/useStore';
import ThreadInput from './components/ThreadInput/ThreadInput';
import ProposalReview from './components/ProposalReview/ProposalReview';
import ProposalPreview from './components/ProposalPreview/ProposalPreview';

function App() {
  const currentScreen = useStore((s) => s.currentScreen);
  const error = useStore((s) => s.error);
  const clearError = useStore((s) => s.clearError);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-brand">
          <h1 className="brand-name">CONCERTIV</h1>
          <span className="brand-tagline">Proposal Generator</span>
        </div>
      </header>
      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={clearError}>&times;</button>
        </div>
      )}
      <main className="app-main">
        {currentScreen === 'input' && <ThreadInput />}
        {currentScreen === 'review' && <ProposalReview />}
        {currentScreen === 'preview' && <ProposalPreview />}
      </main>
    </div>
  );
}

export default App;
