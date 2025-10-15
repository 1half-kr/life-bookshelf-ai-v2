from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


# ===== Shared DTOs =====
class MaterialDto(BaseModel):
    material_num: int
    material_name: str
    w: List[int] = Field(default=[0, 0, 0, 0, 0, 0])
    ex: int = 0
    con: int = 0
    material_count: int = 0
    utter_freq: int = 0


class ChunkDto(BaseModel):
    chunk_num: int
    chunk_name: str
    materials: Dict[str, MaterialDto] = Field(default_factory=dict)


class CategoryDto(BaseModel):
    category_num: int
    category_name: str
    chunks: Dict[str, ChunkDto] = Field(default_factory=dict)
    chunk_weight: Dict[str, int] = Field(default_factory=dict)


class EngineStateDto(BaseModel):
    last_material_id: List[int] = Field(default_factory=list)
    last_material_streak: int = 0
    epsilon: float = 0.10


class MetricsDto(BaseModel):
    sessionId: str
    theme: str
    categories: Dict[str, CategoryDto]
    engine_state: EngineStateDto = Field(default_factory=EngineStateDto)
    asked_total: int = 0
    policyVersion: str = "v1.2.0"


# ===== Session Start DTOs =====
class SessionStartRequestDto(BaseModel):
    sessionId: str
    theme: str
    categories: Dict[str, CategoryDto]
    metrics: MetricsDto
    
    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "test-session-001",
                "theme": "나의 대학 시절",
                "metrics": {
                    "sessionId": "test-session-001",
                    "theme": "나의 대학 시절",
                    "categories": {
                        "cat_1": {
                            "category_num": 1,
                            "category_name": "학업",
                            "chunks": {
                                "chunk_1_1": {
                                    "chunk_num": 1,
                                    "chunk_name": "전공 공부",
                                    "materials": {
                                        "mat_1_1_1": {
                                            "material_num": 1,
                                            "material_name": "좋아했던 과목",
                                            "w": [0, 0, 0, 0, 0, 0],
                                            "ex": 0,
                                            "con": 0,
                                            "material_count": 0,
                                            "utter_freq": 0
                                        }
                                    }
                                }
                            },
                            "chunk_weight": {"chunk_1_1": 2}
                        }
                    },
                    "engine_state": {
                        "last_material_id": [],
                        "last_material_streak": 0,
                        "epsilon": 0.1
                    },
                    "asked_total": 0,
                    "policyVersion": "v1.2.0"
                },
                "categories": {
                    "cat_1": {
                        "category_num": 1,
                        "category_name": "학업",
                        "chunks": {
                            "chunk_1_1": {
                                "chunk_num": 1,
                                "chunk_name": "전공 공부",
                                "materials": {
                                    "mat_1_1_1": {
                                        "material_num": 1,
                                        "material_name": "좋아했던 과목",
                                        "w": [0, 0, 0, 0, 0, 0],
                                        "ex": 0,
                                        "con": 0,
                                        "material_count": 0,
                                        "utter_freq": 0
                                    }
                                }
                            }
                        },
                        "chunk_weight": {"chunk_1_1": 2}
                    }
                }
            }
        }


class SessionStartResponseDto(BaseModel):
    sessionId: str
    first_question: Optional[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "test-session-001",
                "first_question": {
                    "id": "q-fcf8ea8c",
                    "material": "좋아했던 과목",
                    "type": "how",
                    "text": "좋아했던 과목에 대해 방법/과정을 더 자세히 들려주실 수 있을까요?"
                }
            }
        }


# ===== Turn DTOs =====
class QuestionDto(BaseModel):
    id: str
    material: str
    type: str


class QuestionPoolItemDto(BaseModel):
    id: str
    material: str
    keywords: List[Optional[str]]
    type: str
    text: str
    source: str
    status: str


class InterviewChatV2RequestDto(BaseModel):
    sessionId: str
    question: QuestionDto
    answer_text: str
    metrics: Optional[Dict[str, Any]] = None
    question_pool: List[QuestionPoolItemDto] = Field(default_factory=list)
    use_llm_keywords: bool = False


class NextQuestionDto(BaseModel):
    id: str
    material: str
    type: str
    text: str


class InterviewChatV2ResponseDto(BaseModel):
    next_question: Optional[Dict[str, Any]]


# ===== Session End DTOs =====
class SessionEndRequestDto(BaseModel):
    sessionId: str


class SessionEndResponseDto(BaseModel):
    sessionId: str
    final_metrics: Optional[MetricsDto]
    pool_to_save: List[QuestionPoolItemDto]
