import { create } from 'zustand';

const useStore = create((set) => ({
  currentScreen: 'input',
  setScreen: (screen) => set({ currentScreen: screen }),
  currentThread: null,
  setCurrentThread: (thread) => set({ currentThread: thread }),
  currentProposal: null,
  setCurrentProposal: (proposal) => set({ currentProposal: proposal }),
  generatedHtml: null,
  setGeneratedHtml: (html) => set({ generatedHtml: html }),
  isFetching: false,
  setIsFetching: (val) => set({ isFetching: val }),
  isAnalyzing: false,
  setIsAnalyzing: (val) => set({ isAnalyzing: val }),
  isGenerating: false,
  setIsGenerating: (val) => set({ isGenerating: val }),
  threads: [],
  setThreads: (threads) => set({ threads }),
  vendors: [],
  setVendors: (vendors) => set({ vendors }),
  clients: [],
  setClients: (clients) => set({ clients }),
  fetchedThread: null,
  setFetchedThread: (thread) => set({ fetchedThread: thread }),
  error: null,
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
  reset: () => set({ currentThread: null, currentProposal: null, generatedHtml: null, fetchedThread: null, error: null }),
}));

export default useStore;
