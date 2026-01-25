"""
Example: Conversation Demo with AI Core
Demonstrates all 3 personas in action
"""
import asyncio
from app.core import AICore
from app.model import ModelClient


def print_separator(title=""):
    """Print a nice separator"""
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)
    print()


async def demo_conversation():
    """Demo conversation showcasing different personas"""
    
    print_separator("🎭 AI CORE - PERSONA DEMO")
    
    # Initialize AI Core with mock model
    model = ModelClient(provider="mock")
    ai = AICore(model_client=model)
    
    # Conversation scenarios
    scenarios = [
        {
            "title": "💬 CASUAL CHAT",
            "messages": [
                "Chào bạn!",
                "Hôm nay thế nào?",
            ]
        },
        {
            "title": "🔧 TECHNICAL QUESTION",
            "messages": [
                "Giải thích cho tôi về async/await trong Python?",
                "Làm sao để debug lỗi này?",
            ]
        },
        {
            "title": "📚 KNOWLEDGE QUESTION",
            "messages": [
                "Bạn có biết về sách 'Sapiens' không?",
                "Tóm tắt cho tôi về cuốn 'Thinking Fast and Slow'",
            ]
        },
        {
            "title": "⚠️ REFUSING (Thiếu context)",
            "messages": [
                "abc",
                "hmm",
                "???"
            ]
        }
    ]
    
    session_id = None
    
    for scenario in scenarios:
        print_separator(scenario["title"])
        
        for i, message in enumerate(scenario["messages"], 1):
            print(f"👤 User: {message}")
            
            # Process message
            result = await ai.process(message, session_id)
            session_id = result["session_id"]
            
            # Print response
            print(f"🤖 AI: {result['response']}\n")
            
            # Print metadata
            metadata = result["metadata"]
            if "persona" in metadata:
                print(f"   📊 Persona: {metadata['persona']}")
                print(f"   📊 Context: {metadata['context']['context_type']}")
                print(f"   📊 Confidence: {metadata['context']['confidence']:.0%}")
                if metadata.get("warnings"):
                    print(f"   ⚠️  Warnings: {', '.join(metadata['warnings'])}")
            elif "refused" in metadata:
                print(f"   ❌ Refused: {metadata['reason']}")
            
            print()
    
    # Show final stats
    print_separator("📈 SESSION STATS")
    history = ai.short_memory.get_recent_messages(session_id)
    print(f"Total messages in session: {len(history)}")
    print(f"Active sessions: {len(ai.short_memory.sessions)}")
    
    # Count personas used
    from collections import Counter
    persona_counts = Counter([
        msg.persona for msg in history 
        if msg.role == "assistant" and msg.persona
    ])
    
    print(f"\nPersona usage:")
    for persona, count in persona_counts.items():
        print(f"  - {persona}: {count} times")
    
    print_separator()
    print("✅ Demo completed!")
    print("\n💡 Tip: Thay 'mock' bằng 'openai' hoặc 'anthropic' để dùng model thật\n")


if __name__ == "__main__":
    asyncio.run(demo_conversation())
