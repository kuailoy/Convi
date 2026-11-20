# Convi mobile app

Expo / React Native app for Convi, using Expo Router (file-based routes in `src/app/`).
Project overview: [../README.md](../README.md). Rules for coding agents: [AGENTS.md](AGENTS.md).

## Setup

```bash
npm install
cp .env.example .env.local
```

Set `EXPO_PUBLIC_API_BASE_URL` in `.env.local` to the backend base URL. Expo public variables are bundled into the app, so use them only for public values. API keys always stay on the backend.

## Run

```bash
npx expo start      # dev server (Expo Go, simulator or development build)
npx expo lint       # lint
npx tsc --noEmit    # type check
```

## Structure

```text
src/
├── app/            # Screens (routes)
│   ├── (tabs)/     # Home, Learn, Progress
│   ├── session/    # Vocabulary example session: session/[id] = topic slug
│   ├── pattern-drill.tsx   # Placeholder
│   └── settings.tsx
├── api/            # API client and response types
├── state/          # LearningContext: topic cache and local progress
├── ui/             # Shared components, theme, navigation helper
└── utils/          # Grammatical label formatting
```

## Data and progress

- Topics and topic contents come from the backend (`/api/v1/vocabulary/...`).
- Example sentences are read aloud with `expo-speech` (Finnish voice).
- The topic list and learning progress are cached on the device with AsyncStorage. **Settings → Clear learning progress** resets progress; the topic cache is kept.
