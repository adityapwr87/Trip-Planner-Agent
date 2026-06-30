import { Clock, Compass, Plane, X, Scale } from "lucide-react";
import { NavLink } from "react-router-dom";
import "./Sidebar.css";

function Sidebar({
  open,
  onClose,
}) {
  return (
    <>
      <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
        <div className="sidebar-header">
          <NavLink to="/home" className="sidebar-nav-button" onClick={onClose}>
            <Compass size={18} />
            Home
          </NavLink>
          <NavLink to="/plan/new" className="sidebar-nav-button" onClick={onClose}>
            <Plane size={18} />
            Plan a Trip
          </NavLink>
          <NavLink to="/compare" className="sidebar-nav-button" onClick={onClose}>
            <Scale size={18} />
            Compare Destinations
          </NavLink>
          <NavLink to="/trips" className="sidebar-nav-button" onClick={onClose}>
            <Clock size={18} />
            Past Trips
          </NavLink>
          <button className="icon-button mobile-only" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="sidebar-footer">Agentic trip planning workspace</div>
      </aside>
      <div className="mobile-backdrop" onClick={onClose} />
    </>
  );
}

export default Sidebar;
