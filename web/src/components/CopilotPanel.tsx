import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Bot, User, Loader2 } from 'lucide-react';
import { useUIStore } from '../lib/store';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function CopilotPanel() {
  const { setCopilotOpen } = useUIStore();
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hello! I\'m your Engineering Copilot. Ask me anything about your projects, code, or engineering data.' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    // Use the search API as a simple proxy for now
    try {
      const res = await fetch(`/v1/search?query=${encodeURIComponent(userMsg)}&limit=5`);
      const data = await res.json();
      const resultText = data.results?.length
        ? `I found ${data.count} result(s):\n` + data.results.map((r: { label: string }) => `• ${r.label}`).join('\n')
        : 'No results found. Try rephrasing your question.';
      setMessages((prev) => [...prev, { role: 'assistant', content: resultText }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ]);
    }
    setLoading(false);
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: 300 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 300 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        className="fixed bottom-10 right-4 z-40 flex h-[500px] w-96 flex-col rounded-xl border border-[#232323] bg-[#141414] shadow-2xl"
      >
        <div className="flex items-center justify-between border-b border-[#232323] px-4 py-3">
          <div className="flex items-center gap-2">
            <Bot size={16} className="text-[#0c8ee7]" />
            <span className="text-sm font-medium text-white">Engineering Copilot</span>
          </div>
          <button
            onClick={() => setCopilotOpen(false)}
            className="rounded-md p-1 text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300"
          >
            <X size={16} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-3">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role === 'assistant' && (
                <div className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#0c8ee7]/10">
                  <Bot size={14} className="text-[#0c8ee7]" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-xl px-3 py-2 text-sm ${
                  msg.role === 'user'
                    ? 'bg-[#0c8ee7] text-white'
                    : 'bg-zinc-800 text-zinc-200'
                }`}
              >
                <pre className="whitespace-pre-wrap font-sans text-sm">{msg.content}</pre>
              </div>
              {msg.role === 'user' && (
                <div className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-zinc-800">
                  <User size={14} className="text-zinc-400" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-2">
              <div className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#0c8ee7]/10">
                <Bot size={14} className="text-[#0c8ee7]" />
              </div>
              <div className="rounded-xl bg-zinc-800 px-3 py-2">
                <Loader2 size={14} className="animate-spin text-zinc-400" />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-[#232323] p-3">
          <div className="flex items-center gap-2 rounded-lg border border-[#333] bg-[#1a1a1a] px-3 py-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about your engineering data..."
              className="flex-1 bg-transparent text-sm text-white outline-none placeholder:text-zinc-600"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="rounded-md p-1 text-zinc-500 hover:text-[#0c8ee7] disabled:opacity-40"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
