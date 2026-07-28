import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';

export const ImportWorkflowPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [sessionData, setSessionData] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPreview = async () => {
      try {
        const headers = { Authorization: `Bearer ${localStorage.getItem('token')}` };
        const sessionRes = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/import/${sessionId}`, { headers });
        const recordsRes = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/import/${sessionId}/preview`, { headers });
        setSessionData(sessionRes.data);
        setRecords(recordsRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchPreview();
  }, [sessionId]);

  const toggleExclude = async (recordId, currentStatus) => {
    const newStatus = currentStatus === 'STAGED' ? 'DISCARDED' : 'STAGED';
    setRecords(records.map(r => r.id === recordId ? { ...r, status: newStatus } : r));
    try {
      const headers = { Authorization: `Bearer ${localStorage.getItem('token')}` };
      await axios.patch(
        `${import.meta.env.VITE_API_BASE_URL}/api/import/${sessionId}/preview`, 
        { updates: { [recordId]: { status: newStatus } } }, 
        { headers }
      );
    } catch {}
  };

  const updateCategory = async (recordId, newCat) => {
    setRecords(records.map(r => r.id === recordId ? { ...r, ai_category_suggestion: newCat } : r));
    try {
      const headers = { Authorization: `Bearer ${localStorage.getItem('token')}` };
      await axios.patch(
        `${import.meta.env.VITE_API_BASE_URL}/api/import/${sessionId}/preview`, 
        { updates: { [recordId]: { category: newCat } } }, 
        { headers }
      );
    } catch {}
  };

  const confirmImport = async () => {
    try {
      const headers = { Authorization: `Bearer ${localStorage.getItem('token')}` };
      await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/import/${sessionId}/confirm`, {}, { headers });
      navigate('/dashboard');
    } catch (e) {
      alert("Failed to confirm");
    }
  };

  if (loading) return <div className="p-8 text-white">Loading Verification Bounds...</div>;

  const total = records.length;
  const skipped = records.filter(r => r.status === 'DISCARDED').length;
  const toImport = records.filter(r => r.status === 'STAGED').length;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="min-h-screen bg-slate-950 p-8 pt-24 text-white">
      <div className="max-w-6xl mx-auto space-y-8">
        
        <header className="flex justify-between items-center bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">Statement Preview</h1>
            <p className="text-slate-400 mt-2">Validate {total} Extractions | Importing {toImport} | Skipped {skipped}</p>
          </div>
          <div className="flex space-x-4">
            <button onClick={() => navigate('/transactions')} className="px-6 py-2 rounded-xl text-slate-300 hover:bg-slate-800 transition">Cancel</button>
            <button onClick={confirmImport} className="px-6 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 transition text-white shadow-lg shadow-blue-500/20 font-medium">Confirm Execution</button>
          </div>
        </header>

        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-xl">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-900 text-slate-400">
              <tr>
                <th className="p-4 font-medium">Status</th>
                <th className="p-4 font-medium">Date</th>
                <th className="p-4 font-medium">Description</th>
                <th className="p-4 font-medium">Amount</th>
                <th className="p-4 font-medium">AI Category</th>
                <th className="p-4 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {records.map(rec => {
                  const data = JSON.parse(rec.raw_data);
                  const isStaged = rec.status === 'STAGED';
                  return (
                    <tr key={rec.id} className={`transition ${isStaged ? 'hover:bg-slate-800/50' : 'opacity-40 hover:opacity-60 bg-slate-950'}`}>
                      <td className="p-4">
                        {rec.is_duplicate ? (
                           <span className="px-2 py-1 bg-rose-500/20 text-rose-400 rounded-lg text-xs font-semibold">DUPLICATE</span>
                        ) : (
                           <span className={`px-2 py-1 rounded-lg text-xs font-semibold ${isStaged ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-700 text-slate-300'}`}>{isStaged ? 'VALID' : 'SKIPPED'}</span>
                        )}
                      </td>
                      <td className="p-4 text-slate-300">{rec.parsed_date}</td>
                      <td className="p-4 font-medium text-slate-100 max-w-[200px] truncate">{rec.parsed_merchant}</td>
                      <td className={`p-4 font-semibold ${rec.parsed_amount > 0 ? 'text-emerald-400' : 'text-slate-100'}`}>${Math.abs(rec.parsed_amount).toFixed(2)}</td>
                      <td className="p-4 flex items-center gap-2">
                        <input type="text" value={rec.ai_category_suggestion || ''} onChange={(e) => updateCategory(rec.id, e.target.value)} className={`bg-transparent border ${isStaged ? 'border-slate-700 hover:border-slate-500 focus:border-blue-500' : 'border-transparent'} rounded-lg px-2 py-1 text-slate-300 outline-none w-32`} disabled={!isStaged} />
                        {data['category_confidence'] > 0 && <span className="text-xs text-blue-400">({Math.round(data['category_confidence']*100)}%)</span>}
                      </td>
                      <td className="p-4">
                        <button onClick={() => toggleExclude(rec.id, rec.status)} className={`px-3 py-1 rounded-lg text-xs font-medium transition ${isStaged ? 'bg-slate-800 hover:bg-slate-700 text-slate-300' : 'bg-blue-600 hover:bg-blue-500 text-white'}`}>
                          {isStaged ? 'Exclude' : 'Include'}
                        </button>
                      </td>
                    </tr>
                  )
              })}
            </tbody>
          </table>
          {records.length === 0 && <div className="p-8 text-center text-slate-500">No structured components detected inside payload matrix.</div>}
        </div>
      </div>
    </motion.div>
  );
};
