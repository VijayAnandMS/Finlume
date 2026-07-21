import { useNavigate } from 'react-router-dom';

export const LandingPage = () => {
    const navigate = useNavigate();

    return (
        <div className="bg-slate-950 min-h-screen text-slate-100 font-sans selection:bg-indigo-500/30">
            <header className="flex justify-between items-center p-6 lg:px-20 border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
                <div className="text-2xl font-black bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent transform hover:scale-105 transition cursor-pointer">
                    Finlume AI.
                </div>
                <nav className="hidden md:flex space-x-8 text-sm font-medium text-slate-400">
                    <a href="#features" className="hover:text-white transition">Features</a>
                    <a href="#architecture" className="hover:text-white transition">Architecture</a>
                    <a href="#pricing" className="hover:text-white transition">Pricing</a>
                    <a href="#faq" className="hover:text-white transition">FAQ</a>
                </nav>
                <div className="space-x-4">
                    <button onClick={() => navigate('/login')} className="text-sm font-medium hover:text-white transition">Login</button>
                    <button onClick={() => navigate('/login')} className="bg-white text-black px-6 py-2.5 rounded-full text-sm font-bold shadow-lg hover:shadow-white/20 transition-all hover:scale-105">
                        Get Started
                    </button>
                </div>
            </header>

            <main>
                {/* Hero Section */}
                <section className="pt-32 pb-20 px-6 lg:px-20 max-w-6xl mx-auto text-center">
                    <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-xs font-mono font-bold tracking-wider uppercase">
                        v1.0 Release Candidate Available
                    </div>
                    <h1 className="text-6xl md:text-8xl font-black mb-8 leading-tight tracking-tight">
                        The OS for your <br />
                        <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">Financial Future.</span>
                    </h1>
                    <p className="text-xl text-slate-400 mb-12 max-w-2xl mx-auto leading-relaxed">
                        Finlume unifies your transactions, goals, and deep AI intelligence into a single, comprehensive copilot natively extending Gemini and Anthropic reasoning.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
                        <button onClick={() => navigate('/login')} className="bg-white text-black px-8 py-4 rounded-full font-bold shadow-[0_0_40px_rgba(255,255,255,0.3)] hover:scale-105 transition-all text-lg w-full sm:w-auto">
                            Access the Sandbox
                        </button>
                        <button className="px-8 py-4 rounded-full font-bold text-slate-300 border border-slate-700 hover:bg-slate-800 transition-all text-lg w-full sm:w-auto flex items-center justify-center">
                            <span className="mr-2">▶</span> Watch Demo
                        </button>
                    </div>
                </section>

                {/* Feature Highlights */}
                <section id="features" className="py-24 px-6 lg:px-20 bg-slate-900 border-y border-slate-800">
                    <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-12">
                        <div className="space-y-4">
                            <div className="w-12 h-12 bg-blue-500/10 border border-blue-500/20 rounded-2xl flex items-center justify-center text-blue-400 text-xl">🧠</div>
                            <h3 className="text-xl font-bold">Autonomous Agents</h3>
                            <p className="text-sm text-slate-400 leading-relaxed">Multi-agent architecture automatically delegates your queries across Expense, Budget, and Advisor subsystems concurrently.</p>
                        </div>
                        <div className="space-y-4">
                            <div className="w-12 h-12 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-center justify-center text-emerald-400 text-xl">⚡</div>
                            <h3 className="text-xl font-bold">Persistent Memory</h3>
                            <p className="text-sm text-slate-400 leading-relaxed">Powered by ChromaDB. The AI remembers historic conversational context and financial goals eternally mapped in vector space.</p>
                        </div>
                        <div className="space-y-4">
                            <div className="w-12 h-12 bg-purple-500/10 border border-purple-500/20 rounded-2xl flex items-center justify-center text-purple-400 text-xl">🛡️</div>
                            <h3 className="text-xl font-bold">Enterprise Security</h3>
                            <p className="text-sm text-slate-400 leading-relaxed">Docker-wrapped, Postgres-backed, and natively secured with rotating JSON audit protocols and dynamic API rate limiting.</p>
                        </div>
                    </div>
                </section>

                {/* Architecture & Pricing */}
                <section id="pricing" className="py-24 px-6 lg:px-20 max-w-6xl mx-auto text-center">
                    <h2 className="text-4xl font-bold mb-16">Simple Pricing</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                        <div className="p-8 rounded-3xl border border-slate-800 bg-slate-900/50 hover:bg-slate-900 transition-colors">
                            <h3 className="text-2xl font-bold mb-2">Hobbyist</h3>
                            <p className="text-slate-400 text-sm mb-6">Perfect for individual portfolios.</p>
                            <p className="text-5xl font-black mb-8">₹0 <span className="text-lg text-slate-500 font-normal">/mo</span></p>
                            <ul className="space-y-4 text-sm text-slate-300 mb-8 border-t border-slate-800 pt-8 text-left">
                                <li>✓ Standard Analytics</li>
                                <li>✓ Manual Data Entry</li>
                                <li>✓ Local Summaries</li>
                            </ul>
                            <button onClick={() => navigate('/login')} className="w-full py-3 rounded-xl border border-slate-700 hover:bg-slate-800 transition">Get Started</button>
                        </div>
                        <div className="p-8 rounded-3xl border border-indigo-500 bg-slate-900/50 relative transform md:-translate-y-4 shadow-[0_0_40px_rgba(99,102,241,0.15)]">
                            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-indigo-500 text-white text-xs font-bold px-4 py-1 rounded-full">MOST POPULAR</div>
                            <h3 className="text-2xl font-bold mb-2">Pro Copilot</h3>
                            <p className="text-slate-400 text-sm mb-6">Full GPT-4 / Claude Integration.</p>
                            <p className="text-5xl font-black mb-8">₹499 <span className="text-lg text-slate-500 font-normal">/mo</span></p>
                            <ul className="space-y-4 text-sm text-slate-300 mb-8 border-t border-slate-800 pt-8 text-left">
                                <li>✓ ChromaDB Memory Store</li>
                                <li>✓ Multi-Agent Subsystem</li>
                                <li>✓ Financial Forecasting</li>
                                <li>✓ CSV/PDF Report Exports</li>
                            </ul>
                            <button onClick={() => navigate('/login')} className="w-full py-3 rounded-xl bg-white text-black font-bold hover:bg-slate-200 transition">Upgrade to Pro</button>
                        </div>
                    </div>
                </section>
            </main>

            <footer className="py-12 border-t border-slate-900 text-center text-slate-500 text-sm">
                <p>Copyright © 2026 Finlume AI. Designed with premium architecture.</p>
                <div className="mt-4 space-x-6">
                    <a href="#" className="hover:text-slate-300">Terms</a>
                    <a href="#" className="hover:text-slate-300">Privacy</a>
                    <a href="#" className="hover:text-slate-300">Security</a>
                </div>
            </footer>
        </div>
    );
};
