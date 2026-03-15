import { create } from "zustand";

const useUIStore = create((set) => ({
  theme: "light",
  language: "en",
  voiceMuted: false,

  toggleTheme: () =>
    set((state) => ({
      theme: state.theme === "light" ? "dark" : "light",
    })),

  setLanguage: (lang) => set({ language: lang }),

  toggleVoiceMute: () =>
    set((state) => ({ voiceMuted: !state.voiceMuted })),
}));

export default useUIStore;