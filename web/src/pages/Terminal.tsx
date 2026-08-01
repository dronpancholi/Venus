import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Terminal as TerminalIcon } from 'lucide-react';

export default function TerminalPage() {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4 h-full flex flex-col"
    >
      <div className="flex items-center gap-2">
        <TerminalIcon size={18} className="text-zinc-400" />
        <h1 className="text-lg font-semibold text-white">Engineering Terminal</h1>
      </div>

      <div className="flex-1 rounded-xl border border-[#232323] bg-[#0a0a0a] overflow-hidden">
        <div className="flex items-center gap-2 border-b border-[#232323] px-4 py-2">
          <div className="flex gap-1.5">
            <div className="h-3 w-3 rounded-full bg-red-500/50" />
            <div className="h-3 w-3 rounded-full bg-yellow-500/50" />
            <div className="h-3 w-3 rounded-full bg-green-500/50" />
          </div>
          <span className="text-xs text-zinc-600">genesis terminal</span>
        </div>
        <div className="p-4 font-mono text-sm text-green-400">
          <p className="text-zinc-500 mb-2"># Genesis Engineering Terminal</p>
          <p className="text-zinc-500 mb-4"># Type 'help' for commands, 'exit' to quit</p>
          <p className="mb-2">
            <span className="text-[#0c8ee7]">genesis@platform</span>
            <span className="text-zinc-500">:</span>
            <span className="text-amber-400">~</span>
            <span className="text-zinc-500">$</span>{' '}
            <span className="text-white">genesis status</span>
          </p>
          <div className="text-zinc-300 mb-4">
            <p>✓ Configuration Ready</p>
            <p>✓ Fabric Kernel running</p>
            <p>✓ Workspace: ~/Genesis</p>
            <p>○ Desktop available (headless)</p>
            <p>✓ API Server ready</p>
            <p>✓ WebSocket connected</p>
            <p>✓ Terminal online</p>
          </div>
          <p>
            <span className="text-[#0c8ee7]">genesis@platform</span>
            <span className="text-zinc-500">:</span>
            <span className="text-amber-400">~</span>
            <span className="text-zinc-500">$</span>{' '}
            <span className="animate-pulse text-white">_</span>
          </p>
        </div>
      </div>

      <p className="text-xs text-zinc-600">
        Full xterm.js terminal integration coming soon. Use <code className="text-[#0c8ee7]">genesis terminal</code> from CLI for the full experience.
      </p>
    </motion.div>
  );
}
