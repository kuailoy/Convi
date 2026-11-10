const DISPLAY_LABELS: Record<string, string> = {
  n: "Nominative",
  "n sg": "Nominative · singular",
  "g sg": "Genitive · singular",
  "p sg": "Partitive · singular",
  "n pl": "Nominative · plural",
  "g pl": "Genitive · plural",
  "p pl": "Partitive · plural",
  "elative pl": "Elative · plural",
  "inessive pl": "Inessive · plural",
  "accusative object": "Object form",
  object: "Object form",
  "accusative; 1st-person reflexive with possessive suffix": "Accusative · 1st-person reflexive",
  "partitive; 1st-person reflexive with possessive suffix": "Partitive · 1st-person reflexive",
  invariant: "Invariant form",
  "adverb, invariable": "Invariable adverb",
  case_or_usage_pattern: "Usage pattern",
  i: "1st person · singular",
  "you sg": "2nd person · singular",
  "he/she": "3rd person · singular",
  we: "1st person · plural",
  "you pl": "2nd person · plural",
  they: "3rd person · plural",
};

export function formatGrammaticalLabel(label: string) {
  const normalized = label.trim().toLowerCase();
  if (DISPLAY_LABELS[normalized]) return DISPLAY_LABELS[normalized];
  return normalized
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}
