import { create } from "zustand";

const useUIStore = create((set) => ({
  theme: "light",
  language: "en",

  toggleTheme: () =>
    set((state) => ({
      theme: state.theme === "light" ? "dark" : "light",
    })),

  setLanguage: (lang) => set({ language: lang }),
}));

export default useUIStore;