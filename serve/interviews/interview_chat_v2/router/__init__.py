from fastapi import APIRouter, HTTPException, Depends
from promptflow.core import Flow
from starlette.requests import Request
from pydantic_core import ValidationError

from auth import AuthRequired, get_current_user
from interviews.interview_chat_v2.dto import (
    SessionStartRequestDto,
    SessionStartResponseDto,
    InterviewChatV2RequestDto,
    InterviewChatV2ResponseDto,
    SessionEndRequestDto,
    SessionEndResponseDto,
    MetricsDto,
    EngineStateDto,
)
from logs import get_logger

logger = get_logger()

router = APIRouter()


@router.post(
    "/api/v2/interviews/session/start",
    dependencies=[Depends(AuthRequired())],
    response_model=SessionStartResponseDto,
    summary="인터뷰 세션 시작 v2",
    description="세션을 시작하고 첫 질문을 생성합니다.",
    tags=["인터뷰 (Interview)"],
)
async def start_interview_session(
    request: Request, requestDto: SessionStartRequestDto
):
    current_user = get_current_user(request)

    try:
        # categories를 materials 형식으로 변환
        metrics_dict = requestDto.metrics.model_dump()
        materials = {}
        for cat_key, cat in metrics_dict.get("categories", {}).items():
            for chunk_key, chunk in cat.get("chunks", {}).items():
                for mat_key, mat in chunk.get("materials", {}).items():
                    materials[mat["material_name"]] = {
                        "category_name": cat["category_name"],
                        "chunk_name": chunk["chunk_name"],
                        "w1": mat["w"][0], "w2": mat["w"][1], "w3": mat["w"][2],
                        "w4": mat["w"][3], "w5": mat["w"][4], "w6": mat["w"][5],
                        "ex": mat["ex"], "con": mat["con"],
                        "utter_freq": mat["utter_freq"],
                        "material_count": mat["material_count"],
                        "themes": []
                    }
        
        flow_metrics = {
            "theme": metrics_dict.get("theme", ""),
            "materials": materials,
            "chunks": {},
            "global": {}
        }
        
        flow = Flow.load("../flows/interviews/chat/interview_chat_v2/flow.dag.yaml")

        result = flow(
            sessionId=requestDto.sessionId,
            question={"id": "init", "material": "", "type": "init"},
            answer_text="",
            metrics=flow_metrics,
            question_pool=[],
            use_llm_keywords=True,
        )
        
        return SessionStartResponseDto(
            sessionId=requestDto.sessionId,
            first_question=result.get("next_question"),
        )

    except ValidationError as e:
        logger.error(f"Validation error occurred: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post(
    "/api/v2/interviews/interview-chat",
    dependencies=[Depends(AuthRequired())],
    response_model=InterviewChatV2ResponseDto,
    summary="인터뷰 대화 생성 v2",
    description="메트릭 기반으로 다음 질문을 생성합니다.",
    tags=["인터뷰 (Interview)"],
)
async def generate_interview_chat_v2(
    request: Request, requestDto: InterviewChatV2RequestDto
):
    current_user = get_current_user(request)

    try:
        flow = Flow.load("../flows/interviews/chat/interview_chat_v2/flow.dag.yaml")

        # metrics는 서버 메모리/DB에서 로드해야 함 (임시로 빈 메트릭 사용)
        # TODO: 실제 구현 시 DB에서 sessionId로 metrics 조회
        metrics = {
            "sessionId": requestDto.sessionId,
            "theme": "",
            "categories": {},
            "engine_state": {"last_material_id": [], "last_material_streak": 0, "epsilon": 0.1},
            "asked_total": 0,
            "policyVersion": "v1.2.0"
        }

        result = flow(
            sessionId=requestDto.sessionId,
            question=requestDto.question.model_dump(),
            answer_text=requestDto.answer_text,
            metrics=requestDto.metrics if requestDto.metrics else {},
            question_pool=[q.model_dump() for q in requestDto.question_pool] if requestDto.question_pool else [],
            use_llm_keywords=requestDto.use_llm_keywords,
        )
        
        return InterviewChatV2ResponseDto(
            next_question=result.get("next_question"),
        )

    except ValidationError as e:
        logger.error(f"Validation error occurred: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post(
    "/api/v2/interviews/session/end",
    dependencies=[Depends(AuthRequired())],
    response_model=SessionEndResponseDto,
    summary="인터뷰 세션 종료 v2",
    description="세션을 종료하고 최종 메트릭을 반환합니다.",
    tags=["인터뷰 (Interview)"],
)
async def end_interview_session(
    request: Request, requestDto: SessionEndRequestDto
):
    current_user = get_current_user(request)

    try:
        # TODO: 실제 구현 시 세션별로 저장된 metrics와 pool을 조회
        # 임시로 빈 데이터 반환
        final_metrics = MetricsDto(
            sessionId=requestDto.sessionId,
            theme="",
            categories={},
            engine_state=EngineStateDto(),
            asked_total=0,
            policyVersion="v1.2.0"
        )
        
        return SessionEndResponseDto(
            sessionId=requestDto.sessionId,
            final_metrics=final_metrics,
            pool_to_save=[]
        )

    except ValidationError as e:
        logger.error(f"Validation error occurred: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
