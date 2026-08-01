import { motion } from 'framer-motion';
import { Brain, MessageSquare, Search, Zap, Activity, CheckCircle2, AlertCircle, ShieldCheck } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useState } from 'react';

export default function Copilot() {
  const [query, setQuery] = useState('');
  const [goal, setGoal] = useState('');
  const [verifyCmd, setVerifyCmd] = useState('pytest');
  const [execResult, setExecResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const { data: conversations } = useQuery({ queryKey: ['conversations'], queryFn: () => api.conversations() });
  const { data: providers } = useQuery({ queryKey: ['providers'], queryFn: api.providers });

  const runKarpathyGoal = async () => {
    if (!goal.trim()) return;
    setLoading(true);
    setExecResult(null);
    try {
      const res = await fetch('/v1/karpathy/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal, verify_command: verifyCmd }),
      });
      const data = await res.json();
      setExecResult(data);
    } catch (err: any) {
      setExecResult({ success: false, output: err.message || 'Execution error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain size={18} className="text-[#0c8ee7]" />
          <h1 className="text-lg font-semibold text-white">Karpathy Agent Copilot</h1>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-green-500/30 bg-green-500/10 px-3 py-1 text-xs text-green-400">
          <ShieldCheck size={13} />
          <span>Karpathy Guidelines Active</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Karpathy Goal Execution Card */}
          <div className="rounded-xl border border-[#232323] bg-[#0f0f0f] p-5 space-y-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#0c8ee7]/10">
                <Zap size={20} className="text-[#0c8ee7]" />
              </div>
              <div>
                <h2 className="text-sm font-medium text-white">Goal-Driven Execution Engine</h2>
                <p className="text-xs text-zinc-500">
                  Formulates goals, states assumptions, applies surgical edits, and verifies checks
                </p>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs text-zinc-400 mb-1 block">Goal Description</label>
                <input
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  placeholder="e.g. Verify test suite passes and clean up unused imports"
                  className="w-full rounded-lg border border-[#333] bg-[#1a1a1a] py-2.5 px-3 text-sm text-white outline-none focus:border-[#0c8ee7]"
                />
              </div>

              <div>
                <label className="text-xs text-zinc-400 mb-1 block">Verification Command</label>
                <input
                  value={verifyCmd}
                  onChange={(e) => setVerifyCmd(e.target.value)}
                  placeholder="pytest"
                  className="w-full rounded-lg border border-[#333] bg-[#1a1a1a] py-2 px-3 text-sm text-zinc-300 outline-none focus:border-[#0c8ee7]"
                />
              </div>

              <button
                onClick={runKarpathyGoal}
                disabled={loading || !goal.trim()}
                className="w-full rounded-lg bg-[#0c8ee7] py-2.5 text-sm font-medium text-white hover:bg-[#0070c4] transition-colors disabled:opacity-50"
              >
                {loading ? 'Executing & Verifying Goal...' : 'Run Karpathy Goal Engine'}
              </button>
            </div>

            {/* Execution Result */}
            {execResult && (
              <div className="mt-4 rounded-lg border border-zinc-800 bg-[#141414] p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {execResult.success ? (
                      <CheckCircle2 size={16} className="text-green-400" />
                    ) : (
                      <AlertCircle size={16} className="text-red-400" />
                    )}
                    <span className="text-sm font-medium text-white">
                      {execResult.success ? 'Goal Verified & Passed' : 'Goal Verification Failed'}
                    </span>
                  </div>
                  <span className="text-xs text-zinc-500">Iterations: {execResult.iterations || 1}</span>
                </div>

                {execResult.thought?.assumptions?.length > 0 && (
                  <div className="text-xs text-zinc-400 space-y-1">
                    <span className="font-semibold text-zinc-300">Assumptions:</span>
                    <ul className="list-disc pl-4 space-y-0.5">
                      {execResult.thought.assumptions.map((a: string, i: number) => (
                        <li key={i}>{a}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {execResult.output && (
                  <pre className="max-h-40 overflow-y-auto rounded bg-black/50 p-2.5 text-xs text-zinc-300 font-mono">
                    {execResult.output}
                  </pre>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <h2 className="text-sm font-medium text-zinc-400 mb-3">Karpathy Guidelines</h2>
            <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4 text-xs text-zinc-400 space-y-2">
              <p><strong className="text-zinc-200">1. Think Before Coding:</strong> State assumptions explicitly.</p>
              <p><strong className="text-zinc-200">2. Simplicity First:</strong> Minimum code, no speculative abstractions.</p>
              <p><strong className="text-zinc-200">3. Surgical Changes:</strong> Touch only what you must. Clean orphaned code.</p>
              <p><strong className="text-zinc-200">4. Goal-Driven:</strong> Define tests and loop until verified.</p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

