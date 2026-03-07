import { useState, useRef, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Mic, MicOff, Send, Sparkles, AlertCircle, RotateCcw, BarChart2, ExternalLink, CheckCircle2, FileText } from "lucide-react";
import useUIStore from "../../store/useUIStore";
import useConversationStore from "../../store/useConversationStore";
import { t } from "../../lib/i18n";

// ── Language → BCP-47 locale map ─────────────────────────────────
const LOCALE_MAP = { en: "en-IN", hi: "hi-IN", mr: "mr-IN" };
const VOICE_CONFIDENCE_THRESHOLD = 0.7;

const LOW_CONFIDENCE_MSG = {
  en: "I didn't catch that clearly. Could you please repeat?",
  hi: "मुझे स्पष्ट रूप से समझ नहीं आया। कृपया दोहराएं?",
  mr: "मला स्पष्टपणे समजले नाही. कृपया पुन्हा सांगा?",
};

// ── Voice output helper ──────────────────────────────────────────
function speak(text, locale) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utt = new SpeechSynthesisUtterance(text);
  utt.lang = locale;
  utt.rate = 0.95;
  utt.pitch = 1;
  utt.volume = 1;

  const voices = window.speechSynthesis.getVoices();
  const preferred =
    voices.find((v) => v.lang === locale) ||
    voices.find((v) => v.lang.startsWith(locale.split("-")[0])) ||
    null;
  if (preferred) utt.voice = preferred;

  window.speechSynthesis.speak(utt);
}

// ── Welcome message ──────────────────────────────────────────────
const WELCOME = {
  en: "Hello! I'm SamvaadAI. Tell me about yourself — your age, occupation, income, and location — and I'll find government schemes you may be eligible for.",
  hi: "नमस्ते! मैं SamvaadAI हूँ। मुझे अपने बारे में बताएं — आपकी उम्र, पेशा, आय और स्थान — और मैं आपके लिए सरकारी योजनाएं खोजूंगा।",
  mr: "नमस्कार! मी SamvaadAI आहे. मला तुमच्याबद्दल सांगा — तुमचे वय, व्यवसाय, उत्पन्न आणि स्थान — आणि मी तुम्हाला सरकारी योजना शोधून देतो.",
};

export default function Chat() {
  const navigate = useNavigate();
  const language = useUIStore((s) => s.language);
  const locale = LOCALE_MAP[language] ?? "en-IN";

  // ── Store ──────────────────────────────────────────────────────
  const messages = useConversationStore((s) => s.messages);
  const isLoading = useConversationStore((s) => s.isLoading);
  const error = useConversationStore((s) => s.error);
  const eligibility = useConversationStore((s) => s.eligibility);
  const schemes = useConversationStore((s) => s.schemes);
  const documents = useConversationStore((s) => s.documents);
  const sendMessage = useConversationStore((s) => s.sendMessage);
  const clearError = useConversationStore((s) => s.clearError);
  const resetConversation = useConversationStore((s) => s.resetConversation);

  // Check if we have eligibility results to show
  const hasResults =
    eligibility &&
    (eligibility.eligible?.length > 0 ||
      eligibility.partiallyEligible?.length > 0 ||
      eligibility.ineligible?.length > 0);

  // ── Local UI state ─────────────────────────────────────────────
  const [input, setInput] = useState("");
  const [isListening, setIsListening] = useState(false);

  // ── Refs ───────────────────────────────────────────────────────
  const bottomRef = useRef(null);
  const recognitionRef = useRef(null);
  const inputRef = useRef(null);

  // ── Scroll to bottom on new messages ───────────────────────────
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // ── Speak welcome on mount ─────────────────────────────────────
  useEffect(() => {
    if (messages.length === 0) {
      speak(WELCOME[language] || WELCOME.en, locale);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Speak assistant responses ──────────────────────────────────
  useEffect(() => {
    const last = messages[messages.length - 1];
    if (last?.role === "assistant") {
      speak(last.content, locale);
    }
  }, [messages, locale]);

  // ── Cleanup on unmount ─────────────────────────────────────────
  useEffect(() => {
    return () => {
      recognitionRef.current?.abort();
      window.speechSynthesis?.cancel();
    };
  }, []);

  // ── Send handler ───────────────────────────────────────────────
  const handleSend = useCallback(
    async (text) => {
      const value = (text || input).trim();
      if (!value || isLoading) return;

      // Stop speech recognition if active
      if (recognitionRef.current) {
        recognitionRef.current.abort();
        recognitionRef.current = null;
        setIsListening(false);
      }

      // Stop any ongoing speech output
      window.speechSynthesis?.cancel();

      setInput("");
      clearError();
      await sendMessage(value, language);
    },
    [input, isLoading, language, sendMessage, clearError],
  );

  // ── Voice toggle ───────────────────────────────────────────────
  const toggleListening = useCallback(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      // Graceful mic permission error (Phase 5)
      useConversationStore.setState({
        error: "Speech recognition is not supported in this browser. Please type your message instead.",
      });
      return;
    }

    if (recognitionRef.current) {
      recognitionRef.current.abort();
      recognitionRef.current = null;
      setIsListening(false);
      return;
    }

    const rec = new SR();
    rec.lang = locale;
    rec.interimResults = true;
    rec.maxAlternatives = 3;

    rec.onstart = () => setIsListening(true);

    rec.onresult = (e) => {
      const result = e.results[e.results.length - 1];
      // Show interim text in input
      const interim = result[0]?.transcript || "";
      setInput(interim);

      if (!result.isFinal) return;

      // Pick best confidence transcript
      let bestTranscript = "";
      let bestConfidence = -1;
      for (let i = 0; i < result.length; i++) {
        if (result[i].confidence > bestConfidence) {
          bestConfidence = result[i].confidence;
          bestTranscript = result[i].transcript;
        }
      }
      const cleaned = bestTranscript.trim();

      // Voice confidence guard
      if (bestConfidence < VOICE_CONFIDENCE_THRESHOLD && bestConfidence > 0) {
        const msg = LOW_CONFIDENCE_MSG[language] || LOW_CONFIDENCE_MSG.en;
        speak(msg, locale);
        setInput("");
        // Show the low-confidence message as a system note
        useConversationStore.setState((state) => ({
          messages: [...state.messages, { role: "assistant", content: msg }],
        }));
        return;
      }

      if (cleaned) handleSend(cleaned);
    };

    rec.onerror = (e) => {
      setIsListening(false);
      recognitionRef.current = null;

      // Graceful mic permission error handling (Phase 5)
      if (e.error === "not-allowed") {
        useConversationStore.setState({
          error: "Microphone access was denied. Please enable it in browser settings.",
        });
      }
    };

    rec.onend = () => {
      setIsListening(false);
      recognitionRef.current = null;
    };

    recognitionRef.current = rec;
    rec.start();
  }, [locale, handleSend]);

  // ── Build display messages (add welcome if empty) ──────────────
  const displayMessages =
    messages.length === 0
      ? [{ role: "assistant", content: WELCOME[language] || WELCOME.en }]
      : messages;

  return (
    <div className="relative flex flex-col h-[calc(100vh-140px)] bg-transparent">
      {/* ── Listening Pulse Overlay ── */}
      {isListening && (
        <div className="fixed inset-0 flex items-center justify-center pointer-events-none z-50">
          <div className="relative">
            <div className="absolute inset-0 scale-[3] bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
            <div className="relative h-32 w-32 bg-blue-600 rounded-full flex items-center justify-center shadow-2xl shadow-blue-600/50">
              <Mic size={48} className="text-white animate-bounce" />
            </div>
          </div>
        </div>
      )}

      {/* ── Message Thread ── */}
      <div className="flex-1 overflow-y-auto px-4 py-8 space-y-8 max-w-4xl mx-auto w-full">
        {displayMessages.map((msg, i) => (
          <div
            key={i}
            className={`flex animate-in fade-in slide-in-from-bottom-2 duration-500 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.role === "assistant" && (
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shrink-0 mr-3 mt-auto shadow-lg shadow-blue-600/20">
                <Sparkles size={14} className="text-white" />
              </div>
            )}
            <div
              className={`max-w-[80%] px-6 py-4 rounded-[2rem] text-sm leading-relaxed shadow-xl ${msg.role === "user"
                ? "bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-tr-none shadow-blue-600/20"
                : "bg-white/80 dark:bg-gray-900/80 backdrop-blur-md text-gray-900 dark:text-gray-100 dark:border dark:border-white/5 rounded-tl-none shadow-black/5"
                }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {/* ── Processing Indicator (Phase 6) ── */}
        {isLoading && (
          <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600/20 flex items-center justify-center shrink-0 mr-3 mt-auto">
              <Sparkles size={14} className="text-blue-600 animate-pulse" />
            </div>
            <div className="flex items-center gap-3 px-6 py-4 rounded-[2rem] rounded-tl-none bg-white/50 dark:bg-gray-900/50 backdrop-blur-md border border-white/10 shadow-xl">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-bounce" />
              <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-bounce [animation-delay:150ms]" />
              <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-bounce [animation-delay:300ms]" />
              <span className="text-xs text-gray-400 font-medium ml-2">
                {t("processing", language)}
              </span>
            </div>
          </div>
        )}

        {/* ── Error Display (Phase 8) ── */}
        {error && (
          <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2">
            <div className="w-8 h-8 rounded-lg bg-red-500/20 flex items-center justify-center shrink-0 mr-3 mt-auto">
              <AlertCircle size={14} className="text-red-500" />
            </div>
            <div className="max-w-[80%] px-6 py-4 rounded-[2rem] rounded-tl-none bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 shadow-xl">
              <p className="text-sm text-red-700 dark:text-red-400 font-medium">
                {error}
              </p>
              <button
                onClick={() => {
                  clearError();
                  // Retry the last user message
                  const lastUser = [...messages]
                    .reverse()
                    .find((m) => m.role === "user");
                  if (lastUser) handleSend(lastUser.content);
                }}
                className="mt-2 flex items-center gap-1.5 text-xs font-bold text-red-600 dark:text-red-400 hover:underline"
              >
                <RotateCcw size={12} />
                {t("try_again", language)}
              </button>
            </div>
          </div>
        )}

        <div ref={bottomRef} className="h-20" />
      </div>

      {/* ── Scheme Cards ── */}
      {schemes.length > 0 && !isLoading && (
        <div className="px-6 pb-2">
          <div className="max-w-4xl mx-auto">
            <p className="text-[10px] uppercase tracking-wider font-bold text-gray-400 mb-2 px-1">
              {t("eligible_schemes", language) || "Eligible Schemes"}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {schemes.map((scheme, idx) => (
                <div
                  key={scheme.id || idx}
                  className="glass rounded-2xl p-4 border border-white/10 shadow-lg animate-in fade-in slide-in-from-bottom-2 duration-500"
                  style={{ animationDelay: `${idx * 100}ms` }}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <h4 className="font-bold text-sm text-gray-900 dark:text-white">{scheme.name}</h4>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">{scheme.benefit}</p>
                    </div>
                    <span className={`shrink-0 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${scheme.status === "eligible"
                        ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                        : "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                      }`}>
                      {scheme.status === "eligible" ? "✓ Eligible" : "~ Partial"}
                    </span>
                  </div>
                  {scheme.url && (
                    <a
                      href={scheme.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-3 flex items-center gap-1.5 text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      <ExternalLink size={12} />
                      {t("apply_now", language) || "Apply Now"}
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Document Checklist ── */}
      {documents.length > 0 && !isLoading && (
        <div className="px-6 pb-2">
          <div className="max-w-4xl mx-auto glass rounded-2xl p-4 border border-white/10 shadow-lg">
            <p className="flex items-center gap-2 text-[10px] uppercase tracking-wider font-bold text-gray-400 mb-3">
              <FileText size={12} />
              {t("required_documents", language) || "Required Documents"}
            </p>
            <ul className="space-y-2">
              {documents.map((doc, idx) => (
                <li key={idx} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                  <CheckCircle2 size={14} className="text-emerald-500 shrink-0" />
                  {doc}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* ── View Results Floating CTA ── */}
      {hasResults && !isLoading && (
        <div className="px-6 pb-2">
          <div className="max-w-3xl mx-auto">
            <button
              id="view-results-cta"
              onClick={() => navigate("/dashboard/results")}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-bold text-sm hover:bg-emerald-500/20 transition-all animate-in fade-in slide-in-from-bottom-2 duration-500"
            >
              <BarChart2 size={16} />
              {t("view_results", language)}
            </button>
          </div>
        </div>
      )}

      {/* ── Floating Input Dock ── */}
      <div className="px-6 pb-8">
        <div className="max-w-3xl mx-auto glass rounded-[2.5rem] p-3 shadow-2xl shadow-black/10 transition-all focus-within:ring-2 focus-within:ring-blue-500/20">
          <div className="flex flex-col gap-3">
            {/* Voice Toggle */}
            <div className="flex items-center justify-between px-3">
              <p className="text-[10px] uppercase tracking-wider font-bold text-gray-400">
                {isLoading ? t("processing", language) : t("assistant_active", language)}
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    resetConversation();
                    speak(WELCOME[language] || WELCOME.en, locale);
                  }}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[10px] font-bold tracking-wide uppercase bg-gray-100 dark:bg-white/5 text-gray-500 hover:bg-gray-200 dark:hover:bg-white/10 transition-all"
                >
                  <RotateCcw size={10} />
                  {t("new_conversation", language)}
                </button>
                <button
                  onClick={toggleListening}
                  disabled={isLoading}
                  className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-[10px] font-bold tracking-wide uppercase transition-all ${isListening
                    ? "bg-red-500 text-white shadow-lg shadow-red-500/30"
                    : "bg-blue-600/10 text-blue-600 hover:bg-blue-600/20 disabled:opacity-30"
                    }`}
                >
                  {isListening ? <MicOff size={12} /> : <Mic size={12} />}
                  {isListening ? t("listening", language) : t("tap_to_speak", language)}
                </button>
              </div>
            </div>

            {/* Text Input */}
            <div className="flex items-center gap-2 px-1">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                disabled={isLoading}
                placeholder={
                  isLoading
                    ? t("waiting_for_response", language)
                    : t("tell_about_yourself", language)
                }
                className="flex-1 px-5 py-3 rounded-full bg-gray-100/50 dark:bg-white/5 border-none focus:ring-0 text-sm text-gray-900 dark:text-white placeholder:text-gray-500 font-medium disabled:opacity-50"
              />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className="p-3 rounded-full bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-20 transition-all shadow-lg shadow-blue-600/30 active:scale-90"
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
