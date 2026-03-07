# Frontend Integration Plan for Pushkar

## 🎯 Mission-Critical Context

**Product Identity**: Voice-First Eligibility Discovery Platform  
**Core Principle**: Deterministic decisions. AI for language only.  
**Target Users**: Low digital literacy citizens, assisted access operators  
**Key Differentiator**: Conversational, explainable, trustworthy

---

## 📋 Table of Contents

1. [Backend API Specification](#backend-api-specification)
2. [Data Formats & Contracts](#data-formats--contracts)
3. [UI/UX Review & Recommendations](#uiux-review--recommendations)
4. [Voice Integration Guide](#voice-integration-guide)
5. [Performance Requirements](#performance-requirements)
6. [Implementation Checklist](#implementation-checklist)

---

## 🔌 Backend API Specification

### Base URL
```
Development: http://localhost:8000
Production: https://api.samvaadai.com (TBD)
```

### API Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

#### 2. Start Session (P0 - Critical)
```http
POST /v1/session/start
```

**Request:** No body required

**Response:**
```json
{
  "session_id": "uuid-string",
  "created_at": "2025-03-02T10:30:00Z",
  "expires_at": "2025-03-02T11:30:00Z"
}
```

**Frontend Action:**
- Call this on app load
- Store `session_id` in React state/context
- Display session expiry warning at 55 minutes
- Auto-refresh session if user is active

---

#### 3. Conversation Input (P0 - Critical)
```http
POST /v1/conversation/input
```

**Request:**
```json
{
  "session_id": "uuid-string",
  "user_input": "I am a farmer, what schemes can I get?",
  "language": "en"  // "en" | "hi" | "mr"
}
```

**Response:**
```json
{
  "next_question": "What is your age?",
  "collected_attributes": {
    "occupation": "farmer"
  },
  "is_complete": false
}
```

**When `is_complete: true`:**
```json
{
  "next_question": null,
  "collected_attributes": {
    "occupation": "farmer",
    "age": 35,
    "income_band": "0-250000",
    "location": {
      "state": "Maharashtra"
    }
  },
  "is_complete": true
}
```

**Frontend Action:**
- Display `next_question` to user
- Show collected attributes (optional progress indicator)
- When `is_complete: true`, call `/v1/conversation/results`

---

#### 4. Get Results (P0 - Critical)
```http
GET /v1/conversation/results?session_id={session_id}
```

**Response:**
```json
{
  "eligible": [
    {
      "scheme_id": "PM_KISAN",
      "eligibility_status": "eligible",
      "explanation": "You meet all criteria: farmer occupation, income below threshold",
      "last_verified_date": "2025-02-15"
    }
  ],
  "partially_eligible": [
    {
      "scheme_id": "MUDRA_LOAN",
      "eligibility_status": "partially_eligible",
      "explanation": "You need: Bank account",
      "last_verified_date": "2025-02-10"
    }
  ],
  "ineligible": [
    {
      "scheme_id": "OLD_AGE_PENSION",
      "eligibility_status": "ineligible",
      "explanation": "You are not eligible because your age is below 60 years",
      "last_verified_date": "2025-02-20"
    }
  ]
}
```

---

#### 5. Direct Evaluation (Internal - Testing Only)
```http
POST /v1/evaluate
```

**⚠️ NOT FOR PRODUCTION UI**  
This endpoint is for testing only. Use conversational flow in production.

**Request:**
```json
{
  "profile": {
    "age": 35,
    "occupation": "farmer",
    "income_band": "0-250000",
    "location": {
      "state": "Maharashtra"
    }
  }
}
```

**Response:** Same as `/v1/conversation/results`

---

## 📦 Data Formats & Contracts

### User Profile Structure (Internal)

The backend expects this structure from the conversation handler:

```typescript
interface UserProfile {
  age?: number;
  age_range?: string;  // "18-35", "36-60", "60+"
  gender?: "male" | "female" | "other";
  occupation?: string;  // "farmer", "student", "unemployed", etc.
  income_band?: string;  // "0-250000", "250000-500000", etc.
  education_level?: string;  // "10th", "12th", "graduate", etc.
  location?: {
    state: string;  // "Maharashtra"
    district?: string;  // "Kolhapur"
  };
  social_category?: string;  // "SC", "ST", "OBC", "General"
  land_holding?: string;  // "0-2", "2-5", "5+" (in acres)
  bank_account?: boolean;
  has_aadhaar?: boolean;
}
```

### Scheme Data Structure

Each scheme in the response contains:

```typescript
interface SchemeResult {
  scheme_id: string;  // "PM_KISAN", "NAMO_SHETKARI"
  eligibility_status: "eligible" | "partially_eligible" | "ineligible";
  explanation: string;  // Human-readable explanation
  last_verified_date: string;  // ISO date "2025-02-15"
  
  // Additional fields from scheme JSON (for detail view)
  name?: string;
  benefit_summary?: string;
  documents_required?: string[];
  application_process?: string;
  official_website?: string;
}
```

### Language Codes

```typescript
type Language = "en" | "hi" | "mr";

const LANGUAGE_NAMES = {
  en: "English",
  hi: "हिंदी",
  mr: "मराठी"
};
```

---

## 🎨 UI/UX Review & Recommendations

### Current UI Design Analysis (from tldrawFile.png)

**✅ What's Working:**
1. Clean, minimal interface
2. Clear language selection
3. Voice/text input toggle
4. Result cards with status indicators

**⚠️ Missing Critical Elements:**



#### 1. **Data Freshness Indicator (CRITICAL - Requirements.md)**
- **Missing**: `last_verified_date` display
- **Required**: Show "Last verified: [date]" for EVERY scheme
- **Why**: Trust signal for public sector deployment
- **Implementation**: Add timestamp badge to each scheme card

#### 2. **Explanation Visibility (CRITICAL - Requirements.md)**
- **Missing**: Clear "Why am I eligible/not eligible?" section
- **Required**: Display explanation text prominently
- **Why**: Core differentiator - explainability builds trust
- **Implementation**: Expandable explanation section in each card

#### 3. **Partial Eligibility Guidance (CRITICAL - Requirements.md)**
- **Missing**: Actionable next steps for partially eligible schemes
- **Required**: Show "What you need" + "How to get it"
- **Why**: Converts partial eligibility into action
- **Implementation**: Separate section with checklist + guidance

#### 4. **Low-Bandwidth Mode Indicator**
- **Missing**: Connection quality indicator
- **Required**: Show network status, auto-switch to text mode
- **Why**: Target users have 50kbps connections
- **Implementation**: Status badge + graceful degradation

#### 5. **Session Expiry Warning**
- **Missing**: TTL countdown
- **Required**: Warn user at 55 minutes (session expires at 60 min)
- **Why**: No permanent PII storage - session-based only
- **Implementation**: Toast notification + countdown timer

#### 6. **Official Portal Link (CRITICAL)**
- **Missing**: Clear CTA to government portal
- **Required**: "Apply Now" button → external link
- **Why**: We don't process applications - guide to official portal
- **Implementation**: Primary button with external link icon

---

### Recommended UI Structure

```
┌─────────────────────────────────────────┐
│  SamvaadAI Logo    [EN ▼] [🔊/💬]      │
│  ────────────────────────────────────   │
│                                         │
│  🎤 "I am a farmer, what schemes..."    │
│  ────────────────────────────────────   │
│                                         │
│  ✅ ELIGIBLE (2)                        │
│  ┌───────────────────────────────────┐ │
│  │ PM-KISAN                          │ │
│  │ ₹6000/year for farmers            │ │
│  │                                   │ │
│  │ ℹ️ Why eligible?                  │ │
│  │ You meet all criteria: farmer     │ │
│  │ occupation, income below limit    │ │
│  │                                   │ │
│  │ 📅 Last verified: Feb 15, 2025    │ │
│  │                                   │ │
│  │ [Apply Now →]  [View Details]     │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ⚠️ PARTIALLY ELIGIBLE (1)             │
│  ┌───────────────────────────────────┐ │
│  │ MUDRA Loan                        │ │
│  │ Business loan up to ₹10 lakh      │ │
│  │                                   │ │
│  │ ⚠️ What you need:                 │ │
│  │ ☐ Bank account                    │ │
│  │                                   │ │
│  │ 💡 How to get it:                 │ │
│  │ Visit any nationalized bank with  │ │
│  │ Aadhaar and PAN                   │ │
│  │                                   │ │
│  │ 📅 Last verified: Feb 10, 2025    │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ❌ NOT ELIGIBLE (1)                   │
│  ┌───────────────────────────────────┐ │
│  │ Old Age Pension                   │ │
│  │                                   │ │
│  │ ℹ️ Why not eligible?              │ │
│  │ Age requirement: 60+ years        │ │
│  │ Your age: 35 years                │ │
│  │                                   │ │
│  │ 📅 Last verified: Feb 20, 2025    │ │
│  └───────────────────────────────────┘ │
│                                         │
│  [🔄 Start New Search]                 │
│                                         │
│  ⏱️ Session expires in 45 minutes      │
│  🌐 Connection: Good                   │
└─────────────────────────────────────────┘
```

---

## 🎤 Voice Integration Guide

### Web Speech API Implementation

#### 1. Browser Compatibility Check

```typescript
const isSpeechRecognitionSupported = (): boolean => {
  return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
};

const SpeechRecognition = 
  window.SpeechRecognition || window.webkitSpeechRecognition;
```

#### 2. Voice Input Component

```typescript
import { useState, useEffect } from 'react';

interface VoiceInputProps {
  language: 'en' | 'hi' | 'mr';
  onTranscript: (text: string) => void;
  onError: (error: string) => void;
}

const VoiceInput: React.FC<VoiceInputProps> = ({ 
  language, 
  onTranscript, 
  onError 
}) => {
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    if (!isSpeechRecognitionSupported()) {
      onError('Voice input not supported in this browser');
      return;
    }

    const recognitionInstance = new SpeechRecognition();
    
    // Language mapping
    const langMap = {
      en: 'en-IN',  // Indian English
      hi: 'hi-IN',  // Hindi
      mr: 'mr-IN'   // Marathi
    };
    
    recognitionInstance.lang = langMap[language];
    recognitionInstance.continuous = false;
    recognitionInstance.interimResults = false;
    recognitionInstance.maxAlternatives = 1;

    recognitionInstance.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
      setIsListening(false);
    };

    recognitionInstance.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      onError(`Voice input failed: ${event.error}`);
      setIsListening(false);
    };

    recognitionInstance.onend = () => {
      setIsListening(false);
    };

    setRecognition(recognitionInstance);

    return () => {
      if (recognitionInstance) {
        recognitionInstance.stop();
      }
    };
  }, [language]);

  const startListening = () => {
    if (recognition) {
      recognition.start();
      setIsListening(true);
    }
  };

  const stopListening = () => {
    if (recognition) {
      recognition.stop();
      setIsListening(false);
    }
  };

  return (
    <button
      onClick={isListening ? stopListening : startListening}
      className={isListening ? 'listening' : ''}
    >
      {isListening ? '🔴 Listening...' : '🎤 Speak'}
    </button>
  );
};
```

#### 3. Auto-Fallback to Text Mode

```typescript
const [voiceMode, setVoiceMode] = useState(true);
const [voiceError, setVoiceError] = useState<string | null>(null);

const handleVoiceError = (error: string) => {
  setVoiceError(error);
  setVoiceMode(false);  // Auto-switch to text mode
  
  // Show user-friendly message
  toast.error('Voice input unavailable. Switched to text mode.');
};
```

#### 4. Voice-to-Text Latency Tracking

```typescript
const [voiceLatency, setVoiceLatency] = useState<number>(0);

const handleVoiceInput = () => {
  const startTime = performance.now();
  
  recognition.onresult = (event: any) => {
    const endTime = performance.now();
    const latency = endTime - startTime;
    
    setVoiceLatency(latency);
    
    // Warn if exceeding 2 second threshold
    if (latency > 2000) {
      console.warn(`Voice latency ${latency}ms exceeds 2s threshold`);
    }
    
    const transcript = event.results[0][0].transcript;
    onTranscript(transcript);
  };
};
```

---

## ⚡ Performance Requirements

### Critical Thresholds (from requirements.md)

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time | < 500ms (p95) | Network tab |
| Voice-to-Text Latency | < 2 seconds | Performance API |
| UI Render Time | < 100ms | React DevTools |
| Low-Bandwidth Support | 50 kbps | Chrome DevTools throttling |
| Lighthouse Score | > 80 | Lighthouse audit |

### Performance Optimization Checklist

#### 1. Low-Bandwidth Mode

```typescript
// Detect slow connection
const isSlowConnection = (): boolean => {
  const connection = (navigator as any).connection;
  if (!connection) return false;
  
  return connection.effectiveType === 'slow-2g' || 
         connection.effectiveType === '2g' ||
         connection.downlink < 0.5;  // < 500 kbps
};

// Auto-disable voice on slow connection
useEffect(() => {
  if (isSlowConnection()) {
    setVoiceMode(false);
    toast.info('Slow connection detected. Using text mode.');
  }
}, []);
```

#### 2. Response Compression

```typescript
// Axios configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/json'
  }
});
```

#### 3. Local Caching

```typescript
// Cache scheme data locally
const CACHE_KEY = 'samvaadai_schemes';
const CACHE_TTL = 5 * 60 * 1000;  // 5 minutes

const getCachedSchemes = () => {
  const cached = localStorage.getItem(CACHE_KEY);
  if (!cached) return null;
  
  const { data, timestamp } = JSON.parse(cached);
  if (Date.now() - timestamp > CACHE_TTL) {
    localStorage.removeItem(CACHE_KEY);
    return null;
  }
  
  return data;
};

const setCachedSchemes = (data: any) => {
  localStorage.setItem(CACHE_KEY, JSON.stringify({
    data,
    timestamp: Date.now()
  }));
};
```

#### 4. Progressive Enhancement

```typescript
// Load voice features only if supported
const [voiceReady, setVoiceReady] = useState(false);

useEffect(() => {
  if (isSpeechRecognitionSupported()) {
    // Lazy load voice components
    import('./components/VoiceInput').then(() => {
      setVoiceReady(true);
    });
  }
}, []);
```

---

## 🔐 Security & Privacy

### Critical Rules (from requirements.md)

1. **No PII Storage Beyond Session**
   - Never store user data in localStorage permanently
   - Clear session data on logout/expiry
   - Use session_id for all API calls

2. **HTTPS Only**
   - All API calls must use HTTPS in production
   - No mixed content warnings

3. **Input Sanitization**
   - Sanitize all user input before display
   - Prevent XSS attacks

```typescript
import DOMPurify from 'dompurify';

const sanitizeInput = (input: string): string => {
  return DOMPurify.sanitize(input, { 
    ALLOWED_TAGS: [],  // Strip all HTML
    ALLOWED_ATTR: [] 
  });
};
```

4. **Session Management**

```typescript
interface Session {
  sessionId: string;
  createdAt: Date;
  expiresAt: Date;
}

const SESSION_KEY = 'samvaadai_session';

const saveSession = (session: Session) => {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
};

const getSession = (): Session | null => {
  const stored = sessionStorage.getItem(SESSION_KEY);
  if (!stored) return null;
  
  const session = JSON.parse(stored);
  
  // Check expiry
  if (new Date(session.expiresAt) < new Date()) {
    sessionStorage.removeItem(SESSION_KEY);
    return null;
  }
  
  return session;
};

const clearSession = () => {
  sessionStorage.removeItem(SESSION_KEY);
};
```

---

## 📱 Responsive Design Requirements

### Breakpoints

```css
/* Mobile-first approach */
:root {
  --mobile: 320px;
  --tablet: 768px;
  --desktop: 1024px;
}

/* Target: Basic smartphones (320px - 480px) */
@media (min-width: 320px) {
  /* Single column layout */
  /* Large touch targets (min 44px) */
  /* Simplified navigation */
}

/* Target: Tablets (768px+) */
@media (min-width: 768px) {
  /* Two column layout */
  /* Side-by-side scheme cards */
}

/* Target: Desktop (1024px+) */
@media (min-width: 1024px) {
  /* Three column layout */
  /* Enhanced features */
}
```

### Touch Targets

```css
/* Minimum touch target size for low-literacy users */
.button, .input, .card {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 24px;
}

/* Large, clear icons */
.icon {
  font-size: 24px;
  line-height: 1;
}
```

---

## 🌐 Multilingual Support

### Language Switching

```typescript
interface LanguageConfig {
  code: 'en' | 'hi' | 'mr';
  name: string;
  nativeName: string;
  direction: 'ltr' | 'rtl';
}

const LANGUAGES: LanguageConfig[] = [
  { code: 'en', name: 'English', nativeName: 'English', direction: 'ltr' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिंदी', direction: 'ltr' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी', direction: 'ltr' }
];

const LanguageSelector: React.FC = () => {
  const [language, setLanguage] = useState<'en' | 'hi' | 'mr'>('en');
  
  const handleLanguageChange = (newLang: 'en' | 'hi' | 'mr') => {
    setLanguage(newLang);
    // Update document direction if needed
    document.documentElement.lang = newLang;
  };
  
  return (
    <select value={language} onChange={(e) => handleLanguageChange(e.target.value as any)}>
      {LANGUAGES.map(lang => (
        <option key={lang.code} value={lang.code}>
          {lang.nativeName}
        </option>
      ))}
    </select>
  );
};
```

### Translation Keys (MVP Scope)

```typescript
const translations = {
  en: {
    welcome: "Welcome to SamvaadAI",
    askQuestion: "Ask about schemes",
    eligible: "Eligible",
    partiallyEligible: "Partially Eligible",
    notEligible: "Not Eligible",
    whyEligible: "Why am I eligible?",
    whatYouNeed: "What you need",
    howToGet: "How to get it",
    applyNow: "Apply Now",
    viewDetails: "View Details",
    lastVerified: "Last verified",
    sessionExpires: "Session expires in",
    startNewSearch: "Start New Search"
  },
  hi: {
    welcome: "समवाद AI में आपका स्वागत है",
    askQuestion: "योजनाओं के बारे में पूछें",
    eligible: "पात्र",
    partiallyEligible: "आंशिक रूप से पात्र",
    notEligible: "पात्र नहीं",
    whyEligible: "मैं पात्र क्यों हूं?",
    whatYouNeed: "आपको क्या चाहिए",
    howToGet: "इसे कैसे प्राप्त करें",
    applyNow: "अभी आवेदन करें",
    viewDetails: "विवरण देखें",
    lastVerified: "अंतिम सत्यापन",
    sessionExpires: "सत्र समाप्त होगा",
    startNewSearch: "नई खोज शुरू करें"
  },
  mr: {
    welcome: "समवाद AI मध्ये आपले स्वागत आहे",
    askQuestion: "योजनांबद्दल विचारा",
    eligible: "पात्र",
    partiallyEligible: "अंशतः पात्र",
    notEligible: "पात्र नाही",
    whyEligible: "मी पात्र का आहे?",
    whatYouNeed: "तुम्हाला काय हवे आहे",
    howToGet: "ते कसे मिळवायचे",
    applyNow: "आता अर्ज करा",
    viewDetails: "तपशील पहा",
    lastVerified: "शेवटचे सत्यापन",
    sessionExpires: "सत्र संपेल",
    startNewSearch: "नवीन शोध सुरू करा"
  }
};
```

---

## 🧪 Testing Requirements

### Browser Compatibility

Test on:
- ✅ Chrome 90+ (primary)
- ✅ Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+ (iOS)
- ⚠️ Opera, Brave (best effort)

### Voice API Testing

```typescript
// Test voice recognition on different browsers
const testVoiceRecognition = () => {
  const results = {
    supported: isSpeechRecognitionSupported(),
    browser: navigator.userAgent,
    languages: []
  };
  
  if (results.supported) {
    const recognition = new SpeechRecognition();
    results.languages = recognition.lang;
  }
  
  console.log('Voice Recognition Test:', results);
  return results;
};
```

### Network Throttling Test

```bash
# Chrome DevTools → Network tab → Throttling
# Test with:
- Fast 3G (1.6 Mbps down, 750 Kbps up)
- Slow 3G (400 Kbps down, 400 Kbps up)
- Custom: 50 Kbps (requirements.md target)
```

### Lighthouse Audit

```bash
# Run Lighthouse audit
npm run build
npx lighthouse http://localhost:3000 --view

# Target scores:
# Performance: > 80
# Accessibility: > 90
# Best Practices: > 90
# SEO: > 80
```

---

## 📦 Recommended Tech Stack

### Core Framework
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "vite": "^5.0.0"
}
```

### UI Components
```json
{
  "tailwindcss": "^3.4.0",
  "@headlessui/react": "^1.7.0",  // Accessible components
  "lucide-react": "^0.300.0"  // Icons
}
```

### State Management
```json
{
  "zustand": "^4.4.0"  // Lightweight state management
}
```

### API Client
```json
{
  "axios": "^1.6.0",
  "react-query": "^3.39.0"  // API caching & state
}
```

### Voice & Audio
```json
{
  // Use native Web Speech API (no external deps)
}
```

### Utilities
```json
{
  "dompurify": "^3.0.0",  // XSS protection
  "date-fns": "^2.30.0",  // Date formatting
  "react-hot-toast": "^2.4.0"  // Notifications
}
```

---

## 🚀 Implementation Checklist

### Day 1: Setup & API Integration

- [ ] Initialize React + Vite + Tailwind project
- [ ] Set up API client with axios
- [ ] Implement session management
- [ ] Create language selector component
- [ ] Test `/health` and `/v1/session/start` endpoints
- [ ] Set up error handling & logging

### Day 2: Core Features

- [ ] Implement text input component
- [ ] Implement Web Speech API integration
- [ ] Create conversation flow (question → answer loop)
- [ ] Test `/v1/conversation/input` endpoint
- [ ] Implement voice/text mode toggle
- [ ] Add auto-fallback logic

### Day 3: Results Display

- [ ] Create scheme card components
- [ ] Implement eligible/partially eligible/ineligible sections
- [ ] Display explanations prominently
- [ ] Show `last_verified_date` for all schemes
- [ ] Add "Apply Now" buttons with external links
- [ ] Implement partial eligibility guidance UI

### Day 4: Polish & Testing

- [ ] Add session expiry warning
- [ ] Implement low-bandwidth mode indicator
- [ ] Test on 50kbps throttling
- [ ] Run Lighthouse audit (target > 80)
- [ ] Test voice input on multiple browsers
- [ ] Fix UI bugs and polish animations
- [ ] Deploy to Amplify

---

## 🎯 Success Criteria (from EXECUTION_CHARTER.md)

### Definition of Done

- [ ] PWA supports voice and text input
- [ ] 3 languages (Hindi, English, Marathi) selectable
- [ ] Displays eligibility results with explanations
- [ ] Shows `last_verified_date` for every scheme
- [ ] Auto-fallback to text if voice fails
- [ ] Lighthouse score > 80
- [ ] Works on 50kbps (tested)
- [ ] Voice-to-text latency < 2 seconds
- [ ] UI render time < 100ms

### Demo Flow (Must Work End-to-End)

1. User opens PWA
2. User selects language (Hindi/English/Marathi)
3. User speaks or types: "I am a farmer, what schemes can I get?"
4. System asks: "What is your age?"
5. User responds: "35"
6. System asks: "What is your annual income?"
7. User responds: "2 lakh"
8. System evaluates eligibility
9. System shows results:
   - Eligible: PM-KISAN (explanation visible)
   - Partially Eligible: MUDRA Loan (missing: bank account)
   - Not Eligible: Old Age Pension (age < 60)
10. User sees `last_verified_date` for each scheme
11. User clicks PM-KISAN → redirected to official portal

**Demo duration**: < 5 minutes  
**Demo success criteria**: Full eligibility flow works without errors

---

## 📞 Integration Support

### Backend Team Contact
- **Ayush**: Backend + Infrastructure Lead
- **Pranit**: Rule Engine Lead
- **Ratnadeep**: LLM + Bedrock Lead

### API Issues
- Check backend logs in CloudWatch
- Verify API Gateway URL
- Test with Postman first
- Check CORS configuration

### Data Format Questions
- Refer to `backend/api/schemas.py`
- Check scheme JSON files in `docs/` folder
- Review `backend/ARCHITECTURE.md`

---

## 🔗 Quick Reference Links

- **Requirements**: `docs/requirements.md`
- **Design**: `docs/design.md`
- **Execution Charter**: `docs/EXECUTION_CHARTER.md`
- **API Schemas**: `backend/api/schemas.py`
- **Sample Schemes**: `docs/*.json`

---

## ⚠️ Critical Reminders

1. **Voice is PRIMARY, text is FALLBACK** - Not the other way around
2. **Show `last_verified_date` for EVERY scheme** - Trust signal
3. **Display explanations PROMINENTLY** - Core differentiator
4. **Test on 50kbps** - Target users have slow connections
5. **Session expires in 1 hour** - Warn user, no permanent storage
6. **We DON'T process applications** - Guide to official portals only
7. **Lighthouse score > 80** - Performance is critical
8. **Voice latency < 2 seconds** - User experience requirement

---

**Good luck, Pushkar! 🚀**

*This document is your single source of truth for frontend development. Refer to it daily.*
