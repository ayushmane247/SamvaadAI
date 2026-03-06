import { NavLink } from "react-router-dom";
import { MessageSquare, BarChart2, X, LayoutDashboard } from "lucide-react";

const Sidebar = ({ isOpen, onClose }) => {
  const navItems = [
    { name: "Overview", path: "/dashboard", icon: LayoutDashboard },
    { name: "Chat", path: "/dashboard/chat", icon: MessageSquare },
    { name: "Results", path: "/dashboard/results", icon: BarChart2 },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      <div
        className={`fixed inset-0 z-40 bg-black/40 backdrop-blur-sm transition-opacity lg:hidden ${
          isOpen
            ? "opacity-100 pointer-events-auto"
            : "opacity-0 pointer-events-none"
        }`}
        onClick={onClose}
      />

      {/* Sidebar Panel */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-[260px] glass border-r border-white/10 transform transition-transform duration-500 cubic-bezier(0.4, 0, 0.2, 1) lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between h-20 px-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-600/20">
              <span className="text-white font-bold text-xs">S</span>
            </div>
            <span className="text-xl font-bold tracking-tight text-gray-900 dark:text-white">
              SamvaadAI
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-2 lg:hidden text-gray-500 hover:bg-gray-100 dark:hover:bg-white/5 rounded-xl transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onClose}
              end={item.path === "/dashboard"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium transition-all duration-300 group relative overflow-hidden ${
                  isActive
                    ? "text-blue-600 dark:text-white"
                    : "text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <div className="absolute inset-0 bg-blue-600/10 dark:bg-blue-600/20" />
                  )}
                  <item.icon
                    size={18}
                    className={`relative z-10 transition-transform duration-300 group-hover:scale-110 ${isActive ? "text-blue-600 dark:text-blue-400" : ""}`}
                  />
                  <span className="relative z-10">{item.name}</span>
                  {isActive && (
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-blue-600 rounded-l-full shadow-[0_0_10px_#2563eb]" />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;
