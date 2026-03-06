import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { signOut } from "firebase/auth";
import {
  Menu,
  Search,
  Bell,
  User,
  Settings as SettingsIcon,
  LogOut,
  Moon,
  Sun,
} from "lucide-react";

import { auth } from "../lib/firebase";
import useAuthStore from "../store/useAuthStore";
import useUIStore from "../store/useUIStore";
import UserAvatar from "./Navigation/UserAvatar";

const Topbar = ({ onOpenSidebar }) => {
  const navigate = useNavigate();
  const logout = useAuthStore((state) => state.logout);
  const { theme, toggleTheme } = useUIStore();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const toggleDropdown = () => setIsDropdownOpen(!isDropdownOpen);

  const handleLogout = async () => {
    try {
      await signOut(auth);
      logout();
      navigate("/auth");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-30 h-20 glass border-b border-gray-200/50 dark:border-white/5 flex items-center justify-between px-6 md:px-10 transition-all duration-300">
      <div className="flex items-center gap-4">
        <button
          onClick={onOpenSidebar}
          className="p-2.5 -ml-2.5 lg:hidden text-gray-500 hover:bg-white/50 dark:hover:bg-white/5 rounded-2xl transition-all active:scale-90"
        >
          <Menu size={22} />
        </button>

        <div className="hidden md:flex items-center gap-2 px-4 py-2 rounded-2xl bg-gray-100/50 dark:bg-white/5 border border-transparent focus-within:border-blue-500/20 focus-within:bg-white dark:focus-within:bg-gray-900 transition-all">
          <Search size={16} className="text-gray-400" />
          <input
            type="text"
            placeholder="Search schemes..."
            className="bg-transparent border-none focus:ring-0 text-sm w-48 text-gray-900 dark:text-white placeholder:text-gray-500"
          />
        </div>
      </div>

      <div className="flex items-center gap-4 md:gap-6">
        <button className="relative p-2.5 text-gray-500 hover:bg-white/50 dark:hover:bg-white/5 rounded-2xl transition-all group">
          <Bell
            size={20}
            className="group-hover:rotate-12 transition-transform"
          />
          <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-gray-900" />
        </button>

        <div className="h-8 w-[1px] bg-gray-200 dark:bg-white/10 mx-1 hidden sm:block" />

        <div className="relative" ref={dropdownRef}>
          <button
            onClick={toggleDropdown}
            className="flex items-center gap-3 p-1 pr-3 rounded-2xl hover:bg-white/50 dark:hover:bg-white/5 transition-all active:scale-95 group"
          >
            <UserAvatar size="sm" />
            <div className="hidden sm:block text-left">
              <p className="text-xs font-bold text-gray-900 dark:text-white leading-none mb-0.5">
                Profile
              </p>
              <p className="text-[10px] text-gray-500 truncate max-w-[80px]">
                Settings
              </p>
            </div>
          </button>

          {/* Dropdown Menu */}
          {isDropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 rounded-xl shadow-lg bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 overflow-hidden py-1 animate-in fade-in zoom-in duration-200">
              <button
                onClick={() => {
                  navigate("/dashboard/profile");
                  setIsDropdownOpen(false);
                }}
                className="flex items-center gap-3 w-full px-4 py-3 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <User size={16} />
                Profile
              </button>
              <button
                onClick={() => {
                  setIsDropdownOpen(false);
                }}
                className="flex items-center gap-3 w-full px-4 py-3 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <SettingsIcon size={16} />
                Settings
              </button>
              <button
                onClick={() => {
                  toggleTheme();
                  setIsDropdownOpen(false);
                }}
                className="flex items-center gap-3 w-full px-4 py-3 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                {theme === "light" ? <Moon size={16} /> : <Sun size={16} />}
                Change Theme
              </button>
              <div className="h-[1px] bg-gray-100 dark:bg-gray-800 my-1" />
              <button
                onClick={handleLogout}
                className="flex items-center gap-3 w-full px-4 py-3 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors font-medium"
              >
                <LogOut size={16} />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Topbar;
