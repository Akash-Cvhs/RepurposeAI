import { FlaskConical, LayoutDashboard, LibraryBig, Microscope, MoonStar, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import sidebarLogo from "../../assets/sidebar-logo.svg";

type Theme = "light" | "dark";

const THEME_STORAGE_KEY = "repurposeai-theme";

function getInitialTheme(): Theme {
  if (typeof window === "undefined") {
    return "light";
  }

  const saved = window.localStorage.getItem(THEME_STORAGE_KEY);
  if (saved === "light" || saved === "dark") {
    return saved;
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function Sidebar(): JSX.Element {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-brand">
          <img className="sidebar-logo-image" src={sidebarLogo} alt="REPURPOSEAI logo" />
          <div>
            <div>REPURPOSEAI</div>
            <small className="mono">Innovation Workbench</small>
          </div>
        </div>
        <button
          className="theme-toggle"
          type="button"
          onClick={() => setTheme((current) => (current === "light" ? "dark" : "light"))}
          aria-label={theme === "light" ? "Enable dark theme" : "Enable light theme"}
          title={theme === "light" ? "Switch to dark" : "Switch to light"}
        >
          {theme === "light" ? <MoonStar size={14} /> : <Sun size={14} />}
          <span>{theme === "light" ? "Dark" : "Light"}</span>
        </button>
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
