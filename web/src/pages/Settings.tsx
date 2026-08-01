import { motion } from 'framer-motion';
import { Settings as SettingsIcon, Monitor, Globe, Palette, Cpu, Bell, Shield, Database } from 'lucide-react';

const settingsGroups = [
  {
    title: 'General',
    icon: Monitor,
    items: [
      { label: 'Workspace Path', value: '~/Genesis' },
      { label: 'Language', value: 'English' },
      { label: 'Theme', value: 'System' },
    ],
  },
  {
    title: 'Appearance',
    icon: Palette,
    items: [
      { label: 'Dark Mode', value: 'On' },
      { label: 'Accent Color', value: 'Blue' },
      { label: 'Font Size', value: '14px' },
    ],
  },
  {
    title: 'Server',
    icon: Globe,
    items: [
      { label: 'Host', value: '127.0.0.1' },
      { label: 'Port', value: '8080' },
      { label: 'Auth', value: 'Disabled' },
    ],
  },
  {
    title: 'System',
    icon: Cpu,
    items: [
      { label: 'Auto-start Server', value: 'Off' },
      { label: 'Notifications', value: 'On' },
      { label: 'Telemetry', value: 'Off' },
    ],
  },
];

export default function SettingsPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 max-w-2xl"
    >
      <h1 className="text-lg font-semibold text-white">Settings</h1>

      <div className="space-y-4">
        {settingsGroups.map((group) => (
          <div key={group.title} className="rounded-xl border border-[#1a1a1a] bg-[#0f0f0f] overflow-hidden">
            <div className="flex items-center gap-2 border-b border-[#1a1a1a] px-4 py-3">
              <group.icon size={15} className="text-zinc-500" />
              <h2 className="text-sm font-medium text-zinc-400">{group.title}</h2>
            </div>
            <div className="divide-y divide-[#1a1a1a]">
              {group.items.map((item) => (
                <div key={item.label} className="flex items-center justify-between px-4 py-3">
                  <span className="text-sm text-zinc-400">{item.label}</span>
                  <span className="text-sm text-zinc-600">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <p className="text-xs text-zinc-600">
        Settings are managed through the CLI. Run <code className="text-[#0c8ee7]">genesis config</code> to view or <code className="text-[#0c8ee7]">genesis setup</code> to change.
      </p>
    </motion.div>
  );
}
