"""
Common data models for the pipeline system
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """Message type enumeration"""
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"


class ChapterCategory(Enum):
    """Chapter categories"""
    GROWTH = "growth"
    FAMILY = "family"
    SCHOOL = "school"
    CAREER = "career"
    VALUES = "values"
    LIFE_EXPERIENCE = "life_experience"
    EMOTIONS = "emotions"
    SOCIETY = "society"
    OTHERS = "others"


@dataclass
class UserProfile:
    """User profile data model"""
    name: str
    age: int
    gender: str
    birth_place: Optional[str] = None
    occupation: Optional[str] = None
    
    @property
    def birth_decade(self) -> str:
        """Calculate birth decade"""
        current_year = datetime.now().year
        birth_year = current_year - self.age
        decade = (birth_year // 10) * 10
        return f"{decade}s"
    
    @property
    def generation(self) -> str:
        """Determine generation"""
        decade = self.birth_decade
        generation_map = {
            "1920s": "일제강점기 세대",
            "1930s": "일제강점기 세대", 
            "1940s": "해방 세대",
            "1950s": "전쟁 세대",
            "1960s": "산업화 세대"
        }
        return generation_map.get(decade, "현대 세대")


@dataclass
class Message:
    """Message data model"""
    id: str
    content: str
    message_type: MessageType = MessageType.TEXT
    sender: str = "user"  # "user" or "ai"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def word_count(self) -> int:
        """Get word count of the message"""
        return len(self.content.split())
    
    @property
    def is_from_user(self) -> bool:
        """Check if message is from user"""
        return self.sender == "user"


@dataclass
class ConversationSession:
    """Conversation session data model"""
    session_id: str
    user_profile: UserProfile
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    context: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: Message) -> None:
        """Add a message to the session"""
        self.messages.append(message)
        self.last_activity = datetime.utcnow()
    
    @property
    def message_count(self) -> int:
        """Get total message count"""
        return len(self.messages)
    
    @property
    def user_messages(self) -> List[Message]:
        """Get user messages only"""
        return [msg for msg in self.messages if msg.is_from_user]
    
    @property
    def conversation_duration(self) -> float:
        """Get conversation duration in minutes"""
        time_diff = self.last_activity - self.created_at
        return time_diff.total_seconds() / 60


@dataclass
class ChapterClassification:
    """Chapter classification result"""
    chapter_id: str
    confidence: float
    reasoning: Optional[str] = None
    keywords_matched: List[str] = field(default_factory=list)
    alternative_chapters: List[str] = field(default_factory=list)
    
    @property
    def category(self) -> str:
        """Get chapter category"""
        return self.chapter_id.split("_")[0]
    
    @property
    def subcategory(self) -> str:
        """Get chapter subcategory"""
        return self.chapter_id.split("_")[1]
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if confidence is high"""
        return self.confidence >= 0.8


@dataclass
class EmotionAnalysis:
    """Emotion analysis result"""
    primary_emotion: str
    secondary_emotions: List[str] = field(default_factory=list)
    intensity: float = 0.0
    confidence: float = 0.0
    emotional_keywords: List[str] = field(default_factory=list)


@dataclass
class MemoryImportance:
    """Memory importance scoring"""
    importance_score: float
    memory_type: str
    life_stage: str
    autobiographical_relevance: str
    reasoning: Optional[str] = None
    
    @property
    def is_significant(self) -> bool:
        """Check if memory is significant"""
        return self.importance_score >= 0.7


@dataclass
class AnalysisResult:
    """Combined analysis result"""
    message_id: str
    chapter_classification: ChapterClassification
    emotion_analysis: EmotionAnalysis
    memory_importance: MemoryImportance
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AutobiographyChapter:
    """Autobiography chapter data"""
    chapter_id: str
    title: str
    content: str
    source_messages: List[str] = field(default_factory=list)
    word_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Calculate word count after initialization"""
        self.word_count = len(self.content.split()) if self.content else 0


@dataclass
class Autobiography:
    """Complete autobiography data"""
    id: str
    user_profile: UserProfile
    title: str
    chapters: Dict[str, AutobiographyChapter] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "draft"  # draft, in_progress, completed
    
    @property
    def total_word_count(self) -> int:
        """Get total word count"""
        return sum(chapter.word_count for chapter in self.chapters.values())
    
    @property
    def chapter_count(self) -> int:
        """Get chapter count"""
        return len(self.chapters)
    
    @property
    def completion_percentage(self) -> float:
        """Get completion percentage"""
        return (self.chapter_count / 27) * 100


@dataclass
class PipelineEvent:
    """Event data for pipeline communication"""
    event_id: str
    event_type: str
    pipeline_id: str
    step_name: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    destination: str = ""
