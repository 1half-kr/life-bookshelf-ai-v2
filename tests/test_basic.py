#!/usr/bin/env python3
"""
Basic pipeline test
"""
import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pipelines.conversation.pipeline import run_conversation_pipeline


async def test_basic_conversation():
    """Test basic conversation pipeline"""
    print("🧪 Testing basic conversation...")
    
    result = await run_conversation_pipeline(
        session_id="test_001",
        message="안녕하세요. 어린 시절 이야기를 들려드리고 싶어요.",
        user_context={
            "name": "김할머니",
            "age": 75,
            "gender": "여성"
        }
    )
    
    if result.get("success"):
        print("✅ Test passed!")
        print(f"📤 Response: {result['ai_response'][:50]}...")
        return True
    else:
        print("❌ Test failed!")
        print(f"🚨 Error: {result.get('error')}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_basic_conversation())
    sys.exit(0 if success else 1)
