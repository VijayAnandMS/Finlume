import React, { useState, useEffect } from 'react';
import { Sidebar } from '../components/Sidebar';
import api from '../lib/api';

export interface Transaction {
    id: string;
    transaction_date: string;
    category: string;
    transaction_type: string;
    amount: number;
    merchant?: string;
    description?: string;
}

export const TransactionsPage = () => {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState(true);

    // Filtering & Pagination State
    const [search, setSearch] = useState('');
    const [typeFilter, setTypeFilter] = useState('');
    const [page, setPage] = useState(0);
    const [limit] = useState(50);

    // Modal State
    const [showModal, setShowModal] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [form, setForm] = useState({
        transaction_date: new Date().toISOString().split('T')[0],
        category: 'Food',
        transaction_type: 'expense',
        amount: '',
        merchant: '',
        description: ''
    });

    const fetchTransactions = async () => {
        setLoading(true);
        try {
            const q = new URLSearchParams();
            if (search) q.append('search', search);
            if (typeFilter) q.append('type', typeFilter);
            q.append('skip', (page * limit).toString());
            q.append('limit', limit.toString());

            const res = await api.get(`/api/transactions/?${q.toString()}`);
            setTransactions(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTransactions();
    }, [search, typeFilter, page]);

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        const payload = {
            ...form,
            amount: parseFloat(form.amount) || 0
        };
        try {
            if (editingId) {
                await api.put(`/api/transactions/${editingId}`, payload);
            } else {
                await api.post('/api/transactions/', payload);
            }
            setShowModal(false);
            fetchTransactions();
        } catch (err) {
            console.error(err);
            alert('Error saving transaction.');
        }
    };

    const openAdd = () => {
        setEditingId(null);
        setForm({
            transaction_date: new Date().toISOString().split('T')[0],
            category: 'Food',
            transaction_type: 'expense',
            amount: '',
            merchant: '',
            description: ''
        });
        setShowModal(true);
    };

    const openEdit = (tx: Transaction) => {
        setEditingId(tx.id);
        setForm({
            transaction_date: tx.transaction_date,
            category: tx.category,
            transaction_type: tx.transaction_type,
            amount: tx.amount.toString(),
            merchant: tx.merchant || '',
            description: tx.description || ''
        });
        setShowModal(true);
    };

    const handleDelete = async (id: string) => {
        if (!window.confirm("Are you sure you want to delete this?")) return;
        try {
            await api.delete(`/api/transactions/${id}`);
            fetchTransactions();
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex font-inter text-slate-200">
            <Sidebar currentTab="Transactions" />
            <div className="flex-1 ml-20 md:ml-64 p-8 overflow-y-auto">
                <header className="mb-8 flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-extrabold text-white">
                            Transactions
                        </h1>
                        <p className="text-sm text-slate-400 mt-2">Manage, filter, and review cash flows</p>
                    </div>
                    <button onClick={openAdd} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-xl font-semibold shadow transition-colors">
                        + Record Transaction
                    </button>
                </header>

                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                    <div className="flex flex-col md:flex-row gap-4 mb-6">
                        <input
                            type="text"
                            placeholder="Search merchants, descriptions..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="px-4 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm flex-1"
                        />
                        <select
                            value={typeFilter}
                            onChange={(e) => setTypeFilter(e.target.value)}
                            className="px-4 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm"
                        >
                            <option value="">All Types</option>
                            <option value="income">Income</option>
                            <option value="expense">Expense</option>
                        </select>
                    </div>

                    {loading ? (
                        <div className="flex justify-center p-8 mt-10">
                            <div className="w-6 h-6 border-2 border-t-blue-500 rounded-full animate-spin"></div>
                        </div>
                    ) : transactions.length === 0 ? (
                        <div className="text-center p-8 text-slate-500 mt-10 border border-dashed border-slate-700 rounded-xl">
                            No transactions found. Try adjusting your filters or record a new one.
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="border-b border-slate-800 text-slate-400 text-xxs font-bold uppercase tracking-wider">
                                        <th className="py-3 px-4">Date</th>
                                        <th className="py-3 px-4">Category</th>
                                        <th className="py-3 px-4">Type</th>
                                        <th className="py-3 px-4">Merchant</th>
                                        <th className="py-3 px-4 text-right">Amount</th>
                                        <th className="py-3 px-4 text-center">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800/60 text-sm">
                                    {transactions.map((tx: Transaction) => (
                                        <tr key={tx.id} className="hover:bg-slate-950/20 transition-all text-sm">
                                            <td className="py-3 px-4 font-mono text-slate-400">{tx.transaction_date}</td>
                                            <td className="py-3 px-4 font-semibold text-white">{tx.category}</td>
                                            <td className="py-3 px-4">
                                                <span className={`px-2 py-0.5 rounded-full text-xxs font-semibold uppercase ${tx.transaction_type === 'income' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-800 text-slate-400'}`}>
                                                    {tx.transaction_type}
                                                </span>
                                            </td>
                                            <td className="py-3 px-4 text-slate-400 max-w-xs truncate">{tx.merchant || tx.description || '-'}</td>
                                            <td className={`py-3 px-4 text-right font-bold ${tx.transaction_type === 'income' ? 'text-emerald-400' : 'text-slate-200'}`}>
                                                {tx.transaction_type === 'income' ? '+' : '-'} ₹{tx.amount.toLocaleString()}
                                            </td>
                                            <td className="py-3 px-4 text-center">
                                                <button onClick={() => openEdit(tx)} className="text-blue-400 hover:underline mr-3 text-xs">Edit</button>
                                                <button onClick={() => handleDelete(tx.id)} className="text-red-400 hover:underline text-xs">Delete</button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            <div className="flex justify-between items-center mt-6 text-sm text-slate-400">
                                <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} className="hover:text-white disabled:opacity-50">← Previous</button>
                                <span>Page {page + 1}</span>
                                <button onClick={() => setPage(p => p + 1)} disabled={transactions.length < limit} className="hover:text-white disabled:opacity-50">Next →</button>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
                    <div className="bg-slate-900 border border-slate-700 w-full max-w-md rounded-2xl p-6 shadow-2xl relative animate-fadeIn">
                        <h3 className="text-xl font-bold text-white mb-4">{editingId ? 'Edit Transaction' : 'Record Transaction'}</h3>
                        <form onSubmit={handleSave} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-xs text-slate-400 mb-1 block">Type</label>
                                    <select value={form.transaction_type} onChange={e => setForm({ ...form, transaction_type: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-blue-500">
                                        <option value="expense">Expense</option>
                                        <option value="income">Income</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="text-xs text-slate-400 mb-1 block">Date</label>
                                    <input type="date" required value={form.transaction_date} onChange={e => setForm({ ...form, transaction_date: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-blue-500" />
                                </div>
                            </div>
                            <div>
                                <label className="text-xs text-slate-400 mb-1 block">Category</label>
                                <input type="text" required value={form.category} onChange={e => setForm({ ...form, category: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-blue-500" placeholder="e.g. Food, Salary..." />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-xs text-slate-400 mb-1 block">Amount (₹)</label>
                                    <input type="number" required min="0" step="0.01" value={form.amount} onChange={e => setForm({ ...form, amount: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-blue-500" placeholder="0.00" />
                                </div>
                                <div>
                                    <label className="text-xs text-slate-400 mb-1 block">Merchant</label>
                                    <input type="text" value={form.merchant} onChange={e => setForm({ ...form, merchant: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-blue-500" placeholder="Optional" />
                                </div>
                            </div>
                            <div>
                                <label className="text-xs text-slate-400 mb-1 block">Description</label>
                                <textarea rows={2} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-blue-500 resize-none" placeholder="Add some notes..."></textarea>
                            </div>
                            <div className="flex justify-end space-x-3 mt-6">
                                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-slate-400 hover:text-white transition-colors text-sm">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg shadow font-semibold text-sm transition-colors">{editingId ? 'Update' : 'Save'}</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};
