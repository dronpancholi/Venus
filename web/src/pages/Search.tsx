import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Search, FileText, Loader2, Box } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const q = searchParams.get('q') ?? '';
  const [input, setInput] = useState(q);

  const { data, isLoading } = useQuery({
    queryKey: ['search', q],
    queryFn: () => api.search(q),
    enabled: q.length > 0,
  });

  useEffect(() => {
    if (q) setInput(q);
  }, [q]);

  const handleSearch = () => {
    if (input.trim()) {
      setSearchParams({ q: input.trim() });
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <h1 className="text-lg font-semibold text-white">Search</h1>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search across all engineering data..."
            className="w-full rounded-xl border border-[#232323] bg-[#0f0f0f] py-2.5 pl-10 pr-4 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-[#0c8ee7]"
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={!input.trim()}
          className="rounded-xl bg-[#0c8ee7] px-5 py-2.5 text-sm font-medium text-white hover:bg-[#0070c4] disabled:opacity-40 transition-colors"
        >
          Search
        </button>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 size={20} className="animate-spin text-zinc-500" />
        </div>
      )}

      {data && data.results.length > 0 && (
        <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-2">
          <div className="px-3 py-2 text-xs text-zinc-600">
            {data.count} result(s)
          </div>
          <div className="space-y-0.5">
            {data.results.map((r, i) => (
              <div
                key={i}
                className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm hover:bg-zinc-800/50 cursor-pointer"
              >
                <FileText size={14} className="text-zinc-500 shrink-0" />
                <span className="flex-1 text-zinc-300 truncate">{r.label}</span>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-zinc-600 capitalize">{r.type.replace('_', ' ')}</span>
                  <span className="text-[10px] text-zinc-700">{Math.round(r.relevance * 100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {data && data.count === 0 && q && (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Box size={32} className="text-zinc-700 mb-3" />
          <p className="text-sm text-zinc-500">No results for "{q}"</p>
          <p className="text-xs text-zinc-600 mt-1">Try different keywords or check your spelling</p>
        </div>
      )}

      {!q && (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Search size={32} className="text-zinc-700 mb-3" />
          <p className="text-sm text-zinc-500">Search across all engineering data</p>
          <p className="text-xs text-zinc-600 mt-1">
            Projects · Knowledge · Events · Audit · Timeline · AI Providers
          </p>
        </div>
      )}
    </motion.div>
  );
}
