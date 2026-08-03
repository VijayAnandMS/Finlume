import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
    Activity, TrendingUp, AlertTriangle, ShieldCheck,
    Zap, Goal as GoalIcon, Target, Loader2, Sparkles
} from 'lucide-react';
import api from '../lib/api';

const IntelligenceDashboard: React.FC = () => {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchIntelligence = async () => {
            try {
                const res = await api.get('/api/intelligence/dashboard');
                setData(res.data);
            } catch (err) {
                setError('Failed to securely establish neural link with Financial Engine.');
            } finally {
                setLoading(false);
            }
        };
        fetchIntelligence();
    }, []);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-primary-400">
                <Loader2 className="w-12 h-12 animate-spin mb-4" />
                <p className="text-xl font-medium animate-pulse">Initializing Financial Intelligence Core...</p>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-red-500 bg-red-50/5 p-8 rounded-2xl border border-red-500/20">
                <AlertTriangle className="w-16 h-16 mb-4" />
                <h2 className="text-2xl font-bold mb-2">Engine Desynchronization</h2>
                <p>{error}</p>
            </div>
        );
    }

    const { health, forecast, insights, recommendations, risk, goals } = data;

    return (
        <div className="space-y-6 max-w-7xl mx-auto pb-12">
            <header className="mb-8 flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-3">
                        <Sparkles className="w-8 h-8 text-primary-500" />
                        Intelligence Core
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-2 text-lg">
                        Real-time algorithmic mapping of your financial trajectory.
                    </p>
                </div>
            </header>

            {/* Top Row: Health & Risk */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-sm border border-gray-100 dark:border-gray-700/50 relative overflow-hidden"
                >
                    <div className="flex items-start justify-between z-10 relative">
                        <div>
                            <h2 className="text-gray-500 dark:text-gray-400 text-sm tracking-wider uppercase font-semibold mb-1">Health Grade</h2>
                            <p className="text-5xl font-black text-gray-900 dark:text-white">{health.score}</p>
                            <p className={`mt-2 font-medium ${health.score > 70 ? 'text-green-500' : 'text-orange-500'}`}>
                                {health.grade} Trajectory
                            </p>
                        </div>
                        <div className="p-4 bg-primary-50 dark:bg-primary-900/20 rounded-2xl text-primary-500">
                            <Activity className="w-8 h-8" />
                        </div>
                    </div>
                    <p className="mt-6 text-gray-600 dark:text-gray-300 relative z-10 leading-relaxed">
                        {health.summary}
                    </p>
                    <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-gradient-to-br from-primary-500/10 to-transparent rounded-full blur-3xl pointer-events-none" />
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-sm border border-gray-100 dark:border-gray-700/50"
                >
                    <div className="flex items-start justify-between">
                        <div>
                            <h2 className="text-gray-500 dark:text-gray-400 text-sm tracking-wider uppercase font-semibold mb-1">Structural Risk</h2>
                            <p className="text-5xl font-black text-gray-900 dark:text-white">{risk.risk_level}</p>
                            <span className="inline-flex mt-3 items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-500/20 dark:text-red-300">
                                {risk.risk_points} Exposure Points
                            </span>
                        </div>
                        <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-2xl text-red-500">
                            <ShieldCheck className="w-8 h-8" />
                        </div>
                    </div>
                    <ul className="mt-6 space-y-2">
                        {risk.explanations.map((exp: string, idx: number) => (
                            <li key={idx} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
                                <AlertTriangle className="w-4 h-4 text-orange-500 shrink-0 mt-0.5" />
                                {exp}
                            </li>
                        ))}
                    </ul>
                </motion.div>
            </div>

            {/* Middle Row: Forecast & Actionable Logic */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Forecast Sub-panel */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                    className="bg-gradient-to-br from-indigo-500 to-primary-600 rounded-3xl p-8 shadow-lg text-white lg:col-span-1"
                >
                    <div className="flex items-center gap-3 mb-6">
                        <TrendingUp className="w-6 h-6 text-indigo-200" />
                        <h2 className="text-xl font-bold">Velocity Forecast</h2>
                    </div>

                    <div className="space-y-6">
                        <div>
                            <p className="text-indigo-200 text-sm mb-1">7-Day Projection</p>
                            <div className="flex items-end gap-3">
                                <p className="text-3xl font-bold">${forecast['7_day'].forecast_balance}</p>
                                <span className="text-xs bg-white/20 px-2 py-1 rounded-full mb-1">{forecast['7_day'].confidence}% Conf.</span>
                            </div>
                        </div>
                        <div>
                            <p className="text-indigo-200 text-sm mb-1">End of Month Projection</p>
                            <div className="flex items-end gap-3">
                                <p className="text-3xl font-bold">${forecast.end_of_month.forecast_balance}</p>
                            </div>
                        </div>
                    </div>

                    <div className="mt-8 pt-6 border-t border-white/20">
                        <p className="text-sm font-medium">Daily Burn Rate: ${forecast.burn_rate_daily}</p>
                    </div>
                </motion.div>

                {/* Recommendations */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-sm border border-gray-100 dark:border-gray-700/50 lg:col-span-2"
                >
                    <div className="flex items-center gap-3 mb-6">
                        <Zap className="w-6 h-6 text-yellow-500" />
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Prescriptive Logic</h2>
                    </div>

                    <div className="grid gap-4">
                        {recommendations.recommendations.map((rec: string, idx: number) => (
                            <div key={idx} className="flex gap-4 p-4 rounded-2xl bg-gray-50 dark:bg-gray-700/30 border border-gray-100 dark:border-gray-600/50">
                                <div className="hidden sm:flex shrink-0 w-8 h-8 rounded-full bg-yellow-100 dark:bg-yellow-900/30 items-center justify-center text-yellow-600 dark:text-yellow-400 font-bold text-sm">
                                    {idx + 1}
                                </div>
                                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{rec}</p>
                            </div>
                        ))}
                    </div>
                </motion.div>
            </div>

            {/* Bottom Row: AI Insights & Goals */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Behavioral Insights */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-sm border border-gray-100 dark:border-gray-700/50"
                >
                    <div className="flex items-center gap-3 mb-6">
                        <Activity className="w-6 h-6 text-blue-500" />
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Behavioral Insights</h2>
                    </div>
                    <ul className="space-y-4">
                        {insights.insights.map((insight: string, idx: number) => (
                            <li key={idx} className="flex gap-3 text-gray-600 dark:text-gray-300">
                                <span className="bg-blue-500 w-1.5 h-1.5 rounded-full mt-2.5 shrink-0" />
                                {insight}
                            </li>
                        ))}
                    </ul>
                </motion.div>

                {/* Goal Matrices */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-sm border border-gray-100 dark:border-gray-700/50 space-y-6"
                >
                    <div className="flex items-center gap-3 mb-2">
                        <GoalIcon className="w-6 h-6 text-emerald-500" />
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Target Tracking Matrix</h2>
                    </div>
                    {goals.goal_intelligence.length === 0 ? (
                        <p className="text-gray-500">No active tracking patterns mapped globally.</p>
                    ) : (
                        goals.goal_intelligence.map((goal: any, idx: number) => (
                            <div key={idx} className="border-t border-gray-100 dark:border-gray-700/50 pt-4 first:border-0 first:pt-0">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                        <Target className="w-4 h-4 text-emerald-500" />
                                        {goal.name}
                                    </h3>
                                    <span className="text-xs font-bold px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg text-emerald-600 dark:text-emerald-400">
                                        {goal.probability_of_success_percent}% Probable
                                    </span>
                                </div>
                                <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2 mb-3">
                                    <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${goal.progress_percent}%` }}></div>
                                </div>
                                <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                                    "{goal.ai_recommendation}"
                                </p>
                            </div>
                        ))
                    )}
                </motion.div>
            </div>

        </div>
    );
};

export default IntelligenceDashboard;
