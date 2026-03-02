import axios from 'axios';

const API = axios.create({ baseURL: 'http://localhost:8000/api' });

// Outlook integration
export const getVendors = () => API.get('/outlook/vendors/');
export const getClients = () => API.get('/outlook/clients/');
export const fetchOutlookThread = (vendor, client) =>
  API.post('/outlook/fetch/', { vendor, client });

// Thread operations
export const listThreads = () => API.get('/threads/');
export const getThread = (id) => API.get(`/threads/${id}/`);
export const analyzeThread = (threadId) => API.post(`/threads/${threadId}/analyze/`);

// Proposal operations
export const getProposal = (proposalId) => API.get(`/proposals/${proposalId}/`);
export const updateProposal = (proposalId, edits) => API.patch(`/proposals/${proposalId}/`, edits);
export const generateProposal = (proposalId) => API.post(`/proposals/${proposalId}/generate/`);
export const downloadPdf = (proposalId) => API.get(`/proposals/${proposalId}/download/`, { responseType: 'blob' });
