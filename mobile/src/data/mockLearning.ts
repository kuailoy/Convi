// UI preview data only. It is deliberately separate from API responses and database models.
export type MockExercise = {
  mode: string;
  helper: string;
  prompt: string;
  promptLabel: string;
  speechText?: string;
  speechLanguage?: string;
  highlight?: string;
  cue?: string;
  answer: string;
  explanation: string;
};

export const mockTopics = [
  { id: "pronouns-reference", name: "Pronouns and reference", finnish: "Pronominit", wordCount: 29 },
  { id: "questions-connectors", name: "Questions and connectors", finnish: "Kysymykset ja yhdistäjät", wordCount: 49 },
  { id: "relational-words", name: "Relational words", finnish: "Suhdesanat", wordCount: 15 },
  { id: "time-dates-periods", name: "Time, dates and periods", finnish: "Aika ja päivät", wordCount: 21 },
  { id: "sequence-frequency", name: "Sequence and frequency", finnish: "Aikajärjestys", wordCount: 45 },
  { id: "numbers-quantity-comparison", name: "Numbers, quantity and comparison", finnish: "Määrä ja vertailu", wordCount: 44 },
  { id: "place-direction", name: "Place and direction", finnish: "Paikka ja suunta", wordCount: 45 },
  { id: "ability-necessity", name: "Ability and necessity", finnish: "Kyky ja pakko", wordCount: 15 },
  { id: "everyday-verbs", name: "Everyday verbs", finnish: "Arjen verbit", wordCount: 25 },
  { id: "handling-objects-actions", name: "Handling objects and physical actions", finnish: "Esineiden käsittely", wordCount: 20 },
  { id: "movement-travel", name: "Movement and travel", finnish: "Liikkuminen", wordCount: 29 },
  { id: "speaking-conversation", name: "Speaking and conversation", finnish: "Puhuminen", wordCount: 20 },
  { id: "messages-writing", name: "Messages and writing", finnish: "Viestit ja kirjoittaminen", wordCount: 17 },
  { id: "requests-agreements", name: "Requests and agreements", finnish: "Pyynnöt ja sopiminen", wordCount: 13 },
  { id: "senses-perception", name: "Senses and perception", finnish: "Aistit ja havainnot", wordCount: 13 },
  { id: "thinking-understanding", name: "Thinking and understanding", finnish: "Ajattelu", wordCount: 29 },
  { id: "people-family", name: "People and family", finnish: "Ihmiset ja perhe", wordCount: 35 },
  { id: "jobs-social-roles", name: "Jobs and social roles", finnish: "Ammatit ja roolit", wordCount: 12 },
  { id: "feelings-relationships", name: "Feelings and relationships", finnish: "Tunteet ja suhteet", wordCount: 43 },
  { id: "home-housing", name: "Home and housing", finnish: "Koti", wordCount: 20 },
  { id: "food-drink", name: "Food and drink", finnish: "Ruoka ja juoma", wordCount: 9 },
  { id: "body-health", name: "Body and health", finnish: "Keho ja terveys", wordCount: 23 },
  { id: "study-languages", name: "Study and languages", finnish: "Opiskelu ja kielet", wordCount: 14 },
  { id: "work-business", name: "Work and business", finnish: "Työ ja yritykset", wordCount: 34 },
  { id: "money-shopping", name: "Money and shopping", finnish: "Raha ja ostokset", wordCount: 16 },
  { id: "society-law", name: "Society and law", finnish: "Yhteiskunta ja laki", wordCount: 26 },
  { id: "places-buildings", name: "Places and buildings", finnish: "Paikat ja rakennukset", wordCount: 10 },
  { id: "transport-technology", name: "Transport and technology", finnish: "Liikenne ja tekniikka", wordCount: 16 },
  { id: "nature-animals-weather", name: "Nature, animals and weather", finnish: "Luonto ja sää", wordCount: 21 },
  { id: "culture-media-leisure", name: "Culture, media and leisure", finnish: "Kulttuuri ja vapaa-aika", wordCount: 22 },
  { id: "religion-belief", name: "Religion and belief", finnish: "Uskonto", wordCount: 9 },
  { id: "crime-safety", name: "Crime and safety", finnish: "Rikokset ja turvallisuus", wordCount: 11 },
  { id: "changes-decisions", name: "Changes and decisions", finnish: "Muutokset ja päätökset", wordCount: 31 },
  { id: "problems-coping", name: "Problems and coping", finnish: "Ongelmat", wordCount: 21 },
  { id: "size-properties", name: "Size and physical properties", finnish: "Koko ja ominaisuudet", wordCount: 23 },
  { id: "appearance-temperature", name: "Appearance and temperature", finnish: "Ulkonäkö ja lämpötila", wordCount: 9 },
  { id: "evaluation-correctness", name: "Evaluation and correctness", finnish: "Arviot", wordCount: 21 },
  { id: "ease-suitability", name: "Ease and suitability", finnish: "Helppous ja sopivuus", wordCount: 9 },
  { id: "personality-impressions", name: "Personality and impressions", finnish: "Luonne ja vaikutelma", wordCount: 26 },
  { id: "manner-certainty", name: "Manner and certainty", finnish: "Tavat ja varmuus", wordCount: 39 },
  { id: "reasons-abstract-concepts", name: "Reasons and abstract concepts", finnish: "Syyt ja käsitteet", wordCount: 20 },
];

export const mockTopicExamples = {
  "time-frequency": { word: "aika", meaning: "time", forms: ["aika", "aikaa · some time"], example: "Aika kuluu nopeasti.", translation: "Time passes quickly.", formSentence: "Minulla on aikaa.", formTranslation: "I have time.", pattern: "Minulla on {amount} aikaa." },
  "people-relationships": { word: "ystävä", meaning: "friend", forms: ["ystävä", "ystäväni · my friend"], example: "Hän on ystäväni.", translation: "He is my friend.", formSentence: "Tapaan ystäväni tänään.", formTranslation: "I’m meeting my friend today.", pattern: "Hän on {person}." },
  "movement-location": { word: "kauppa", meaning: "shop", forms: ["kauppa", "kaupassa · at the shop", "kauppaan · to the shop"], example: "Tämä on kauppa.", translation: "This is a shop.", formSentence: "Olen kaupassa.", formTranslation: "I am at the shop.", pattern: "Minä menen {place}." },
  "emotions-feelings": { word: "iloinen", meaning: "happy", forms: ["iloinen · happy", "väsynyt · tired"], example: "Olen iloinen tänään.", translation: "I am happy today.", formSentence: "Olen väsynyt.", formTranslation: "I am tired.", pattern: "Olen {feeling}." },
  "common-verbs": { word: "mennä", meaning: "to go", forms: ["mennä · to go", "menen · I go"], example: "Minä menen kotiin.", translation: "I am going home.", formSentence: "Minä menen kauppaan.", formTranslation: "I am going to the shop.", pattern: "Minä menen {place}." },
  "thinking-understanding": { word: "ymmärtää", meaning: "to understand", forms: ["ymmärtää · to understand", "ymmärrän · I understand"], example: "Ymmärrän sinua.", translation: "I understand you.", formSentence: "Ymmärrän kysymyksen.", formTranslation: "I understand the question.", pattern: "Ymmärrän {idea}." },
  "questions-connectors": { word: "missä", meaning: "where", forms: ["missä · where", "missä on · where is"], example: "Missä on kauppa?", translation: "Where is the shop?", formSentence: "Missä on asema?", formTranslation: "Where is the station?", pattern: "Missä on {place}?" },
  "numbers-comparison": { word: "paljon", meaning: "a lot / many", forms: ["paljon · a lot", "enemmän · more"], example: "Minulla on paljon aikaa.", translation: "I have a lot of time.", formSentence: "Tänään on enemmän aikaa.", formTranslation: "There is more time today.", pattern: "Minulla on {amount}." },
} as const;

export const mockExercises: MockExercise[] = [
  { mode: "Vocabulary in context", helper: "Say the Finnish word.", prompt: "shop", promptLabel: "SAY IT IN FINNISH", speechLanguage: "en-US", answer: "Tämä on kauppa.", explanation: "Kauppa means “shop”." },
  { mode: "Transformation", helper: "Use the Finnish form.", prompt: "I am at the shop.", promptLabel: "SAY IT IN FINNISH", speechLanguage: "en-US", cue: "kaupassa · at the shop", answer: "Olen kaupassa.", explanation: "Kaupassa means “at the shop”." },
  { mode: "Substitution", helper: "Replace the highlighted word.", prompt: "Minä menen kauppaan.", promptLabel: "SENTENCE PATTERN", highlight: "kauppaan", cue: "koulu", answer: "Minä menen kouluun.", explanation: "Koulu becomes kouluun for movement into the school." },
  { mode: "Sentence completion", helper: "Complete the sentence.", prompt: "Asema on ___.", promptLabel: "FINISH THE SENTENCE", answer: "Asema on lähellä.", explanation: "Lähellä means “nearby” or “close”." },
  { mode: "Question & answer", helper: "Answer in Finnish.", prompt: "Missä sinä käyt ostoksilla?", promptLabel: "QUESTION", speechText: "Missä sinä käyt ostoksilla?", speechLanguage: "fi-FI", answer: "Käyn kaupassa.", explanation: "Käyn kaupassa means “I go shopping”." },
  { mode: "Contextual speaking", helper: "Say it naturally.", prompt: "The shop is nearby.", promptLabel: "SAY IT IN FINNISH", speechText: "The shop is nearby.", speechLanguage: "en-US", answer: "Kauppa on lähellä.", explanation: "Kauppa on lähellä means “The shop is nearby”." },
];

export function getMockExercises(topicId: string): MockExercise[] {
  if (topicId === "movement-location") return mockExercises;
  const sample = mockTopicExamples[topicId as keyof typeof mockTopicExamples] ?? mockTopicExamples["movement-location"];
  return [
    { mode: "Vocabulary in context", helper: "Say the Finnish word.", prompt: sample.meaning, promptLabel: "SAY IT IN FINNISH", speechLanguage: "en-US", answer: sample.example, explanation: `${sample.word} means “${sample.meaning}”.` },
    { mode: "Transformation", helper: "Use the Finnish form.", prompt: sample.formTranslation, promptLabel: "SAY IT IN FINNISH", speechLanguage: "en-US", cue: sample.forms[sample.forms.length - 1], answer: sample.formSentence, explanation: `${sample.formSentence} is one natural way to say it.` },
    { mode: "Sentence pattern", helper: "Use the sentence pattern.", prompt: sample.translation, promptLabel: "SAY IT IN FINNISH", speechLanguage: "en-US", answer: sample.example, explanation: `${sample.example} means “${sample.translation}”.` },
  ];
}

export const initialPreviewProgress = {
  activeTopicId: null as string | null,
  sessionPositions: {} as Record<string, number>,
  topicSessions: {} as Record<string, { sessionsCompleted: number; lastStudiedAt: string }>,
};
