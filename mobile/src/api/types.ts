export type VocabularyTopic = {
  slug: string;
  name_en: string;
  name_fi: string;
  sort_order: number;
  word_count: number;
};

export type VocabularyExample = {
  id: string;
  finnish_sentence: string;
  written_finnish_sentence: string;
  english_translation: string;
  difficulty: string;
  role: string;
  validation_status: string;
  target_validation_status: string;
};

export type VocabularyForm = {
  id: string;
  form: string;
  grammatical_label: string;
  target_type: string;
  display_order: number;
  notes: string | null;
  examples: VocabularyExample[];
};

export type VocabularyItem = {
  id: string;
  word: string;
  meaning: string | null;
  language_code: string;
  meaning_language_code: string;
  topic_order: number;
  cefr_level: string | null;
  context: string | null;
  register: string | null;
  forms: VocabularyForm[];
};

export type VocabularyTopicContents = {
  topic: {
    id: string;
    slug: string;
    name_en: string;
    name_fi: string;
    sort_order: number;
  };
  vocabulary: VocabularyItem[];
};
