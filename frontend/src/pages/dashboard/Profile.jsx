import { useNavigate } from "react-router-dom";
import { signOut } from "firebase/auth";
import { User, Mail, Globe, LogOut, Edit2 } from "lucide-react";
import { auth } from "../../lib/firebase";
import useAuthStore from "../../store/useAuthStore";
import useUIStore from "../../store/useUIStore";

export default function Profile() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { language } = useUIStore();

  const handleLogout = async () => {
    try {
      await signOut(auth);
      logout();
      navigate("/auth");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const photoURL =
    user?.photoURL ||
    `https://ui-avatars.com/api/?name=${encodeURIComponent(user?.displayName || "User")}&background=0D8ABC&color=fff&bold=true&size=128`;

  const languageNames = {
    en: "English",
    hi: "Hindi",
    mr: "Marathi",
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-8 rounded-3xl shadow-xl bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Profile Header */}
      <div className="flex flex-col items-center text-center space-y-4">
        <div className="relative group">
          <img
            src={photoURL}
            alt={user?.displayName}
            className="w-32 h-32 rounded-full object-cover border-4 border-white dark:border-gray-800 shadow-lg group-hover:opacity-90 transition-opacity"
          />
          <button className="absolute bottom-0 right-0 p-2 bg-blue-600 rounded-full text-white shadow-lg hover:scale-110 active:scale-95 transition-all">
            <Edit2 size={16} />
          </button>
        </div>

        <div className="space-y-1">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {user?.displayName || "Guest User"}
          </h2>
          <p className="text-sm text-gray-500 font-medium">Account Settings</p>
        </div>
      </div>

      {/* Info Sections */}
      <div className="mt-8 space-y-4">
        <div className="flex items-center gap-4 p-4 rounded-2xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-white/5 transition-all hover:bg-white dark:hover:bg-gray-800 shadow-sm">
          <div className="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600">
            <User size={20} />
          </div>
          <div className="flex-1">
            <p className="text-[10px] uppercase font-black tracking-widest text-gray-400">
              Full Name
            </p>
            <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">
              {user?.displayName || "Not set"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 p-4 rounded-2xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-white/5 transition-all hover:bg-white dark:hover:bg-gray-800 shadow-sm">
          <div className="w-10 h-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600">
            <Mail size={20} />
          </div>
          <div className="flex-1">
            <p className="text-[10px] uppercase font-black tracking-widest text-gray-400">
              Email Address
            </p>
            <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">
              {user?.email || "Not set"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 p-4 rounded-2xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-white/5 transition-all hover:bg-white dark:hover:bg-gray-800 shadow-sm">
          <div className="w-10 h-10 rounded-xl bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center text-orange-600">
            <Globe size={20} />
          </div>
          <div className="flex-1">
            <p className="text-[10px] uppercase font-black tracking-widest text-gray-400">
              Preferred Language
            </p>
            <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">
              {languageNames[language] || "English"}
            </p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-8 space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <button className="px-4 py-3 rounded-2xl border border-gray-200 dark:border-white/5 text-sm font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/10 transition-colors">
            Edit Profile
          </button>
          <button className="px-4 py-3 rounded-2xl border border-gray-200 dark:border-white/5 text-sm font-bold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/10 transition-colors">
            Change Language
          </button>
        </div>

        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 px-6 py-4 rounded-2xl bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400 font-bold text-sm hover:bg-red-600 hover:text-white dark:hover:bg-red-500 transition-all group"
        >
          <LogOut
            size={18}
            className="group-hover:-translate-x-1 transition-transform"
          />
          Logout from SamvaadAI
        </button>
      </div>
    </div>
  );
}
