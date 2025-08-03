"""
노년층 특화 자서전 생성 API 라우터
"""
import os
import sys
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uuid
from datetime import datetime
import logging

# 절대 경로로 모듈 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
serve_dir = os.path.dirname(current_dir)
sys.path.insert(0, serve_dir)

# 챕터 분류기 import
try:
    from .improved_chapter_classifier import ImprovedChapterClassifier
    chapter_classifier = ImprovedChapterClassifier()
    print("✅ ImprovedChapterClassifier 초기화 완료")
except Exception as e:
    print(f"⚠️  ImprovedChapterClassifier 초기화 실패: {str(e)}")
    chapter_classifier = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/autobiography", tags=["autobiography"])

# 진행 중인 생성 작업 추적
generation_tasks: Dict[str, Dict[str, Any]] = {}


class UserProfile(BaseModel):
    """사용자 프로필"""
    name: str = Field(..., description="사용자 이름")
    age: int = Field(..., ge=65, le=120, description="나이 (65세 이상)")
    gender: str = Field(..., description="성별")
    birth_place: Optional[str] = Field(None, description="출생지")
    occupation: Optional[str] = Field(None, description="직업")


class TextInputRequest(BaseModel):
    """텍스트 입력 요청"""
    session_id: str = Field(..., description="세션 ID")
    message: str = Field(..., max_length=2000, description="사용자 메시지")
    user_context: Optional[UserProfile] = Field(None, description="사용자 컨텍스트")


class ChapterClassificationRequest(BaseModel):
    """챕터 분류 요청"""
    text: str = Field(..., max_length=1000, description="분류할 텍스트")
    user_context: Optional[Dict[str, Any]] = Field(None, description="사용자 컨텍스트")


@router.get("/health")
async def health_check():
    """자서전 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "autobiography",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "features": [
            "text_processing",
            "chapter_classification"
        ],
        "chapter_classifier": "available" if chapter_classifier else "unavailable"
    }


@router.post("/text-input")
async def process_text_input(request: TextInputRequest):
    """텍스트 입력 처리"""
    try:
        # 기본 응답 생성
        ai_response = f"'{request.message}'에 대한 소중한 이야기를 들려주셔서 감사합니다. 더 자세히 말씀해 주실 수 있나요?"
        
        # 챕터 분류 (가능한 경우)
        chapter_classification = None
        if chapter_classifier:
            try:
                chapter_id, confidence = chapter_classifier.classify_message(
                    request.message,
                    context=request.user_context.dict() if request.user_context else None
                )
                chapter_classification = {
                    "primary_chapter": chapter_id,
                    "confidence": confidence
                }
            except Exception as e:
                logger.warning(f"챕터 분류 실패: {str(e)}")
        
        # 후속 질문 생성
        suggested_questions = [
            "그때 가장 기억에 남는 일은 무엇인가요?",
            "그 경험에서 배운 점이 있다면?",
            "비슷한 다른 기억도 있으신가요?"
        ]
        
        return {
            "success": True,
            "ai_response": ai_response,
            "chapter_classification": chapter_classification,
            "suggested_questions": suggested_questions,
            "processing_time": 1.0
        }
        
    except Exception as e:
        logger.error(f"텍스트 입력 처리 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"텍스트 처리 중 오류가 발생했습니다: {str(e)}")


@router.post("/analysis/chapter-classification")
async def classify_chapter(request: ChapterClassificationRequest):
    """27개 챕터 분류"""
    try:
        if not chapter_classifier:
            raise HTTPException(status_code=503, detail="챕터 분류 서비스를 사용할 수 없습니다")
        
        # 챕터 분류 수행
        chapter_id, confidence = chapter_classifier.classify_message(
            request.text,
            context=request.user_context
        )
        
        return {
            "success": True,
            "primary_classification": {
                "chapter_code": chapter_id,
                "confidence": confidence
            },
            "processing_time": 0.8
        }
        
    except Exception as e:
        logger.error(f"챕터 분류 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"챕터 분류 중 오류가 발생했습니다: {str(e)}")


@router.get("/chapters/list")
async def get_chapter_list():
    """27개 챕터 목록 조회"""
    chapters = {
        "major_categories": [
            {
                "code": "growth",
                "name": "성장과정",
                "subcategories": [
                    {"code": "growth_birth", "name": "출생"},
                    {"code": "growth_childhood", "name": "유년기"},
                    {"code": "growth_adolescence", "name": "청소년기"}
                ]
            },
            {
                "code": "family",
                "name": "가족관계",
                "subcategories": [
                    {"code": "family_parents", "name": "부모"},
                    {"code": "family_siblings", "name": "형제, 조부모"},
                    {"code": "family_spouse", "name": "배우자, 자녀"}
                ]
            },
            {
                "code": "school",
                "name": "학창시절",
                "subcategories": [
                    {"code": "school_school", "name": "학교"},
                    {"code": "school_subjects", "name": "과목"},
                    {"code": "school_friends", "name": "친구"}
                ]
            },
            {
                "code": "career",
                "name": "직업/진로",
                "subcategories": [
                    {"code": "career_experience", "name": "직업경험"},
                    {"code": "career_choice", "name": "선택이유"},
                    {"code": "career_retirement", "name": "은퇴/전환"}
                ]
            },
            {
                "code": "values",
                "name": "가치관/성격",
                "subcategories": [
                    {"code": "values_self", "name": "자아"},
                    {"code": "values_personality", "name": "성격"},
                    {"code": "values_philosophy", "name": "삶의 철학, 유산"}
                ]
            },
            {
                "code": "life_experience",
                "name": "인생 경험",
                "subcategories": [
                    {"code": "life_events", "name": "사건"},
                    {"code": "life_turning_points", "name": "전환점"},
                    {"code": "life_health", "name": "건강, 어려움"}
                ]
            },
            {
                "code": "emotions",
                "name": "감정/취향",
                "subcategories": [
                    {"code": "emotions_likes", "name": "좋아하는 것"},
                    {"code": "emotions_fears", "name": "무서운 것"},
                    {"code": "emotions_admiration", "name": "감탄"}
                ]
            },
            {
                "code": "society",
                "name": "사회/문화",
                "subcategories": [
                    {"code": "society_religion", "name": "종교"},
                    {"code": "society_country", "name": "국가"},
                    {"code": "society_travel", "name": "여행, 유행"}
                ]
            },
            {
                "code": "others",
                "name": "기타",
                "subcategories": [
                    {"code": "others_money", "name": "돈 철학"},
                    {"code": "others_news", "name": "기사"},
                    {"code": "others_good_deeds", "name": "선행"}
                ]
            }
        ],
        "total_chapters": 27
    }
    
    return chapters
