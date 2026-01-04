
import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  const location = useLocation();
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-4">
      <div className="container mx-auto flex justify-between items-center glass px-6 py-3 rounded-2xl">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-full border-2 border-yellow-400 flex items-center justify-center transition-transform group-hover:scale-110">
            <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
          </div>
          <span className="text-xl font-bold tracking-tighter">ORBIT<span className="text-yellow-400">VPN</span></span>
        </Link>
        
        <div className="hidden md:flex items-center gap-8 text-sm font-medium">
          <Link to="/" className="hover:text-yellow-400 transition-colors">Network</Link>
          <Link to="/" className="hover:text-yellow-400 transition-colors">Security</Link>
          <Link to="/" className="hover:text-yellow-400 transition-colors">Pricing</Link>
        </div>

        <div className="flex items-center gap-4">
          {!isAuthPage && (
            <>
              <Link to="/login" className="text-sm font-medium hover:text-yellow-400 transition-colors">Log In</Link>
              <Link to="/register" className="bg-yellow-400 text-black px-5 py-2 rounded-full text-sm font-bold hover:bg-yellow-300 transition-all active:scale-95">
                Join Now
              </Link>
            </>
          )}
          {isAuthPage && (
            <Link to="/" className="text-sm font-medium hover:text-yellow-400 transition-colors flex items-center gap-1">
              ← Back to Site
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
