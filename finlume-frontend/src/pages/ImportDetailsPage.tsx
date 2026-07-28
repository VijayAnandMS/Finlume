import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';

export const ImportDetailsPage = () => {
    const { sessionId } = useParams();
    const navigate = useNavigate();
    const [details, setDetails] = useState(null);
    const [audits, setAudits] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAudits = async () => {
            try {
                const headers = { Authorization: `Bearer ${localStorage.getItem('token')}` };
                const sessionRes = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/import/history/${sessionId}`, { headers });
                const auditRes = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/import/history/${sessionId}/audit`, { headers });
                setDetails(sessionRes.data);
                setAudits(auditRes.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchAudits();
    }, [sessionId]);

    if (loading) return <div className="p-8 text-white">Extracting Native Audit Blocks...</div>;

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="min-h-screen bg-slate-950 p-8 pt-24 text-white">
            <div className="max-w-4xl mx-auto space-y-8">

                <header className="flex justify-between items-center bg-slate-900 border border-slate-800 p-6 rounded-2xl">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-100">Audit Details</h1>
                        <p className="text-slate-400 mt-2">File: {details.filename} - Status: {details.status}</p>
                    </div>
                    <button onClick={() => navigate('/import/history')} className="px-6 py-2 rounded-xl text-slate-300 hover:bg-slate-800 transition">Back to History</button>
                </header>

                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col items-center">
                        <span className="text-sm text-slate-400">Imported Hooks</span>
                        <span className="text-2xl font-bold text-emerald-400">{details.imported_count || '-'}</span>
                    </div>
                    <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col items-center">
                        <span className="text-sm text-slate-400">Duplicates Isolated</span>
                        <span className="text-2xl font-bold text-rose-400">{details.duplicates_found || '-'}</span>
                    </div>
                    <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col items-center">
                        <span className="text-sm text-slate-400">Total Bounds</span>
                        <span className="text-2xl font-bold text-blue-400">{details.total_records || '-'}</span>
                    </div>
                    <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col items-center">
                        <span className="text-sm text-slate-400">Duration (ms)</span>
                        <span className="text-2xl font-bold text-amber-400">{details.duration_ms || '-'}</span>
                    </div>
                </div>

                <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 overflow-hidden backdrop-blur-xl">
                    <h2 className="text-xl font-semibold mb-6">Execution Timeline</h2>
                    <div className="space-y-4">
                        {audits.map((audit, i) => (
                            <div key={audit.id} className="flex gap-4 items-start relative">
                                {i !== audits.length - 1 && <div className="absolute left-[11px] top-6 bottom-[-24px] w-px bg-slate-800" />}
                                <div className="w-6 h-6 rounded-full bg-blue-600/20 border border-blue-500/50 flex-shrink-0 mt-1 z-10" />
                                <div className="flex-1 bg-slate-950 p-4 rounded-xl border border-slate-800/50">
                                    <div className="flex justify-between">
                                        <span className="font-semibold text-blue-400">{audit.action}</span>
                                        <span className="text-xs text-slate-500">{new Date(audit.timestamp).toLocaleTimeString()}</span>
                                    </div>
                                    {audit.resource && <div className="text-sm text-slate-400 mt-1 font-mono">Res: {audit.resource}</div>}
                                    {audit.details && <div className="text-sm text-slate-300 mt-2 bg-slate-900 p-2 rounded-lg">{audit.details}</div>}
                                </div>
                            </div>
                        ))}
                        {audits.length === 0 && <span className="text-slate-500">No audit executions stored.</span>}
                    </div>
                </div>

            </div>
        </motion.div>
    );
};
