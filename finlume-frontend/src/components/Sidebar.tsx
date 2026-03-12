interface SidebarProps {
  currentTab?: string;
  onTabChange?: (tab: string) => void;
}

const menuItems = [
  { name: 'Dashboard', icon: '📊' },
  { name: 'AI Chat', icon: '💬' },
  { name: 'Transactions', icon: '💸' },
  { name: 'Budget', icon: '👛' },
  { name: 'Goals', icon: '🎯' },
  { name: 'Advisor', icon: '🧠' },
  { name: 'Investments', icon: '📈' },
  { name: 'Reports', icon: '📁' },
  { name: 'Settings', icon: '⚙️' },
];

export const Sidebar = ({ currentTab = 'Dashboard', onTabChange }: SidebarProps) => {
  return (
    <aside className="w-64 bg-slate-900 text-white min-h-screen p-4 flex flex-col justify-between shadow-lg">
      <div>
        <div className="flex items-center space-x-3 px-4 py-6 border-b border-slate-800">
          <span className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
            Finlume AI
          </span>
        </div>
        <nav className="mt-8 space-y-1">
          {menuItems.map((item) => {
            const isActive = currentTab === item.name;
            return (
              <button
                key={item.name}
                onClick={() => onTabChange && onTabChange(item.name)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-all duration-150 ${
                  isActive
                    ? 'bg-blue-600 text-white font-semibold'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                }`}
              >
                <span className="text-xl">{item.icon}</span>
                <span>{item.name}</span>
              </button>
            );
          })}
        </nav>
      </div>
      <div className="p-4 border-t border-slate-800 text-center text-xs text-slate-500">
        v1.0.0
      </div>
    </aside>
  );
};
