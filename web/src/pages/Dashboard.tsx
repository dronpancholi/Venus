import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useNavigate } from 'react-router-dom';
import {
  Activity,
  Layers,
  GitCommit,
  Cpu,
  FolderKanban,
  Bot,
  BarChart3,
  Database,
  Users,
  Clock,
  HardDrive,
  MessageSquare,
  ArrowRight,
} from 'lucide-react';

function StatCard({ icon: Icon, label, value, sub }: { icon: typeof Activity; label: string; value: string; sub?: string }) {
  return (
    <motion.div
      whileHover={{ y: -1 }}
      className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4"
    >
      <div className="flex items-center gap-2 mb-2">
        <Icon size={14} className="text-zinc-500" />
        <span className="text-xs text-zinc-500">{label}</span>
      </div>
      <span className="text-xl font-semibold text-white">{value}</span>
      {sub && <span className="ml-2 text-xs text-zinc-600">{sub}</span>}
    </motion.div>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: api.health, refetchInterval: 5000 });
  const { data: services } = useQuery({ queryKey: ['services'], queryFn: api.services });
  const { data: agents } = useQuery({ queryKey: ['agents'], queryFn: api.agents });
  const { data: tasks } = useQuery({ queryKey: ['tasks'], queryFn: () => api.tasks() });
  const { data: repos } = useQuery({ queryKey: ['repository'], queryFn: api.repository });
  const { data: metrics } = useQuery({ queryKey: ['metrics'], queryFn: api.metrics });
  const { data: conversations } = useQuery({ queryKey: ['conversations'], queryFn: () => api.conversations() });
  const { data: storage } = useQuery({ queryKey: ['storage'], queryFn: api.storage });
  const { data: execution } = useQuery({ queryKey: ['execution'], queryFn: api.execution });

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-white">Dashboard</h1>
        <div className="flex items-center gap-2 text-xs text-zinc-500">
          <span className="flex items-center gap-1">
            <Activity size={12} className="text-green-500" />
            Live
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <StatCard icon={Activity} label="Status" value={health?.status ?? '—'} />
        <StatCard icon={Layers} label="Services" value={String(services?.count ?? '—')} />
        <StatCard icon={Cpu} label="Executions" value={String(execution?.execution_count ?? '—')} />
        <StatCard icon={GitCommit} label="Messages" value={String(health?.messages ?? '—')} />
        <StatCard icon={Users} label="Sessions" value={String(health?.sessions ?? '—')} />
        <StatCard icon={HardDrive} label="Storage" value={storage?.connected ? 'Connected' : 'Offline'} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-medium text-zinc-400">Projects</h2>
            <button onClick={() => navigate('/knowledge')} className="flex items-center gap-1 text-xs text-[#0c8ee7]">
              View all <ArrowRight size={12} />
            </button>
          </div>
          <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
            {repos?.watchers && Object.keys(repos.watchers).length > 0 ? (
              <div className="space-y-2">
                {Object.entries(repos.watchers).map(([name, state]) => (
                  <motion.button
                    key={name}
                    whileHover={{ x: 2 }}
                    onClick={() => navigate(`/project/${encodeURIComponent(name)}`)}
                    className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-left hover:bg-zinc-800/50"
                  >
                    <div className="flex items-center gap-2">
                      <FolderKanban size={15} className="text-zinc-500" />
                      <span className="text-sm text-zinc-300">{name}</span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-zinc-600">
                      <span>{state.change_count} changes</span>
                      <span>{state.scan_count} scans</span>
                    </div>
                  </motion.button>
                ))}
              </div>
            ) : (
              <p className="py-6 text-center text-sm text-zinc-600">
                No projects imported. Run <code className="text-[#0c8ee7]">genesis import &lt;path&gt;</code> from the CLI.
              </p>
            )}
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-medium text-zinc-400">AI Activity</h2>
            <button onClick={() => navigate('/copilot')} className="flex items-center gap-1 text-xs text-[#0c8ee7]">
              Open Copilot <ArrowRight size={12} />
            </button>
          </div>
          <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
            <div className="flex items-center gap-3 mb-3">
              <Bot size={16} className="text-[#0c8ee7]" />
              <span className="text-sm text-zinc-400">
                {agents && (agents as { agents?: unknown[] }).agents
                  ? `${(agents as { agents: unknown[] }).agents.length} agents available`
                  : 'AI Ready'}
              </span>
            </div>
            {conversations?.conversations && conversations.conversations.length > 0 ? (
              <div className="space-y-1">
                {conversations.conversations.slice(0, 3).map((c) => (
                  <div key={c.id} className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-zinc-500">
                    <MessageSquare size={12} />
                    <span className="truncate">{c.title || 'Untitled'}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-zinc-600">No conversations yet</p>
            )}
          </div>
        </div>
      </div>

      {metrics?.metrics && (
        <div>
          <h2 className="text-sm font-medium text-zinc-400 mb-3">System Metrics</h2>
          <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
            <pre className="text-xs text-zinc-500 overflow-x-auto">
              {JSON.stringify(metrics.metrics, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </motion.div>
  );
}
