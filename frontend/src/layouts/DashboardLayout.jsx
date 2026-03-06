import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import BackgroundBlobs from "../components/Visuals/BackgroundBlobs";

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white dark:bg-black selection:bg-blue-100 dark:selection:bg-blue-900 transition-colors duration-300">
      <BackgroundBlobs />

      {/* Sidebar Navigation */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Wrapper */}
      <div className="flex flex-col min-h-screen lg:pl-[260px] transition-all duration-500 ease-in-out">
        {/* Top Header */}
        <Topbar onOpenSidebar={() => setSidebarOpen(true)} />

        {/* Scrollable Main Area */}
        <main className="flex-1 overflow-y-auto px-6 py-10 md:px-12 md:py-16">
          <div className="max-w-6xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
