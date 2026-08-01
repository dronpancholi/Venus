import { useUIStore } from '../lib/store';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Wifi, WifiOff, Activity, Layers, GitCommit } from 'lucide-react';

export default function StatusBar() {
  const wsConnected = useUIStore((s) => s.wsConnected);
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: api.health,
    refetchInterval: 5000,
  });

  return (
    <footer className="flex h-8 items-center justify-between border-t border-[#1a1a1a] bg-[#0a0a0a] px-4 text-[11px] text-zinc-500">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5">
          {wsConnected ? (
            <Wifi size={12} className="text-green-500" />
          ) : (
            <WifiOff size={12} className="text-red-500" />
          )}
          <span className={wsConnected ? 'text-green-500' : 'text-red-500'}>
            {wsConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        {health && (
          <>
            <div className="flex items-center gap-1">
              <Activity size={12} />
              <span>{health.status}</span>
            </div>
            <div className="flex items-center gap-1">
              <Layers size={12} />
              <span>{health.services} services</span>
            </div>
            <div className="flex items-center gap-1">
              <GitCommit size={12} />
              <span>{health.messages} msgs</span>
            </div>
          </>
        )}
      </div>
      <div className="flex items-center gap-3">
        <span>Genesis v1.0.0</span>
      </div>
    </footer>
  );
}
