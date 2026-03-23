import { Navigate, Route, Routes } from "react-router-dom";
import MainLayout from "./components/layout/MainLayout.tsx";
import Dashboard from "./pages/Dashboard.tsx";
import ReportPage from "./pages/ReportPage.tsx";

function App(): JSX.Element {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/archive" element={<Dashboard defaultTab="archive" />} />
        <Route path="/report/:reportId?" element={<ReportPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
