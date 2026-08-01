import { Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { wsClient } from './lib/websocket';
import { useUIStore } from './lib/store';
import Layout from './components/Layout';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Project from './pages/Project';
import Knowledge from './pages/Knowledge';
import Timeline from './pages/Timeline';
import Terminal from './pages/Terminal';
import Copilot from './pages/Copilot';
import Search from './pages/Search';
import Settings from './pages/Settings';

export default function App() {
  const setWsConnected = useUIStore((s) => s.setWsConnected);

  useEffect(() => {
    wsClient.connect();
    const unsub = wsClient.on('_connected', () => setWsConnected(true));
    const unsub2 = wsClient.on('_disconnected', () => setWsConnected(false));
    return () => {
      unsub();
      unsub2();
      wsClient.disconnect();
    };
  }, [setWsConnected]);

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/desktop" element={<Dashboard />} />
        <Route path="/app" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/project/:name" element={<Project />} />
        <Route path="/knowledge" element={<Knowledge />} />
        <Route path="/timeline" element={<Timeline />} />
        <Route path="/terminal" element={<Terminal />} />
        <Route path="/copilot" element={<Copilot />} />
        <Route path="/search" element={<Search />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
