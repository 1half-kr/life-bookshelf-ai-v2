"""
AWS Bedrock 전용 클라이언트
Claude 3 모델만 사용하는 깔끔한 구현
"""

import boto3
import json
import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

# 환경 변수 로드 확인
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env.development")


class BedrockConfig(BaseModel):
    """Bedrock 설정"""
    model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    region_name: str = "ap-northeast-2"
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 0.9


class BedrockClient:
    """AWS Bedrock Claude 3 전용 클라이언트"""
    
    def __init__(self, config: BedrockConfig = None):
        self.config = config or BedrockConfig()
        
        # 환경 변수 다시 로드 (확실히 하기 위해)
        load_dotenv(dotenv_path=".env.development")
        
        # AWS 자격 증명 확인 (여러 방법으로)
        aws_access_key = (
            os.getenv("AWS_ACCESS_KEY_ID") or 
            os.environ.get("AWS_ACCESS_KEY_ID")
        )
        aws_secret_key = (
            os.getenv("AWS_SECRET_ACCESS_KEY") or 
            os.environ.get("AWS_SECRET_ACCESS_KEY")
        )
        
        print(f"🔍 AWS 자격 증명 확인:")
        print(f"   AWS_ACCESS_KEY_ID: {'설정됨' if aws_access_key else '없음'}")
        print(f"   AWS_SECRET_ACCESS_KEY: {'설정됨' if aws_secret_key else '없음'}")
        
        if not aws_access_key or not aws_secret_key:
            print("⚠️  AWS 자격 증명이 설정되지 않았습니다.")
            print("   .env.development 파일을 확인하거나 환경 변수를 설정하세요.")
            self.client = None
            self.credentials_available = False
        else:
            try:
                # Bedrock 클라이언트 초기화
                self.client = boto3.client(
                    'bedrock-runtime',
                    region_name=self.config.region_name,
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key
                )
                self.credentials_available = True
                print(f"✅ AWS Bedrock 클라이언트 초기화 완료 (리전: {self.config.region_name})")
            except Exception as e:
                print(f"❌ AWS Bedrock 클라이언트 초기화 실패: {str(e)}")
                self.client = None
                self.credentials_available = False
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Claude 3 모델로 응답 생성"""
        
        if not self.credentials_available:
            return "죄송합니다. 현재 AI 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해주세요."
        
        try:
            messages = []
            
            # 시스템 프롬프트가 있으면 추가
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 사용자 메시지 추가
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Claude 3 API 호출을 위한 페이로드 구성
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                "temperature": kwargs.get('temperature', self.config.temperature),
                "top_p": kwargs.get('top_p', self.config.top_p),
                "messages": messages
            }
            
            # API 호출
            response = self.client.invoke_model(
                modelId=self.config.model_id,
                body=json.dumps(body),
                contentType='application/json'
            )
            
            # 응답 파싱
            response_body = json.loads(response['body'].read())
            
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0]['text']
            else:
                return "응답을 생성할 수 없습니다."
                
        except Exception as e:
            print(f"❌ Bedrock API 호출 실패: {str(e)}")
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    def generate_response_sync(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """동기 버전의 응답 생성"""
        
        if not self.credentials_available:
            return "죄송합니다. 현재 AI 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해주세요."
        
        try:
            messages = []
            
            # 시스템 프롬프트가 있으면 추가
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 사용자 메시지 추가
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Claude 3 API 호출을 위한 페이로드 구성
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                "temperature": kwargs.get('temperature', self.config.temperature),
                "top_p": kwargs.get('top_p', self.config.top_p),
                "messages": messages
            }
            
            # API 호출
            response = self.client.invoke_model(
                modelId=self.config.model_id,
                body=json.dumps(body),
                contentType='application/json'
            )
            
            # 응답 파싱
            response_body = json.loads(response['body'].read())
            
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0]['text']
            else:
                return "응답을 생성할 수 없습니다."
                
        except Exception as e:
            print(f"❌ Bedrock API 호출 실패: {str(e)}")
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    def is_available(self) -> bool:
        """클라이언트 사용 가능 여부 확인"""
        return self.credentials_available
    
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 반환"""
        return {
            "model_id": self.config.model_id,
            "region": self.config.region_name,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "available": self.credentials_available
        }


# 전역 클라이언트 인스턴스 (선택적)
_bedrock_client = None

def get_bedrock_client() -> BedrockClient:
    """전역 Bedrock 클라이언트 반환"""
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = BedrockClient()
    return _bedrock_client
