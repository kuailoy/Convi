// UI preview data only. It is deliberately separate from API responses and database models.
export type MockExercise = {
  prompt: string;
  promptLabel: string;
  speechLanguage: string;
  highlight: string;
  caseLabel: string;
  translation: string;
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

const defaultVocabularyExercises: MockExercise[] = [
  { prompt: "Tämä on kauppa.", promptLabel: "SAY THE SENTENCE", speechLanguage: "fi-FI", highlight: "kauppa", caseLabel: "Nominative", translation: "This is a shop." },
  { prompt: "Olen kaupassa.", promptLabel: "SAY THE SENTENCE", speechLanguage: "fi-FI", highlight: "kaupassa", caseLabel: "Inessive", translation: "I am at the shop." },
  { prompt: "Menen kauppaan.", promptLabel: "SAY THE SENTENCE", speechLanguage: "fi-FI", highlight: "kauppaan", caseLabel: "Illative", translation: "I am going to the shop." },
];

const topicVocabularyExercises: Record<string, MockExercise[]> = {
  "time-dates-periods": [
    { prompt: "Aika kuluu nopeasti.", promptLabel: "SAY THE SENTENCE", speechLanguage: "fi-FI", highlight: "Aika", caseLabel: "Nominative", translation: "Time passes quickly." },
    { prompt: "Minulla on aikaa.", promptLabel: "SAY THE SENTENCE", speechLanguage: "fi-FI", highlight: "aikaa", caseLabel: "Partitive", translation: "I have time." },
    { prompt: "Puhun ajasta.", promptLabel: "SAY THE SENTENCE", speechLanguage: "fi-FI", highlight: "ajasta", caseLabel: "Elative", translation: "I am talking about time." },
  ],
  "people-family": [
    { prompt: "Ystävä tulee tänään.", promptLabel: "SAY THE SENTENCE", speechLanguage: "fi-FI", highlight: "Ystävä", caseLabel: "Nominative", translation: "A friend is coming today." },
    { prompt: "Tapaan ystävän.", promptLabel: "SAY THE SENTENCE", speechLanguage: "fi-FI", highlight: "ystävän", caseLabel: "Genitive", translation: "I am meeting a friend." },
    { prompt: "Puhun ystävästä.", promptLabel: "SAY THE SENTENCE", speechLanguage: "fi-FI", highlight: "ystävästä", caseLabel: "Elative", translation: "I am talking about a friend." },
  ],
};

export function getMockExercises(topicId: string): MockExercise[] {
  return topicVocabularyExercises[topicId] ?? defaultVocabularyExercises;
}

export function needsMockPreparation(topicId: string) {
  return !Object.prototype.hasOwnProperty.call(topicVocabularyExercises, topicId);
}

export const initialPreviewProgress = {
  activeTopicId: null as string | null,
  sessionPositions: {} as Record<string, number>,
  topicSessions: {} as Record<string, { sessionsCompleted: number; lastStudiedAt: string }>,
};
