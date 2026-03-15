import { useState } from "react";
import { Mic, MicOff } from "lucide-react";

/**
 * QuickSelectChips - Interactive chip selector for structured data collection
 * 
 * Supports:
 * - Click to select
 * - Voice input with fuzzy matching
 * - Text input fallback
 * - Multilingual labels
 */
export default function QuickSelectChips({ question, onSelect, language, onVoiceStart, onVoiceEnd }) {
  const [textInput, setTextInput] = useState("");
  const [isListening, setIsListening] = useState(false);

  if (!question) return null;

  const handleChipClick = (option) => {
    onSelect(option.value, option.label);
  };

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      onSelect(textInput.trim(), textInput.trim());
      setTextInput("");
    }
  };

  const handleVoiceInput = () => {
    if (isListening) {
      setIsListening(false);
      onVoiceEnd?.();
    } else {
      setIsListening(true);
      onVoiceStart?.(question.options);
    }
  };

  return (
    <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shrink-0 mr-3 mt-auto shadow-lg shadow-blue-600/20">
        <span className="text-white text-sm">🤖</span>
      </div>
      
      <div className="max-w-[85%] glass rounded-[2rem] rounded-tl-none p-5 border border-white/10 shadow-xl">
        {/* Question Text */}
        <p className="text-sm font-medium text-gray-900 dark:text-white mb-4">
          {question.text}
        </p>
        
        {/* Chip Options */}
        <div className="flex flex-wrap gap-2 mb-4">
          {question.options.map((opt, idx) => (
            <button
              key={idx}
              onClick={() => handleChipClick(opt)}
              className="px-4 py-2.5 rounded-full bg-blue-100 dark:bg-blue-900/30 
                         text-blue-700 dark:text-blue-300 font-medium text-sm
                         hover:bg-blue-200 dark:hover:bg-blue-900/50 
                         hover:scale-105 transition-all active:scale-95
                         border border-blue-200 dark:border-blue-800/30
                         shadow-sm hover:shadow-md"
            >
              {opt.label}
            </button>
          ))}
        </div>
        
        {/* Text Input Fallback */}
        {question.allow_text_input && (
          <div className="flex items-center gap-2 pt-3 border-t border-gray-200 dark:border-white/10">
            <input
              type="text"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleTextSubmit();
              }}
              placeholder="Or type your answer..."
              className="flex-1 px-4 py-2 rounded-full bg-gray-100/50 dark:bg-white/5 
                         border-none focus:ring-2 focus:ring-blue-500/20 text-sm 
                         text-gray-900 dark:text-white placeholder:text-gray-500"
            />
            <button
              onClick={handleVoiceInput}
              className={`p-2.5 rounded-full transition-all shadow-lg ${
                isListening
                  ? "bg-red-500 text-white shadow-red-500/30 animate-pulse"
                  : "bg-blue-600 text-white shadow-blue-600/30 hover:bg-blue-700"
              }`}
            >
              {isListening ? <MicOff size={18} /> : <Mic size={18} />}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
