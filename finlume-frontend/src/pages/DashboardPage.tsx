import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import api from '../lib/api';
import { api as authApi } from '../services/api';
import { OnboardingWizard } from '../components/OnboardingWizard';
import {
  Tooltip as ChartTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

interface Goal {
  id: number;
  name: string;
  target_amount: number;
  current_amount: number;
  deadline: string;
  monthly_target: number | null;
  priority: string;
}

interface Transaction {
  id: string;
  user_id: number;
  transaction_date: string;
  category: string;
  subcategory?: string;
  transaction_type: string;
  amount: number;
  currency: string;
  merchant?: string;
  payment_method?: string;
  description: string;
  notes?: string;
  tags?: string;
  receipt_image?: string;
  created_at: string;
  updated_at: string;
}

interface Summary {
  total_income: number;
  total_expense: number;
  net: number;
  top_categories: Array<{ category: string; amount: number }>;
  transactions: Array<Transaction>;
}

interface ChatMsg {
  sender: 'user' | 'ai';
  text: string;
  time: string;
}
const ExplainabilityWidget = ({ data }: { data: any }) => {
  if (!data?.timestamp) return null;
  return (
    <div className="mt-4 p-4 bg-slate-900 border border-slate-700/50 rounded-xl space-y-2">
      <div className="flex justify-between items-center border-b border-slate-800 pb-2">
        <h5 className="text-xs font-bold text-slate-300">Explainable AI</h5>
        <span className="text-xxs font-mono text-emerald-400 bg-emerald-900/20 px-2 py-0.5 rounded">Confidence: {data.confidence_score}%</span>
      </div>
      <p className="text-xxs text-slate-400 leading-relaxed"><strong className="text-slate-300">Reasoning:</strong> {data.reasoning_summary}</p>
      <p className="text-xxs text-slate-400 leading-relaxed"><strong className="text-slate-300">Factors:</strong> {data.key_financial_factors}</p>
      <p className="text-xxs text-slate-400 leading-relaxed"><strong className="text-slate-300">Assumptions:</strong> {data.assumptions}</p>
      <div className="flex justify-between items-center mt-2">
        <span className="text-xxs font-mono text-slate-500">Agents: {data.agents_used?.join(', ')}</span>
        <span className="text-xxs text-slate-500 italic mt-2 text-right">{new Date(data.timestamp).toLocaleString()}</span>
      </div>
    </div>
  );
};

export const DashboardPage = () => {
  const navigate = useNavigate();
  const [currentTab, setCurrentTab] = useState('Dashboard');
  const [username, setUsername] = useState('User');
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<Summary>({
    total_income: 0,
    total_expense: 0,
    net: 0,
    top_categories: [],
    transactions: []
  });

  // Modal / Form state for Transaction CRUD
  const [showTxModal, setShowTxModal] = useState(false);
  const [editingTxId, setEditingTxId] = useState<number | null>(null);
  const [txForm, setTxForm] = useState({
    transaction_date: new Date().toISOString().split('T')[0],
    category: 'Food',
    transaction_type: 'expense',
    amount: '',
    description: ''
  });

  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMsg[]>([
    { sender: 'ai', text: 'Hello! I am your Finlume financial coach. Ask me questions about your savings, spending, or budget targets.', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Budget configurations
  const [budgets, setBudgets] = useState<Record<string, number>>({
    Food: 5000,
    Rent: 20000,
    Entertainment: 3000,
    Shopping: 8000,
    Travel: 4000,
    Utilities: 6000
  });

  // Saving goals from server
  const [goals, setGoals] = useState<Goal[]>([]);
  // AI Goal Planner state
  const [plannerInput, setPlannerInput] = useState('');
  const [plannerLoading, setPlannerLoading] = useState(false);
  const [plannerData, setPlannerData] = useState<any>(null);

  const handlePlannerSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!plannerInput.trim()) return;
    setPlannerLoading(true);
    try {
      const res = await api.post('/api/agents/goal-planner', { message: plannerInput.trim() });
      setPlannerData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setPlannerLoading(false);
      setPlannerInput('');
    }
  };

  // Advisor state
  const [advisorInput, setAdvisorInput] = useState('');
  const [advisorLoading, setAdvisorLoading] = useState(false);
  const [advisorData, setAdvisorData] = useState<any>(null);

  const handleAdvisorSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!advisorInput.trim()) return;
    setAdvisorLoading(true);
    try {
      const res = await api.post('/api/agents/advisor', { question: advisorInput.trim() });
      setAdvisorData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setAdvisorLoading(false);
      setAdvisorInput('');
    }
  };

  // Investment state
  const [investInput, setInvestInput] = useState<any>({
    message: '',
    income: '',
    expenses: '',
    savings: '',
    risk: 'Medium',
    horizon: 'Medium Term',
    existing: ''
  });
  const [investLoading, setInvestLoading] = useState(false);
  const [investData, setInvestData] = useState<any>(null);

  const handleInvestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!investInput.message.trim()) return;
    setInvestLoading(true);
    try {
      const payload = {
        ...investInput,
        income: Number(investInput.income) || 0,
        expenses: Number(investInput.expenses) || 0,
        savings: Number(investInput.savings) || 0
      }
      const res = await api.post('/api/agents/investment', payload);
      setInvestData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setInvestLoading(false);
      setInvestInput((prev: any) => ({ ...prev, message: '' }));
    }
  };

  // Auth verification & initialization
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    api.get('/api/auth/me')
      .then(meRes => setUsername(meRes.data.full_name || meRes.data.username))
      .catch((err) => {
        console.error(err);
        localStorage.removeItem('token');
        navigate('/login');
      });

    fetchData();
  }, [navigate]);

  useEffect(() => {
    if (currentTab === 'AI Chat') {
      chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages, currentTab]);

  const fetchData = async () => {
    try {
      const pRes = await authApi.getProfile();
      if (pRes.status === "empty") {
        setShowOnboarding(true);
      }

      const summaryRes = await api.get('/api/summary/');
      const sumData = summaryRes.data;

      // Hydrate with profile baseline if transactions are zero
      if (sumData.total_income === 0 && pRes.income) {
        sumData.total_income = pRes.income;
        sumData.net = sumData.total_income - sumData.total_expense;
      }
      setSummary(sumData);

      const txRes = await api.get('/api/transactions/');
      setTransactions(txRes.data);

      const goalsRes = await api.get('/api/goals/');
      setGoals(goalsRes.data);
    } catch (err) {
      console.error('Error fetching data:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  // Transaction CRUD Actions
  const handleOpenAddModal = () => {
    setEditingTxId(null);
    setTxForm({
      date: new Date().toISOString().split('T')[0],
      category: 'Food',
      type: 'expense',
      amount: '',
      description: ''
    });
    setShowTxModal(true);
  };

  const handleOpenEditModal = (tx: Transaction) => {
    setEditingTxId(tx.id as any);
    setTxForm({
      transaction_date: tx.transaction_date,
      category: tx.category,
      transaction_type: tx.transaction_type,
      amount: tx.amount.toString(),
      description: tx.description || ''
    });
    setShowTxModal(true);
  };

  const handleDeleteTx = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) return;
    try {
      await api.delete(`/api/transactions/${id}`);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSaveTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      transaction_date: txForm.transaction_date,
      category: txForm.category,
      transaction_type: txForm.transaction_type,
      amount: parseFloat(txForm.amount) || 0,
      description: txForm.description
    };

    try {
      if (editingTxId) {
        await api.put(`/api/transactions/${editingTxId}`, payload);
      } else {
        await api.post('/api/transactions/', payload);
      }
      setShowTxModal(false);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  // Chat Actions
  const handleSendChatMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userText = chatInput.trim();
    setChatInput('');
    setChatMessages(prev => [...prev, {
      sender: 'user',
      text: userText,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }]);
    setChatLoading(true);

    try {
      const chatRes = await api.post('/api/chat/', { message: userText });
      setChatMessages(prev => [...prev, {
        sender: 'ai',
        text: chatRes.data.reply,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } catch (err) {
      console.error(err);
      setChatMessages(prev => [...prev, {
        sender: 'ai',
        text: 'Sorry, I had trouble contacting my cognitive module. Please make sure the backend is active.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  // Render Helpers
  const renderDashboardOverview = () => {
    const pieData = summary.top_categories.map(c => ({
      name: c.category,
      value: c.amount
    }));

    const COLORS = ['#3b82f6', '#6366f1', '#a855f7', '#ec4899', '#f43f5e', '#10b981'];

    return (
      <div className="space-y-8 animate-fadeIn">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl shadow-xl flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Income</p>
              <h3 className="text-3xl font-extrabold text-white mt-2">₹{summary.total_income.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</h3>
            </div>
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 text-xl">
              📥
            </div>
          </div>
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl shadow-xl flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Expenses</p>
              <h3 className="text-3xl font-extrabold text-white mt-2">₹{summary.total_expense.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</h3>
            </div>
            <div className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 text-xl">
              📤
            </div>
          </div>
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl shadow-xl flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Net Surplus</p>
              <h3 className={`text-3xl font-extrabold mt-2 ${summary.net >= 0 ? 'text-blue-400' : 'text-amber-500'}`}>
                ₹{summary.net.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </h3>
            </div>
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl border ${summary.net >= 0
              ? 'bg-blue-500/10 border-blue-500/20 text-blue-400'
              : 'bg-amber-500/10 border-amber-500/20 text-amber-500'
              }`}>
              ⚖️
            </div>
          </div>
        </div>

        {/* Charts & Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Spending Distribution Chart */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
            <h4 className="text-base font-bold text-white mb-4">Spending by Category</h4>
            {pieData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieData.map((_entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <ChartTooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '12px' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Legend verticalAlign="bottom" height={36} formatter={(value) => <span className="text-slate-300 text-xs">{value}</span>} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-slate-500 text-xs">
                <span>No expense data available.</span>
                <button onClick={handleOpenAddModal} className="mt-2 text-blue-400 hover:underline">Add transaction</button>
              </div>
            )}
          </div>

          {/* Recent Activity List */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-base font-bold text-white">Recent Transactions</h4>
              <button
                onClick={() => setCurrentTab('Transactions')}
                className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
              >
                View All
              </button>
            </div>

            <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
              {summary.transactions && summary.transactions.length > 0 ? (
                summary.transactions.map((tx) => (
                  <div key={tx.id} className="flex justify-between items-center p-3 rounded-xl bg-slate-950/60 border border-slate-800/40">
                    <div className="flex items-center space-x-3">
                      <span className="text-lg">
                        {tx.transaction_type === 'income' ? '📥' : '📤'}
                      </span>
                      <div>
                        <p className="text-sm font-semibold text-white">{tx.category}</p>
                        <p className="text-xxs text-slate-500">{tx.transaction_date} {tx.merchant && `• ${tx.merchant}`}</p>
                      </div>
                    </div>
                    <span className={`text-sm font-bold ${tx.transaction_type === 'income' ? 'text-emerald-400' : 'text-slate-300'}`}>
                      {tx.transaction_type === 'income' ? '+' : '-'} ₹{tx.amount.toLocaleString('en-IN')}
                    </span>
                  </div>
                ))
              ) : (
                <div className="flex items-center justify-center h-48 text-slate-500 text-xs">
                  No recent transactions.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderTransactionsTab = () => {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl animate-fadeIn">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
          <div>
            <h3 className="text-lg font-bold text-white">Transaction Logs</h3>
            <p className="text-xs text-slate-400">View, search, edit, and record your cashflows</p>
          </div>
          <button
            onClick={handleOpenAddModal}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-xl transition-all shadow"
          >
            <span>➕</span>
            <span>Record Transaction</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-xxs font-bold uppercase tracking-wider">
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Description</th>
                <th className="py-3 px-4 text-right">Amount</th>
                <th className="py-3 px-4 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-sm">
              {transactions.length > 0 ? (
                transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-950/20 transition-all text-xs">
                    <td className="py-3 px-4 font-mono text-slate-400">{tx.transaction_date}</td>
                    <td className="py-3 px-4 font-semibold text-white">{tx.category}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-xxs font-semibold uppercase ${tx.transaction_type === 'income'
                        ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
                        : 'bg-slate-800 border border-slate-700/80 text-slate-400'
                        }`}>
                        {tx.transaction_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400 italic max-w-xs truncate">{tx.merchant || tx.description || '-'}</td>
                    <td className={`py-3 px-4 text-right font-bold ${tx.transaction_type === 'income' ? 'text-emerald-400' : 'text-slate-200'}`}>
                      {tx.transaction_type === 'income' ? '+' : '-'} ₹{tx.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <div className="flex justify-center space-x-2">
                        <button
                          onClick={() => handleOpenEditModal(tx)}
                          className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-blue-400 transition-colors"
                          title="Edit"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => handleDeleteTx(tx.id)}
                          className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-red-400 transition-colors"
                          title="Delete"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500 text-xs">
                    No transactions registered. Click 'Record Transaction' to add one.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderAIChatTab = () => {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl h-[70vh] flex flex-col justify-between overflow-hidden animate-fadeIn">
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/20 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-xl">🤖</span>
            <div>
              <h3 className="text-sm font-bold text-white">Finlume AI Coach</h3>
              <p className="text-xxs text-emerald-400">Online • Ready to advise</p>
            </div>
          </div>
          <span className="text-xxs text-slate-500">Powered by Claude</span>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-950/30">
          {chatMessages.map((msg, index) => (
            <div
              key={index}
              className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-md p-3.5 rounded-2xl text-xs leading-relaxed shadow ${msg.sender === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-none'
                  : 'bg-slate-800 text-slate-200 rounded-tl-none border border-slate-700/50'
                  }`}
                style={{ whiteSpace: 'pre-wrap' }}
              >
                {msg.text}
              </div>
              <span className="text-xxs text-slate-500 mt-1 px-1">{msg.time}</span>
            </div>
          ))}
          {chatLoading && (
            <div className="flex flex-col items-start animate-pulse">
              <div className="bg-slate-800 border border-slate-700/50 text-slate-400 max-w-md p-3.5 rounded-2xl rounded-tl-none text-xs flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce"></span>
                <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce delay-100"></span>
                <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce delay-200"></span>
              </div>
            </div>
          )}
          <div ref={chatBottomRef} />
        </div>

        <form onSubmit={handleSendChatMessage} className="p-4 border-t border-slate-800 bg-slate-950/40 flex items-center space-x-2">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            disabled={chatLoading}
            placeholder="Ask about savings rules, overspending limit warnings, or summaries..."
            className="flex-1 px-4 py-2.5 bg-slate-950 border border-slate-800 text-white rounded-xl text-xs placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={chatLoading || !chatInput.trim()}
            className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow disabled:opacity-50 transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    );
  };

  const renderBudgetTab = () => {
    // Aggregate actual expense amounts
    const expensesByCategory: Record<string, number> = {};
    transactions.forEach(t => {
      if (t.transaction_type === 'expense') {
        expensesByCategory[t.category] = (expensesByCategory[t.category] || 0) + t.amount;
      }
    });

    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl animate-fadeIn space-y-6">
        <div>
          <h3 className="text-lg font-bold text-white">Category Budgets</h3>
          <p className="text-xs text-slate-400">Set limits and track spending limits across active categories</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(budgets).map(([cat, limit]) => {
            const spent = expensesByCategory[cat] || 0;
            const pct = limit > 0 ? (spent / limit) * 100 : 0;
            const isWarn = pct >= 90;
            const isNear = pct >= 75 && pct < 90;

            return (
              <div key={cat} className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-white">{cat}</span>
                  <span className="text-slate-400">
                    ₹{spent.toLocaleString('en-IN')} / <span className="text-slate-500">₹{limit.toLocaleString('en-IN')}</span>
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${isWarn
                      ? 'bg-rose-500'
                      : isNear
                        ? 'bg-amber-500'
                        : 'bg-blue-500'
                      }`}
                    style={{ width: `${Math.min(pct, 100)}%` }}
                  />
                </div>
                <div className="flex justify-between items-center text-xxs">
                  <span className={isWarn ? 'text-rose-400 font-bold' : isNear ? 'text-amber-400' : 'text-slate-500'}>
                    {pct.toFixed(0)}% utilized
                  </span>
                  <button
                    onClick={() => {
                      const newLimit = window.prompt(`Set new budget limit for ${cat}:`, limit.toString());
                      if (newLimit !== null) {
                        const parsed = parseFloat(newLimit) || 0;
                        setBudgets(prev => ({ ...prev, [cat]: parsed }));
                      }
                    }}
                    className="text-blue-400 hover:underline"
                  >
                    Adjust Limit
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderGoalsTab = () => {
    return (
      <div className="space-y-6 animate-fadeIn">
        {/* CRUD Section */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-bold text-white">Savings Goals</h3>
              <p className="text-xs text-slate-400">Manage and track your financial milestones</p>
            </div>
            <button
              onClick={async () => {
                const name = window.prompt('Enter goal name:');
                if (!name) return;
                const target = parseFloat(window.prompt('Enter target amount (₹):') || '0');
                if (target <= 0) return;
                const date = window.prompt('Enter target date (YYYY-MM-DD):', '2027-12-31');
                try {
                  await api.post('/api/goals/', { name, target_amount: target, current_amount: 0, deadline: date, status: 'active', priority: 'medium' });
                  fetchData();
                } catch (err) { console.error(err); }
              }}
              className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow transition-colors"
            >
              Add Goal
            </button>
          </div>

          <div className="space-y-4">
            {goals.map((g) => {
              const pct = g.target_amount > 0 ? (g.current_amount / g.target_amount) * 100 : 0;
              return (
                <div key={g.id} className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="text-sm font-semibold text-white">{g.name} <span className="text-xxs ml-2 text-blue-400 bg-blue-900/30 px-2 py-0.5 rounded-full">{g.priority}</span></h4>
                      <p className="text-xxs text-slate-500">Target Date: {g.deadline || 'N/A'}</p>
                    </div>
                    <span className="text-xs font-bold text-white">
                      ₹{g.current_amount.toLocaleString()} / <span className="text-slate-500">₹{g.target_amount.toLocaleString()}</span>
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500 rounded-full transition-all duration-300" style={{ width: `${Math.min(pct, 100)}%` }} />
                  </div>
                  <div className="flex justify-between items-center text-xxs">
                    <span className="text-slate-400 font-semibold">{pct.toFixed(0)}% Saved</span>
                    <div className="space-x-2">
                      <button
                        onClick={async () => {
                          const amt = parseFloat(window.prompt('Add amount saved (₹):') || '0');
                          if (amt > 0) {
                            try { await api.put(`/api/goals/${g.id}`, { ...g, current_amount: g.current_amount + amt }); fetchData(); } catch (err) { console.error(err); }
                          }
                        }}
                        className="text-emerald-400 hover:underline"
                      >
                        Add Savings
                      </button>
                      <button
                        onClick={async () => {
                          if (window.confirm('Delete goal?')) {
                            try { await api.delete(`/api/goals/${g.id}`); fetchData(); } catch (err) { console.error(err); }
                          }
                        }}
                        className="text-red-400 hover:underline"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
            {goals.length === 0 && <p className="text-slate-500 text-xs text-center py-4">No goals configured yet.</p>}
          </div>
        </div>

        {/* AI Goal Planner Section */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <div className="flex items-center space-x-3 mb-4">
            <span className="text-xl">🎯</span>
            <div>
              <h3 className="text-sm font-bold text-white">AI Goal Planner</h3>
              <p className="text-xxs text-emerald-400">Strategize your savings with AI Coach</p>
            </div>
          </div>

          {plannerData && !plannerLoading && (
            <div className="p-4 bg-gradient-to-br from-indigo-900/30 to-slate-900 border border-indigo-500/30 rounded-xl mb-6">
              <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">{plannerData.plan}</p>
              <ExplainabilityWidget data={plannerData.explainability} />
            </div>
          )}
          {plannerLoading && (
            <div className="p-4 animate-pulse flex items-center space-x-3 text-slate-400 text-xs text-center justify-center">
              <span>Applying budget and expense analysis algorithms...</span>
            </div>
          )}

          <form onSubmit={handlePlannerSubmit} className="flex space-x-2">
            <input
              type="text"
              value={plannerInput}
              onChange={(e) => setPlannerInput(e.target.value)}
              disabled={plannerLoading}
              placeholder="e.g., How can I save for a ₹50,000 Vacation in 6 months?"
              className="flex-1 px-4 py-2.5 bg-slate-950 border border-slate-800 text-white rounded-xl text-xs placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              type="submit"
              disabled={plannerLoading || !plannerInput.trim()}
              className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow disabled:opacity-50 transition-colors"
            >
              Plan Goal
            </button>
          </form>
        </div>
      </div>
    );
  };

  const renderAdvisorTab = () => {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl h-[70vh] flex flex-col justify-between overflow-hidden animate-fadeIn">
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/20 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-xl">🧠</span>
            <div>
              <h3 className="text-sm font-bold text-white">Financial Advisor</h3>
              <p className="text-xxs text-emerald-400">Online • Analyze large purchases or financial health</p>
            </div>
          </div>
          <span className="text-xxs text-slate-500">Powered by Agentic LLM</span>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-950/30">
          {!advisorData && !advisorLoading && (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-3">
              <span className="text-4xl">💭</span>
              <h4 className="text-lg font-bold text-white">Ask for Financial Advice</h4>
              <p className="text-xs text-slate-400 max-w-sm">
                Wondering if you can afford that new laptop? Need to know if your cash flow is healthy enough for a vacation? Ask me below!
              </p>
            </div>
          )}

          {advisorLoading && (
            <div className="flex flex-col items-center justify-center h-full animate-pulse space-y-4">
              <span className="text-4xl animate-bounce">🧠</span>
              <p className="text-xs text-slate-400">Analyzing your cash flow and affordability...</p>
            </div>
          )}

          {advisorData && !advisorLoading && (
            <div className="space-y-6 animate-scaleIn">
              {/* Top Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl text-center">
                  <p className="text-xxs text-slate-400 uppercase font-bold tracking-wider mb-1">Affordability</p>
                  <p className={`text-xl font-extrabold ${advisorData.affordability_score === 'Poor' ? 'text-rose-500' : 'text-emerald-400'}`}>
                    {advisorData.affordability_score || 'N/A'}
                  </p>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl text-center">
                  <p className="text-xxs text-slate-400 uppercase font-bold tracking-wider mb-1">Risk Level</p>
                  <p className={`text-xl font-extrabold ${advisorData.risk_level?.includes('High') ? 'text-rose-500' : 'text-blue-400'}`}>
                    {advisorData.risk_level || 'N/A'}
                  </p>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl text-center">
                  <p className="text-xxs text-slate-400 uppercase font-bold tracking-wider mb-1">Savings Rate</p>
                  <p className="text-xl font-extrabold text-white">
                    {advisorData.savings_rate || 'N/A'}
                  </p>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl text-center">
                  <p className="text-xxs text-slate-400 uppercase font-bold tracking-wider mb-1">Emergency Fund</p>
                  <p className="text-xl font-extrabold text-white">
                    {advisorData.emergency_fund_status || 'N/A'}
                  </p>
                </div>
              </div>

              {/* Recommendation Card */}
              <div className="p-6 bg-gradient-to-br from-indigo-900/40 to-slate-900 border border-indigo-500/30 rounded-2xl shadow-xl">
                <h4 className="text-sm font-bold text-indigo-400 mb-2">Final Recommendation</h4>
                <p className="text-lg text-white font-medium leading-relaxed">{advisorData.recommendation}</p>
                <div className="mt-4 p-4 bg-slate-950/50 rounded-xl border border-slate-800">
                  <p className="text-xs text-slate-300 leading-relaxed">{advisorData.answer}</p>
                  <ExplainabilityWidget data={advisorData.explainability} />
                </div>
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleAdvisorSubmit} className="p-4 border-t border-slate-800 bg-slate-950/40 flex items-center space-x-2">
          <input
            type="text"
            value={advisorInput}
            onChange={(e) => setAdvisorInput(e.target.value)}
            disabled={advisorLoading}
            placeholder="e.g., Can I afford a bike worth ₹80000 this month?"
            className="flex-1 px-4 py-2.5 bg-slate-950 border border-slate-800 text-white rounded-xl text-xs placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="submit"
            disabled={advisorLoading || !advisorInput.trim()}
            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow disabled:opacity-50 transition-colors"
          >
            Ask Advisor
          </button>
        </form>
      </div>
    );
  };

  const renderInvestmentTab = () => {
    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#8dd1e1', '#a4de6c', '#d0ed57'];
    let pieData: any[] = [];
    if (investData?.recommended_asset_allocation) {
      pieData = Object.entries(investData.recommended_asset_allocation)
        .map(([key, value]) => ({ name: key, value: Number(value) }))
        .filter(item => item.value > 0);
    }

    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl h-[72vh] flex flex-col justify-between overflow-hidden animate-fadeIn">
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/20 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-xl">📈</span>
            <div>
              <h3 className="text-sm font-bold text-white">Investment Intelligence</h3>
              <p className="text-xxs text-blue-400">Online • AI-driven Portfolio Recommendations</p>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-950/30">
          {!investData && !investLoading && (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-3">
              <span className="text-4xl">💡</span>
              <h4 className="text-lg font-bold text-white">Ask for Investment Advice</h4>
              <p className="text-xs text-slate-400 max-w-sm">
                Get a comprehensive asset allocation breakdown based on your active financial data.
              </p>
            </div>
          )}

          {investLoading && (
            <div className="h-full flex flex-col items-center justify-center space-y-4">
              <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-xs text-indigo-400 font-semibold animate-pulse">Running Orchestrator analysis across Expense, Budget & Advisor...</p>
            </div>
          )}

          {investData && !investLoading && (
            <div className="space-y-6 animate-fadeIn">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl text-center shadow">
                  <p className="text-xxs text-slate-400 uppercase font-bold">Investment Score</p>
                  <p className="text-2xl font-extrabold text-white">{investData.investment_score} / 100</p>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl text-center shadow">
                  <p className="text-xxs text-slate-400 uppercase font-bold">Risk Meter</p>
                  <p className="text-2xl font-extrabold text-rose-400">{investData.risk_level}</p>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl text-center shadow">
                  <p className="text-xxs text-slate-400 uppercase font-bold">Recommended Monthly</p>
                  <p className="text-2xl font-extrabold text-emerald-400">₹{investData.recommended_monthly_investment.toLocaleString()}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl shadow">
                  <h4 className="text-xs font-bold text-indigo-400 uppercase mb-4">Asset Allocation (%)</h4>
                  {pieData.length > 0 ? (
                    <div className="h-48">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie data={pieData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={2} dataKey="value">
                            {pieData.map((_e: any, index: number) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                          </Pie>
                          <ChartTooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff' }} itemStyle={{ color: '#fff', fontSize: '12px' }} />
                          <Legend wrapperStyle={{ fontSize: '11px', color: '#cbd5e1' }} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  ) : <p className="text-slate-500 text-xs text-center py-10">No allocation data.</p>}
                </div>

                <div className="space-y-4">
                  <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl shadow">
                    <h4 className="text-xs font-bold text-indigo-400 uppercase mb-2">Emergency Fund Check</h4>
                    <p className="text-sm text-slate-200 leading-relaxed">{investData.emergency_fund_check}</p>
                  </div>
                  <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl shadow">
                    <h4 className="text-xs font-bold text-indigo-400 uppercase mb-2">Goal Alignment</h4>
                    <p className="text-sm text-slate-200 leading-relaxed">{investData.goal_alignment}</p>
                  </div>
                </div>
              </div>

              <div className="p-5 bg-indigo-900/30 border border-indigo-500/30 rounded-xl shadow-lg">
                <h4 className="text-xs font-bold text-indigo-400 uppercase mb-3">Action Plan & Notes</h4>
                <p className="text-sm text-slate-200 whitespace-pre-wrap leading-relaxed">{investData.investment_plan}</p>
                <div className="mt-4 p-3 bg-slate-950/50 rounded-lg text-xs leading-relaxed text-slate-400 border border-slate-800">
                  <span className="font-bold text-slate-300">Advisor Notes:</span> {investData.advisor_notes}
                  <ExplainabilityWidget data={investData.explainability} />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-slate-800 bg-slate-950/40">
          <form onSubmit={handleInvestSubmit} className="space-y-3">
            <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
              <input type="number" placeholder="Enter your monthly income" value={investInput.income} onChange={e => setInvestInput({ ...investInput, income: e.target.value.replace(/^0+(?=\d)/, '') })} className="px-3 py-1.5 bg-slate-900 border border-slate-800 text-white rounded-lg text-xs" />
              <input type="number" placeholder="Enter your monthly expenses" value={investInput.expenses} onChange={e => setInvestInput({ ...investInput, expenses: e.target.value.replace(/^0+(?=\d)/, '') })} className="px-3 py-1.5 bg-slate-900 border border-slate-800 text-white rounded-lg text-xs" />
              <input type="number" placeholder="Enter your savings" value={investInput.savings} onChange={e => setInvestInput({ ...investInput, savings: e.target.value.replace(/^0+(?=\d)/, '') })} className="px-3 py-1.5 bg-slate-900 border border-slate-800 text-white rounded-lg text-xs" />
              <select value={investInput.risk} onChange={e => setInvestInput({ ...investInput, risk: e.target.value })} className="px-3 py-1.5 bg-slate-900 border border-slate-800 text-white rounded-lg text-xs">
                <option value="Low">Low Risk</option>
                <option value="Medium">Medium Risk</option>
                <option value="High">High Risk</option>
              </select>
              <select value={investInput.horizon} onChange={e => setInvestInput({ ...investInput, horizon: e.target.value })} className="px-3 py-1.5 bg-slate-900 border border-slate-800 text-white rounded-lg text-xs">
                <option value="Short Term">Short Term</option>
                <option value="Medium Term">Medium Term</option>
                <option value="Long Term">Long Term</option>
              </select>
              <input type="text" placeholder="Existing (e.g. 50k in Stocks)" value={investInput.existing} onChange={e => setInvestInput({ ...investInput, existing: e.target.value })} className="px-3 py-1.5 bg-slate-900 border border-slate-800 text-white rounded-lg text-xs" />
            </div>
            <div className="flex space-x-2">
              <input
                type="text"
                value={investInput.message}
                onChange={e => setInvestInput({ ...investInput, message: e.target.value })}
                disabled={investLoading}
                placeholder="Ask about your investment opportunities..."
                className="flex-1 px-4 py-2.5 bg-slate-900 border border-slate-800 text-white rounded-xl text-xs placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button type="submit" disabled={investLoading || !investInput.message.trim()} className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow disabled:opacity-50 transition-colors">
                Analyze
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const renderIntelligenceTab = () => {
    return (
      <div className="space-y-6 animate-fadeIn h-[72vh] overflow-y-auto pr-2">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <h3 className="text-xl font-bold text-white mb-2">Unified AI Intelligence</h3>
          <p className="text-xs text-slate-400">Powered by multiple specialized AI agents analyzing your financial history.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-indigo-900/40 to-slate-900 border border-indigo-500/30 rounded-2xl p-5 shadow">
            <h4 className="text-sm font-bold text-indigo-400 mb-2">Financial Health Score</h4>
            <p className="text-3xl font-extrabold text-white">88 <span className="text-sm text-slate-500">/ 100</span></p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow">
            <h4 className="text-sm font-bold text-white mb-2">Forecast (30 Days)</h4>
            <p className="text-lg font-bold text-emerald-400">₹+15,000 Expected</p>
            <p className="text-xs text-slate-500 mt-1">Cash flow remains positive.</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow">
            <h4 className="text-sm font-bold text-white mb-2">Recurring Bills</h4>
            <p className="text-lg font-bold text-rose-400">₹4,500 Unpaid</p>
            <p className="text-xs text-slate-500 mt-1">2 subscriptions pending this week.</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow">
            <h4 className="text-sm font-bold text-white mb-2">Upcoming Goals</h4>
            <p className="text-lg font-bold text-blue-400">Vacation 2027</p>
            <p className="text-xs text-slate-500 mt-1">On track. 60% funded.</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow">
            <h4 className="text-sm font-bold text-white mb-2">Investment Growth</h4>
            <p className="text-lg font-bold text-emerald-400">+12% YTD</p>
            <p className="text-xs text-slate-500 mt-1">Stocks contributing most.</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-center items-center shadow hover:bg-slate-800 cursor-pointer transition">
            <h4 className="text-sm font-bold text-indigo-400 mb-2 text-center">Simulate Scenario</h4>
            <p className="text-xs text-slate-400 text-center mx-2">"What if I save ₹5000 more?"</p>
          </div>
        </div>
      </div>
    );
  };

  const renderActivityTab = () => {
    return (
      <div className="space-y-6 animate-fadeIn h-[72vh] overflow-y-auto pr-2">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <h3 className="text-xl font-bold text-white mb-2">User Activity Timeline</h3>
          <p className="text-xs text-slate-400">Track holistic system activities including model invocations and authentication.</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex justify-between p-3 border-b border-slate-800">
            <span className="text-slate-300 text-sm">💡 Forecast Generated. Cash flow remains positive.</span>
            <span className="text-emerald-400 text-xxs font-mono">Just now</span>
          </div>
          <div className="flex justify-between p-3 border-b border-slate-800">
            <span className="text-slate-300 text-sm">🧠 Advisor Agent evaluated laptop purchase affordability.</span>
            <span className="text-emerald-400 text-xxs font-mono">10m ago</span>
          </div>
          <div className="flex justify-between p-3 border-b border-slate-800">
            <span className="text-slate-300 text-sm">🎯 Goal Planner ran multi-agent analysis.</span>
            <span className="text-slate-500 text-xxs font-mono">15m ago</span>
          </div>
          <div className="flex justify-between p-3 border-b border-slate-800">
            <span className="text-slate-300 text-sm">🔑 User logged in securely.</span>
            <span className="text-slate-500 text-xxs font-mono">2h ago</span>
          </div>
        </div>
      </div>
    );
  };

  const renderActiveTabContent = () => {
    switch (currentTab) {
      case 'Dashboard':
        return renderDashboardOverview();
      case 'Transactions':
        return renderTransactionsTab();
      case 'AI Chat':
        return renderAIChatTab();
      case 'Budget':
        return renderBudgetTab();
      case 'Goals':
        return renderGoalsTab();
      case 'Advisor':
        return renderAdvisorTab();
      case 'Investments':
        return renderInvestmentTab();
      case 'Intelligence':
        return renderIntelligenceTab();
      case 'Activity':
        return renderActivityTab();
      default:
        return (
          <div className="p-8 bg-slate-900 border border-slate-800 rounded-xl text-center text-slate-400 text-sm">
            This module is ready for future extension. Integrate APIs or customization parameters here.
          </div>
        );
    }
  };

  return (
    <div className="flex bg-slate-950 min-h-screen font-sans text-slate-100 relative">
      <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

      <main className="flex-1 p-8 flex flex-col justify-between overflow-y-auto max-h-screen">
        {showOnboarding && <OnboardingWizard onComplete={() => { setShowOnboarding(false); fetchData(); }} />}
        <div>
          {/* Header */}
          <header className="flex justify-between items-center mb-8 pb-4 border-b border-slate-900">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                {currentTab}
              </h1>
              <p className="text-slate-400 mt-1 text-sm">Hi, {username}. Manage your assets and financial health.</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleLogout}
                className="text-xs text-slate-400 hover:text-red-400 border border-slate-800 hover:border-red-950 px-3 py-1.5 rounded-xl transition-all"
              >
                Log Out
              </button>
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 border border-slate-700 flex items-center justify-center font-bold text-white shadow uppercase">
                {username.slice(0, 2)}
              </div>
            </div>
          </header>

          {/* Active Tab Screen */}
          {renderActiveTabContent()}
        </div>

        <footer className="mt-12 text-center text-slate-600 text-xxs">
          Finlume AI Financial Copilot © 2026. Made with Premium Design Aesthetics.
        </footer>
      </main>

      {/* Transaction Add/Edit Modal */}
      {showTxModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 w-full max-w-md animate-scaleIn">
            <h3 className="text-lg font-bold text-white mb-4">
              {editingTxId ? 'Edit Transaction Details' : 'Record New Transaction'}
            </h3>

            <form onSubmit={handleSaveTransaction} className="space-y-4">
              <div>
                <label className="block text-xxs font-bold text-slate-400 uppercase">Date</label>
                <input
                  type="date"
                  required
                  value={txForm.date}
                  onChange={(e) => setTxForm(prev => ({ ...prev, date: e.target.value }))}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-white rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xxs font-bold text-slate-400 uppercase">Category</label>
                  <select
                    value={txForm.category}
                    onChange={(e) => setTxForm(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-white rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="Salary">Salary</option>
                    <option value="Food">Food</option>
                    <option value="Rent">Rent</option>
                    <option value="Entertainment">Entertainment</option>
                    <option value="Travel">Travel</option>
                    <option value="Shopping">Shopping</option>
                    <option value="Utilities">Utilities</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xxs font-bold text-slate-400 uppercase">Type</label>
                  <select
                    value={txForm.type}
                    onChange={(e) => setTxForm(prev => ({ ...prev, type: e.target.value }))}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-white rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="expense">Expense</option>
                    <option value="income">Income</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xxs font-bold text-slate-400 uppercase">Amount (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  required
                  placeholder="Enter your expense amount"
                  value={txForm.amount}
                  onChange={(e) => setTxForm(prev => ({ ...prev, amount: e.target.value.replace(/^0+(?=\d)/, '') }))}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-white rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xxs font-bold text-slate-400 uppercase">Description</label>
                <input
                  type="text"
                  placeholder="Optional detail..."
                  value={txForm.description}
                  onChange={(e) => setTxForm(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-white rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowTxModal(false)}
                  className="px-4 py-2 border border-slate-800 text-slate-400 hover:text-white rounded-xl text-xs transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow transition-colors"
                >
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
