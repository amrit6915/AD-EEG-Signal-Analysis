import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Toast {
  id: string;
  message: string;
  severity: 'success' | 'error' | 'info' | 'warning';
}

interface UiState {
  sidebarOpen: boolean;
  darkMode: boolean;
  toasts: Toast[];
  globalLoading: boolean;
}

const initialState: UiState = {
  sidebarOpen: true,
  darkMode: false,
  toasts: [],
  globalLoading: false,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar(state) {
      state.sidebarOpen = !state.sidebarOpen;
    },
    toggleDarkMode(state) {
      state.darkMode = !state.darkMode;
    },
    addToast(state, action: PayloadAction<{ message: string; severity: Toast['severity'] }>) {
      const id = Date.now().toString();
      state.toasts.push({ id, ...action.payload });
    },
    removeToast(state, action: PayloadAction<string>) {
      state.toasts = state.toasts.filter((t) => t.id !== action.payload);
    },
    setGlobalLoading(state, action: PayloadAction<boolean>) {
      state.globalLoading = action.payload;
    },
  },
});

export const { toggleSidebar, toggleDarkMode, addToast, removeToast, setGlobalLoading } = uiSlice.actions;
export default uiSlice.reducer;
