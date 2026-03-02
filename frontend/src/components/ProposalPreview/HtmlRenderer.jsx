import React, { useRef, useEffect } from 'react';

function HtmlRenderer({ html }) {
  const iframeRef = useRef(null);
  useEffect(() => {
    if (iframeRef.current && html) {
      const doc = iframeRef.current.contentDocument;
      doc.open();
      doc.write(html);
      doc.close();
    }
  }, [html]);

  if (!html) return <p style={{ textAlign: 'center', padding: '40px' }}>No proposal generated yet.</p>;
  return (
    <iframe ref={iframeRef} title="Proposal Preview" className="html-preview-frame"
      style={{ width: '100%', minHeight: '800px', border: 'none', background: '#fff' }} />
  );
}
export default HtmlRenderer;
