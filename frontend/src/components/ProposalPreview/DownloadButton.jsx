import React, { useState } from 'react';
import * as api from '../../services/api';

function DownloadButton({ proposalId }) {
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    if (!proposalId) return;
    try {
      setDownloading(true);
      const res = await api.downloadPdf(proposalId);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `proposal_${proposalId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setDownloading(false);
    } catch (err) {
      setDownloading(false);
      alert('Failed to download PDF');
    }
  };

  return (
    <button className="btn-primary" onClick={handleDownload} disabled={downloading || !proposalId}>
      {downloading ? 'Downloading...' : 'Download PDF'}
    </button>
  );
}
export default DownloadButton;
