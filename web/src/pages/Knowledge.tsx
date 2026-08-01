import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { BookOpen, FileText, Box, Search, ExternalLink } from 'lucide-react';
import { useState } from 'react';

export default function Knowledge() {
  const [query, setQuery] = useState('');
  const { data: events } = useQuery({ queryKey: ['events'], queryFn: () => api.events({ limit: 50 }) });
  const { data: repos } = useQuery({ queryKey: ['repository'], queryFn: api.repository });
  const { data: searchResults } = useQuery({
    queryKey: ['search', query],
    queryFn: () => api.search(query),
    enabled: query.length > 2,
  });

  const catalogItems = repos?.watchers ? Object.keys(repos.watchers) : [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-white">Knowledge</h1>
      </div>

      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search knowledge..."
          className="w-full rounded-xl border border-[#232323] bg-[#0f0f0f] py-2.5 pl-10 pr-4 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-[#0c8ee7]"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-sm font-medium text-zinc-400 mb-3">Knowledge Catalog</h2>
          <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
            {catalogItems.length > 0 ? (
              <div className="space-y-1">
                {catalogItems.map((name) => (
                  <div
                    key={name}
                    className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-zinc-300 hover:bg-zinc-800/50 cursor-pointer"
                  >
                    <BookOpen size={15} className="text-zinc-500 shrink-0" />
                    <span className="flex-1">{name}</span>
                    <ExternalLink size={13} className="text-zinc-600" />
                  </div>
                ))}
              </div>
            ) : (
              <p className="py-6 text-center text-sm text-zinc-600">
                No knowledge catalog. Import a project to build one.
              </p>
            )}
          </div>
        </div>

        <div>
          <h2 className="text-sm font-medium text-zinc-400 mb-3">Knowledge Events</h2>
          <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4 max-h-80 overflow-y-auto">
            {events?.events && events.events.length > 0 ? (
              <div className="space-y-1">
                {events.events.map((ev: unknown, i: number) => {
                  const e = ev as { type?: string; origin?: string; timestamp?: number };
                  return (
                    <div key={(ev as { id?: string }).id ?? i} className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm">
                      <Box size={12} className="text-zinc-600" />
                      <span className="text-zinc-400 truncate">{e.type ?? 'event'}</span>
                      <span className="text-zinc-600 text-xs ml-auto">{e.origin}</span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="py-6 text-center text-sm text-zinc-600">No events yet</p>
            )}
          </div>
        </div>
      </div>

      {searchResults && searchResults.results.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-zinc-400 mb-3">Search Results</h2>
          <div className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] p-4">
            <div className="space-y-1">
              {searchResults.results.map((r, i) => (
                <div key={i} className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm">
                  <FileText size={12} className="text-zinc-600" />
                  <span className="text-zinc-300 truncate">{r.label}</span>
                  <span className="text-[10px] text-zinc-600 ml-auto">{r.type}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
