# Convi — Project Background & Development Handover

**Document type:** Project Context / Agent Handover  
**Last updated:** 2026-11-20  
**Project name:** Convi  
**Tagline:** Turn knowledge into fluency.  
**Product description:** Your personal AI language coach.  
**Supporting message:** Practice with AI. Speak with confidence.

---

# 1. Project Overview

## 1.1 What is Convi?

Convi is an AI-powered language learning application designed to help learners transform passive language knowledge into active speaking ability.

Its central idea is:

**Turn knowledge into fluency through structured, repetitive, contextualized practice.**

Traditional language learning often focuses on:
- Memorizing vocabulary.
- Studying grammar rules.
- Reading textbooks.
- Watching videos.
- Understanding conversations.

However, understanding a sentence does not necessarily mean being able to produce it naturally and quickly.

A learner may recognize a word, understand a grammatical structure, and even know how to construct a sentence, but still struggle to use it in spontaneous conversation.

Convi aims to address this gap.

Rather than simply providing more learning materials, Convi focuses on converting existing language knowledge into usable language skills through repeated production.

## 1.2 Core Philosophy

The product is built around several principles.

### 1. Knowledge is not fluency

Knowing a word or understanding a sentence is different from being able to use it automatically.

Convi should emphasize active production rather than passive recognition.

### 2. Patterns are more useful than isolated vocabulary

Learning individual words is important, but words become useful when learners understand how they work in complete sentences.

For example:

Instead of learning only:

- käydä — to visit / go
- kauppa — shop
- huomenna — tomorrow

Learn a reusable pattern:

- Käyn kaupassa.
- Käyn huomenna kaupassa.
- Käytkö sinä kaupassa?
- En käy tänään kaupassa.

The learner gradually understands how vocabulary, grammatical forms, and sentence structures interact.

### 3. Repetition builds automaticity

Repeatedly producing a sentence pattern helps develop faster retrieval and more automatic speech.

The goal is not simply to answer correctly once.

The goal is to reach a point where producing the sentence requires little conscious effort.

### 4. Context matters

Language should be learned through meaningful situations, natural conversations, and realistic expressions.

Convi should prioritize:
- Short dialogues.
- Natural spoken expressions.
- Common sentence patterns.
- Frequently used chunks.
- Contextualized examples.
- Practical everyday language.

### 5. Structured practice before free production

Completely open-ended AI conversations can be overwhelming, especially for intermediate and lower-level learners.

Convi should provide a progression from controlled practice to more independent production.

AI should support this learning process rather than simply act as a chatbot.

---

# 2. Product Vision and Learning Objectives

## 2.1 Long-term Vision

Convi should become a personal AI language coach that helps learners:

1. Build a structured vocabulary and language knowledge base.
2. Discover useful sentence patterns from learning materials.
3. Practice vocabulary and grammar through structured drills.
4. Develop automaticity through repetition.
5. Improve listening and speaking abilities.
6. Track learning progress over time.
7. Gradually move from controlled exercises to spontaneous communication.

The application should support different proficiency levels and different languages.

## 2.2 Different Learning Needs by CEFR Level

The learning strategy should adapt to proficiency levels.

| Level | Main learning focus | Suitable content |
|---|---|---|
| A1 | Basic vocabulary and simple sentences | Everyday words, basic sentence structures |
| A2 | Vocabulary application and fundamental grammar | Common expressions, short dialogues |
| B1 | Sentence production and communication | Everyday conversations, useful chunks |
| B2 | Natural expression and fluency | Authentic conversations, collocations, nuanced expressions |
| C1+ | Precision and sophistication | Advanced chunks, idiomatic expressions, specialized materials |

These are intended learning priorities rather than finalized curriculum rules.

A particularly important distinction:

- Beginners need help constructing correct sentences.
- Intermediate learners need help producing natural expressions efficiently.
- Advanced learners need help improving precision, flexibility, and expressive range.

## 2.3 Initial Personal Use Case

The original development motivation comes from the need to improve Finnish and English.

Current learning context:

- Finnish: Developing foundational vocabulary, grammar, listening, and everyday communication.
- English: Approximately B1–B2 as a working estimate, with particular interest in speaking, natural expressions, and common chunks.

These are initial personal use cases, not restrictions on the product's eventual target audience.

---

# 3. Learning Methodology

This is one of the most important parts of the project.

Convi should not be designed as a generic AI conversation application.

Its main learning mechanism should be structured language drills.

## 3.1 FSI-Inspired Pattern Drills

The project draws inspiration from FSI (Foreign Service Institute) language training methods.

The important characteristics are:

- Repetition.
- Immediate response.
- Sentence pattern manipulation.
- Vocabulary substitution.
- Grammatical transformation.
- Increasing response speed.
- Active sentence production.

The learner should repeatedly produce variations of a sentence rather than simply read explanations.

Example:

Base sentence:

> Minä asun Helsingissä.

Substitution:

- Tampereella
- Turussa
- Kuopiossa

Expected responses:

- Minä asun Tampereella.
- Minä asun Turussa.
- Minä asun Kuopiossa.

The learner practices both vocabulary retrieval and grammatical adaptation.

## 3.2 Main Drill Types

The following drill types form the conceptual foundation.

### A. Substitution Drill

Replace one or more elements in a sentence while preserving the underlying pattern.

Example:

Base:

> I usually drink coffee in the morning.

Prompts:
- tea
- milk
- water

Responses:
- I usually drink tea in the morning.
- I usually drink milk in the morning.
- I usually drink water in the morning.

For Finnish, substitution must account for morphological changes.

A replacement word may require a different case, ending, or grammatical form.

### B. Transformation Drill

Transform a sentence according to a grammatical instruction.

Examples:

- Affirmative → Negative
- Statement → Question
- Present → Past
- Singular → Plural
- First person → Third person

Example:

> Minä asun Helsingissä.

Transformation:

Make it negative.

> En asu Helsingissä.

### C. Expansion Drill

Gradually expand a simple sentence with additional information.

Example:

Base:

> I work.

Expansion:

> I work in Finland.

> I work in Finland as a software developer.

> I work in Finland as a software developer, but I am currently studying IoT.

This helps learners develop longer and more complex sentences.

### D. Guided Production

The learner receives a situation, a prompt, or several required elements and produces a sentence or short response.

Example:

Situation: You want to explain why you are late.

Required elements:
- bus
- yesterday
- problem

The learner constructs a meaningful response.

### E. Free Production

The learner produces language more independently.

Examples:
- Answer a question.
- Describe an experience.
- Explain an opinion.
- Participate in a conversation.

AI can evaluate the response and provide corrections.

These drill types should be independently configurable.

Not every piece of learning material needs to support every drill type.

## 3.3 Important Learning Progression

A conceptual learning progression:

1. Understand the original sentence.
2. Recognize its grammatical structure.
3. Practice substitution.
4. Practice grammatical transformation.
5. Expand the sentence.
6. Produce the sentence with fewer hints.
7. Use the pattern in a short dialogue.
8. Use it independently in conversation.

This is the preferred progression, not necessarily a rigid sequence that every exercise must follow.

## 3.4 Audio and Speaking

The initial implementation should prioritize text-based validation of the learning methodology.

Audio and speech functionality should come later.

Potential future capabilities:

- Text-to-speech.
- Speech recognition.
- Spoken substitution drills.
- Pronunciation feedback.
- Listening exercises.
- AI voice conversations.

Do not make voice interaction a prerequisite for the initial MVP.

---

# 4. Learning Content and Material Management

## 4.1 Two Main Sources of Learning Content

Convi should support two complementary content sources.

**Source A: Structured vocabulary database**

A database of vocabulary, grammatical forms, and generated example sentences.

**Source B: Learning materials**

Textbooks, dialogues, transcripts, articles, and other authentic language resources.

These sources serve different purposes.

Vocabulary provides systematic coverage of frequently used words and grammatical forms.

Learning materials provide natural expressions, reusable sentence patterns, and context.

## 4.2 Vocabulary-Based Learning

The original Finnish vocabulary project uses a frequency-based vocabulary list.

Known progress:

- Approximately 949 common Finnish words have been collected.
- Vocabulary entries contain source information and frequency-related fields.
- The dataset includes fields such as:
  - LEMMA
  - POS_CLASS
  - ABS_FREQ_S24

The exact schema should be checked against the current database and source files.

The objective is to transform this raw vocabulary list into structured learning content.

The vocabulary system should eventually support:

- Lemma.
- Part of speech.
- Frequency.
- CEFR level.
- Grammatical information.
- Inflected forms.
- Example sentences.
- Topics.
- Learning status.
- Exercise history.

CEFR labels should be treated as useful learning metadata, not automatically assumed to be authoritative for every frequency-list entry.

## 4.3 Finnish Morphology

Finnish requires particular attention to morphology.

A vocabulary item cannot always be substituted directly into a sentence.

For example:

> talo

Possible forms:

- talo
- talon
- taloa
- talossa
- talosta
- taloon
- talolla

Convi should eventually distinguish:

- Lemma.
- Inflected form.
- Grammatical case.
- Number.
- Person.
- Tense.
- Other relevant grammatical features.

The application should avoid treating Finnish vocabulary as a simple English-style word-to-translation mapping.

The goal is to teach learners how words behave inside sentences.

---

# 5. Vocabulary Form Generation Project

This is a current data preparation workstream.

## 5.1 Objective

Generate structured form targets for the Finnish vocabulary database.

These targets describe which grammatical forms are relevant for a particular vocabulary item.

They can subsequently be used to generate example sentences and build exercises.

## 5.2 Current Progress

As of the latest confirmed project checkpoint:

- 949 vocabulary entries have been classified.
- A pilot validation was completed.
- The pilot contained 20 words.
- It produced 82 form targets.
- The pilot review passed.
- One special positional label associated with `koti` was corrected.
- No remaining duplicate or structural problems were identified in the pilot.

Important: The 949-word classification is complete, but the bulk form-generation process had not yet started at the last confirmed checkpoint.

Do not assume that all 949 words already have generated and validated form targets.

Additional facts confirmed by repository inspection (2026-11-20):

- The 949-word classification is stored in `backend/data-generation/vocabulary/vocabulary_classification.csv`.
- Topics 1–3 (93 words) already have 233 **v0** form targets in `vocabulary_forms`, using legacy labels. Decision: regenerate them with the v1 policy and replace the v0 rows.
- Generation output uses the field name `target_type`, matching the database.

Current status: [STATUS.md](STATUS.md) · workstream detail: [FORM_TARGET_GENERATION_CHECKPOINT.md](data-generation/FORM_TARGET_GENERATION_CHECKPOINT.md).

## 5.3 Generation Strategy

The agreed approach is topic-based batch processing.

Recommended batch size:

- Default: 15 words.
- Acceptable range: 10–20 words.

The proposed workflow:

1. Select a vocabulary topic.
2. Retrieve the corresponding words.
3. Generate form targets through an AI API.
4. Validate the returned JSON.
5. Run structural and duplicate checks.
6. Save the results locally as JSON and CSV.
7. Review the generated content.
8. Import approved results into PostgreSQL.

**Important decision: Do not write bulk-generated results directly into PostgreSQL before validation and approval.**

The intended destination table is:

`vocabulary_forms`

## 5.4 Existing Documentation and Files

The following files were explicitly created and should be preserved. Actual locations (reorganized 2026-11-20):

```text
docs/
└── data-generation/
    ├── FORM_TARGET_GENERATION_CHECKPOINT.md
    ├── grammatical-label-policy.md
    ├── form-generation-policy.md
    └── legacy/wordforms-topic-1-3.md      # source of the v0 forms

backend/data-generation/
├── vocabulary/
│   ├── finnish_vocabulary.csv
│   ├── vocabulary_classification.csv
│   └── vocabulary_classification_report.md
├── form_targets/
│   ├── prompts/form_generation_v1.md
│   └── outputs/pilot/{pilot.json, pilot.csv}
└── legacy_v0/vocabulary_forms_topic_1_3.json
```

These files represent the existing documentation, datasets and pilot artifacts.

Do not delete or replace them without inspecting their contents. Prompts are versioned: create a new prompt version instead of editing one that produced reviewed output.

## 5.5 Next Confirmed Action

The last confirmed next step was:

1. ~~Check the completeness and consistency of the existing directory structure.~~ Done 2026-11-20.
2. Implement an independent batch-processing tool.
3. Keep generation outputs in local JSON/CSV.
4. Continue validating before database import.

The batch-processing tool should ideally separate:

- Input selection.
- AI generation.
- JSON parsing.
- Schema validation.
- Duplicate detection.
- Output persistence.
- Error reporting.

---

# 6. AI-Generated Example Sentences

## 6.1 Motivation

A vocabulary list alone is not sufficient for learning.

Each vocabulary item should eventually have enough contextualized example sentences to support meaningful practice.

For example, a word may appear in several grammatical forms and contexts.

The system should generate sentences that demonstrate actual usage.

## 6.2 Proposed Generation Workflow

The agreed conceptual approach:

1. The learner selects a vocabulary group or topic.
2. Convi checks whether enough example sentences already exist.
3. If sufficient content exists, the learner can immediately start practicing.
4. If content is insufficient, AI generates additional examples.
5. Generated examples are validated and saved.
6. Future sessions reuse the existing examples.

This avoids unnecessary generation every time the learner starts a session.

## 6.3 Topic-Based Content Generation

Example:

Topic: Daily activities.

Vocabulary:
- herätä
- syödä
- käydä
- tehdä
- mennä

AI generates sentences using these words in realistic situations.

The generated material should ideally include:

- Finnish sentence.
- Translation.
- Target vocabulary.
- Target grammatical form.
- Sentence pattern.
- Context or topic.
- CEFR estimate.
- Source type.
- Generation metadata.

These fields are proposed content requirements; the final database schema should be checked before implementation.

## 6.4 Content Quality Requirements

Generated sentences should be:

- Grammatically correct.
- Natural rather than mechanically constructed.
- Appropriate for the learner's proficiency level.
- Short enough for repeated speaking practice.
- Contextually meaningful.
- Useful in real communication.

For Finnish, grammatical correctness and morphological accuracy are especially important.

The AI should not simply insert a target word into a sentence without checking its inflection.

---

# 7. Learning Materials and Pattern Extraction

## 7.1 Why External Materials Matter

Vocabulary-based content provides systematic learning coverage.

However, real conversations contain expressions and chunks that cannot be adequately captured through isolated vocabulary lists.

Examples:

- I was wondering if...
- It turns out that...
- As far as I know...
- I don't really feel like...
- The thing is...

These expressions are useful because they provide reusable language structures.

Convi should therefore support importing existing learning materials.

## 7.2 Supported Material Types

Initial material-processing priorities:

1. EPUB.
2. Searchable PDF.
3. TXT.
4. DOCX may also be supported.

Scanned PDFs and OCR are not a priority for the initial implementation.

## 7.3 Material Processing Pipeline

Proposed workflow:

```text
Learning Material
       |
       v
Document Parsing
       |
       v
Chapter / Dialogue Extraction
       |
       v
AI Content Extraction
       |
       +---- Chunks
       |
       +---- Sentence Patterns
       |
       +---- Drills
       |
       +---- Context
       |
       +---- Difficulty
       |
       v
Structured JSON
       |
       v
Schema Validation
       |
       v
Human Review
       |
       v
Database
```

## 7.4 Pattern Extraction

For example, from a conversation:

> Are you doing anything this weekend?

A useful pattern could be:

`Are you doing anything + time expression?`

Potential variations:

- Are you doing anything tonight?
- Are you doing anything tomorrow?
- Are you doing anything next weekend?

This can become substitution-drill material.

Another example:

> I was wondering if you could help me.

Reusable pattern:

`I was wondering if you could + verb`

Potential variations:

- I was wondering if you could explain this.
- I was wondering if you could give me a hand.
- I was wondering if you could send me the information.

The goal is to identify reusable structures, not simply collect isolated sentences.

## 7.5 Material Source and Copyright Distinction

The database should distinguish:

- Original source material.
- AI-extracted structures.
- AI-generated examples.
- Human-edited content.

Source information should be retained.

The same source material may be useful for different learning modes.

For example, one dialogue may produce:

- Substitution drills.
- Transformation drills.
- Listening exercises.
- Guided production.

The user explicitly accepted that the same underlying material may be stored more than once when it serves different training modes.

A training-mode field or equivalent relationship should make these distinctions explicit.

---

# 8. Training Content Data Model

The following is a conceptual model, not a claim that all these tables have already been implemented.

## 8.1 Main Conceptual Entities

| Entity | Responsibility |
|---|---|
| Vocabulary | Stores words and lemmas |
| Vocabulary Forms | Stores grammatical forms and form targets |
| Topics | Groups learning content |
| Learning Materials | Stores imported books, dialogues, and documents |
| Patterns | Stores reusable sentence structures |
| Chunks | Stores useful multi-word expressions |
| Example Sentences | Stores contextualized examples |
| Exercises | Defines drill content and training mode |
| Exercise Items | Stores individual prompts and expected responses |
| Learning Sessions | Records practice sessions |
| User Progress | Tracks learning status and performance |

## 8.2 Important Relationships

```text
Vocabulary
    |
    +---- Vocabulary Forms
    |
    +---- Example Sentences
    |
    +---- Topics

Learning Materials
    |
    +---- Extracted Patterns
    |
    +---- Extracted Chunks
    |
    +---- Source Sentences

Patterns
    |
    +---- Exercises
              |
              +---- Exercise Items
              |
              +---- Learning Sessions
```

The actual relational model should be designed according to the existing PostgreSQL schema.

Do not create duplicate tables or redefine existing entities before inspecting the database.

## 8.3 Important Metadata

Content should carry useful metadata, including:

- Language.
- Topic.
- CEFR level.
- Source.
- Training mode.
- Target vocabulary.
- Target grammatical forms.
- Difficulty.
- Validation status.
- Generation model or prompt version where appropriate.

This makes it possible to reuse content across different learning experiences.

---

# 9. Application Architecture and Technology Stack

## 9.1 Architectural Philosophy

The initial goal is to validate the core learning logic before investing heavily in UI development.

The project should keep the learning engine independent from the frontend.

This makes it possible to:

- Test core functions locally.
- Generate content through Python scripts.
- Validate database operations.
- Add HTTP APIs later.
- Reuse the same backend for web and mobile applications.

## 9.2 Frontend

Current technology direction:

| Technology | Purpose |
|---|---|
| React | UI framework |
| TypeScript | Type safety |
| Vite | Web development and build tooling |
| React Native | Mobile application |
| Expo | React Native development environment |

The initial web MVP uses React, TypeScript, and Vite.

React Native with Expo is the intended direction for mobile development.

## 9.3 Backend

Python is the preferred initial backend language.

Reasons:

- Good AI integration ecosystem.
- Convenient data processing.
- Easy document parsing.
- Good support for batch generation.
- Suitable for language-processing tasks.
- Can be exposed through HTTP APIs later.

The intended architecture is:

```text
React / React Native
         |
         | HTTP API
         v
      Python Backend
         |
         +---- AI Services
         |
         +---- Content Processing
         |
         +---- Learning Engine
         |
         +---- PostgreSQL
```

The backend should not be tightly coupled to either frontend.

## 9.4 Database

PostgreSQL is the intended persistent database.

Azure Database for PostgreSQL has been explored.

Previous cost concerns led to a reduction in compute capacity to the B1ms tier, with discussion of the student subscription's 750 free hours.

The current database status and actual billing configuration must be checked before assuming the service is still running or available.

## 9.5 Local Development First

The original development approach:

- Keep frontend and backend in one repository.
- Run Python backend functions locally.
- Validate API behavior.
- Test database operations.
- Implement the learning engine independently.
- Add a thin HTTP API layer.
- Deploy the backend later.

The user understands that Python business logic can be reused when deploying the backend as a cloud service, with an API layer added around it.

---

# 10. Development Environment and Existing Technical Progress

## 10.1 React Native / Expo

The following initial steps have already been explored:

- Created an Expo application.
- Connected the application through Expo Go.
- Established a basic mobile development environment.
- Tested communication between the frontend and backend.

An API connectivity issue was encountered:

**CORS error when the Expo development application called the backend API.**

The backend was reportedly configured in a production mode at that point.

The appropriate development configuration or proxy strategy still needs to be checked.

Do not assume this issue has been resolved.

## 10.2 Azure PostgreSQL

The user has:

- Explored Azure PostgreSQL.
- Investigated student subscription benefits.
- Changed compute capacity to B1ms.
- Asked whether free compute hours mean actual usage hours or server uptime.
- Asked whether changing compute capacity preserves existing database data.

Before modifying the database, inspect its current configuration and ensure data is backed up.

## 10.3 API Design

The general design direction is:

- Frontend communicates through HTTP.
- Backend owns business logic.
- Database operations remain on the backend.
- AI calls are not made directly from the client.
- Document processing and content generation are backend responsibilities.

Detailed API endpoints and request/response schemas have not been fully established in the available project history.

---

# 11. Initial MVP Scope

The project should prioritize validating the core learning mechanism rather than building a large application immediately.

## 11.1 MVP Objectives

The first meaningful version should demonstrate that a learner can:

1. Select vocabulary or learning material.
2. Retrieve existing learning content.
3. Generate missing content when necessary.
4. Start a structured drill.
5. Receive and respond to prompts.
6. Have responses evaluated.
7. Receive useful corrections.
8. Repeat the exercise.
9. Track basic learning progress.

## 11.2 Suggested MVP Features

### Content Management
- Vocabulary list.
- Topic-based organization.
- Example sentence storage.
- Pattern and chunk storage.
- Basic material import.

### Learning Engine
- Substitution drills.
- Transformation drills.
- Basic sentence production.
- Expected answer validation.
- AI-assisted feedback.

### Progress Tracking
- Completed exercises.
- Correct and incorrect answers.
- Exercise history.
- Basic vocabulary learning status.

### User Interface
- Minimal navigation.
- Topic selection.
- Exercise screen.
- Prompt and answer display.
- Feedback display.
- Session completion.

The UI should remain simple while the underlying learning experience is being validated.

## 11.3 Development Priorities

Recommended priority:

1. Reliable content data model.
2. Vocabulary and form generation.
3. Example sentence generation.
4. Drill execution engine.
5. Answer evaluation.
6. Basic progress tracking.
7. Minimal frontend.
8. Audio and speech integration.

The exact order should be adjusted according to the existing repository and completed implementation.

---

# 12. Current Project Status

This section is particularly important for the desktop Agent.

> This table was originally written from project discussions. It has been corrected after the repository inspection on 2026-11-20. **[STATUS.md](STATUS.md) is the authoritative, maintained status.**

| Workstream | Status | Notes |
|---|---|---|
| Product concept | Established | AI language coach focused on fluency |
| Learning philosophy | Established | Pattern drills and active production |
| Drill methodology | Designed | Substitution, transformation, expansion, guided/free production |
| Frontend technology | Selected direction | React, TypeScript, Vite — no web project exists yet |
| Mobile technology | Implemented (partial) | Expo app with topic browsing and example sessions |
| Backend technology | Implemented (partial) | Python, FastAPI, SQLAlchemy, Alembic |
| Database technology | Implemented | PostgreSQL on Azure, 7 tables |
| Finnish vocabulary collection | Completed | 949 words, 41 topics, in the database |
| Vocabulary classification | Completed | 949 entries; CSV in `backend/data-generation/vocabulary/` |
| Form targets v0 (topics 1–3) | In database, to be replaced | 233 targets, legacy labels |
| Form target pilot (v1) | Completed | 20 words, 82 targets |
| Pilot validation | Passed | One `koti` positional-label correction |
| Form generation policies | Documented | Use `target_type` |
| Batch form generation | Next | Tool not started |
| Example sentence generation | Implemented | Script and API endpoint with automatic validation |
| Material import | Designed conceptually | EPUB, searchable PDF, TXT |
| Pattern extraction | Designed conceptually | AI extraction and review |
| Learning sessions | Partial | Example-sentence sessions in the mobile app; no drill engine |
| Speech functionality | Future scope | Text-to-speech only; not an MVP dependency |

---

# 13. Immediate Development Roadmap

## Phase 1 — Stabilize Data Generation

Goal: Establish a reliable, repeatable content-generation pipeline.

Tasks:

- [x] Inspect the current project directory.
- [x] Verify all existing documentation and prompts.
- [x] Review the vocabulary classification output.
- [ ] Implement an independent batch form-generation tool.
- [ ] Support topic-based selection.
- [ ] Support configurable batch sizes, defaulting to 15.
- [ ] Generate JSON outputs.
- [ ] Generate CSV outputs.
- [ ] Implement schema validation.
- [ ] Implement duplicate detection.
- [ ] Produce a clear error report.
- [ ] Validate multiple batches.
- [ ] Review the generated content.
- [ ] Import approved results into `vocabulary_forms`.

Important: Do not directly insert unreviewed AI output into PostgreSQL.

## Phase 2 — Example Sentence Generation

Goal: Build a reusable example sentence repository.

Tasks:

- [ ] Define example sentence requirements.
- [ ] Define a suitable structured output schema.
- [ ] Generate sentences by topic.
- [ ] Include target vocabulary and grammatical forms.
- [ ] Validate Finnish morphology.
- [ ] Store approved examples.
- [ ] Implement a content availability check.
- [ ] Reuse existing examples when sufficient.
- [ ] Generate additional examples only when needed.

## Phase 3 — Core Drill Engine

Goal: Make the learning methodology executable.

Tasks:

- [ ] Define exercise data structures.
- [ ] Implement substitution drill logic.
- [ ] Implement transformation drill logic.
- [ ] Implement prompt generation.
- [ ] Implement expected answer handling.
- [ ] Implement answer evaluation.
- [ ] Implement correction and feedback.
- [ ] Support repeated practice.
- [ ] Add basic session tracking.

The drill engine should be independent of the UI.

## Phase 4 — Learning Material Import

Goal: Support importing and extracting useful patterns from external materials.

Tasks:

- [ ] Implement TXT parsing.
- [ ] Implement EPUB parsing.
- [ ] Implement searchable PDF parsing.
- [ ] Extract chapters and dialogues.
- [ ] Implement AI-based pattern extraction.
- [ ] Extract useful chunks.
- [ ] Associate extracted content with its source.
- [ ] Add validation and human review.
- [ ] Store approved content in the database.
- [ ] Associate content with suitable training modes.

## Phase 5 — Basic Frontend

Goal: Connect the learning engine to a usable application.

Tasks:

- [ ] Establish frontend/backend communication.
- [ ] Implement topic selection.
- [ ] Implement vocabulary selection.
- [ ] Implement exercise screens.
- [ ] Display prompts and expected responses.
- [ ] Display corrections.
- [ ] Implement session completion.
- [ ] Display basic progress.

## Phase 6 — Expansion

Potential future features:

- [ ] Audio playback.
- [ ] Speech recognition.
- [ ] Pronunciation feedback.
- [ ] AI speaking conversations.
- [ ] Personalized learning recommendations.
- [ ] Spaced repetition.
- [ ] Advanced progress analytics.
- [ ] More languages.
- [ ] More sophisticated material processing.

These are long-term possibilities, not current MVP requirements.

---

# 14. Important Product and Architecture Decisions

The following decisions should be respected unless the user explicitly changes them.

### Decision 1: FSI-Inspired Drills Are Central

Convi should not become just another AI chatbot.

Structured repetition and pattern drills are the core learning mechanism.

### Decision 2: Controlled Production Comes Before Free Conversation

Open-ended conversation should not be the primary initial exercise.

The learner should first develop the ability to produce useful sentence patterns.

### Decision 3: Content and Learning Logic Should Be Separated

Vocabulary, patterns, examples, and exercises should be stored as reusable content.

The frontend should not contain the core learning logic.

### Decision 4: Content Generation Should Be Reusable

AI-generated content should be saved and reused.

Do not regenerate the same content every time a learner opens a topic.

### Decision 5: Topic-Based Generation

Vocabulary and example sentence generation should be organized by topic.

This makes generation easier to manage, validate, and review.

### Decision 6: Validate Before Database Import

Generation output should first be stored locally and validated.

Database insertion should happen only after appropriate checks and approval.

### Decision 7: One Source Can Support Multiple Drill Modes

The same dialogue or sentence can support different exercises.

The data model should accommodate this.

### Decision 8: Text First, Audio Later

The initial learning engine should work without speech recognition or voice APIs.

### Decision 9: Keep the First UI Simple

Do not spend excessive time on visual design before the learning mechanism is validated.

### Decision 10: Maintain a Clear Project Record

Use documentation and checkpoints to preserve decisions and progress.

Avoid relying on conversational history as the only source of project knowledge.

---

# 15. Project Organization and Documentation

The project should maintain a clear separation between:

```text
docs/
    Project documentation
    Architecture decisions
    Data policies
    Generation checkpoints

data_generation/
    Generation scripts
    Prompts
    Validation utilities

outputs/
    Generated JSON
    CSV exports
    Pilot results
    Review artifacts

backend/
    Python business logic
    API
    Database access

frontend/
    React application

mobile/
    React Native / Expo application
```

This is an organizational illustration. The actual repository layout is documented in the [documentation index](README.md): project documents live in `docs/`, and datasets, prompts and generated outputs live in `backend/data-generation/`. There is no separate `frontend/` directory yet.

Recommended documentation practices:

- Keep project overview and architecture documents.
- Maintain a checkpoint for each major data-generation workstream.
- Version prompts and generation policies.
- Record important architectural decisions.
- Document completed tasks and remaining tasks.
- Keep raw generation outputs separate from approved production data.

---

# 16. Instructions for the Desktop Agent

The Agent should behave as a technical collaborator and project assistant.

## 16.1 First Action: Inspect Before Changing

Before making code changes:

1. Inspect the repository.
2. Read README and project documentation.
3. Read existing generation policies.
4. Inspect current database schemas.
5. Inspect existing scripts and generated data.
6. Identify what is implemented versus merely documented.
7. Report discrepancies between this handover and the repository.

Do not assume the status table represents the exact current code state.

## 16.2 Do Not Rebuild Existing Work

Preserve existing implementations and documentation whenever possible.

Do not:
- Recreate already completed datasets.
- Replace existing database schemas without justification.
- Delete previous generation outputs.
- Introduce unnecessary dependencies.
- Rewrite working components merely to follow a different architectural preference.

## 16.3 Work Incrementally

The user prefers a step-by-step development workflow.

For larger tasks:

1. Explain the immediate objective.
2. Identify the relevant files.
3. Propose the smallest implementation.
4. Explain important design decisions.
5. Implement one manageable step.
6. Run tests or validation.
7. Summarize what changed.
8. Update documentation and the checkpoint.
9. Explain the next step.

Avoid presenting a large number of unrelated tasks simultaneously.

## 16.4 Distinguish Facts from Suggestions

When proposing an architecture or schema:

- Clearly identify existing decisions.
- Explain when something is a new recommendation.
- Do not silently change established requirements.
- Ask before making significant architectural changes.

## 16.5 Prioritize Data Quality

For AI-generated language content:

- Use structured output.
- Validate schemas.
- Detect duplicates.
- Preserve source information.
- Check grammatical consistency.
- Review edge cases.
- Keep generated and approved content distinguishable.

For Finnish, grammatical form accuracy is particularly important.

## 16.6 Documentation Is Part of Development

Whenever an important implementation or decision is completed:

- Update the relevant documentation.
- Update the corresponding checkpoint.
- Record what is complete.
- Record known limitations.
- Record the next actionable task.

This is necessary because the project is developed across multiple sessions and tools.

---

# 17. Open Questions and Items Requiring Verification

The following points should not be treated as finalized.

1. Exact current PostgreSQL schema.
2. Exact relationships between vocabulary, forms, topics, patterns, and examples.
3. Final CEFR assignment methodology.
4. Final example sentence schema.
5. Exact content sufficiency thresholds for each topic.
6. Whether content generation should use one model or different models for different tasks.
7. Final API framework and endpoint structure.
8. Final authentication strategy.
9. Exact progress-tracking model.
10. Final deployment architecture.
11. Whether learning materials should be stored as full documents or extracted segments.
12. How AI feedback should distinguish grammatical errors from stylistic alternatives.
13. How Finnish colloquial speech (puhekieli) should be represented alongside standard Finnish.

These should be resolved when the corresponding implementation requires them, not all at once.

---

# 18. Definition of Success

Convi will have achieved its initial product objective when a learner can:

1. Select a topic.
2. Access relevant vocabulary and contextualized examples.
3. Practice useful sentence patterns through substitution and transformation.
4. Produce answers independently.
5. Receive accurate and understandable feedback.
6. Repeat exercises efficiently.
7. Revisit previously learned material.
8. Observe measurable improvements in their ability to produce language.

The most important success metric is not the amount of content generated or the number of exercises completed.

It is whether learners become increasingly capable of producing natural language without consciously constructing every sentence from scratch.

---

# 19. Final Project Summary

**Convi is an AI-powered language learning application focused on converting passive language knowledge into active speaking ability.**

Its core methodology combines:

- Frequency-based vocabulary learning.
- Grammatical form awareness.
- Contextualized example sentences.
- Authentic learning materials.
- Reusable chunks and sentence patterns.
- FSI-inspired substitution and transformation drills.
- Guided and free production.
- AI-assisted feedback.
- Progress tracking.

The technical direction is:

- React + TypeScript + Vite for the initial web application.
- React Native + Expo for mobile.
- Python for backend and content-processing logic.
- PostgreSQL for persistent data.
- AI APIs for content generation, extraction, and evaluation.

The immediate priority is to establish a reliable language-content pipeline, beginning with Finnish vocabulary form generation and subsequently example sentence generation.

The project should develop incrementally, validating its learning methodology and data quality before investing heavily in interface complexity.

**Convi — Turn knowledge into fluency.**