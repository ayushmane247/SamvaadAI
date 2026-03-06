import { useState, useRef, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Mic, MicOff, Send, Sparkles } from "lucide-react";
import useUIStore from "../../store/useUIStore";

// ── Language → BCP-47 locale map ─────────────────────────────────────────────
const LOCALE_MAP = { en: "en-IN", hi: "hi-IN", mr: "mr-IN" };

// ── Question definitions ──────────────────────────────────────────────────────
const QUESTIONS = [
  {
    id: "occupation",
    text: "What is your occupation?",
    type: "options",
    options: ["Farmer", "Student", "Business", "Other"],
  },
  {
    id: "income",
    text: "What is your annual income? (in ₹)",
    type: "text",
    placeholder: "e.g. 250000",
  },
  {
    id: "land",
    text: "Do you own agricultural land?",
    type: "options",
    options: ["Yes", "No"],
  },
];

// ── Message builders ──────────────────────────────────────────────────────────
const aiMsg = (content) => ({ role: "ai", content });
const userMsg = (content) => ({ role: "user", content });

// ── Voice output helper ───────────────────────────────────────────────────────
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

export default function Chat() {
  const navigate = useNavigate();
  const language = useUIStore((s) => s.language);
  const locale = LOCALE_MAP[language] ?? "en-IN";

  // ── Core state ──────────────────────────────────────────────────────────────
  const [messages, setMessages] = useState(() => [aiMsg(QUESTIONS[0].text)]);
  const [questionStep, setQuestionStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);

  // ── Refs ────────────────────────────────────────────────────────────────────
  const bottomRef = useRef(null);
  const recognitionRef = useRef(null);
  const stateRef = useRef({ questionStep, answers, messages });

  useEffect(() => {
    stateRef.current = { questionStep, answers, messages };
  }, [questionStep, answers, messages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  useEffect(() => {
    speak(QUESTIONS[0].text, locale);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    return () => {
      recognitionRef.current?.abort();
      window.speechSynthesis?.cancel();
    };
  }, []);

  const handleAnswer = useCallback(
    (rawValue) => {
      const value = rawValue.trim();
      if (!value) return;

      if (recognitionRef.current) {
        recognitionRef.current.abort();
        recognitionRef.current = null;
        setIsListening(false);
      }

      const {
        questionStep: step,
        answers: prev,
        messages: msgs,
      } = stateRef.current;
      const currentQ = QUESTIONS[step];
      const updatedAnswers = { ...prev, [currentQ.id]: value };
      const nextStep = step + 1;
      const withUser = [...msgs, userMsg(value)];

      setInput("");

      if (nextStep < QUESTIONS.length) {
        setMessages(withUser);
        setQuestionStep(nextStep);
        setAnswers(updatedAnswers);
        setIsTyping(true);

        setTimeout(() => {
          const nextText = QUESTIONS[nextStep].text;
          setIsTyping(false);
          setMessages((m) => [...m, aiMsg(nextText)]);
          speak(nextText, locale);
        }, 900);
      } else {
        const closingText = "Thank you! Finding the best schemes for you…";
        setMessages([...withUser, aiMsg(closingText)]);
        setAnswers(updatedAnswers);
        speak(closingText, locale);

        setTimeout(() => {
          navigate("/dashboard/results", {
            state: { answers: updatedAnswers },
          });
        }, 1800);
      }
    },
    [locale, navigate],
  );

  const toggleListening = useCallback(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      alert("Speech recognition is not supported in this browser.");
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
      if (!result.isFinal) return;
      let bestTranscript = "";
      let bestConfidence = -1;
      for (let i = 0; i < result.length; i++) {
        if (result[i].confidence > bestConfidence) {
          bestConfidence = result[i].confidence;
          bestTranscript = result[i].transcript;
        }
      }
      const cleaned = bestTranscript
        .toLowerCase()
        .replace(/[^a-z0-9\u0900-\u097f\s]/g, "")
        .trim();
      const { questionStep: step } = stateRef.current;
      const currentQ = QUESTIONS[step];
      if (currentQ.type === "text") {
        setInput(cleaned);
      } else {
        const match = currentQ.options.find((opt) =>
          cleaned.includes(opt.toLowerCase()),
        );
        handleAnswer(match ?? cleaned);
      }
    };
    rec.onerror = () => {
      setIsListening(false);
      recognitionRef.current = null;
    };
    rec.onend = () => {
      setIsListening(false);
      recognitionRef.current = null;
    };
    recognitionRef.current = rec;
    rec.start();
  }, [locale, handleAnswer]);

  const currentQuestion = QUESTIONS[questionStep];
  const isComplete = questionStep >= QUESTIONS.length;
  const inputDockLocked = isComplete || isTyping;

  return (
    <div className="relative flex flex-col h-[calc(100vh-140px)] bg-transparent">
      {/* ── Listening Pulse View ── */}
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
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex animate-in fade-in slide-in-from-bottom-2 duration-500 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.role === "ai" && (
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shrink-0 mr-3 mt-auto shadow-lg shadow-blue-600/20">
                <Sparkles size={14} className="text-white" />
              </div>
            )}
            <div
              className={`max-w-[80%] px-6 py-4 rounded-[2rem] text-sm leading-relaxed shadow-xl ${
                msg.role === "user"
                  ? "bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-tr-none shadow-blue-600/20"
                  : "bg-white/80 dark:bg-gray-900/80 backdrop-blur-md text-gray-900 dark:text-gray-100 dark:border dark:border-white/5 rounded-tl-none shadow-black/5"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600/20 flex items-center justify-center shrink-0 mr-3 mt-auto">
              <Sparkles size={14} className="text-blue-600 animate-pulse" />
            </div>
            <div className="flex items-center gap-2 px-6 py-4 rounded-[2rem] rounded-tl-none bg-white/50 dark:bg-gray-900/50 backdrop-blur-md border border-white/10 shadow-xl">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-bounce" />
              <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-bounce [animation-delay:150ms]" />
              <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-bounce [animation-delay:300ms]" />
            </div>
          </div>
        )}

        <div ref={bottomRef} className="h-20" />
      </div>

      {/* ── Floating Input Dock ── */}
      {!inputDockLocked && (
        <div className="px-6 pb-8">
          <div className="max-w-3xl mx-auto glass rounded-[2.5rem] p-3 shadow-2xl shadow-black/10 transition-all focus-within:ring-2 focus-within:ring-blue-500/20">
            <div className="flex flex-col gap-3">
              {/* Voice Toggle */}
              <div className="flex items-center justify-between px-3">
                <p className="text-[10px] uppercase tracking-wider font-bold text-gray-400">
                  Assistant Active
                </p>
                <button
                  onClick={toggleListening}
                  className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-[10px] font-bold tracking-wide uppercase transition-all ${
                    isListening
                      ? "bg-red-500 text-white shadow-lg shadow-red-500/30"
                      : "bg-blue-600/10 text-blue-600 hover:bg-blue-600/20"
                  }`}
                >
                  {isListening ? <MicOff size={12} /> : <Mic size={12} />}
                  {isListening ? "Listening..." : "Tap to Speak"}
                </button>
              </div>

              <div className="flex flex-col gap-3">
                {currentQuestion.type === "options" && (
                  <div className="flex flex-wrap gap-2 px-2">
                    {currentQuestion.options.map((opt) => (
                      <button
                        key={opt}
                        onClick={() => handleAnswer(opt)}
                        className="px-6 py-2.5 rounded-full text-xs font-bold border border-blue-100 dark:border-white/5 text-blue-600 dark:text-blue-400 bg-white dark:bg-black/20 hover:bg-blue-600 hover:text-white dark:hover:bg-blue-600 transition-all shadow-sm"
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                )}

                {currentQuestion.type === "text" && (
                  <div className="flex items-center gap-2 px-1">
                    <input
                      type="number"
                      autoFocus
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) =>
                        e.key === "Enter" && handleAnswer(input)
                      }
                      placeholder={currentQuestion.placeholder}
                      className="flex-1 px-5 py-3 rounded-full bg-gray-100/50 dark:bg-white/5 border-none focus:ring-0 text-sm text-gray-900 dark:text-white placeholder:text-gray-500 font-medium"
                    />
                    <button
                      onClick={() => handleAnswer(input)}
                      disabled={!input.trim()}
                      className="p-3 rounded-full bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-20 transition-all shadow-lg shadow-blue-600/30 active:scale-90"
                    >
                      <Send size={18} />
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
