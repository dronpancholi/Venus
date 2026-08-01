import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import {
  ArrowLeft,
  FolderKanban,
  Activity,
  Clock,
  FileText,
  BarChart3,
  GitBranch,
  Cpu,
} from 'lucide-react';

export default function Project() {
  const { name } = useParams<{ name: string }>();
  const navigate = useNavigate();
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: api.health });
  const { data: repos } = useQuery({ queryKey: ['repository'], queryFn: api.repository });
  const { data: tasks } = useQuery({ queryKey: ['tasks'], queryFn: () => api.tasks() });
  const { data: events } = useQuery({ queryKey: ['events'], queryFn: () => api.events({ limit: 20 }) });

  const watcher = repos?.watchers?.[name ?? ''];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(-1)}
          className="rounded-lg p-2 text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300"
        >
          <ArrowLeft size={18} />
        </button>
        <div>
          <h1 className="text-lg font-semibold text-white">{decodeURIComponent(name ?? 'Unknown')}</h1>
          <p className="text-sm text-zinc-500">Project Overview</p>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity size={14} className="text-green-500" />
            <span className="text-xs text-zinc-500">Status</span>
          </div>
          <span className="text-lg font-semibold text-white">
            {watcher?.active ? 'Active' : 'Imported'}
          </span>
        </div>
        <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
          <div className="flex items-center gap-2 mb-2">
            <FileText size={14} className="text-[#0c8ee7]" />
            <span className="text-xs text-zinc-500">Scans</span>
          </div>
          <span className="text-lg font-semibold text-white">{watcher?.scan_count ?? '—'}</span>
        </div>
        <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
          <div className="flex items-center gap-2 mb-2">
            <GitBranch size={14} className="text-purple-400" />
            <span className="text-xs text-zinc-500">Changes</span>
          </div>
          <span className="text-lg font-semibold text-white">{watcher?.change_count ?? '—'}</span>
        </div>
        <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
          <div className="flex items-center gap-2 mb-2">
            <Clock size={14} className="text-amber-400" />
            <span className="text-xs text-zinc-500">Last Scan</span>
          </div>
          <span className="text-lg font-semibold text-white truncate">
            {watcher?.last_scan ? new Date(watcher.last_scan).toLocaleDateString() : '—'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-sm font-medium text-zinc-400 mb-3">Recent Events</h2>
          <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
            {events?.events && events.events.length > 0 ? (
              <div className="space-y-1">
                {events.events.slice(0, 10).map((ev: unknown) => {
                  const e = ev as { type?: string; origin?: string; timestamp?: number };
                  return (
                    <div key={(ev as { id?: string }).id} className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm">
                      <Activity size={12} className="text-zinc-600" />
                      <span className="text-zinc-400 truncate">{e.type ?? 'event'}</span>
                      <span className="text-zinc-600 text-xs">from {e.origin}</span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="py-6 text-center text-sm text-zinc-600">No events recorded</p>
            )}
          </div>
        </div>

        <div>
          <h2 className="text-sm font-medium text-zinc-400 mb-3">Active Tasks</h2>
          <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
            {tasks && (tasks as { tasks?: unknown[] }).tasks && (tasks as { tasks: unknown[] }).tasks.length > 0 ? (
              <div className="space-y-1">
                {(tasks as { tasks: { id?: string; name?: string; status?: string }[] }).tasks.slice(0, 10).map((t) => (
                  <div key={t.id} className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm">
                    <Cpu size={12} className="text-zinc-600" />
                    <span className="text-zinc-400 truncate">{t.name}</span>
                    <span className="text-zinc-600 text-xs ml-auto">{t.status}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="py-6 text-center text-sm text-zinc-600">No tasks</p>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
