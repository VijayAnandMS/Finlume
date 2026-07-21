

export const Notifications = () => {
    const events = [
        { type: 'warning', title: 'Budget Threshold Reached', time: '1 hour ago', msg: 'You have exceeded 80% of your Food budget.' },
        { type: 'success', title: 'Goal Milestone', time: '5 hours ago', msg: 'You are now 50% towards your "Emergency Fund" goal!' },
        { type: 'info', title: 'Forecast Anomaly', time: '2 days ago', msg: 'AI detected a recurring ₹4,500 pending deduction.' }
    ];

    return (
        <div className="space-y-6 animate-fadeIn h-[72vh] overflow-y-auto pr-2" role="region" aria-label="Notification Center">
            <div className="flex justify-between items-end border-b border-slate-800 pb-4">
                <div>
                    <h2 className="text-2xl font-bold">Notifications</h2>
                    <p className="text-slate-400 text-sm mt-1">Review AI alerts and system updates.</p>
                </div>
                <button aria-label="Mark all alerts as read" className="text-xs font-bold text-indigo-400 hover:text-white transition">Mark All Read</button>
            </div>

            <div className="space-y-4">
                {events.map((evt, i) => (
                    <div key={i} tabIndex={0} className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex items-start gap-4 hover:border-slate-700 transition cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <div className={`w-3 h-3 mt-1.5 rounded-full ${evt.type === 'warning' ? 'bg-amber-400' : evt.type === 'success' ? 'bg-emerald-400' : 'bg-blue-400'}`}></div>
                        <div>
                            <div className="flex justify-between items-center w-full">
                                <h4 className="font-bold text-white text-sm">{evt.title}</h4>
                                <span className="text-xxs text-slate-500 font-mono ml-8">{evt.time}</span>
                            </div>
                            <p className="text-xs text-slate-400 mt-1">{evt.msg}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
