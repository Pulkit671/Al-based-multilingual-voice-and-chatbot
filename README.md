<<<<<<< HEAD
# MedAI Chatbot

A full-stack multilingual medical chatbot starter built with a React frontend and a FastAPI backend. This version is intentionally model-free for now and uses a dummy medical response that is translated into the user's selected language. The project is structured so a disease prediction or diagnosis model can be plugged in later without rewriting the authentication, chat, MongoDB persistence, or UI layers.

## Features

- React + Vite frontend with ChatGPT-style chat layout
- FastAPI backend with modular routes and utilities
- JWT authentication with signup, login, logout-ready flow, and protected chat routes
- MongoDB storage for users, chats, and messages
- Multilingual support with English and Hindi, designed for future language expansion
- Language selector in the navbar with immediate persistence to MongoDB
- New chat creation and conversation history sidebar
- Voice message upload support with backend file storage
- Dummy multilingual medical responses for now
- Responsive medical-themed UI
- API structure ready for future ML model integration

## Folder structure

```text
med_ai/
+-- README.md
+-- backend/
¦   +-- .env.example
¦   +-- requirements.txt
¦   +-- app/
¦       +-- __init__.py
¦       +-- config.py
¦       +-- database.py
¦       +-- main.py
¦       +-- models/
¦       ¦   +-- __init__.py
¦       +-- routes/
¦       ¦   +-- __init__.py
¦       ¦   +-- auth.py
¦       ¦   +-- chats.py
¦       +-- schemas/
¦       ¦   +-- __init__.py
¦       ¦   +-- auth.py
¦       ¦   +-- chat.py
¦       +-- uploads/
¦       ¦   +-- __init__.py
¦       ¦   +-- voice/
¦       +-- utils/
¦           +-- __init__.py
¦           +-- auth.py
¦           +-- translator.py
+-- frontend/
    +-- index.html
    +-- package.json
    +-- vite.config.js
    +-- src/
        +-- App.jsx
        +-- main.jsx
        +-- styles.css
        +-- api/
        ¦   +-- auth.js
        ¦   +-- axios.js
        ¦   +-- chats.js
        +-- assets/
        +-- components/
        ¦   +-- ChatInput.jsx
        ¦   +-- ChatWindow.jsx
        ¦   +-- MessageBubble.jsx
        ¦   +-- Navbar.jsx
        ¦   +-- Sidebar.jsx
        ¦   +-- VoiceUpload.jsx
        +-- context/
        ¦   +-- AuthContext.jsx
        ¦   +-- LanguageContext.jsx
        +-- pages/
        ¦   +-- Chat.jsx
        ¦   +-- Login.jsx
        ¦   +-- Signup.jsx
        +-- routes/
            +-- ProtectedRoute.jsx
```

## Backend API

### Auth routes

- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`
- `PUT /auth/language`

### Chat routes

- `POST /chats/new`
- `GET /chats/`
- `GET /chats/{chat_id}`
- `POST /chats/{chat_id}/message`
- `POST /chats/{chat_id}/upload-voice`

## Database collections

### users

- `_id`
- `full_name`
- `email`
- `hashed_password`
- `preferred_language`
- `created_at`

### chats

- `_id`
- `user_id`
- `title`
- `created_at`
- `updated_at`

### messages

- `_id`
- `chat_id`
- `user_id`
- `role`
- `text`
- `language`
- `voice_path`
- `created_at`

## How multilingual behavior works right now

1. The frontend sends every message with the currently selected language code.
2. The backend normalizes and stores that language for the message and the user preference.
3. The backend generates a dummy medical response in English.
4. The backend translates the reply into the selected language using `deep-translator`.
5. If translation fails, a built-in fallback response is returned.

## How to run locally

### 1. Start MongoDB

Make sure MongoDB is running locally on:

```bash
mongodb://localhost:27017
```

### 2. Run the FastAPI backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

The backend will run at [http://localhost:8000](http://localhost:8000).

### 3. Run the React frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at [http://localhost:5173](http://localhost:5173).

## Future model integration point

The main future integration point is the `POST /chats/{chat_id}/message` endpoint in `backend/app/routes/chats.py`. Right now it creates a placeholder medical response through the translator service. Later you can replace that response generation with:

- symptom preprocessing
- disease prediction model inference
- confidence scoring
- disease description lookup
- precaution generation
- multilingual translation on the final structured answer

## Notes

- Voice upload is stored under `backend/app/uploads/voice/`.
- Uploaded voice files are stored on disk and the path is saved in MongoDB.
- No transcription or ML prediction is connected yet.
- The frontend and backend contracts are aligned and ready for future expansion.
=======
# Med_ai-chatbot
>>>>>>> 5268dc60b4e80806a7dbf29e86c2b00a9a12c923
