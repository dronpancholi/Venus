import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import {
  ArrowRight,
  Activity,
  Layers,
  GitCommit,
  Bot,
  BookOpen,
  Clock,
  Network,
  FolderKanban,
  Cpu,
} from 'lucide-react';
import { useUIStore } from '../lib/store';

export default function Home() {
  const navigate = useNavigate();
  const setSearchOpen = useUIStore((s) => s.setSearchOpen);
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: api.health });
  const { data: repos } = useQuery({ queryKey: ['repository'], queryFn: api.repository });
  const { data: tasks } = useQuery({ queryKey: ['tasks'], queryFn: () => api.tasks() });

  const stats = [
    { icon: Activity, label: 'Status', value: health?.status ?? '—', color: 'text-green-500' },
    { icon: Layers, label: 'Services', value: String(health?.services ?? '—'), color: 'text-[#0c8ee7]' },
    { icon: GitCommit, label: 'Messages', value: String(health?.messages ?? '—'), color: 'text-purple-400' },
    { icon: Cpu, label: 'Sessions', value: String(health?.sessions ?? '—'), color: 'text-amber-400' },
  ];

  const quickActions = [
    { label: 'Dashboard', icon: Activity, path: '/dashboard', shortcut: '⌘2' },
    { label: 'Knowledge', icon: BookOpen, path: '/knowledge', shortcut: '⌘3' },
    { label: 'Timeline', icon: Clock, path: '/timeline', shortcut: '⌘4' },
    { label: 'AI Copilot', icon: Bot, path: '/copilot', shortcut: '⌘5' },
    { label: 'Terminal', icon: Cpu, path: '/terminal', shortcut: '⌘6' },
    { label: 'Search', icon: Network, action: () => setSearchOpen(true), shortcut: '⌘K' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
      <div className="pt-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#0c8ee7]">
            <Network size={22} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-white">Genesis</h1>
            <p className="text-sm text-zinc-500">Engineering Computing Platform</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {stats.map((stat) => (
          <motion.div
            key={stat.label}
            whileHover={{ y: -1 }}
            className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4"
          >
            <div className="flex items-center gap-2 mb-2">
              <stat.icon size={15} className={stat.color} />
              <span className="text-xs text-zinc-500">{stat.label}</span>
            </div>
            <span className="text-2xl font-semibold text-white">{stat.value}</span>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-sm font-medium text-zinc-400 mb-3">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-2">
            {quickActions.map((action) => (
              <motion.button
                key={action.label}
                whileHover={{ y: -1 }}
                onClick={() => (action.action ? action.action() : navigate(action.path!))}
                className="flex items-center gap-3 rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] px-4 py-3 text-left transition-colors hover:border-[#333]"
              >
                <action.icon size={17} className="text-zinc-400" />
                <span className="flex-1 text-sm text-zinc-300">{action.label}</span>
                <span className="text-[10px] text-zinc-600">{action.shortcut}</span>
              </motion.button>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-medium text-zinc-400">Recent Activity</h2>
            <button
              onClick={() => navigate('/timeline')}
              className="flex items-center gap-1 text-xs text-[#0c8ee7] hover:text-[#0070c4]"
            >
              View all <ArrowRight size={12} />
            </button>
          </div>
          <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
            {repos?.watchers && Object.keys(repos.watchers).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(repos.watchers).slice(0, 5).map(([name, state]) => (
                  <div key={name} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <FolderKanban size={14} className="text-zinc-500" />
                      <span className="text-zinc-300">{name}</span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-zinc-500">
                      <span>{state.change_count} changes</span>
                      <span>{state.scan_count} scans</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-zinc-600 text-center py-4">
                No imported projects yet. Use{' '}
                <code className="text-[#0c8ee7]">genesis import</code> to get started.
              </p>
            )}
          </div>
        </div>
      </div>

      {tasks && (tasks as { tasks?: unknown[] }).tasks && (tasks as { tasks: unknown[] }).tasks.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-zinc-400 mb-3">Active Tasks</h2>
          <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
            <pre className="text-xs text-zinc-500">
              {JSON.stringify(tasks, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </motion.div>
  );
}
