import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { ReportPage } from './pages/ReportPage';
import { SettingsPage } from './pages/SettingsPage';
import { ToastContainer } from './components/ui/Toast';
import { useSettingsStore } from './utils/settingsStore';

const AnimatedRoutes = () => {
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('Research Chat');
  const accentColor = useSettingsStore(s => s.accentColor);
  const compactMode = useSettingsStore(s => s.compactMode);

  useEffect(() => {
    document.documentElement.style.setProperty('--brand-orange', accentColor);
  }, [accentColor]);

  useEffect(() => {
    if (compactMode) {
      document.documentElement.classList.add('compact');
    } else {
      document.documentElement.classList.remove('compact');
    }
  }, [compactMode]);

  return (
    <div key={location.pathname} className="animate-fade-in w-full h-full">
      <Routes location={location}>
        <Route path="/" element={
          <MainLayout activeTab={activeTab} setActiveTab={setActiveTab}>
            <Dashboard activeTab={activeTab} setActiveTab={setActiveTab} />
          </MainLayout>
        } />
        <Route path="/settings" element={
          <MainLayout activeTab={activeTab} setActiveTab={setActiveTab}>
            <SettingsPage />
          </MainLayout>
        } />
        <Route path="/report/:runId" element={<ReportPage />} />
      </Routes>
    </div>
  );
};

export const App = () => {
  return (
    <BrowserRouter>
      <ToastContainer />
      <AnimatedRoutes />
    </BrowserRouter>
  );
}

export default App;
