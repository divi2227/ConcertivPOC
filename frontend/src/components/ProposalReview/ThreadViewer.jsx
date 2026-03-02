import React, { useMemo } from 'react';
import MessageCard from './MessageCard';
import { getHighlightTerms } from './highlightUtils';

function ThreadViewer({ thread, proposal }) {
  const messages = thread?.messages || [];
  const highlightTerms = useMemo(() => getHighlightTerms(proposal), [proposal]);

  return (
    <div className="thread-viewer">
      <h3>EMAIL THREAD</h3>
      {highlightTerms.length > 0 && (
        <div className="highlight-legend">
          <span className="highlight-legend-icon">&#9679;</span>
          Extracted values highlighted in yellow
        </div>
      )}
      <div className="messages-list">
        {messages.map((msg, i) => (
          <MessageCard key={msg.id || i} message={msg} index={i} highlightTerms={highlightTerms} />
        ))}
      </div>
    </div>
  );
}
export default ThreadViewer;
