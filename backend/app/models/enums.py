from enum import StrEnum


class ContentType(StrEnum):
    SENTENCE_PATTERN = "sentence_pattern"
    EXPRESSION = "expression"
    VOCABULARY_ITEM = "vocabulary_item"
    SCENARIO = "scenario"


class PracticeMode(StrEnum):
    STRUCTURED_DRILL = "structured_drill"
    VOCABULARY_PHRASE_PRACTICE = "vocabulary_phrase_practice"
    GUIDED_CONVERSATION = "guided_conversation"


class PracticeMethod(StrEnum):
    SUBSTITUTION = "substitution"
    TRANSFORMATION = "transformation"
    EXPANSION = "expansion"
    ACTIVE_RECALL = "active_recall"
    COLLOCATION_PRACTICE = "collocation_practice"
    CONTEXTUAL_USE = "contextual_use"
    ROLE_PLAY = "role_play"
    GUIDED_QA = "guided_qa"


class CefrLevel(StrEnum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class ContentStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ExerciseSetStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ProgressStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PRACTICED = "practiced"


class Register(StrEnum):
    FORMAL = "formal"
    NEUTRAL = "neutral"
    INFORMAL = "informal"
