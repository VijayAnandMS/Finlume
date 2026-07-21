import { useState } from 'react';
import { api } from '../services/api';
import { Loader2, Settings, FileCheck } from 'lucide-react';

export const OnboardingWizard = ({ onComplete }: { onComplete: () => void }) => {
    const [step, setStep] = useState(1);
    const [isSaving, setIsSaving] = useState(false);
    const [formData, setFormData] = useState({
        income: 0,
        currency: 'USD',
        salary_frequency: 'Monthly',
        monthly_expenses: '{}',
        financial_goals: '[]',
        risk_level: 'Moderate',
        investment_experience: 'Intermediate',
        emergency_fund: 0,
        existing_investments: 0,
        loan_amount: 0
    });

    const steps = [
        { title: "Welcome to Finlume AI", desc: "Let's calibrate your autonomous financial operating system." },
        { title: "Income Analytics", desc: "Configure your primary pipeline metrics." },
        { title: "Expense Modeling", desc: "How much are your estimated overheads?" },
        { title: "Financial Trajectory", desc: "Select target zones." },
        { title: "Risk Profiling", desc: "Calibrate portfolio volatility parameters." },
        { title: "Balance Validation", desc: "Current savings and liabilities." },
        { title: "Initialize Core", desc: "Review telemetry and deploy AI routines." }
    ];

    const handleSubmit = async () => {
        setIsSaving(true);
        try {
            await api.updateProfile(formData);
            onComplete();
        } catch (e) {
            console.error("Profile sync failed", e);
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-700 shadow-2xl rounded-3xl max-w-lg w-full p-8 animate-fadeIn">
                <div className="flex items-center space-x-4 mb-2">
                    <div className="w-10 h-10 bg-indigo-500/20 rounded-xl flex items-center justify-center text-indigo-400 font-black">
                        {step}
                    </div>
                    <h3 className="text-xl font-bold text-white">{steps[step - 1].title}</h3>
                </div>
                <p className="text-slate-400 text-sm leading-relaxed mb-8 h-12 ml-14">
                    {steps[step - 1].desc}
                </p>

                {/* Content Frame */}
                <div className="h-64 overflow-y-auto pr-2 mb-8 space-y-4 text-sm font-medium">
                    {step === 1 && (
                        <div className="flex flex-col items-center justify-center h-full space-y-4 text-center">
                            <div className="w-20 h-20 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white shadow-[0_0_20px_rgba(99,102,241,0.5)]">
                                <Settings className="w-10 h-10 animate-spin-slow" />
                            </div>
                            <p className="text-slate-300 max-w-xs">We need exactly 3 minutes of context to ensure AI agents are rendering deterministic output paths uniquely tailored for your situation.</p>
                        </div>
                    )}

                    {step === 2 && (
                        <div className="space-y-4 pt-4">
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Estimated Monthly Income</label>
                                <input type="number" required value={formData.income} onChange={e => setFormData({ ...formData, income: Number(e.target.value) })} className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-white" />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Currency</label>
                                    <select value={formData.currency} onChange={e => setFormData({ ...formData, currency: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-white">
                                        <option>USD</option><option>EUR</option><option>GBP</option><option>INR</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">Frequency</label>
                                    <select value={formData.salary_frequency} onChange={e => setFormData({ ...formData, salary_frequency: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-white">
                                        <option>Monthly</option><option>Bi-Weekly</option><option>Weekly</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    )}

                    {step === 3 && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Approximate Fixed Overheads (Rent, Utilities, etc.)</label>
                                <input type="number" placeholder="Value mapping" className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-white" />
                                <span className="text-xs text-slate-500 mt-1 block">JSON Blob parsing is automatically simulated below this layer in Prod.</span>
                            </div>
                        </div>
                    )}

                    {step === 4 && (
                        <div className="space-y-3 pt-4">
                            {['Emergency Fund', 'Buy House', 'Buy Car', 'Vacation', 'Education', 'Retirement'].map(g => (
                                <label key={g} className="flex items-center space-x-3 p-3 rounded-xl border border-slate-800 bg-slate-950 hover:border-indigo-500 transition cursor-pointer">
                                    <input type="checkbox" className="rounded text-indigo-500 bg-slate-900 border-slate-700" />
                                    <span className="text-white">{g}</span>
                                </label>
                            ))}
                        </div>
                    )}

                    {step === 5 && (
                        <div className="space-y-6 pt-2">
                            <div>
                                <label className="block text-xs text-slate-400 mb-2">Risk Tolerance Vector</label>
                                <div className="grid grid-cols-3 gap-2">
                                    {['Conservative', 'Moderate', 'Aggressive'].map(r => (
                                        <button key={r} onClick={() => setFormData({ ...formData, risk_level: r })} className={`py-2 rounded-lg text-xs font-bold border transition ${formData.risk_level === r ? 'bg-indigo-500 text-white border-indigo-400' : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'}`}>{r}</button>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <label className="block text-xs text-slate-400 mb-2">Market Experience</label>
                                <div className="grid grid-cols-3 gap-2">
                                    {['Beginner', 'Intermediate', 'Advanced'].map(e => (
                                        <button key={e} onClick={() => setFormData({ ...formData, investment_experience: e })} className={`py-2 rounded-lg text-xs font-bold border transition ${formData.investment_experience === e ? 'bg-indigo-500 text-white border-indigo-400' : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'}`}>{e}</button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {step === 6 && (
                        <div className="space-y-4 pt-4">
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Current Liquid Savings</label>
                                <input type="number" required value={formData.emergency_fund} onChange={e => setFormData({ ...formData, emergency_fund: Number(e.target.value) })} className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-white" />
                            </div>
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Existing Investments (Approx)</label>
                                <input type="number" required value={formData.existing_investments} onChange={e => setFormData({ ...formData, existing_investments: Number(e.target.value) })} className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-white" />
                            </div>
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">Outstanding Loans</label>
                                <input type="number" required value={formData.loan_amount} onChange={e => setFormData({ ...formData, loan_amount: Number(e.target.value) })} className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-white" />
                            </div>
                        </div>
                    )}

                    {step === 7 && (
                        <div className="h-full flex flex-col justify-center items-center text-center space-y-4">
                            <div className="w-16 h-16 rounded-full border border-indigo-500/30 flex items-center justify-center bg-indigo-500/10">
                                <FileCheck className="w-8 h-8 text-indigo-400" />
                            </div>
                            <p className="text-white font-bold">Calibration Complete.</p>
                            <p className="text-slate-400 text-xs max-w-xs">Connecting variables to ChromaDB and locking telemetry loops. Click Initialize to deploy.</p>
                        </div>
                    )}
                </div>

                {/* Progress Dots */}
                <div className="flex justify-center space-x-2 mb-6">
                    {steps.map((_, i) => (
                        <div key={i} className={`h-1.5 rounded-full transition-all duration-300 ${step - 1 === i ? 'w-8 bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.8)]' : 'w-2 bg-slate-800'}`} />
                    ))}
                </div>

                <div className="flex space-x-4">
                    <button disabled={step === 1 || isSaving} onClick={() => setStep(s => Math.max(1, s - 1))} className="flex-1 py-3 px-4 rounded-xl border border-slate-700 text-slate-300 font-bold hover:bg-slate-800 transition-all disabled:opacity-50">
                        Previous Sequence
                    </button>
                    <button disabled={isSaving} onClick={() => step === steps.length ? handleSubmit() : setStep(s => s + 1)} className="flex-1 py-3 px-4 rounded-xl bg-white text-black font-bold hover:bg-slate-200 transition-all shadow-[0_0_15px_rgba(255,255,255,0.2)] flex items-center justify-center">
                        {isSaving ? <><Loader2 className="w-5 h-5 animate-spin mr-2" /> Compiling...</> : step === steps.length ? 'Initialize Platform' : 'Next Sequence'}
                    </button>
                </div>
            </div>
        </div>
    );
};
