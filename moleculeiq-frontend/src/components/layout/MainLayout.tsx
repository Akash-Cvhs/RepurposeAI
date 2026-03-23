import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";

function MainLayout(): JSX.Element {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-area">
        <Outlet />
      </main>
    </div>
  );
}

export default MainLayout;
