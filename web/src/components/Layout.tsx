import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import StatusBar from './StatusBar';
import SearchDialog from './SearchDialog';
import CopilotPanel from './CopilotPanel';
import { useUIStore } from '../lib/store';

export default function Layout() {
  const searchOpen = useUIStore((s) => s.searchOpen);
  const copilotOpen = useUIStore((s) => s.copilotOpen);
  const sidebarOpen = useUIStore((s) => s.sidebarOpen);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-black">
      <Sidebar />
      <div className="flex flex-1 flex-col min-w-0">
        <main
          className={`flex-1 overflow-auto transition-all duration-200 ${
            sidebarOpen ? 'ml-60' : 'ml-0'
          }`}
        >
          <div className="mx-auto max-w-7xl p-6">
            <Outlet />
          </div>
        </main>
        <StatusBar />
      </div>
      {searchOpen && <SearchDialog />}
      {copilotOpen && <CopilotPanel />}
    </div>
  );
}
