import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Eye, EyeOff, Loader2, AlertTriangle, AlertCircle } from 'lucide-react';

export const LoginPage = () => {
  const navigate = useNavigate();
  const [identity, setIdentity] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const [showPassword, setShowPassword] = useState(false);
  const [capsLock, setCapsLock] = useState(false);

  // Caps Lock UI listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.getModifierState('CapsLock')) {
        setCapsLock(true);
      } else {
        setCapsLock(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyDown);
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await api.customLogin(identity.trim(), password);
      localStorage.setItem('token', response.access_token);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 selection:bg-indigo-500/30">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-40 h-40 bg-indigo-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-40 h-40 bg-emerald-500/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2 pointer-events-none"></div>

        <div className="relative z-10 flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-black mb-4 shadow-[0_0_20px_rgba(99,102,241,0.5)]">
            F.
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-slate-400 text-sm text-center">Access your financial intelligence copilot.</p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl text-sm font-medium text-center bg-red-500/10 border border-red-500/50 text-red-400 block break-words animate-fadeIn flex flex-col items-center">
            <div className="flex items-center justify-center mb-1">
              <AlertCircle className="w-4 h-4 mr-2" />
              <span>{error}</span>
            </div>
            {error.toLowerCase().includes('verify') && (
              <Link to={`/verify-email?email=${encodeURIComponent(identity)}`} className="text-indigo-400 font-bold hover:text-indigo-300 mt-1">
                Check verification status
              </Link>
            )}
          </div>
        )}

        <form onSubmit={handleSubmit} className="relative z-10 space-y-5">
          <div>
            <input
              type="text"
              placeholder="Username or Email Address"
              required
              value={identity}
              onChange={(e) => setIdentity(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-medium"
            />
          </div>

          <div className="relative">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-4 pr-12 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-medium"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 focus:outline-none transition-colors"
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>

          {/* Caps Lock Indicator */}
          {capsLock && (
            <div className="flex items-center text-amber-500 text-xs font-semibold px-1 animate-pulse">
              <AlertTriangle className="w-3 h-3 mr-1" />
              Caps Lock is ON
            </div>
          )}

          <div className="flex justify-between items-center px-1">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input type="checkbox" className="rounded bg-slate-900 border-slate-700 text-indigo-500 focus:ring-indigo-500/50 w-4 h-4" />
              <span className="text-xs text-slate-400 font-medium hover:text-slate-300">Remember me</span>
            </label>
            <Link to="/forgot-password" className="text-xs text-indigo-400 font-bold hover:text-indigo-300 transition-colors">Forgot Password?</Link>
          </div>

          <button
            type="submit"
            disabled={isLoading || !identity || !password}
            className="w-full flex items-center justify-center bg-white text-black font-bold rounded-xl py-3.5 hover:bg-slate-200 transition-all shadow-[0_0_20px_rgba(255,255,255,0.1)] disabled:opacity-50 disabled:cursor-not-allowed mt-2"
          >
            {isLoading ? <><Loader2 className="w-5 h-5 animate-spin mr-2" /> Authenticating...</> : 'Sign In'}
          </button>
        </form>

        <div className="relative z-10 mt-8 text-center pt-6 border-t border-slate-800">
          <p className="text-slate-400 text-sm font-medium">
            New to Finlume? <Link to="/register" className="text-white font-bold hover:text-indigo-200 transition-colors ml-1">Create an account</Link>
          </p>
        </div>
      </div>

      <div className="mt-8 text-xs font-mono text-slate-600 tracking-widest uppercase">
        Enterprise SECURE &bull; AI OPERATING SYSTEM
      </div>
    </div>
  );
};
