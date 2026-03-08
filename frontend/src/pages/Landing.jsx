import { Link } from "react-router-dom";
import {
  Mic,
  MessageSquare,
  CheckSquare,
  Languages,
  Zap,
  Landmark,
  ShieldCheck,
} from "lucide-react";

// Note: Ensure samvaad-hero-illustration.png is placed in d:/SamvaadAI/frontend/src/assets/
// Place samvaad-hero-illustration.png inside frontend/public/ and it will load automatically.
// const heroIllustration = "/samvaad-hero-illustration.png";

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#f8fafc] dark:bg-slate-950 transition-colors">
      <style>{`
        @keyframes float {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
          100% { transform: translateY(0px); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-float {
          animation: float 4s ease-in-out infinite;
        }
        .animate-fade-in {
          animation: fadeIn 0.8s ease-out forwards;
        }
      `}</style>
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50">
        <div className="max-w-6xl mx-auto mt-6 px-6 py-3 rounded-full bg-white/70 dark:bg-slate-900/70 backdrop-blur-md shadow-md flex items-center justify-between border border-white/20 dark:border-slate-800/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
              S
            </div>
            <span className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
              SamvaadAI
            </span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <a
              href="#how-it-works"
              className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors relative group"
            >
              How It Works
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all group-hover:w-full"></span>
            </a>
            <a
              href="#schemes"
              className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors relative group"
            >
              Schemes
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all group-hover:w-full"></span>
            </a>
            <a
              href="#about"
              className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors relative group"
            >
              About
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all group-hover:w-full"></span>
            </a>
          </div>

          <Link
            to="/auth"
            className="bg-blue-600 text-white px-5 py-2 rounded-full font-semibold hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/20 active:scale-95 text-sm"
          >
            Login / Register
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
<section
  className="relative min-h-[100vh] flex items-center"
  style={{
    backgroundImage: "url('/SamvaadAI.jpeg')",
    backgroundSize: "cover",
    backgroundPosition: "center top",
    backgroundRepeat: "no-repeat"
  }}
>
  {/* Overlay for readability */}
  <div className="absolute inset-0 bg-white/30 dark:bg-slate-950/30"></div>

  {/* Content */}
  <div className="relative z-10 max-w-7xl mx-auto px-6 w-full">
    <div className="max-w-xl">

      <h1 className="text-5xl md:text-6xl font-extrabold text-slate-900 dark:text-white leading-tight">
        Explore Indian
        <span className="text-black-600 block">Government Schemes</span>
        With SamvaadAI
      </h1>

      <p className="mt-6 text-lg text-black-600 dark:text-gray-300">
        Talk in your language, Discover your benefits,
        Avoid middlemen. Try now.
      </p>

      <div className="mt-8 flex gap-4">
        <Link 
        to ="/auth">
        <button className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-full font-semibold shadow-lg">
          Get Started with Voice
        </button> 
        </Link>

        {/* <link rel="stylesheet" href="" />
        <button className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-full font-semibold shadow-lg">
          Get Started with Voice
        </button> */}

        <button className="px-6 py-3 rounded-full border-gray-300 dark:border-gray-700 bg-green-500 hover:bg-green-600 text-white">
          Learn More
        </button>
      </div>

    </div>
  </div>
</section>

      {/* How It Works Section */}
      <section id="how-it-works" className="px-6 py-16">
        <div className="max-w-5xl mx-auto bg-gray-200 dark:bg-slate-900 rounded-3xl shadow-2xl shadow-slate-200 dark:shadow-black/50 border border-gray-200/50 dark:border-slate-800/50 p-8 md:p-12 text-center animate-fade-in [animation-delay:0.5s]">
          <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 dark:text-white mb-12">
            How it works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative">
            {/* Step 1 */}
            <div className="flex flex-col items-center space-y-4 group">
              <div className="w-16 h-16 bg-blue-50 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center text-blue-600 dark:text-blue-400 group-hover:scale-110 transition-transform">
                <Mic size={32} />
              </div>
              <p className="text-lg font-bold text-slate-800 dark:text-slate-200 leading-snug">
                1. Speak or Type in <br /> Your Language
              </p>
            </div>

            {/* Step 2 */}
            <div className="flex flex-col items-center space-y-4 group">
              <div className="w-16 h-16 bg-orange-50 dark:bg-orange-900/30 rounded-2xl flex items-center justify-center text-orange-600 dark:text-orange-400 group-hover:scale-110 transition-transform">
                <MessageSquare size={32} />
              </div>
              <p className="text-lg font-bold text-slate-800 dark:text-slate-200 leading-snug">
                2. Get Adaptive <br /> Questions
              </p>
            </div>

            {/* Step 3 */}
            <div className="flex flex-col items-center space-y-4 group">
              <div className="w-16 h-16 bg-green-50 dark:bg-green-900/30 rounded-2xl flex items-center justify-center text-green-600 dark:text-green-400 group-hover:scale-110 transition-transform">
                <CheckSquare size={32} />
              </div>
              <p className="text-lg font-bold text-slate-800 dark:text-slate-200 leading-snug">
                3. View Your <br /> Eligible Schemes
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-16 bg-white dark:bg-slate-950 border-t border-slate-100 dark:border-slate-900">
        <div className="max-w-6xl mx-auto py-8 px-6 flex flex-col sm:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-8 order-2 sm:order-1">
            <a
              href="#"
              className="text-sm font-medium text-slate-500 hover:text-blue-600 transition-colors"
            >
              Privacy Policy
            </a>
            <a
              href="#"
              className="text-sm font-medium text-slate-500 hover:text-blue-600 transition-colors"
            >
              Contact Us
            </a>
          </div>
          <div className="flex items-center gap-2 order-1 sm:order-2">
            <div className="w-6 h-6 bg-slate-900 dark:bg-white rounded flex items-center justify-center text-white dark:text-slate-900 text-[10px] font-bold">
              S
            </div>
            <span className="text-base font-bold text-slate-900 dark:text-white">
              SamvaadAI
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
