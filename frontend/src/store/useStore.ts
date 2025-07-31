import { create } from 'zustand';

interface State {
  count: number;
  increase: () => void;
}

export const useStore = create<State>((set) => ({
  count: 0,
  increase: () => set((state) => ({ count: state.count + 1 })),
}));
