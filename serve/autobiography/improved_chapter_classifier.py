"""
개선된 챕터 분류기 - 더 정확한 키워드 매칭과 문맥 분석
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re
from collections import Counter

@dataclass
class ImprovedChapter:
    """개선된 챕터 정보"""
    major_category: str
    minor_category: str
    chapter_id: str
    primary_keywords: List[str]      # 핵심 키워드 (가중치 3)
    secondary_keywords: List[str]    # 보조 키워드 (가중치 2)
    context_keywords: List[str]      # 문맥 키워드 (가중치 1)
    negative_keywords: List[str]     # 제외 키워드 (가중치 -2)
    questions: List[str]

class ImprovedChapterClassifier:
    """개선된 27개 챕터 분류기"""
    
    def __init__(self):
        self.chapters = self._initialize_improved_chapters()
        self.chapter_map = {chapter.chapter_id: chapter for chapter in self.chapters}
        
        # 시대별 키워드 매핑
        self.historical_periods = {
            "일제강점기": ["일제강점기", "일본", "조선", "해방", "광복", "독립"],
            "한국전쟁": ["전쟁", "6.25", "피난", "부산", "인민군", "유엔군", "중공군"],
            "산업화": ["새마을", "경제개발", "공장", "도시화", "이농"],
            "민주화": ["민주화", "학생운동", "시위", "독재", "민주주의"]
        }
    
    def _initialize_improved_chapters(self) -> List[ImprovedChapter]:
        """개선된 27개 챕터 초기화"""
        return [
            # 1. 성장과정
            ImprovedChapter(
                major_category="성장과정",
                minor_category="출생",
                chapter_id="growth_birth",
                primary_keywords=["태어나", "출생", "태생", "분만"],
                secondary_keywords=["산부인과", "첫울음", "신생아", "출산"],
                context_keywords=["어머니 뱃속", "임신", "배", "낳"],
                negative_keywords=[],
                questions=[
                    "어디서 태어나셨나요?",
                    "태어날 때 특별한 일이 있었나요?",
                    "출생에 관한 가족들의 이야기가 있다면 들려주세요."
                ]
            ),
            
            ImprovedChapter(
                major_category="성장과정",
                minor_category="유년기",
                chapter_id="growth_childhood",
                primary_keywords=["어린시절", "유년기", "어렸을 때", "꼬마시절"],
                secondary_keywords=["아기", "기저귀", "젖병", "첫걸음", "말문", "동네", "골목"],
                context_keywords=["놀이", "장난감", "친구들과"],
                negative_keywords=["학교", "공부", "시험", "교회", "절"],
                questions=[
                    "어린 시절 가장 기억에 남는 일은 무엇인가요?",
                    "어떤 아이였나요?",
                    "유년기에 좋아했던 놀이나 장난감이 있었나요?"
                ]
            ),
            
            ImprovedChapter(
                major_category="성장과정",
                minor_category="청소년기",
                chapter_id="growth_adolescence",
                primary_keywords=["중학교", "고등학교", "사춘기", "10대", "청소년"],
                secondary_keywords=["반항", "꿈", "진로고민", "사춘기"],
                context_keywords=["친구", "선생님", "공부"],
                negative_keywords=["대학교", "직장"],
                questions=[
                    "청소년 시절은 어떠셨나요?",
                    "그때 꿈이나 목표가 있었나요?",
                    "사춘기 때 특별한 경험이 있으셨나요?"
                ]
            ),
            
            # 8. 사회/문화 - 국가 (전쟁 관련 강화)
            ImprovedChapter(
                major_category="사회/문화",
                minor_category="국가",
                chapter_id="society_country",
                primary_keywords=["전쟁", "6.25", "한국전쟁", "일제강점기", "해방"],
                secondary_keywords=["피난", "부산", "인민군", "유엔군", "폭격", "방공호"],
                context_keywords=["나라", "국가", "조선", "정치", "대통령", "정부"],
                negative_keywords=["종교", "신앙", "교회", "절"],
                questions=[
                    "전쟁이나 역사적 사건을 직접 경험하셨나요?",
                    "그때 가장 기억에 남는 일은 무엇인가요?",
                    "나라의 변화를 어떻게 느끼셨나요?"
                ]
            ),
            
            ImprovedChapter(
                major_category="사회/문화",
                minor_category="종교",
                chapter_id="society_religion",
                primary_keywords=["종교", "신앙", "교회", "절", "기도"],
                secondary_keywords=["믿음", "신", "부처", "예수", "하나님"],
                context_keywords=["성경", "불경", "예배", "법회", "미사"],
                negative_keywords=["전쟁", "정치", "나라"],
                questions=[
                    "종교나 신앙이 있으신가요?",
                    "신앙이 인생에 어떤 도움이 되었나요?",
                    "종교적 경험이나 깨달음이 있으셨나요?"
                ]
            ),
            
            # 나머지 챕터들도 동일한 방식으로 개선...
            # (간단히 몇 개만 더 예시)
            
            ImprovedChapter(
                major_category="가족관계",
                minor_category="부모",
                chapter_id="family_parents",
                primary_keywords=["아버지", "어머니", "아빠", "엄마", "부모님"],
                secondary_keywords=["아버님", "어머님", "아버지께서", "어머니께서"],
                context_keywords=["가족", "집", "가정", "효도"],
                negative_keywords=["친구", "동료", "선생님"],
                questions=[
                    "부모님은 어떤 분이셨나요?",
                    "부모님께 가장 감사한 점은 무엇인가요?",
                    "부모님과의 특별한 추억이 있다면 들려주세요."
                ]
            ),
            
            ImprovedChapter(
                major_category="직업/진로",
                minor_category="직업경험",
                chapter_id="career_experience",
                primary_keywords=["직장", "회사", "일", "업무", "직업"],
                secondary_keywords=["근무", "출근", "퇴근", "동료", "상사"],
                context_keywords=["월급", "승진", "부서", "프로젝트"],
                negative_keywords=["학교", "공부", "시험"],
                questions=[
                    "어떤 일을 하셨나요?",
                    "직장에서의 기억에 남는 경험이 있으신가요?",
                    "일하면서 가장 보람을 느꼈던 순간은 언제인가요?"
                ]
            )
        ]
    
    def classify_message(self, message: str, context: Dict[str, Any] = None) -> Tuple[str, float]:
        """
        개선된 메시지 분류 알고리즘
        
        Args:
            message: 사용자 메시지
            context: 대화 컨텍스트
            
        Returns:
            (chapter_id, confidence_score) 튜플
        """
        message_lower = message.lower()
        scores = {}
        
        # 1. 시대적 맥락 분석
        historical_context = self._analyze_historical_context(message_lower)
        
        for chapter in self.chapters:
            score = 0
            
            # 키워드 가중치 매칭 (정확한 단어 매칭)
            # 핵심 키워드 (가중치 3)
            for keyword in chapter.primary_keywords:
                if self._exact_word_match(keyword, message_lower):
                    score += 3
            
            # 보조 키워드 (가중치 2)
            for keyword in chapter.secondary_keywords:
                if self._exact_word_match(keyword, message_lower):
                    score += 2
            
            # 문맥 키워드 (가중치 1)
            for keyword in chapter.context_keywords:
                if self._exact_word_match(keyword, message_lower):
                    score += 1
            
            # 제외 키워드 (가중치 -2)
            for keyword in chapter.negative_keywords:
                if self._exact_word_match(keyword, message_lower):
                    score -= 2
            
            # 3. 시대적 맥락 보너스
            if historical_context and chapter.chapter_id == "society_country":
                score += 5  # 전쟁/역사 관련은 국가 챕터로 강하게 유도
            
            # 4. 문장 길이 정규화
            if score > 0:
                word_count = len(message_lower.split())
                score = (score / word_count) * 10  # 정규화
            
            scores[chapter.chapter_id] = max(0, score)  # 음수 방지
        
        # 5. 최고 점수 챕터 반환
        if scores and max(scores.values()) > 0:
            best_chapter = max(scores.items(), key=lambda x: x[1])
            confidence = min(best_chapter[1] / 10, 1.0)  # 0-1 범위로 정규화
            return best_chapter[0], confidence
        
        # 6. 분류 실패 시 기본 챕터 (가장 일반적인 주제)
        return "growth_childhood", 0.1
    
    def _exact_word_match(self, keyword: str, text: str) -> bool:
        """정확한 단어 매칭 (부분 문자열 방지)"""
        import re
        # 단어 경계를 고려한 정확한 매칭
        pattern = r'\b' + re.escape(keyword) + r'\b'
        return bool(re.search(pattern, text))
    
    def _analyze_historical_context(self, message: str) -> Optional[str]:
        """시대적 맥락 분석"""
        for period, keywords in self.historical_periods.items():
            for keyword in keywords:
                if keyword in message:
                    return period
        return None
    
    def get_classification_explanation(self, message: str) -> Dict[str, Any]:
        """분류 결과에 대한 설명 제공"""
        chapter_id, confidence = self.classify_message(message)
        chapter = self.get_chapter_info(chapter_id)
        
        # 매칭된 키워드 찾기
        matched_keywords = []
        message_lower = message.lower()
        
        if chapter:
            for keyword in chapter.primary_keywords + chapter.secondary_keywords:
                if keyword in message_lower:
                    matched_keywords.append(keyword)
        
        return {
            "classified_chapter": chapter_id,
            "confidence": confidence,
            "matched_keywords": matched_keywords,
            "historical_context": self._analyze_historical_context(message_lower),
            "explanation": f"'{', '.join(matched_keywords)}' 키워드를 기반으로 분류되었습니다."
        }
    
    def get_chapter_info(self, chapter_id: str) -> Optional[ImprovedChapter]:
        """챕터 ID로 챕터 정보 조회"""
        return self.chapter_map.get(chapter_id)
    
    def suggest_better_chapter(self, message: str, current_chapter_id: str) -> List[Tuple[str, float]]:
        """더 적합한 챕터 제안"""
        all_scores = {}
        message_lower = message.lower()
        
        for chapter in self.chapters:
            if chapter.chapter_id == current_chapter_id:
                continue
                
            score = 0
            for keyword in chapter.primary_keywords:
                if keyword in message_lower:
                    score += 3
            for keyword in chapter.secondary_keywords:
                if keyword in message_lower:
                    score += 2
                    
            if score > 0:
                all_scores[chapter.chapter_id] = score
        
        # 상위 3개 제안
        sorted_suggestions = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        return [(chapter_id, score/10) for chapter_id, score in sorted_suggestions]

    def get_all_chapters(self) -> List[Dict[str, Any]]:
        """모든 챕터 정보를 딕셔너리 형태로 반환"""
        return [
            {
                "chapter_id": chapter.chapter_id,
                "major_category": chapter.major_category,
                "minor_category": chapter.minor_category,
                "keywords": chapter.primary_keywords + chapter.secondary_keywords
            }
            for chapter in self.chapters
        ]
    
    def get_chapters_by_major_category(self, major_category: str) -> List[ImprovedChapter]:
        """대분류별 챕터 목록 반환"""
        return [
            chapter for chapter in self.chapters 
            if chapter.major_category == major_category
        ]
    
    def get_follow_up_questions(self, chapter_id: str) -> List[str]:
        """챕터에 맞는 후속 질문 반환"""
        chapter = self.get_chapter_info(chapter_id)
        return chapter.questions if chapter else []
    
    def suggest_next_chapter(self, completed_chapters: List[str]) -> Optional[str]:
        """완료된 챕터를 바탕으로 다음 챕터 제안"""
        remaining_chapters = [
            chapter.chapter_id for chapter in self.chapters
            if chapter.chapter_id not in completed_chapters
        ]
        
        if remaining_chapters:
            # 간단한 우선순위: 성장과정 → 가족관계 → 학창시절 순
            priority_order = [
                "growth_birth", "growth_childhood", "growth_adolescence",
                "family_parents", "family_siblings_grandparents", "family_spouse_children",
                "school_institution", "school_subjects", "school_friends"
            ]
            
            for chapter_id in priority_order:
                if chapter_id in remaining_chapters:
                    return chapter_id
            
            # 우선순위에 없는 챕터 중 첫 번째 반환
            return remaining_chapters[0]
        
        return None

# 전역 인스턴스
_improved_classifier = None

def get_improved_chapter_classifier() -> ImprovedChapterClassifier:
    """개선된 전역 챕터 분류기 반환"""
    global _improved_classifier
    if _improved_classifier is None:
        _improved_classifier = ImprovedChapterClassifier()
    return _improved_classifier
