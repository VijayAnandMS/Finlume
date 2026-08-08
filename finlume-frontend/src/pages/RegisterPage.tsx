import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Eye, EyeOff, CheckCircle2, XCircle, Loader2 } from 'lucide-react';

export const RegisterPage = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        full_name: '', username: '', email: '', phone_number: '', password: '', confirm_password: ''
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // UI Polish State
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const isMatch = formData.password && formData.confirm_password && formData.password === formData.confirm_password;
    const isMismatch = formData.confirm_password && formData.password !== formData.confirm_password;
    const isLengthValid = formData.password.length >= 8;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        if (!isMatch) {
            setError('Passwords do not match');
            return;
        }
        if (!isLengthValid) {
            setError('Password must be at least 8 characters');
            return;
        }

        setIsLoading(true);
        try {
            await api.register(formData.full_name, formData.username, formData.email, formData.password, formData.phone_number);
            navigate(`/verify-email?email=${encodeURIComponent(formData.email)}`);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Registration failed');
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 selection:bg-indigo-500/30">
            <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>

                <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-black mb-8 shadow-[0_0_20px_rgba(99,102,241,0.5)]">
                    F.
                </div>

                <h1 className="text-3xl font-bold text-white mb-2">Create an Account</h1>
                <p className="text-slate-400 text-sm mb-8">Join the Finlume Intelligence Network</p>

                {error && (
                    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-xl flex items-center text-red-400 text-sm font-medium animate-fadeIn">
                        <XCircle className="w-5 h-5 mr-2 flex-shrink-0" />
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <input type="text" placeholder="Full Name *" required value={formData.full_name} onChange={(e) => setFormData({ ...formData, full_name: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-medium" />

                    <div className="grid grid-cols-2 gap-4">
                        <input type="text" placeholder="Username *" required value={formData.username} onChange={(e) => setFormData({ ...formData, username: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-medium" />
                        <input type="tel" placeholder="Phone (Optional)" value={formData.phone_number} onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-medium" />
                    </div>

                    <input type="email" placeholder="Email Address *" required value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-medium" />

                    <div className="relative">
                        <input type={showPassword ? "text" : "password"} placeholder="Password *" required value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-4 pr-12 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-medium" />
                        <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 focus:outline-none transition-colors">
                            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                    </div>

                    <div className="h-1.5 w-full bg-slate-800 rounded-full mt-2 mb-4 overflow-hidden">
                        <div className={`h-full transition-all duration-300 ${formData.password.length > 10 ? 'bg-emerald-500 w-full' : formData.password.length > 7 ? 'bg-blue-500 w-2/3' : formData.password.length > 0 ? 'bg-amber-500 w-1/3' : 'w-0'}`}></div>
                    </div>

                    <div className="relative">
                        <input type={showConfirmPassword ? "text" : "password"} placeholder="Confirm Password *" required value={formData.confirm_password} onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })} className={`w-full bg-slate-950 border rounded-xl pl-4 pr-12 py-3 text-white placeholder-slate-500 focus:outline-none transition-all font-medium ${isMismatch ? 'border-red-500/50 focus:border-red-500 focus:ring-1 focus:ring-red-500' : isMatch ? 'border-emerald-500/50 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500' : 'border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}`} />
                        <button type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)} className="absolute right-10 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 focus:outline-none transition-colors">
                            {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                        {isMatch && <CheckCircle2 className="w-5 h-5 text-emerald-500 absolute right-3 top-1/2 -translate-y-1/2" />}
                        {isMismatch && <XCircle className="w-5 h-5 text-red-500 absolute right-3 top-1/2 -translate-y-1/2" />}
                    </div>

                    <button type="submit" disabled={isLoading || !isMatch || !isLengthValid} className="w-full flex items-center justify-center bg-white text-black font-bold rounded-xl py-3.5 hover:bg-slate-200 transition-all shadow-[0_0_20px_rgba(255,255,255,0.15)] disabled:opacity-50 disabled:cursor-not-allowed mt-6">
                        {isLoading ? <><Loader2 className="w-5 h-5 animate-spin mr-2" /> Creating Account...</> : 'Create Account'}
                    </button>
                </form>

                <div className="mt-8 text-center pt-6 border-t border-slate-800">
                    <Link to="/login" className="text-slate-400 text-sm font-medium hover:text-white transition-colors">Already registered? Log in</Link>
                </div>
            </div>
        </div>
    );
};
