import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';

export interface ImportHistory {
    id: string;
    created_at: string;
    filename: string;
    status: string;
    imported_count: number;
    duplicates_found: number;
}

export const ImportHistoryPage = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState<ImportHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const headers = { Authorization: `Bearer ${localStorage.getItem('token')}` };
        const res = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/import/history/list`, { headers });
        setHistory(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  if (loading) return <div className="p-8 text-white">Loading History Bounds...</div>;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="min-h-screen bg-slate-950 p-8 pt-24 text-white">
      <div className="max-w-6xl mx-auto space-y-8">
        
        <header className="flex justify-between items-center bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <div>
            <h1 className="text-3xl font-bold text-slate-100">Import History</h1>
            <p className="text-slate-400 mt-2">Tracking explicit chronological audit chains natively</p>
          </div>
        </header>

        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-xl">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-900 text-slate-400">
              <tr>
                <th className="p-4">Date</th>
                <th className="p-4">File Name</th>
                <th className="p-4">Status</th>
                <th className="p-4">Imported</th>
                <th className="p-4">Duplicates</th>
                <th className="p-4">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {history.map(item => (
                    <tr key={item.id} className="transition hover:bg-slate-800/50 bg-slate-950">
                      <td className="p-4 text-slate-300">{new Date(item.created_at).toLocaleDateString()}</td>
                      <td className="p-4 text-slate-300 font-medium">{item.filename}</td>
                      <td className="p-4">
                         <span className={`px-2 py-1 rounded-lg text-xs font-semibold ${item.status === 'COMPLETED' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-700 text-slate-300'}`}>{item.status}</span>
                      </td>
                      <td className="p-4 text-emerald-400 font-bold">{item.imported_count || '-'}</td>
                      <td className="p-4 text-rose-400">{item.duplicates_found}</td>
                      <td className="p-4">
                        <button onClick={() => navigate(`/import/history/${item.id}`)} className="px-3 py-1 bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 rounded-lg text-xs font-medium transition">
                          View Audits
                        </button>
                      </td>
                    </tr>
              ))}
            </tbody>
          </table>
          {history.length === 0 && <div className="p-8 text-center text-slate-500">No imported archives tracked over this account.</div>}
        </div>
      </div>
    </motion.div>
  );
};
