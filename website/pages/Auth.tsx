
import React, { useState } from 'react';
import { Mail, Lock, User, Eye, EyeOff, ArrowRight } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import GlassCard from '../components/GlassCard';
import { AuthMode } from '../types';

interface AuthProps {
  initialMode: AuthMode;
}

const Auth: React.FC<AuthProps> = ({ initialMode }) => {
  const [mode, setMode] = useState<AuthMode>(initialMode);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      navigate('/');
    }, 1500);
  };

  return (
    <div className="min-h-screen pt-32 pb-12 flex items-center justify-center px-6 relative overflow-hidden">
      {/* Background blobs */}
      <div className="absolute top-1/4 left-1/4 -z-10 w-96 h-96 bg-yellow-400/5 rounded-full blur-[100px]"></div>
      <div className="absolute bottom-1/4 right-1/4 -z-10 w-96 h-96 bg-white/5 rounded-full blur-[100px]"></div>

      <div className="w-full max-w-md">
        <GlassCard hoverEffect={false} className="border-white/5 shadow-2xl">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold mb-2">
              {mode === 'login' ? 'Welcome Back' : 'Join the Orbit'}
            </h2>
            <p className="text-gray-400 text-sm">
              {mode === 'login' 
                ? 'Enter your credentials to access your secure tunnel.' 
                : 'Create your account and start exploring securely.'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {mode === 'register' && (
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Full Name</label>
                <div className="relative group">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 group-focus-within:text-yellow-400 transition-colors" />
                  <input 
                    type="text" 
                    required
                    placeholder="John Doe"
                    className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-4 outline-none focus:border-yellow-400 focus:bg-white/10 transition-all text-sm"
                  />
                </div>
              </div>
            )}

            <div className="space-y-2">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Email Address</label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 group-focus-within:text-yellow-400 transition-colors" />
                <input 
                  type="email" 
                  required
                  placeholder="name@company.com"
                  className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-4 outline-none focus:border-yellow-400 focus:bg-white/10 transition-all text-sm"
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Password</label>
                {mode === 'login' && (
                  <button type="button" className="text-[10px] font-bold text-yellow-400 hover:text-yellow-300 uppercase tracking-widest">
                    Forgot?
                  </button>
                )}
              </div>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 group-focus-within:text-yellow-400 transition-colors" />
                <input 
                  type={showPassword ? "text" : "password"} 
                  required
                  placeholder="••••••••"
                  className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-12 outline-none focus:border-yellow-400 focus:bg-white/10 transition-all text-sm"
                />
                <button 
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button 
              disabled={loading}
              className="w-full bg-yellow-400 text-black py-4 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-yellow-300 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed group shadow-[0_0_20px_rgba(250,204,21,0.1)]"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-black/20 border-t-black rounded-full animate-spin"></div>
              ) : (
                <>
                  {mode === 'login' ? 'Launch Dashboard' : 'Create Orbit ID'}
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          <div className="mt-10 pt-8 border-t border-white/5 text-center">
            <p className="text-gray-500 text-sm">
              {mode === 'login' ? "Don't have an account?" : "Already have an account?"}
              <button 
                onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
                className="ml-2 text-yellow-400 font-bold hover:text-yellow-300 transition-colors"
              >
                {mode === 'login' ? 'Join Orbit' : 'Sign in'}
              </button>
            </p>
          </div>
        </GlassCard>
        
        <div className="mt-8 text-center text-[10px] text-gray-600 uppercase tracking-[0.2em]">
          Secured by OrbitX Quantum Cryptography
        </div>
      </div>
    </div>
  );
};

export default Auth;
