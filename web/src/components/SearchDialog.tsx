import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, ArrowRight, Loader2, BookOpen, Clock, HardDrive, MessageSquare, Box } from 'lucide-react';
import { useUIStore } from '../lib/store';
import { api } from '../lib/api';
import { useNavigate } from 'react-router-dom';
import type { SearchResult } from '../lib/types';
import clsx from 'clsx';

const typeIcons: Record<string, typeof Box> = {
  engineering_object: Box,
  knowledge: BookOpen,
  event: Clock,
  audit: HardDrive,
  timeline: Clock,
  provider: MessageSquare,
};

export default function SearchDialog() {
  const { setSearchOpen } = useUIStore();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    inputRef.current?.focus();
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSearchOpen(false);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [setSearchOpen]);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await api.search(query);
        setResults(res.results);
      } catch {
        setResults([]);
      }
      setLoading(false);
    }, 200);
    return () => clearTimeout(timer);
  }, [query]);

  const handleSelect = (r: SearchResult) => {
    setSearchOpen(false);
    if (r.type === 'engineering_object' && r.id) {
      navigate(`/project/${encodeURIComponent(r.id)}`);
    } else if (r.type === 'knowledge') {
      navigate('/knowledge');
    } else if (r.type === 'event' || r.type === 'timeline') {
      navigate('/timeline');
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 pt-[15vh]"
        onClick={() => setSearchOpen(false)}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -20 }}
          transition={{ duration: 0.15 }}
          className="w-full max-w-xl rounded-xl border border-[#232323] bg-[#141414] shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center gap-3 border-b border-[#232323] px-4 py-3">
            <Search size={18} className="text-zinc-500" />
            <input
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search projects, knowledge, events, objects..."
              className="flex-1 bg-transparent text-sm text-white outline-none placeholder:text-zinc-600"
            />
            {loading ? (
              <Loader2 size={16} className="animate-spin text-zinc-500" />
            ) : (
              <kbd className="rounded-md border border-[#333] bg-[#1a1a1a] px-1.5 py-0.5 text-[10px] text-zinc-500">
                ESC
              </kbd>
            )}
            <button onClick={() => setSearchOpen(false)} className="text-zinc-500 hover:text-zinc-300">
              <X size={16} />
            </button>
          </div>
          <div className="max-h-80 overflow-y-auto p-2">
            {results.length === 0 && query.trim() && !loading && (
              <p className="py-8 text-center text-sm text-zinc-600">No results found</p>
            )}
            {results.map((r, i) => {
              const Icon = typeIcons[r.type] || Box;
              return (
                <button
                  key={`${r.type}-${r.id ?? i}`}
                  onClick={() => handleSelect(r)}
                  className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-colors hover:bg-zinc-800"
                >
                  <Icon size={16} className="text-zinc-500 shrink-0" />
                  <span className="flex-1 truncate text-zinc-300">{r.label}</span>
                  <span className="text-[10px] text-zinc-600 capitalize">{r.type.replace('_', ' ')}</span>
                  <ArrowRight size={14} className="text-zinc-600 shrink-0" />
                </button>
              );
            })}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
