import { create } from 'zustand';

interface UIState {
  sidebarOpen: boolean;
  searchOpen: boolean;
  copilotOpen: boolean;
  terminalOpen: boolean;
  currentProject: string | null;
  wsConnected: boolean;
  toggleSidebar: () => void;
  setSearchOpen: (open: boolean) => void;
  setCopilotOpen: (open: boolean) => void;
  setTerminalOpen: (open: boolean) => void;
  setCurrentProject: (id: string | null) => void;
  setWsConnected: (connected: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  searchOpen: false,
  copilotOpen: false,
  terminalOpen: false,
  currentProject: null,
  wsConnected: false,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSearchOpen: (open) => set({ searchOpen: open }),
  setCopilotOpen: (open) => set({ copilotOpen: open }),
  setTerminalOpen: (open) => set({ terminalOpen: open }),
  setCurrentProject: (id) => set({ currentProject: id }),
  setWsConnected: (c) => set({ wsConnected: c }),
}));
