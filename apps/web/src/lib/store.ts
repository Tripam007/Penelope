import { create } from "zustand";
import { AuthUser, getStoredUser } from "./firebase";

export interface AlertToast {
  id: string;
  severity: "Low" | "Moderate" | "High" | "Very High";
  title: string;
  message: string;
  villageName?: string;
  timestamp: string;
}

interface PenelopeState {
  language: "en" | "hi";
  setLanguage: (lang: "en" | "hi") => void;

  currentUser: AuthUser | null;
  setCurrentUser: (user: AuthUser | null) => void;

  isAuthModalOpen: boolean;
  setAuthModalOpen: (open: boolean) => void;

  activeNavTab: string;
  setActiveNavTab: (tab: string) => void;

  selectedVillageId: string | null;
  setSelectedVillageId: (id: string | null) => void;

  selectedSensorCode: string | null;
  setSelectedSensorCode: (code: string | null) => void;

  isAuthorityModalOpen: boolean;
  setAuthorityModalOpen: (open: boolean) => void;

  isTransparencyModalOpen: boolean;
  setTransparencyModalOpen: (open: boolean) => void;

  isSensorPanelOpen: boolean;
  setSensorPanelOpen: (open: boolean) => void;

  activeAlert: AlertToast | null;
  setActiveAlert: (alert: AlertToast | null) => void;

  simulatedSurgeNotice: string | null;
  setSimulatedSurgeNotice: (notice: string | null) => void;
}

export const usePenelopeStore = create<PenelopeState>((set) => ({
  language: "en",
  setLanguage: (lang) => set({ language: lang }),

  currentUser: getStoredUser(),
  setCurrentUser: (user) => set({ currentUser: user }),

  isAuthModalOpen: false,
  setAuthModalOpen: (open) => set({ isAuthModalOpen: open }),

  activeNavTab: "home",
  setActiveNavTab: (tab) => set({ activeNavTab: tab }),

  selectedVillageId: null,
  setSelectedVillageId: (id) => set({ selectedVillageId: id }),

  selectedSensorCode: null,
  setSelectedSensorCode: (code) => set({ selectedSensorCode: code }),

  isAuthorityModalOpen: false,
  setAuthorityModalOpen: (open) => set({ isAuthorityModalOpen: open }),

  isTransparencyModalOpen: false,
  setTransparencyModalOpen: (open) => set({ isTransparencyModalOpen: open }),

  isSensorPanelOpen: false,
  setSensorPanelOpen: (open) => set({ isSensorPanelOpen: open }),

  activeAlert: null,
  setActiveAlert: (alert) => set({ activeAlert: alert }),

  simulatedSurgeNotice: null,
  setSimulatedSurgeNotice: (notice) => set({ simulatedSurgeNotice: notice }),
}));
