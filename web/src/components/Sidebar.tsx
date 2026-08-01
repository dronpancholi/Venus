import { NavLink, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  FolderKanban,
  Brain,
  GitBranch,
  Terminal,
  Search,
  MessageSquare,
  Settings,
  BookOpen,
  Clock,
  Network,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useUIStore } from '../lib/store';
import clsx from 'clsx';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Home', shortcut: '⌘1' },
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', shortcut: '⌘2' },
  { to: '/knowledge', icon: BookOpen, label: 'Knowledge', shortcut: '⌘3' },
  { to: '/timeline', icon: Clock, label: 'Timeline', shortcut: '⌘4' },
  { to: '/copilot', icon: Brain, label: 'AI Copilot', shortcut: '⌘5' },
  { to: '/terminal', icon: Terminal, label: 'Terminal', shortcut: '⌘6' },
  { to: '/settings', icon: Settings, label: 'Settings', shortcut: '⌘7' },
];

export default function Sidebar() {
  const { sidebarOpen, toggleSidebar, setSearchOpen } = useUIStore();
  const navigate = useNavigate();

  return (
    <motion.aside
      animate={{ width: sidebarOpen ? 240 : 0 }}
      className="fixed left-0 top-0 z-30 h-full overflow-hidden border-r border-[#1a1a1a] bg-[#0a0a0a]"
    >
      <div className="flex h-full w-60 flex-col">
        <div className="flex h-14 items-center justify-between px-4 border-b border-[#1a1a1a]">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#0c8ee7]">
              <Network size={14} className="text-white" />
            </div>
            {sidebarOpen && (
              <span className="text-sm font-semibold text-white">Genesis</span>
            )}
          </div>
          <button
            onClick={toggleSidebar}
            className="rounded-md p-1.5 text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300 transition-colors"
          >
            {sidebarOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-2 space-y-0.5">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                  isActive
                    ? 'bg-zinc-800 text-white'
                    : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
                )
              }
            >
              <item.icon size={17} />
              <span className="flex-1">{item.label}</span>
              <span className="text-[10px] text-zinc-600">{item.shortcut}</span>
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-[#1a1a1a] p-2 space-y-0.5">
          <button
            onClick={() => setSearchOpen(true)}
            className={clsx(
              'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-zinc-400 transition-colors hover:bg-zinc-800/50 hover:text-zinc-200'
            )}
          >
            <Search size={17} />
            <span className="flex-1">Search</span>
            <span className="text-[10px] text-zinc-600">⌘K</span>
          </button>
        </div>
      </div>
    </motion.aside>
  );
}
