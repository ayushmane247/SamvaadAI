# 🎨 SamvaadAI Frontend

**Voice-first React application for conversational government scheme discovery**

[![React](https://img.shields.io/badge/React-19.2-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-7.3-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind](https://img.shields.io/badge/Tailwind-3.4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Deployed](https://img.shields.io/badge/Deployed-AWS%20Amplify-FF9900?style=flat-square&logo=aws-amplify&logoColor=white)](https://main.d1ldcuarhn106p.amplifyapp.com/)

🔗 **[Live Demo](https://main.d1ldcuarhn106p.amplifyapp.com/)**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Development](#development)
- [Build & Deployment](#build--deployment)
- [Components](#components)
- [State Management](#state-management)
- [Voice Integration](#voice-integration)

---

## 🎯 Overview

The SamvaadAI frontend is a modern React application built with Vite, featuring a voice-first conversational interface for discovering government welfare schemes. It provides an accessible, multilingual experience optimized for low-literacy users.

### Key Features

✅ **Voice-First Interface**: Natural conversation using Web Speech API  
✅ **Real-Time Transcription**: See what you're saying as you speak  
✅ **Multilingual Support**: English, Hindi, Marathi  
✅ **Responsive Design**: Works on mobile, tablet, and desktop  
✅ **Offline-Ready**: Progressive Web App capabilities  
✅ **Accessible**: WCAG-compliant design patterns  

---

## ✨ Features

### 🎤 Voice Interaction
- **Web Speech API Integration**: Browser-native voice recognition
- **Real-time Transcription**: Live text display as you speak
- **Confidence Thresholds**: Automatic retry for low-confidence inputs
- **Voice Output**: Text-to-speech for responses
- **Manual Fallback**: Switch to text input anytime

### 🌍 Multilingual Support
- **3 Languages**: English, Hindi (हिंदी), Marathi (मराठी)
- **Language Detection**: Automatic language switching
- **Localized UI**: All interface elements translated
- **Voice Localization**: Language-appropriate TTS voices

### 💬 Conversational UI
- **Chat Interface**: Familiar messaging-style layout
- **Typing Indicators**: Visual feedback during processing
- **Error Handling**: User-friendly error messages
- **Session Persistence**: Conversation history maintained
- **Quick Actions**: Predefined response buttons

### 📊 Results Display
- **Scheme Cards**: Visual representation of eligible schemes
- **Eligibility Status**: Color-coded badges (eligible/partial/ineligible)
- **Document Checklist**: Required documents for each scheme
- **Official Links**: Direct links to government portals
- **Benefit Summary**: Clear benefit amounts in Indian numbering

---

## 📁 Project Structure

```
frontend/
├── public/                       # Static assets
│   ├── SamvaadAI.jpeg           # App logo
│   └── vite.svg                 # Vite logo
│
├── src/
│   ├── api/                     # API layer
│   │   └── apiClient.js         # Backend API client
│   │
│   ├── components/              # Reusable components
│   │   ├── Navigation/
│   │   │   └── UserAvatar.jsx   # User avatar component
│   │   ├── Visuals/
│   │   │   └── BackgroundBlobs.jsx  # Animated background
│   │   ├── ProtectedRoute.jsx   # Auth route guard
│   │   ├── Sidebar.jsx          # Navigation sidebar
│   │   └── Topbar.jsx           # Top navigation bar
│   │
│   ├── layouts/                 # Layout components
│   │   └── DashboardLayout.jsx  # Main dashboard layout
│   │
│   ├── lib/                     # Utilities
│   │   ├── firebase.js          # Firebase configuration
│   │   └── i18n.js              # Internationalization
│   │
│   ├── pages/                   # Page components
│   │   ├── dashboard/
│   │   │   ├── Chat.jsx         # Main chat interface
│   │   │   ├── Home.jsx         # Dashboard home
│   │   │   ├── Profile.jsx      # User profile
│   │   │   ├── Results.jsx      # Eligibility results
│   │   │   └── SchemeDetail.jsx # Scheme details
│   │   ├── Auth.jsx             # Authentication page
│   │   ├── Landing.jsx          # Landing page
│   │   └── NotFound.jsx         # 404 page
│   │
│   ├── store/                   # State management
│   │   ├── useAuthStore.js      # Authentication state
│   │   ├── useConversationStore.js  # Conversation state
│   │   └── useUIStore.js        # UI state
│   │
│   ├── App.jsx                  # Root component
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
│
├── .env                         # Environment variables
├── .env.example                 # Environment template
├── package.json                 # Dependencies
├── vite.config.js               # Vite configuration
├── tailwind.config.js           # Tailwind configuration
└── postcss.config.js            # PostCSS configuration
```

---

## 🚀 Setup & Installation

### Prerequisites

- Node.js 18+
- npm or yarn
- Git

### Installation Steps

#### 1. Clone and Navigate
```bash
git clone https://github.com/yourusername/samvaadai.git
cd samvaadai/frontend
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Configure Environment
```bash
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_URL=http://localhost:8000
```

#### 4. Start Development Server
```bash
npm run dev
```

Application will run on `http://localhost:5173`

---

## 💻 Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Fix linting issues
npm run lint:fix
```

### Development Workflow

1. **Start Backend**: Ensure backend is running on `http://localhost:8000`
2. **Start Frontend**: Run `npm run dev`
3. **Open Browser**: Navigate to `http://localhost:5173`
4. **Hot Reload**: Changes auto-reload in browser

### Code Style

- **ESLint**: Configured with React rules
- **Prettier**: Auto-formatting on save
- **Tailwind**: Utility-first CSS
- **Component Structure**: Functional components with hooks

---

## 🏗️ Build & Deployment

### Production Build

```bash
npm run build
```

Output: `dist/` directory

### Deploy to AWS Amplify

#### Option 1: Amplify Console (Recommended)

1. Connect GitHub repository
2. Configure build settings:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: dist
       files:
         - '**/*'
     cache:
       paths:
         - node_modules/**/*
   ```
3. Set environment variables in Amplify Console
4. Deploy

#### Option 2: Amplify CLI

```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Initialize Amplify
amplify init

# Add hosting
amplify add hosting

# Publish
amplify publish
```

### Environment Variables (Production)

```env
VITE_API_URL=https://your-api-gateway-url.amazonaws.com/prod
```

---

## 🧩 Components

### Chat Component
**File**: `src/pages/dashboard/Chat.jsx`

Main conversational interface with voice input/output.

**Features**:
- Voice recognition with Web Speech API
- Real-time transcription display
- Message history with user/assistant roles
- Scheme card display
- Document checklist
- Error handling with retry

**Usage**:
```jsx
import Chat from './pages/dashboard/Chat';

<Chat />
```

### API Client
**File**: `src/api/apiClient.js`

Centralized backend communication with retry and caching.

**Features**:
- Request/response normalization
- Automatic retry with exponential backoff
- Query-level caching (1-minute TTL)
- Request deduplication
- Throttling (2-second minimum gap)
- AbortController support

**Usage**:
```javascript
import { sendConversation, startSession } from './api/apiClient';

// Start session
const session = await startSession();

// Send query
const result = await sendConversation({
  query: "I am a farmer",
  language: "en",
  sessionId: session.sessionId
});
```

---

## 🗄️ State Management

### Zustand Stores

#### useConversationStore
**File**: `src/store/useConversationStore.js`

Manages conversation state and backend communication.

**State**:
```javascript
{
  messages: [],           // Chat history
  sessionId: null,        // Current session
  profile: {},            // User profile
  eligibility: null,      // Eligibility results
  schemes: [],            // Scheme cards
  documents: [],          // Required documents
  isLoading: false,       // Processing state
  error: null             // Error message
}
```

**Actions**:
- `sendMessage(query, language)`: Send user message
- `resetConversation()`: Clear conversation
- `clearError()`: Clear error state

**Usage**:
```javascript
import useConversationStore from './store/useConversationStore';

const { messages, sendMessage, isLoading } = useConversationStore();

await sendMessage("I am a farmer", "en");
```

#### useUIStore
**File**: `src/store/useUIStore.js`

Manages UI state (language, theme, sidebar).

**State**:
```javascript
{
  language: "en",         // Current language
  sidebarOpen: false,     // Sidebar visibility
  theme: "light"          // Theme mode
}
```

#### useAuthStore
**File**: `src/store/useAuthStore.js`

Manages authentication state with Firebase.

---

## 🎤 Voice Integration

### Web Speech API

#### Voice Input (Speech Recognition)

```javascript
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.lang = "en-IN";  // or "hi-IN", "mr-IN"
recognition.interimResults = true;
recognition.maxAlternatives = 3;

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  const confidence = event.results[0][0].confidence;
  
  if (confidence > 0.7) {
    // Process transcript
  }
};

recognition.start();
```

#### Voice Output (Speech Synthesis)

```javascript
const utterance = new SpeechSynthesisUtterance(text);
utterance.lang = "en-IN";
utterance.rate = 0.95;
utterance.pitch = 1.0;
utterance.volume = 1.0;

window.speechSynthesis.speak(utterance);
```

### Supported Languages

| Language | Code | Voice Recognition | Text-to-Speech |
|----------|------|-------------------|----------------|
| English  | en-IN | ✅ | ✅ |
| Hindi    | hi-IN | ✅ | ✅ |
| Marathi  | mr-IN | ✅ | ✅ |

---

## 🎨 Styling

### Tailwind CSS

Utility-first CSS framework for rapid UI development.

**Configuration**: `tailwind.config.js`

**Custom Theme**:
```javascript
{
  colors: {
    primary: '#3B82F6',
    secondary: '#10B981',
    accent: '#F59E0B'
  },
  fontFamily: {
    sans: ['Inter', 'sans-serif']
  }
}
```

### Dark Mode

Automatic dark mode support with `dark:` prefix:

```jsx
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  Content
</div>
```

---

## 📱 Responsive Design

### Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Mobile-First Approach

```jsx
<div className="w-full md:w-1/2 lg:w-1/3">
  {/* Full width on mobile, half on tablet, third on desktop */}
</div>
```

---

## 🔒 Security

- ✅ Environment variables for sensitive data
- ✅ HTTPS-only in production
- ✅ Content Security Policy headers
- ✅ XSS protection
- ✅ CORS configuration

---

## 📊 Performance

### Optimization Techniques

- **Code Splitting**: Route-based lazy loading
- **Image Optimization**: WebP format with fallbacks
- **Bundle Size**: Tree-shaking and minification
- **Caching**: Service worker for offline support
- **CDN**: CloudFront for static assets

### Performance Metrics

- **First Contentful Paint**: <1.5s
- **Time to Interactive**: <3s
- **Lighthouse Score**: 90+

---

## 🤝 Contributing

See the main [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

---

<div align="center">

**Built with ❤️ using React and Vite**

</div>
