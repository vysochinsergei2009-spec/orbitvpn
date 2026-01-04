
import React, { useState } from 'react';
import { HashRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Home from './pages/Home';
import Auth from './pages/Auth';
import Navbar from './components/Navbar';

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-black text-white selection:bg-yellow-400 selection:text-black">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Auth initialMode="login" />} />
            <Route path="/register" element={<Auth initialMode="register" />} />
          </Routes>
        </main>
        
        <footer className="py-12 border-t border-white/10 mt-20">
          <div className="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-8">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full border-2 border-yellow-400 flex items-center justify-center">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
              </div>
              <span className="text-xl font-bold tracking-tighter">ORBIT<span className="text-yellow-400">VPN</span></span>
            </div>
            <div className="flex gap-8 text-sm text-gray-400">
              <a href="#" className="hover:text-yellow-400 transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-yellow-400 transition-colors">Terms of Service</a>
              <a href="#" className="hover:text-yellow-400 transition-colors">Contact</a>
            </div>
            <p className="text-sm text-gray-500">© 2024 OrbitVPN. All rights reserved.</p>
          </div>
        </footer>
      </div>
    </Router>
  );
};

export default App;
