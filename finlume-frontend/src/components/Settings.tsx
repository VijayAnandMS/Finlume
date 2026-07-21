

export const Settings = () => {
    return (
        <div className="space-y-8 animate-fadeIn max-w-3xl" role="region" aria-label="Application Settings">
            <div>
                <h2 className="text-2xl font-bold">Settings</h2>
                <p className="text-slate-400 text-sm mt-1">Manage infrastructure bounds, tokens, and preferences.</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden divide-y divide-slate-800">

                {/* Profile */}
                <div className="p-6">
                    <h3 className="text-sm font-bold text-white mb-4">Profile Synchronization</h3>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label htmlFor="settings-name" className="block text-xs font-bold text-slate-400 mb-1">Display Name</label>
                            <input id="settings-name" type="text" className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none transition" defaultValue="User" />
                        </div>
                        <div>
                            <label htmlFor="settings-email" className="block text-xs font-bold text-slate-400 mb-1">Email Address</label>
                            <input id="settings-email" type="email" disabled className="w-full bg-slate-950/50 border border-slate-800 rounded-lg py-2 px-3 text-sm text-slate-500 cursor-not-allowed" value="demo@finlume.ai" />
                        </div>
                    </div>
                </div>

                {/* API Provisioning */}
                <div className="p-6">
                    <h3 className="text-sm font-bold text-white mb-4">AI Integration Keys <span className="ml-2 text-xxs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">Active</span></h3>
                    <p className="text-xs text-slate-400 mb-4">Your orchestration pipeline evaluates these inputs targeting robust deterministic endpoints.</p>
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="settings-gemini" className="block text-xs font-bold text-slate-400 mb-1">Google Gemini API Key</label>
                            <input id="settings-gemini" type="password" placeholder="••••••••••••••••" className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none transition" />
                        </div>
                        <div>
                            <label htmlFor="settings-anthropic" className="block text-xs font-bold text-slate-400 mb-1">Anthropic Claude API Key</label>
                            <input id="settings-anthropic" type="password" placeholder="••••••••••••••••" className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 px-3 text-sm text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none transition" />
                        </div>
                    </div>
                </div>

                <div className="p-6 flex justify-end">
                    <button className="bg-white text-black px-6 py-2.5 rounded-lg text-sm font-bold shadow hover:bg-slate-200 transition focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-slate-900">
                        Save Configuration
                    </button>
                </div>
            </div>
        </div>
    );
};
