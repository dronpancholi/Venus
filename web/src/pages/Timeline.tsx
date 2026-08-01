import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Clock, Activity, GitCommit, GitBranch, Box } from 'lucide-react';

export default function Timeline() {
  const { data: events } = useQuery({ queryKey: ['events'], queryFn: () => api.events({ limit: 100 }), refetchInterval: 10000 });
  const { data: audit } = useQuery({ queryKey: ['audit'], queryFn: () => api.audit({ limit: 50 }) });
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: api.health, refetchInterval: 5000 });

  const timelineItems = [
    ...(events?.events?.map((e: unknown) => ({
      id: (e as { id?: string }).id ?? '',
      type: (e as { type?: string }).type ?? 'event',
      origin: (e as { origin?: string }).origin ?? '',
      timestamp: (e as { timestamp?: number }).timestamp ?? Date.now(),
      category: 'event' as const,
    })) ?? []),
    ...(audit?.entries?.map((e) => ({
      id: e.id,
      type: e.action,
      origin: e.actor,
      timestamp: e.timestamp * 1000,
      category: 'audit' as const,
    })) ?? []),
  ].sort((a, b) => b.timestamp - a.timestamp);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-white">Timeline</h1>
        <div className="flex items-center gap-2 text-xs text-zinc-500">
          <Activity size={12} className={health?.status === 'healthy' ? 'text-green-500' : 'text-yellow-500'} />
          {health?.status}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
          <div className="flex items-center gap-2 mb-2">
            <GitCommit size={14} className="text-[#0c8ee7]" />
            <span className="text-xs text-zinc-500">Events</span>
          </div>
          <span className="text-2xl font-semibold text-white">{events?.count ?? '—'}</span>
        </div>
        <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
          <div className="flex items-center gap-2 mb-2">
            <GitBranch size={14} className="text-purple-400" />
            <span className="text-xs text-zinc-500">Audit Entries</span>
          </div>
          <span className="text-2xl font-semibold text-white">{audit?.total ?? '—'}</span>
        </div>
        <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
          <div className="flex items-center gap-2 mb-2">
            <Clock size={14} className="text-amber-400" />
            <span className="text-xs text-zinc-500">Uptime</span>
          </div>
          <span className="text-2xl font-semibold text-white">
            {health?.uptime_seconds ? `${Math.floor(health.uptime_seconds / 60)}m` : '—'}
          </span>
        </div>
      </div>

      <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f]">
        <div className="border-b border-[#1a1a1a] px-4 py-3">
          <h2 className="text-sm font-medium text-zinc-400">Activity Log</h2>
        </div>
        <div className="max-h-96 overflow-y-auto p-2">
          {timelineItems.length > 0 ? (
            <div className="relative pl-6 space-y-0">
              <div className="absolute left-[11px] top-2 bottom-2 w-px bg-[#232323]" />
              {timelineItems.slice(0, 100).map((item) => (
                <div key={`${item.category}-${item.id}`} className="relative flex items-start gap-3 py-2">
                  <div className={`absolute left-[-17px] top-[10px] h-2.5 w-2.5 rounded-full border-2 ${
                    item.category === 'event'
                      ? 'border-[#0c8ee7] bg-[#0a0a0a]'
                      : 'border-purple-500 bg-[#0a0a0a]'
                  }`} />
                  <Box size={14} className="mt-0.5 text-zinc-600 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-sm text-zinc-300">{item.type}</p>
                    <p className="text-xs text-zinc-600">
                      {item.origin} · {new Date(item.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="py-8 text-center text-sm text-zinc-600">No activity yet</p>
          )}
        </div>
      </div>
    </motion.div>
  );
}
