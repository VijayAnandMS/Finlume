import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Loader2, KeyRound, Eye, EyeOff, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

export const ResetPasswordPage = () => {
    const navigate = useNavigate();
    const [token, setToken] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [msg, setMsg] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);

    const [showPassword, setShowPassword] = useState(false);

    const isMatch = password && confirmPassword && password === confirmPassword;
    const isMismatch = confirmPassword && password !== confirmPassword;
    const isLengthValid = password.length >= 8;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!isMatch || !isLengthValid) return;

        setIsLoading(true);
        setError('');

        try {
            await api.resetPassword(token, password);
            setIsSuccess(true);
            setMsg('Password payload accepted. Routing to hook authentication.');
            setTimeout(() => navigate('/login'), 2500);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Handshake failed. Token expired or invalid.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 selection:bg-indigo-500/30">
            <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-10 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 left-0 w-40 h-40 bg-emerald-500/20 rounded-full blur-3xl -translate-y-1/2 -translate-x-1/2 pointer-events-none"></div>

                <div className="flex flex-col items-center text-center">
                    <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full flex items-center justify-center text-white mb-6 shadow-[0_0_20px_rgba(16,185,129,0.5)]">
                        <KeyRound className="w-8 h-8" />
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-2">Finalize Override</h1>
                    <p className="text-slate-400 text-sm mb-8 leading-relaxed max-w-[280px]">
                        Cryptographically seal your new access credentials mapped via UUID block.
                    </p>
                </div>

                {msg && (
                    <div className="mb-6 mx-auto p-4 bg-emerald-500/10 border border-emerald-500/50 rounded-xl flex items-center text-emerald-400 text-sm font-medium animate-fadeIn">
                        <CheckCircle2 className="w-5 h-5 mr-3 flex-shrink-0" />
                        <span className="text-left">{msg}</span>
                    </div>
                )}

                {error && (
                    <div className="mb-6 mx-auto p-4 bg-red-500/10 border border-red-500/50 rounded-xl flex items-center justify-center text-red-400 text-sm font-medium animate-fadeIn text-center">
                        <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
                        {error}
                    </div>
                )}

                {!isSuccess && (
                    <form onSubmit={handleSubmit} className="w-full space-y-5">
                        <input
                            type="text"
                            placeholder="Access Token (UUID)"
                            required
                            value={token}
                            onChange={e => setToken(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 font-mono text-sm transition-all shadow-inner"
                        />

                        <div className="relative">
                            <input
                                type={showPassword ? "text" : "password"}
                                placeholder="New Password"
                                required
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-4 pr-12 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 font-medium transition-all"
                            />
                            <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 focus:outline-none">
                                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                            </button>
                        </div>

                        <div className="h-1.5 w-full bg-slate-800 rounded-full my-2 overflow-hidden">
                            <div className={`h-full transition-all duration-300 ${password.length > 10 ? 'bg-emerald-500 w-full' : password.length > 7 ? 'bg-blue-500 w-2/3' : password.length > 0 ? 'bg-amber-500 w-1/3' : 'w-0'}`}></div>
                        </div>

                        <div className="relative">
                            <input
                                type={showPassword ? "text" : "password"}
                                placeholder="Confirm Password"
                                required
                                value={confirmPassword}
                                onChange={e => setConfirmPassword(e.target.value)}
                                className={`w-full bg-slate-950 border rounded-xl pl-4 pr-12 py-3 text-white placeholder-slate-500 focus:outline-none font-medium transition-all ${isMismatch ? 'border-red-500/50 focus:border-red-500 focus:ring-1 focus:ring-red-500' : isMatch ? 'border-emerald-500/50 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500' : 'border-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500'}`}
                            />
                            {isMatch && <CheckCircle2 className="w-5 h-5 text-emerald-500 absolute right-3 top-1/2 -translate-y-1/2" />}
                            {isMismatch && <XCircle className="w-5 h-5 text-red-500 absolute right-3 top-1/2 -translate-y-1/2" />}
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading || !token || !isMatch || !isLengthValid}
                            className="w-full flex items-center justify-center bg-white text-black font-bold rounded-xl py-3.5 mt-2 hover:bg-slate-200 transition-all shadow-[0_0_15px_rgba(255,255,255,0.15)] disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Decrypting...</> : 'Reset Password'}
                        </button>
                    </form>
                )}
            </div>
            <div className="fixed bottom-4 font-mono text-xs text-slate-800">For mock testing, tokens are outputted directly in backend logs.</div>
        </div>
    );
};
