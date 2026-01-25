"""Test script for AI Core"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.core import AICore
from app.model import ModelClient


async def main():
    """Test AI Core"""
    print("=== AI CORE TEST ===\n")
    
    # Initialize with mock model
    model = ModelClient(provider="mock")
    ai = AICore(model_client=model)
    
    # Test messages
    test_messages = [
        "Xin chào!",
        "Giải thích cho tôi về Python?",
        "Bạn có biết về sách 'Đắc Nhân Tâm' không?",
        "abc",  # Short message - should refuse
    ]
    
    session_id = None
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {msg}")
        print(f"{'='*60}")
        
        result = await ai.process(msg, session_id)
        session_id = result["session_id"]
        
        print(f"\nResponse: {result['response']}")
        print(f"\nMetadata:")
        
        # Check if metadata has full structure (not refused)
        metadata = result['metadata']
        if 'persona' in metadata:
            print(f"  - Persona: {metadata['persona']}")
            print(f"  - Context: {metadata['context']['context_type']}")
            print(f"  - Confidence: {metadata['context']['confidence']:.2f}")
            print(f"  - Valid: {metadata['valid']}")
            if metadata['warnings']:
                print(f"  - Warnings: {metadata['warnings']}")
        elif 'refused' in metadata:
            print(f"  - Refused: {metadata['refused']}")
            print(f"  - Reason: {metadata['reason']}")
            print(f"  - Context: {metadata['context']['context_type']}")
        else:
            print(f"  - Raw metadata: {metadata}")
    
    print(f"\n{'='*60}")
    print("✅ ALL TESTS COMPLETED")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
