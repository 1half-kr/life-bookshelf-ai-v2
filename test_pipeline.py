#!/usr/bin/env python3
"""
Pipeline architecture testing script
"""
import asyncio
import json
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pipelines.conversation.pipeline import run_conversation_pipeline


async def test_conversation_pipeline():
    """Test the conversation pipeline"""
    print("🧪 Testing Conversation Pipeline...")
    print("=" * 50)
    
    # Test data
    test_cases = [
        {
            "name": "Basic conversation test",
            "session_id": "test_session_001",
            "message": "안녕하세요. 어린 시절 이야기를 들려드리고 싶어요.",
            "user_context": {
                "name": "김할머니",
                "age": 75,
                "gender": "여성",
                "birth_place": "부산",
                "occupation": "교사"
            }
        },
        {
            "name": "Family story test",
            "session_id": "test_session_002", 
            "message": "우리 가족은 6.25 전쟁 때 피난을 갔었어요.",
            "user_context": {
                "name": "박할아버지",
                "age": 82,
                "gender": "남성",
                "birth_place": "서울",
                "occupation": "공무원"
            }
        },
        {
            "name": "Work experience test",
            "session_id": "test_session_003",
            "message": "젊었을 때 직장에서 정말 열심히 일했어요.",
            "user_context": {
                "name": "이할머니",
                "age": 68,
                "gender": "여성",
                "birth_place": "대구",
                "occupation": "간호사"
            }
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            # Run pipeline
            result = await run_conversation_pipeline(
                session_id=test_case["session_id"],
                message=test_case["message"],
                user_context=test_case["user_context"]
            )
            
            # Check result
            if result.get("success"):
                print("✅ Pipeline execution: SUCCESS")
                print(f"📤 AI Response: {result['ai_response'][:100]}...")
                print(f"❓ Suggested Questions: {len(result['suggested_questions'])} questions")
                print(f"⏱️  Processing Time: {result.get('processing_time', 'N/A')} seconds")
                
                results.append({
                    "test_case": test_case["name"],
                    "status": "PASSED",
                    "processing_time": result.get("processing_time", 0),
                    "response_length": len(result["ai_response"]),
                    "questions_count": len(result["suggested_questions"])
                })
            else:
                print("❌ Pipeline execution: FAILED")
                print(f"🚨 Error: {result.get('error', 'Unknown error')}")
                
                results.append({
                    "test_case": test_case["name"],
                    "status": "FAILED",
                    "error": result.get("error", "Unknown error")
                })
                
        except Exception as e:
            print(f"💥 Exception occurred: {str(e)}")
            results.append({
                "test_case": test_case["name"],
                "status": "ERROR",
                "error": str(e)
            })
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"💥 Errors: {errors}")
    print(f"📈 Success Rate: {(passed / len(results)) * 100:.1f}%")
    
    if passed > 0:
        avg_time = sum(r.get("processing_time", 0) for r in results if r["status"] == "PASSED") / passed
        avg_response_length = sum(r.get("response_length", 0) for r in results if r["status"] == "PASSED") / passed
        avg_questions = sum(r.get("questions_count", 0) for r in results if r["status"] == "PASSED") / passed
        
        print(f"⏱️  Average Processing Time: {avg_time:.2f} seconds")
        print(f"📝 Average Response Length: {avg_response_length:.0f} characters")
        print(f"❓ Average Questions Count: {avg_questions:.1f}")
    
    return results


async def test_pipeline_components():
    """Test individual pipeline components"""
    print("\n🔧 Testing Pipeline Components...")
    print("=" * 50)
    
    try:
        # Test pipeline creation
        from pipelines.conversation.pipeline import create_conversation_pipeline
        
        pipeline = create_conversation_pipeline()
        status = pipeline.get_pipeline_status()
        
        print("✅ Pipeline Creation: SUCCESS")
        print(f"📋 Pipeline Name: {status['pipeline_name']}")
        print(f"🔢 Step Count: {status['step_count']}")
        print(f"🆔 Pipeline ID: {status['pipeline_id']}")
        
        # Test individual steps
        from pipelines.conversation.steps.validation import InputValidationStep
        from pipelines.conversation.steps.context_loader import ContextLoaderStep
        from pipelines.conversation.steps.llm_processor import LLMProcessorStep
        from pipelines.conversation.steps.response_builder import ResponseBuilderStep
        
        steps = [
            ("Input Validation", InputValidationStep),
            ("Context Loader", ContextLoaderStep),
            ("LLM Processor", LLMProcessorStep),
            ("Response Builder", ResponseBuilderStep)
        ]
        
        for step_name, step_class in steps:
            try:
                step = step_class()
                print(f"✅ {step_name} Step: Initialized successfully")
            except Exception as e:
                print(f"❌ {step_name} Step: Failed to initialize - {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"💥 Component testing failed: {str(e)}")
        return False


async def test_data_models():
    """Test data models"""
    print("\n📊 Testing Data Models...")
    print("=" * 50)
    
    try:
        from shared.models.data import UserProfile, Message, ConversationSession, MessageType
        
        # Test UserProfile
        user_profile = UserProfile(
            name="테스트 사용자",
            age=75,
            gender="여성",
            birth_place="서울",
            occupation="교사"
        )
        print(f"✅ UserProfile: {user_profile.name}, {user_profile.generation}")
        
        # Test Message
        message = Message(
            id="test_msg_001",
            content="안녕하세요",
            message_type=MessageType.TEXT,
            sender="user"
        )
        print(f"✅ Message: {message.word_count} words, from {message.sender}")
        
        # Test ConversationSession
        session = ConversationSession(
            session_id="test_session",
            user_profile=user_profile
        )
        session.add_message(message)
        print(f"✅ ConversationSession: {session.message_count} messages")
        
        return True
        
    except Exception as e:
        print(f"💥 Data model testing failed: {str(e)}")
        return False


async def main():
    """Main test function"""
    print("🚀 Life Bookshelf AI v2 - Pipeline Architecture Testing")
    print("=" * 60)
    
    # Test components
    component_test = await test_pipeline_components()
    
    # Test data models
    model_test = await test_data_models()
    
    # Test full pipeline
    if component_test and model_test:
        pipeline_results = await test_conversation_pipeline()
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 60)
        
        passed_tests = sum(1 for r in pipeline_results if r["status"] == "PASSED")
        total_tests = len(pipeline_results)
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Pipeline architecture is working correctly.")
            return 0
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed. Please check the issues above.")
            return 1
    else:
        print("❌ Component or model tests failed. Cannot proceed with pipeline testing.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
