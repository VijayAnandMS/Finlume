import {
  LayoutDashboard,
  MessageSquare,
  ArrowRightLeft,
  Wallet,
  Target,
  BrainCircuit,
  TrendingUp,
  Zap,
  History,
  FileText,
  Settings
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface SidebarProps {
  currentTab?: string;
  onTabChange?: (tab: string) => void;
}

const menuItems = [
  { name: 'Dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
  { name: 'AI Chat', icon: <MessageSquare className="w-5 h-5" /> },
  { name: 'Transactions', icon: <ArrowRightLeft className="w-5 h-5" /> },
  { name: 'Budget', icon: <Wallet className="w-5 h-5" /> },
  { name: 'Goals', icon: <Target className="w-5 h-5" /> },
  { name: 'Advisor', icon: <BrainCircuit className="w-5 h-5" /> },
  { name: 'Investments', icon: <TrendingUp className="w-5 h-5" /> },
  { name: 'Intelligence', icon: <Zap className="w-5 h-5" /> },
  { name: 'Activity', icon: <History className="w-5 h-5" /> },
  { name: 'Reports', icon: <FileText className="w-5 h-5" /> },
  { name: 'Settings', icon: <Settings className="w-5 h-5" /> },
];

export const Sidebar = ({ currentTab = 'Dashboard', onTabChange }: SidebarProps) => {
  const navigate = useNavigate();
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 text-white min-h-screen p-4 flex flex-col justify-between shadow-lg">
      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
        <div className="flex items-center space-x-3 px-4 py-6 border-b border-slate-800 mb-4 sticky top-0 bg-slate-900 z-10">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-black shadow-[0_0_15px_rgba(99,102,241,0.5)]">
            F.
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent transform transition-all duration-300">
            Finlume AI
          </span>
        </div>

        <nav className="space-y-1.5 pb-4">
          {menuItems.map((item) => {
            const isActive = currentTab === item.name;
            return (
              <button
                key={item.name}
                onClick={() => {
                  if (item.name === 'Transactions') {
                    navigate('/transactions');
                  } else if (item.name === 'Dashboard') {
                    navigate('/dashboard');
                  } else if (item.name === 'Intelligence') {
                    navigate('/intelligence');
                  } else if (onTabChange) {
                    onTabChange(item.name);
                  }
                }}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-300 group relative overflow-hidden ${isActive
                  ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white font-semibold shadow-md'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                  }`}
              >
                {isActive && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full shadow-[0_0_10px_rgba(255,255,255,1)]"></div>
                )}
                <span className={`transform transition-transform duration-300 ${isActive ? 'scale-110' : 'group-hover:scale-110 group-hover:text-indigo-400'}`}>
                  {item.icon}
                </span>
                <span className="text-sm font-medium tracking-wide">{item.name}</span>
              </button>
            );
          })}
        </nav>
      </div>
      <div className="p-4 border-t border-slate-800 text-center text-xs text-slate-500 font-mono mt-auto pt-6">
        Enterprise Build 1.0.0
      </div>
    </aside>
  );
};
