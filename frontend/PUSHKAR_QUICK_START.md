# Pushkar's Quick Start Guide 🚀

## 📋 Your Mission

Build a **voice-first eligibility discovery PWA** that helps low-literacy citizens discover government schemes.

**Timeline**: 4 days  
**Your Role**: Frontend & Voice (React PWA) Lead  
**Integration Partner**: Ayush (Backend API)

---

## ⚡ Quick Setup (30 minutes)

### 1. Initialize Project

```bash
# Create React + Vite project
npm create vite@latest samvaadai-frontend -- --template react-ts
cd samvaadai-frontend

# Install dependencies
npm install
npm install -D tailwindcss postcss autoprefixer
npm install axios zustand react-hot-toast date-fns dompurify
npm install lucide-react @headlessui/react

# Initialize Tailwind
npx tailwindcss init -p
```

### 2. Configure Tailwind

```js
// tailwind.config.js
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        eligible: '#10b981',
        partial: '#f59e0b',
        ineligible: '#ef4444',
      }
    },
  },
  plugins: [],
}
```

### 3. Set Up API Client

```typescript
// src/api/client.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for session ID
api.interceptors.request.use((config) => {
  const sessionId = sessionStorage.getItem('session_id');
  if (sessionId) {
    config.headers['X-Session-ID'] = sessionId;
  }
  return config;
});
```

### 4. Create .env File

```bash
# .env
VITE_API_URL=http://localhost:8000
```

---

## 🎯 Day-by-Day Plan

### Day 1: API Integration ✅

**Goal**: Connect to backend, test all endpoints

**Tasks**:
1. ✅ Test `/health` endpoint
2. ✅ Implement session management
3. ✅ Create language selector
4. ✅ Test `/v1/session/start`
5. ✅ Set up error handling

**Code to Write**:
```typescript
// src/hooks/useSession.ts
export const useSession = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  const startSession = async () => {
    const response = await api.post('/v1/session/start');
    setSessionId(response.data.session_id);
    sessionStorage.setItem('session_id', response.data.session_id);
  };
  
  return { sessionId, startSession };
};
```

---

### Day 2: Voice + Conversation ✅

**Goal**: Voice input working, conversation flow complete

**Tasks**:
1. ✅ Implement Web Speech API
2. ✅ Create text input fallback
3. ✅ Build conversation component
4. ✅ Test `/v1/conversation/input`
5. ✅ Add voice/text toggle

**Code to Write**:
```typescript
// src/components/VoiceInput.tsx
export const VoiceInput = ({ language, onTranscript }) => {
  const [isListening, setIsListening] = useState(false);
  
  const startListening = () => {
    const recognition = new webkitSpeechRecognition();
    recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
    };
    recognition.start();
    setIsListening(true);
  };
  
  return (
    <button onClick={startListening}>
      {isListening ? '🔴 Listening...' : '🎤 Speak'}
    </button>
  );
};
```

---

### Day 3: Results Display ✅

**Goal**: Full eligibility results with all required elements

**Tasks**:
1. ✅ Create scheme card components
2. ✅ Display eligible/partially/ineligible sections
3. ✅ Show explanations prominently
4. ✅ Add `last_verified_date` badges
5. ✅ Implement "Apply Now" buttons

**Code to Write**:
```typescript
// src/components/SchemeCard.tsx
export const SchemeCard = ({ scheme }) => {
  return (
    <div className="scheme-card">
      <h3>{scheme.scheme_id}</h3>
      
      {/* CRITICAL: Explanation */}
      <div className="explanation">
        <InfoIcon />
        <p>{scheme.explanation}</p>
      </div>
      
      {/* CRITICAL: Data Freshness */}
      <div className="freshness">
        <CalendarIcon />
        <span>Last verified: {scheme.last_verified_date}</span>
      </div>
      
      {/* CRITICAL: Apply Button */}
      <a href={scheme.official_website} target="_blank">
        Apply Now <ExternalLinkIcon />
      </a>
    </div>
  );
};
```

---

### Day 4: Polish & Testing ✅

**Goal**: Production-ready, all tests passing

**Tasks**:
1. ✅ Add session expiry warning
2. ✅ Implement connection indicator
3. ✅ Test on 50kbps throttling
4. ✅ Run Lighthouse audit (> 80)
5. ✅ Deploy to Amplify

---

## 🔥 Critical Requirements (Must Have)

### 1. Data Freshness (P0)
```jsx
<span className="text-sm text-gray-600">
  📅 Last verified: {formatDate(scheme.last_verified_date)}
</span>
```

### 2. Explanation (P0)
```jsx
<div className="bg-blue-50 p-4 rounded">
  <h4 className="font-semibold">ℹ️ Why am I {status}?</h4>
  <p>{scheme.explanation}</p>
</div>
```

### 3. Partial Eligibility Guidance (P0)
```jsx
{status === 'partially_eligible' && (
  <div className="bg-yellow-50 p-4 rounded">
    <h4>⚠️ What you need:</h4>
    <ul>{scheme.missing_data.map(item => <li>☐ {item}</li>)}</ul>
    <h4>💡 How to get it:</h4>
    <p>{scheme.user_guidance}</p>
  </div>
)}
```

### 4. Official Portal Link (P0)
```jsx
<a 
  href={scheme.official_website}
  target="_blank"
  rel="noopener noreferrer"
  className="btn-primary"
>
  Apply Now <ExternalLinkIcon />
</a>
```

### 5. Session Expiry (P1)
```jsx
<div className="session-warning">
  ⏱️ Session expires in {remainingMinutes} minutes
</div>
```

---

## 🧪 Testing Checklist

### Browser Testing
- [ ] Chrome 90+ (primary)
- [ ] Edge 90+
- [ ] Firefox 88+
- [ ] Safari 14+ (iOS)

### Voice Testing
- [ ] English voice recognition
- [ ] Hindi voice recognition
- [ ] Marathi voice recognition
- [ ] Auto-fallback to text

### Performance Testing
- [ ] API response < 500ms
- [ ] Voice latency < 2 seconds
- [ ] UI render < 100ms
- [ ] Works on 50kbps
- [ ] Lighthouse score > 80

### Network Throttling
```bash
# Chrome DevTools → Network → Throttling
1. Fast 3G (1.6 Mbps)
2. Slow 3G (400 Kbps)
3. Custom: 50 Kbps ← TEST THIS
```

---

## 📞 API Endpoints (Quick Reference)

```typescript
// 1. Start Session
POST /v1/session/start
Response: { session_id, created_at, expires_at }

// 2. Conversation Input
POST /v1/conversation/input
Body: { session_id, user_input, language }
Response: { next_question, collected_attributes, is_complete }

// 3. Get Results
GET /v1/conversation/results?session_id={id}
Response: { eligible[], partially_eligible[], ineligible[] }

// 4. Health Check
GET /health
Response: { status: "ok", version: "1.0.0" }
```

---

## 🚨 Common Mistakes to Avoid

1. ❌ Hiding explanations → ✅ Show prominently
2. ❌ Small freshness date → ✅ Make it visible
3. ❌ Complex language → ✅ Simple, clear text
4. ❌ Ignoring voice latency → ✅ Track and optimize
5. ❌ Storing PII permanently → ✅ Session-only
6. ❌ Skipping 50kbps test → ✅ Test thoroughly
7. ❌ No external link icon → ✅ Show clearly

---

## 📚 Documentation Links

- **Full Integration Plan**: `docs/FRONTEND_INTEGRATION_PLAN.md`
- **UI Improvements**: `docs/UI_IMPROVEMENTS_REQUIRED.md`
- **Requirements**: `docs/requirements.md`
- **Design**: `docs/design.md`
- **Execution Charter**: `docs/EXECUTION_CHARTER.md`

---

## 🎯 Success Criteria

### Definition of Done
- [ ] Voice and text input working
- [ ] 3 languages supported (en, hi, mr)
- [ ] Results display with explanations
- [ ] `last_verified_date` visible on all schemes
- [ ] Auto-fallback to text if voice fails
- [ ] Lighthouse score > 80
- [ ] Works on 50kbps
- [ ] Voice latency < 2 seconds

### Demo Flow (Must Work)
1. Open PWA → Select language
2. Speak: "I am a farmer, what schemes can I get?"
3. Answer questions (age, income)
4. See results with explanations
5. Click "Apply Now" → Redirect to portal

**Demo Duration**: < 5 minutes  
**Demo Success**: No errors, smooth flow

---

## 💡 Pro Tips

1. **Start with text mode** - Get conversation flow working first
2. **Add voice later** - Voice is enhancement, not blocker
3. **Test early, test often** - Don't wait until Day 4
4. **Use mock data** - Don't wait for backend if blocked
5. **Focus on mobile** - Target users are on smartphones
6. **Keep it simple** - Low-literacy users need clarity

---

## 🆘 Need Help?

### Backend Issues
- **Ayush**: API endpoints, session management
- Check: `backend/api/routes.py`
- Test: Use Postman first

### Data Format Questions
- **Pranit**: Scheme data structure
- Check: `docs/*.json` (sample schemes)
- Check: `backend/api/schemas.py`

### LLM Response Format
- **Ratnadeep**: Explanation text format
- Check: `backend/llm_service/`

---

## 🚀 Let's Build This!

**Remember**: You're building for low-literacy citizens in low-bandwidth environments. Every design decision must serve them first.

**Your superpower**: Making complex government schemes accessible through voice and simple UI.

**Good luck, Pushkar! 💪**

---

*Last Updated: March 2, 2025*  
*Version: 1.0*
