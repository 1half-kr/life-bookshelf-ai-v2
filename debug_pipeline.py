#!/usr/bin/env python3
"""
Pipeline debugging script
"""
import asyncio
import json
import sys
import traceback
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def debug_single_step():
    """Debug individual pipeline steps"""
    print("🔍 Debugging Individual Pipeline Steps...")
    print("=" * 50)
    
    try:
        from shared.models.pipeline import StepContext
        from shared.models.data import UserProfile, MessageType
        from pipelines.conversation.steps.validation import InputValidationStep
        
        # Test validation step
        print("1️⃣ Testing Validation Step...")
        
        context = StepContext(
            pipeline_id="debug_test",
            step_name="validation",
            input_data={
                "session_id": "test_session_001",
                "message": "안녕하세요. 어린 시절 이야기를 들려드리고 싶어요.",
                "user_context": {
                    "name": "김할머니",
                    "age": 75,
                    "gender": "여성",
                    "birth_place": "부산",
                    "occupation": "교사"
                },
                "message_type": "text"
            }
        )
        
        validation_step = InputValidationStep()
        result = await validation_step.execute(context)
        
        print(f"   Status: {result.status}")
        print(f"   Success: {result.is_successful}")
        if result.error_message:
            print(f"   Error: {result.error_message}")
        else:
            print(f"   Output keys: {list(result.output_data.keys())}")
        
        if not result.is_successful:
            print("❌ Validation step failed!")
            return False
        
        print("✅ Validation step passed!")
        
        # Test context loader step
        print("\n2️⃣ Testing Context Loader Step...")
        
        from pipelines.conversation.steps.context_loader import ContextLoaderStep
        
        context_loader_input = StepContext(
            pipeline_id="debug_test",
            step_name="context_loader",
            input_data={
                "validated_session_id": result.output_data["validated_session_id"],
                "validated_user_profile": result.output_data["validated_user_profile"]
            }
        )
        
        context_loader_step = ContextLoaderStep()
        context_result = await context_loader_step.execute(context_loader_input)
        
        print(f"   Status: {context_result.status}")
        print(f"   Success: {context_result.is_successful}")
        if context_result.error_message:
            print(f"   Error: {context_result.error_message}")
        else:
            print(f"   Output keys: {list(context_result.output_data.keys())}")
        
        if not context_result.is_successful:
            print("❌ Context loader step failed!")
            return False
        
        print("✅ Context loader step passed!")
        
        # Test LLM processor step
        print("\n3️⃣ Testing LLM Processor Step...")
        
        from pipelines.conversation.steps.llm_processor import LLMProcessorStep
        
        llm_input = StepContext(
            pipeline_id="debug_test",
            step_name="llm_processor",
            input_data={
                "validated_message": result.output_data["validated_message"],
                "validated_user_profile": result.output_data["validated_user_profile"],
                "conversation_context": context_result.output_data["conversation_context"],
                "generation_context": context_result.output_data["generation_context"],
                "historical_context": context_result.output_data["historical_context"],
                "is_new_session": context_result.output_data["is_new_session"]
            }
        )
        
        llm_step = LLMProcessorStep()
        llm_result = await llm_step.execute(llm_input)
        
        print(f"   Status: {llm_result.status}")
        print(f"   Success: {llm_result.is_successful}")
        if llm_result.error_message:
            print(f"   Error: {llm_result.error_message}")
        else:
            print(f"   Output keys: {list(llm_result.output_data.keys())}")
            print(f"   AI Response: {llm_result.output_data.get('ai_response', '')[:100]}...")
        
        if not llm_result.is_successful:
            print("❌ LLM processor step failed!")
            return False
        
        print("✅ LLM processor step passed!")
        
        return True
        
    except Exception as e:
        print(f"💥 Exception in step debugging: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


async def debug_full_pipeline():
    """Debug full pipeline execution"""
    print("\n🔍 Debugging Full Pipeline...")
    print("=" * 50)
    
    try:
        from pipelines.conversation.pipeline import ConversationPipeline
        
        # Create pipeline with debug config
        config = {
            "max_message_length": 2000,
            "min_age": 65,
            "max_age": 120,
            "max_context_messages": 10,
            "session_timeout_hours": 2,
            "model_id": "claude-3-sonnet-20240229",
            "fallback_model_id": "claude-3-haiku-20240307",
            "max_tokens": 1000,
            "temperature": 0.7,
            "timeout_seconds": 30,
            "include_analysis": True,
            "include_suggestions": True
        }
        
        pipeline = ConversationPipeline(config)
        
        # Test input data
        input_data = {
            "session_id": "debug_session_001",
            "message": "안녕하세요. 어린 시절 이야기를 들려드리고 싶어요.",
            "user_context": {
                "name": "김할머니",
                "age": 75,
                "gender": "여성",
                "birth_place": "부산",
                "occupation": "교사"
            },
            "message_type": "text"
        }
        
        print("📤 Input data prepared")
        print(f"   Session ID: {input_data['session_id']}")
        print(f"   Message: {input_data['message'][:50]}...")
        print(f"   User: {input_data['user_context']['name']}")
        
        # Execute pipeline
        print("\n🚀 Executing pipeline...")
        result = await pipeline.execute(input_data)
        
        print(f"📊 Pipeline Result:")
        print(f"   Status: {result.status}")
        print(f"   Success: {result.is_successful}")
        print(f"   Total Steps: {len(result.step_results)}")
        print(f"   Execution Time: {result.total_execution_time:.2f} seconds")
        
        # Check each step result
        for i, step_result in enumerate(result.step_results, 1):
            print(f"\n   Step {i}: {step_result.step_name}")
            print(f"      Status: {step_result.status}")
            print(f"      Success: {step_result.is_successful}")
            print(f"      Time: {step_result.execution_time:.2f}s")
            if step_result.error_message:
                print(f"      Error: {step_result.error_message}")
            if step_result.output_data:
                print(f"      Output Keys: {list(step_result.output_data.keys())}")
        
        if result.is_successful:
            print("\n✅ Full pipeline execution successful!")
            return True
        else:
            print("\n❌ Full pipeline execution failed!")
            failed_steps = result.failed_steps
            for failed_step in failed_steps:
                print(f"   Failed Step: {failed_step.step_name}")
                print(f"   Error: {failed_step.error_message}")
            return False
        
    except Exception as e:
        print(f"💥 Exception in full pipeline debugging: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


async def debug_pipeline_runner():
    """Debug the pipeline runner function"""
    print("\n🔍 Debugging Pipeline Runner...")
    print("=" * 50)
    
    try:
        from pipelines.conversation.pipeline import run_conversation_pipeline
        
        result = await run_conversation_pipeline(
            session_id="debug_runner_001",
            message="안녕하세요. 어린 시절 이야기를 들려드리고 싶어요.",
            user_context={
                "name": "김할머니",
                "age": 75,
                "gender": "여성",
                "birth_place": "부산",
                "occupation": "교사"
            },
            message_type="text"
        )
        
        print(f"📊 Runner Result:")
        print(f"   Success: {result.get('success', False)}")
        
        if result.get("success"):
            print(f"   AI Response: {result.get('ai_response', '')[:100]}...")
            print(f"   Questions: {len(result.get('suggested_questions', []))}")
            print(f"   Processing Time: {result.get('processing_time', 'N/A')}")
            print("✅ Pipeline runner successful!")
            return True
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            print(f"   Failed Steps: {result.get('failed_steps', [])}")
            print(f"   Error Messages: {result.get('error_messages', [])}")
            print("❌ Pipeline runner failed!")
            return False
        
    except Exception as e:
        print(f"💥 Exception in pipeline runner debugging: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


async def main():
    """Main debug function"""
    print("🐛 Life Bookshelf AI v2 - Pipeline Debugging")
    print("=" * 60)
    
    # Debug individual steps
    step_success = await debug_single_step()
    
    if step_success:
        # Debug full pipeline
        pipeline_success = await debug_full_pipeline()
        
        if pipeline_success:
            # Debug pipeline runner
            runner_success = await debug_pipeline_runner()
            
            if runner_success:
                print("\n🎉 All debugging tests passed!")
                return 0
    
    print("\n❌ Debugging revealed issues. Please check the output above.")
    return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
