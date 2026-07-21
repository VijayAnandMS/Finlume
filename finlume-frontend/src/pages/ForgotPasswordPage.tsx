import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Loader2, ArrowRight, ShieldAlert, CheckCircle2 } from 'lucide-react';

export const ForgotPasswordPage = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [msg, setMsg] = useState('');
    const [isSuccess, setIsSuccess] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            await api.forgotPassword(email);
            setIsSuccess(true);
            setMsg('Reset token dispatched securely. Directing pipeline...');
            setTimeout(() => navigate('/reset-password'), 2500);
        } catch {
            // For security, do not reveal if email exists unless authenticated
            setIsSuccess(true);
            setMsg('If verified, a reset marker was generated.');
            setTimeout(() => navigate('/reset-password'), 2500);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 selection:bg-indigo-500/30">
            <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-10 shadow-2xl relative overflow-hidden flex flex-col items-center text-center">
                <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>

                <div className="w-16 h-16 bg-gradient-to-br from-amber-500 to-orange-600 rounded-full flex items-center justify-center text-white text-2xl font-black mb-6 shadow-[0_0_20px_rgba(245,158,11,0.5)]">
                    <ShieldAlert className="w-8 h-8" />
                </div>

                <h1 className="text-3xl font-bold text-white mb-2">Account Recovery</h1>
                <p className="text-slate-400 text-sm mb-8 leading-relaxed">
                    Provide the email associated with your core node to restore cryptographic access.
                </p>

                {msg && (
                    <div className="mb-6 p-4 w-full bg-emerald-500/10 border border-emerald-500/50 rounded-xl flex items-center text-emerald-400 text-sm font-medium animate-fadeIn">
                        <CheckCircle2 className="w-5 h-5 mr-3 flex-shrink-0" />
                        <span className="text-left">{msg}</span>
                    </div>
                )}

                {!isSuccess && (
                    <form onSubmit={handleSubmit} className="w-full space-y-5">
                        <input
                            type="email"
                            placeholder="Email Address"
                            required
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3.5 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-medium transition-all"
                        />
                        <button
                            type="submit"
                            disabled={isLoading || !email}
                            className="w-full bg-white text-black font-bold rounded-xl py-3.5 hover:bg-slate-200 transition-all shadow-[0_0_15px_rgba(255,255,255,0.15)] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                        >
                            {isLoading ? <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Processing...</> : <><ArrowRight className="w-5 h-5 mr-2" /> Issue Override Token</>}
                        </button>
                    </form>
                )}

                <div className="mt-8 border-t border-slate-800 pt-6 w-full">
                    <Link to="/login" className="text-slate-400 font-bold hover:text-white transition-colors text-sm">
                        Abort Protocol (Back to Login)
                    </Link>
                </div>
            </div>
        </div>
    );
};
