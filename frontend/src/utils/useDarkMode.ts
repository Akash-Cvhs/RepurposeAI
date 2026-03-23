import { useEffect } from 'react';
import { useSettingsStore } from './settingsStore';

export const useDarkMode = () => {
  const isDark = useSettingsStore((state) => state.isDark);
  const setIsDark = useSettingsStore((state) => state.setIsDark);

  useEffect(() => {
    const root = window.document.documentElement;
    if (isDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [isDark]);

  const toggleDark = () => {
    setIsDark(!isDark);
  };

  return { isDark, toggleDark };
};
