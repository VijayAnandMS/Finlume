import React, { useEffect, useState } from 'react';
import {
    TrendingUp, AlertTriangle, Sparkles, Loader2, DollarSign,
    Percent, PiggyBank, RefreshCw, Calendar, AlertCircle, Bookmark, ShieldAlert
} from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import api from '../lib/api';

import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, BarChart, Bar, Cell
} from 'recharts';

interface MonthlySummary {
    month: string;
    income: number;
    expense: number;
    net: number;
}

interface SpendByCategory {
    category: string;
    amount: number;
    percentage: number;
}

interface LargestExpense {
    id: string;
    transaction_date: string;
    category: string;
    amount: number;
    merchant: string;
}

interface RecurringMerchant {
    merchant: string;
    amount: number;
    frequency: string;
    count: number;
}

interface CashFlowTrend {
    date: string;
    balance: number;
}

interface MonthlyComparison {
    current_month_expense: number;
    previous_month_expense: number;
    difference_absolute: number;
    difference_percentage: number;
}

interface SpendingAnomaly {
    category: string;
    current_spending: number;
    trailing_average: number;
    increase_factor: number;
}

interface InsightsData {
    monthly_summaries: MonthlySummary[];
    spend_by_category: SpendByCategory[];
    largest_expenses: LargestExpense[];
    recurring_merchants: RecurringMerchant[];
    cash_flow_trend: CashFlowTrend[];
    savings_rate_percent: number;
    monthly_comparison: MonthlyComparison;
    spending_anomalies: SpendingAnomaly[];
    ai_generated_summary: string;
}

const COLORS = ['#818CF8', '#34D399', '#F472B6', '#FB7185', '#FBBF24', '#60A5FA', '#A78BFA'];

export const InsightsDashboard: React.FC = () => {
    const [data, setData] = useState<InsightsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchInsights = async () => {
        try {
            setLoading(true);
            const res = await api.get('/api/intelligence/insights_engine');
            setData(res.data);
            setError('');
        } catch (err: any) {
            setError('Failed to fetch finance statistics. Ensure backend server is running and authenticated.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchInsights();
    }, []);

    if (loading) {
        return (
            <div className="flex bg-slate-950 text-white min-h-screen">
                <Sidebar currentTab="Reports" />
                <main className="flex-1 flex flex-col items-center justify-center min-h-[60vh] text-indigo-400">
                    <Loader2 className="w-12 h-12 animate-spin mb-4" />
                    <p className="text-xl font-medium animate-pulse">Assembling Intelligence Dashboard...</p>
                </main>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="flex bg-slate-950 text-white min-h-screen">
                <Sidebar currentTab="Reports" />
                <main className="flex-1 p-8">
                    <div className="max-w-4xl mx-auto flex flex-col items-center justify-center min-h-[60vh] text-red-400 bg-red-950/20 p-8 rounded-2xl border border-red-500/20">
                        <AlertTriangle className="w-16 h-16 mb-4 text-red-500" />
                        <h2 className="text-2xl font-bold mb-2">Engine Signal Lost</h2>
                        <p className="mb-4 text-slate-400 text-center">{error}</p>
                        <button
                            onClick={fetchInsights}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-xl transition duration-200 flex items-center gap-2"
                        >
                            <RefreshCw className="w-4 h-4" /> Try Again
                        </button>
                    </div>
                </main>
            </div>
        );
    }

    const {
        monthly_summaries,
        spend_by_category,
        largest_expenses,
        recurring_merchants,
        cash_flow_trend,
        savings_rate_percent,
        monthly_comparison,
        spending_anomalies,
        ai_generated_summary
    } = data;

    // Estimate current monthly net values
    const currentMonthData = monthly_summaries[monthly_summaries.length - 1] || { income: 0, expense: 0, net: 0 };

    return (
        <div className="flex bg-slate-950 text-slate-100 min-h-screen font-sans">
            <Sidebar currentTab="Reports" />

            <main className="flex-1 p-6 md:p-8 overflow-y-auto max-h-screen custom-scrollbar">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 pb-6 border-b border-slate-900 gap-4">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight flex items-center gap-3 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                            <Sparkles className="w-8 h-8 text-indigo-500" />
                            Financial Insights
                        </h1>
                        <p className="text-slate-400 mt-2">
                            Advanced mathematical modeling of your historical earnings and expenditures.
                        </p>
                    </div>
                    <button
                        onClick={fetchInsights}
                        className="self-start md:self-center bg-slate-900 hover:bg-slate-800 border border-slate-800 p-2.5 rounded-xl transition text-slate-300"
                    >
                        <RefreshCw className="w-5 h-5" />
                    </button>
                </div>

                {/* Grid 1: KPI Stats Summary */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div className="bg-slate-900/60 border border-slate-900 p-6 rounded-2xl shadow-sm flex items-center justify-between">
                        <div>
                            <p className="text-slate-400 text-sm font-semibold tracking-wide uppercase">Monthly Earnings</p>
                            <p className="text-2xl font-black mt-1 text-white">₹{currentMonthData.income.toLocaleString()}</p>
                        </div>
                        <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl">
                            <DollarSign className="w-6 h-6" />
                        </div>
                    </div>

                    <div className="bg-slate-900/60 border border-slate-900 p-6 rounded-2xl shadow-sm flex items-center justify-between">
                        <div>
                            <p className="text-slate-400 text-sm font-semibold tracking-wide uppercase">Monthly Outgoings</p>
                            <p className="text-2xl font-black mt-1 text-white">₹{currentMonthData.expense.toLocaleString()}</p>
                        </div>
                        <div className="p-3 bg-rose-500/10 text-rose-400 rounded-xl">
                            <DollarSign className="w-6 h-6" />
                        </div>
                    </div>

                    <div className="bg-slate-900/60 border border-slate-900 p-6 rounded-2xl shadow-sm flex items-center justify-between">
                        <div>
                            <p className="text-slate-400 text-sm font-semibold tracking-wide uppercase">Savings Rate</p>
                            <p className="text-2xl font-black mt-1 text-white">{savings_rate_percent}%</p>
                        </div>
                        <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl">
                            <Percent className="w-6 h-6" />
                        </div>
                    </div>

                    <div className="bg-slate-900/60 border border-slate-900 p-6 rounded-2xl shadow-sm flex items-center justify-between">
                        <div>
                            <p className="text-slate-400 text-sm font-semibold tracking-wide uppercase">Monthly Delta change</p>
                            <p className={`text-2xl font-black mt-1 ${monthly_comparison.difference_percentage <= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {monthly_comparison.difference_percentage <= 0 ? '' : '+'}{monthly_comparison.difference_percentage.toFixed(1)}%
                            </p>
                        </div>
                        <div className="p-3 bg-cyan-500/10 text-cyan-400 rounded-xl">
                            <PiggyBank className="w-6 h-6" />
                        </div>
                    </div>
                </div>

                {/* Grid 2: Charts (Cash Flow Area Chart & Expenses Bar Chart) */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {/* Trend Chart */}
                    <div className="bg-slate-900/40 border border-slate-900/80 p-6 rounded-2xl">
                        <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-white">
                            <TrendingUp className="w-5 h-5 text-indigo-400" />
                            Cash Flow Trend (Last 30 Days)
                        </h3>
                        <div className="h-72 w-full">
                            {cash_flow_trend.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={cash_flow_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                        <XAxis dataKey="date" stroke="#64748b" tickFormatter={(v) => v.slice(5)} />
                                        <YAxis stroke="#64748b" />
                                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} />
                                        <Area type="monotone" dataKey="balance" stroke="#6366f1" strokeWidth={2.5} fillOpacity={1} fill="url(#colorBalance)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="flex h-full items-center justify-center text-slate-500">No balance trends populated yet.</div>
                            )}
                        </div>
                    </div>

                    {/* Spend by Category Chart */}
                    <div className="bg-slate-900/40 border border-slate-900/80 p-6 rounded-2xl">
                        <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-white">
                            <Bookmark className="w-5 h-5 text-purple-400" />
                            Spending Breakdown by Category (Current Month)
                        </h3>
                        <div className="h-72 w-full">
                            {spend_by_category.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={spend_by_category} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                        <XAxis dataKey="category" stroke="#64748b" />
                                        <YAxis stroke="#64748b" />
                                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} />
                                        <Bar dataKey="amount" radius={[8, 8, 0, 0]}>
                                            {spend_by_category.map((_, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="flex h-full items-center justify-center text-slate-500">No category transactions this month.</div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Grid 3: AI Recommendations Panel */}
                <div className="bg-gradient-to-r from-slate-900 to-indigo-950/20 border border-indigo-950 p-6 rounded-3xl mb-8 relative overflow-hidden">
                    <div className="absolute right-0 top-0 w-64 h-64 bg-indigo-500/5 blur-3xl rounded-full"></div>
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-indigo-300">
                        <Sparkles className="w-6 h-6" />
                        AI Financial Analyst Analysis
                    </h3>
                    <div className="whitespace-pre-line text-slate-300 antialiased leading-relaxed tracking-wide font-mono text-sm max-w-5xl">
                        {ai_generated_summary}
                    </div>
                </div>

                {/* Grid 4: Anomalies, Recurring Merchants & Outliers */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                    {/* Anomaly warnings */}
                    <div className="bg-slate-900/40 border border-slate-900/80 p-6 rounded-2xl lg:col-span-1">
                        <h4 className="font-bold text-white mb-4 flex items-center gap-2">
                            <ShieldAlert className="w-5 h-5 text-rose-400" />
                            Spending Anomalies
                        </h4>
                        <div className="space-y-4">
                            {spending_anomalies.length > 0 ? (
                                spending_anomalies.map((anom, idx) => (
                                    <div key={idx} className="bg-rose-950/20 border border-rose-900/30 p-4 rounded-xl">
                                        <p className="font-bold text-rose-400 capitalize">{anom.category} spike</p>
                                        <p className="text-xs text-slate-400 mt-1">
                                            Current: ₹{anom.current_spending.toLocaleString()} vs 3-mo Trailing Avg: ₹{anom.trailing_average.toLocaleString()}
                                        </p>
                                        <div className="inline-block mt-2 bg-rose-500/10 text-rose-400 px-2 py-0.5 rounded text-[10px] font-bold">
                                            {anom.increase_factor}x Increase
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-slate-500 text-sm flex items-center gap-2 py-4">
                                    <AlertCircle className="w-4 h-4 text-emerald-400" />
                                    No category spending anomalies detected this month.
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Recurring merchants */}
                    <div className="bg-slate-900/40 border border-slate-900/80 p-6 rounded-2xl lg:col-span-1">
                        <h4 className="font-bold text-white mb-4 flex items-center gap-2">
                            <Calendar className="w-5 h-5 text-amber-400" />
                            Recurring Merchants
                        </h4>
                        <div className="space-y-3">
                            {recurring_merchants.length > 0 ? (
                                recurring_merchants.map((rec, idx) => (
                                    <div key={idx} className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800 flex justify-between items-center">
                                        <div>
                                            <p className="font-semibold text-slate-200">{rec.merchant}</p>
                                            <p className="text-xs text-slate-400 mt-0.5 capitalize">{rec.frequency}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-bold text-white">₹{rec.amount}</p>
                                            <p className="text-[10px] text-slate-500">Hits: {rec.count}</p>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-slate-500 text-sm py-4">No regular charges found. Keep importing lists.</div>
                            )}
                        </div>
                    </div>

                    {/* Largest expenses */}
                    <div className="bg-slate-900/40 border border-slate-900/80 p-6 rounded-2xl lg:col-span-1">
                        <h4 className="font-bold text-white mb-4 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-indigo-400" />
                            Largest Expenses (Current Month)
                        </h4>
                        <div className="space-y-3">
                            {largest_expenses.length > 0 ? (
                                largest_expenses.map((exp, idx) => (
                                    <div key={idx} className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800 flex justify-between items-center">
                                        <div className="truncate max-w-[160px]">
                                            <p className="font-semibold text-slate-200 truncate">{exp.merchant}</p>
                                            <p className="text-xs text-slate-400 mt-0.5 truncate capitalize">{exp.category} • {exp.transaction_date}</p>
                                        </div>
                                        <p className="font-bold text-white flex-shrink-0">₹{exp.amount.toLocaleString()}</p>
                                    </div>
                                ))
                            ) : (
                                <div className="text-slate-500 text-sm py-4">No expenses recorded yet.</div>
                            )}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};
