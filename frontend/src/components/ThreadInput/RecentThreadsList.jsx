import React from 'react';

function RecentThreadsList({ threads, onSelect }) {
  return (
    <div className="recent-threads">
      <h3>Recent Threads</h3>
      <ul>
        {threads.map((t) => (
          <li key={t.id} onClick={() => onSelect(t)} className="thread-item">
            <span className="thread-subject">{t.subject}</span>
            <span className="thread-date">{new Date(t.created_at).toLocaleDateString()}</span>
            <span className="thread-arrow">&rarr;</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
export default RecentThreadsList;
