import React from 'react';
import { highlightText } from './highlightUtils';

function HighlightedBody({ text, highlightTerms }) {
  const segments = highlightText(text, highlightTerms);
  return (
    <>
      {segments.map((seg, i) =>
        seg.highlight ? (
          <mark key={i} className="extracted-highlight" title={seg.label}>
            {seg.text}
          </mark>
        ) : (
          <span key={i}>{seg.text}</span>
        )
      )}
    </>
  );
}

function MessageCard({ message, index, highlightTerms }) {
  const body = message.raw_body || message.clean_body;
  return (
    <div className="message-card">
      <div className="msg-header">
        <span className="msg-id">[{message.message_id}]</span>
        <span className="msg-from">{message.sender_name}</span>
      </div>
      <div className="msg-meta">
        <span>{new Date(message.timestamp).toLocaleString()}</span>
      </div>
      <div className="msg-body">
        {highlightTerms && highlightTerms.length > 0 ? (
          <HighlightedBody text={body} highlightTerms={highlightTerms} />
        ) : (
          body
        )}
      </div>
    </div>
  );
}
export default MessageCard;
