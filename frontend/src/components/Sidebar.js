import { useContext } from "react";
import { Clock, Compass, Plane, X, Scale, LogOut } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import "./Sidebar.css";

function Sidebar({
  open,
  onClose,
}) {
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

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

        <div className="sidebar-footer">
          <button className="sidebar-nav-button" onClick={handleLogout} style={{ width: '100%', background: 'transparent', border: 'none', textAlign: 'left', color: 'inherit', cursor: 'pointer' }}>
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </aside>
      <div className="mobile-backdrop" onClick={onClose} />
    </>
  );
}

export default Sidebar;
