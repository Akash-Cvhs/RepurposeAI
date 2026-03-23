import { FlaskConical, LayoutDashboard, LibraryBig, Microscope } from "lucide-react";
import { NavLink } from "react-router-dom";

function Sidebar(): JSX.Element {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="sidebar-mark" />
        <div>
          <div>MoleculeIQ</div>
          <small className="mono">Repurposing Studio</small>
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavLink className="nav-link" to="/">
          <LayoutDashboard size={15} style={{ marginRight: 8 }} /> Dashboard
        </NavLink>
        <NavLink className="nav-link" to="/archive">
          <LibraryBig size={15} style={{ marginRight: 8 }} /> Archives
        </NavLink>
        <NavLink className="nav-link" to="/report/latest">
          <Microscope size={15} style={{ marginRight: 8 }} /> Report Viewer
        </NavLink>
        <a className="nav-link" href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
          <FlaskConical size={15} style={{ marginRight: 8 }} /> FastAPI Docs
        </a>
      </nav>
    </aside>
  );
}

export default Sidebar;
