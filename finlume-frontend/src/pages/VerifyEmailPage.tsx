import { useState, useRef, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../services/api';
import { ShieldCheck, Loader2, AlertCircle } from 'lucide-react';

export const VerifyEmailPage = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const email = searchParams.get('email') || '';

    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [resendCooldown, setResendCooldown] = useState(0);
    const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

    useEffect(() => {
        let timer: ReturnType<typeof setInterval>;
        if (resendCooldown > 0) {
            timer = setInterval(() => setResendCooldown(c => c - 1), 1000);
        }
        return () => clearInterval(timer);
    }, [resendCooldown]);

    const handleVerify = async (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        const code = otp.join('');
        if (code.length !== 6) return setError('Please complete the 6-digit code');
        setIsLoading(true);
        setError('');
        try {
            await api.verifyEmail(email, code);
            navigate('/login');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Verification failed');
            setIsLoading(false);
        }
    };

    const handleResend = async () => {
        if (resendCooldown > 0) return;
        try {
            await api.resendOTP(email);
            setResendCooldown(60);
            setError('A new OTP has been sent securely.');
        } catch (err) { }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>, index: number) => {
        const value = e.target.value;
        if (!/^[0-9]*$/.test(value)) return;

        const newOtp = [...otp];
        newOtp[index] = value;
        setOtp(newOtp);

        if (value && index < 5) {
            inputRefs.current[index + 1]?.focus();
        }

        // Auto-verify if completed
        if (value && index === 5 && newOtp.every(d => d !== '')) {
            // Give react state a tick to update
            setTimeout(() => {
                const code = newOtp.join('');
                if (code.length === 6) {
                    api.verifyEmail(email, code).then(() => navigate('/login')).catch(err => {
                        setError(err.response?.data?.detail || 'Verification failed');
                        setIsLoading(false);
                    });
                }
            }, 50);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
        if (e.key === 'Backspace' && !otp[index] && index > 0) {
            inputRefs.current[index - 1]?.focus();
        }
    };

    const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
        if (pastedData) {
            const newOtp = [...otp];
            for (let i = 0; i < pastedData.length; i++) {
                newOtp[i] = pastedData[i];
            }
            setOtp(newOtp);
            if (pastedData.length === 6) {
                // Auto trigger logic handled by length check
                if (inputRefs.current[5]) inputRefs.current[5]?.focus();
            } else {
                inputRefs.current[pastedData.length]?.focus();
            }
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 selection:bg-indigo-500/30">
            <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-10 shadow-2xl relative overflow-hidden flex flex-col items-center">
                <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>

                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-2xl font-black mb-6 shadow-[0_0_20px_rgba(99,102,241,0.5)] animate-pulse">
                    <ShieldCheck className="w-8 h-8" />
                </div>

                <h1 className="text-3xl font-bold text-white mb-2 text-center">Verify Identity</h1>
                <p className="text-slate-400 text-sm mb-8 text-center max-w-[280px]">
                    To comply with security mandates, enter the 6-digit OTP sent dynamically.<br />
                    <span className="text-indigo-400 font-bold block mt-2">{email}</span>
                </p>

                {error && (
                    <div className={`mb-8 px-4 py-3 w-full bg-slate-950 border rounded-xl flex items-center justify-center text-sm font-medium animate-fadeIn ${error.includes('sent') ? 'border-emerald-500/50 text-emerald-400' : 'border-amber-500/50 text-amber-500'}`}>
                        <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
                        {error}
                    </div>
                )}

                <form onSubmit={handleVerify} className="space-y-8 flex flex-col items-center w-full">
                    <div className="flex gap-2 sm:gap-3 justify-center w-full">
                        {otp.map((digit, index) => (
                            <input
                                key={index}
                                ref={(el) => { inputRefs.current[index] = el; }}
                                type="text"
                                maxLength={1}
                                value={digit}
                                onChange={(e) => handleChange(e, index)}
                                onKeyDown={(e) => handleKeyDown(e, index)}
                                onPaste={handlePaste}
                                className="w-12 h-14 sm:w-14 sm:h-16 bg-slate-950 border border-slate-800 rounded-xl text-center text-2xl text-white font-bold focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 outline-none transition-all shadow-inner"
                            />
                        ))}
                    </div>

                    <button type="submit" disabled={isLoading || otp.join('').length < 6} className="w-full bg-white text-black font-bold rounded-xl py-3.5 hover:bg-slate-200 transition-all shadow-[0_0_15px_rgba(255,255,255,0.15)] disabled:opacity-50 disabled:cursor-not-allowed">
                        {isLoading ? <span className="flex items-center justify-center"><Loader2 className="w-5 h-5 animate-spin mr-2" /> Verifying...</span> : 'Confirm Protocol'}
                    </button>
                </form>

                <div className="mt-8 text-center">
                    <button
                        onClick={handleResend}
                        disabled={resendCooldown > 0}
                        className="text-slate-500 hover:text-white transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {resendCooldown > 0 ? `Resend Code available in ${resendCooldown}s` : 'Resend Security Code'}
                    </button>
                </div>
            </div>
            {/* Dev Helper */}
            <div className="fixed bottom-4 font-mono text-xs text-slate-800">For mock testing, OTP is embedded in console logs locally.</div>
        </div>
    );
};
