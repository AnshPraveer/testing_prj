import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Home, PlusSquare, User, LogOut, Camera } from 'lucide-react';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/" className="navbar-brand">
          SocialApp
        </Link>
        
        <div className="navbar-nav">
          <Link to="/" className="navbar-link">
            <Home size={20} />
            <span>Home</span>
          </Link>
          
          <Link to="/create" className="navbar-link">
            <PlusSquare size={20} />
            <span>Create</span>
          </Link>
          
          <Link to="/stories" className="navbar-link">
            <Camera size={20} />
            <span>Stories</span>
          </Link>
          
          <Link to="/profile" className="navbar-link">
            <User size={20} />
            <span>Profile</span>
          </Link>
        </div>

        <div className="navbar-user">
          {user?.profile_pic ? (
            <img 
              src={user.profile_pic} 
              alt={user.username} 
              className="avatar avatar-sm"
            />
          ) : (
            <div className="avatar avatar-sm" style={{ backgroundColor: '#0095f6', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '12px' }}>
              {user?.username?.charAt(0).toUpperCase()}
            </div>
          )}
          <span>{user?.username}</span>
          <button onClick={handleLogout} className="navbar-link" style={{ border: 'none', background: 'none' }}>
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;