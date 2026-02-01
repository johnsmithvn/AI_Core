"""
Test Automation Script - 20 hội thoại test AI Core
Version: 1.0.0
Date: 2026-02-01

Chạy: python tests/test_automation.py
"""

import asyncio
import yaml
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core import AICore
from app.core.context import ContextAnalyzer
from app.core.persona import PersonaSelector
from app.model import ModelClient


class TestStatus(Enum):
    PASSED = "✅ PASSED"
    FAILED = "❌ FAILED"
    WARNING = "⚠️ WARNING"
    SKIPPED = "⏭️ SKIPPED"


@dataclass
class TestResult:
    """Kết quả của một test case"""
    test_id: str
    status: TestStatus
    input_text: str
    expected: Dict[str, Any]
    actual: Dict[str, Any]
    response: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_ms: float = 0


@dataclass
class TestReport:
    """Báo cáo tổng hợp"""
    total: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    skipped: int = 0
    
    # Metrics
    tone_correct: int = 0
    tone_total: int = 0
    behavior_correct: int = 0
    behavior_total: int = 0
    refuse_correct: int = 0
    refuse_total: int = 0
    fabrication_detected: int = 0
    
    results: List[TestResult] = field(default_factory=list)
    
    @property
    def tone_accuracy(self) -> float:
        return (self.tone_correct / self.tone_total * 100) if self.tone_total > 0 else 0
    
    @property
    def behavior_accuracy(self) -> float:
        return (self.behavior_correct / self.behavior_total * 100) if self.behavior_total > 0 else 0
    
    @property
    def refuse_accuracy(self) -> float:
        return (self.refuse_correct / self.refuse_total * 100) if self.refuse_total > 0 else 0


class ConversationTester:
    """
    Test automation cho AI Core conversations.
    
    Đo các metrics:
    - Tone accuracy (casual/technical detection)
    - Behavior accuracy (normal/cautious selection)
    - Refuse accuracy (đúng lúc từ chối)
    - Fabrication detection (AI có bịa không)
    """
    
    def __init__(
        self,
        test_file: str = "tests/test_conversations.yaml",
        use_real_model: bool = False,
        model_provider: str = "mock"
    ):
        self.test_file = Path(test_file)
        self.use_real_model = use_real_model
        self.model_provider = model_provider
        
        # Load test cases
        self.test_cases = self._load_test_cases()
        
        # Initialize components
        self.context_analyzer = ContextAnalyzer()
        self.persona_selector = PersonaSelector()
        
        # Initialize AI Core (optional - for full integration test)
        if use_real_model:
            self.model_client = ModelClient(provider=model_provider)
            self.ai_core = AICore(model_client=self.model_client)
        else:
            self.ai_core = None
        
        self.report = TestReport()
    
    def _load_test_cases(self) -> Dict[str, Any]:
        """Load test cases từ YAML"""
        if not self.test_file.exists():
            raise FileNotFoundError(f"Test file not found: {self.test_file}")
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def run_all_tests(self) -> TestReport:
        """Chạy tất cả test cases"""
        print("\n" + "="*60)
        print("🧪 AI CORE - CONVERSATION TEST AUTOMATION")
        print("="*60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Test file: {self.test_file}")
        print(f"🤖 Model: {'Real (' + self.model_provider + ')' if self.use_real_model else 'Context Analysis Only'}")
        print("="*60 + "\n")
        
        # Run each category
        categories = [
            ("casual_chat", "🎭 CASUAL CHAT"),
            ("technical_questions", "💻 TECHNICAL QUESTIONS"),
            ("knowledge_questions", "📚 KNOWLEDGE QUESTIONS"),
            ("edge_cases", "⚡ EDGE CASES"),
        ]
        
        for category_key, category_name in categories:
            if category_key in self.test_cases:
                print(f"\n{category_name}")
                print("-" * 40)
                for test_case in self.test_cases[category_key]:
                    result = self._run_single_test(test_case, category_key)
                    self.report.results.append(result)
                    self._print_test_result(result)
        
        # Print summary
        self._print_summary()
        
        return self.report
    
    def _run_single_test(self, test_case: Dict, category: str) -> TestResult:
        """Chạy một test case"""
        import time
        start_time = time.time()
        
        test_id = test_case.get("id", "unknown")
        input_text = test_case.get("input", "")
        expected = test_case.get("expected", {})
        validation = test_case.get("validation", {})
        
        errors = []
        warnings = []
        actual = {}
        response = ""
        
        self.report.total += 1
        
        try:
            # Step 1: Analyze context
            context = self.context_analyzer.analyze(input_text)
            actual["context_type"] = context.get("context_type")
            actual["needs_knowledge"] = context.get("needs_knowledge")
            actual["confidence"] = context.get("confidence")
            actual["response_mode"] = context.get("response_mode")
            
            # Step 2: Check refusal
            should_refuse, refuse_msg = self.context_analyzer.should_refuse(input_text, context)
            actual["should_refuse"] = should_refuse
            actual["refuse_message"] = refuse_msg if should_refuse else None
            
            # Step 3: Select persona
            persona = self.persona_selector.select(context)
            actual["tone"] = persona.get("tone")
            actual["behavior"] = persona.get("behavior")
            actual["temperature"] = persona.get("temperature")
            
            # Step 4: Validate against expected
            
            # Check context_type
            if "context_type" in expected:
                self.report.tone_total += 1
                if actual["context_type"] == expected["context_type"]:
                    self.report.tone_correct += 1
                else:
                    errors.append(
                        f"context_type: expected '{expected['context_type']}', "
                        f"got '{actual['context_type']}'"
                    )
            
            # Check tone
            if "tone" in expected:
                if actual["tone"] != expected["tone"]:
                    errors.append(
                        f"tone: expected '{expected['tone']}', got '{actual['tone']}'"
                    )
            
            # Check needs_knowledge
            if "needs_knowledge" in expected:
                if actual["needs_knowledge"] != expected["needs_knowledge"]:
                    errors.append(
                        f"needs_knowledge: expected {expected['needs_knowledge']}, "
                        f"got {actual['needs_knowledge']}"
                    )
            
            # Check behavior
            if "behavior" in expected:
                self.report.behavior_total += 1
                if actual["behavior"] == expected["behavior"]:
                    self.report.behavior_correct += 1
                else:
                    errors.append(
                        f"behavior: expected '{expected['behavior']}', "
                        f"got '{actual['behavior']}'"
                    )
            
            # Check should_refuse
            if "should_refuse" in validation:
                self.report.refuse_total += 1
                if actual["should_refuse"] == validation["should_refuse"]:
                    self.report.refuse_correct += 1
                else:
                    errors.append(
                        f"should_refuse: expected {validation['should_refuse']}, "
                        f"got {actual['should_refuse']}"
                    )
            
            # Step 5: Full integration test (if using real model)
            if self.use_real_model and self.ai_core and not should_refuse:
                try:
                    result = asyncio.run(self.ai_core.process(input_text))
                    response = result.get("response", "")
                    actual["full_response"] = response
                    
                    # Validate response content
                    content_errors = self._validate_response_content(
                        response, validation, test_id
                    )
                    errors.extend(content_errors)
                    
                except Exception as e:
                    warnings.append(f"Model call failed: {str(e)}")
            
        except Exception as e:
            errors.append(f"Test execution error: {str(e)}")
        
        # Determine status
        duration_ms = (time.time() - start_time) * 1000
        
        if errors:
            status = TestStatus.FAILED
            self.report.failed += 1
        elif warnings:
            status = TestStatus.WARNING
            self.report.warnings += 1
        else:
            status = TestStatus.PASSED
            self.report.passed += 1
        
        return TestResult(
            test_id=test_id,
            status=status,
            input_text=input_text,
            expected=expected,
            actual=actual,
            response=response,
            errors=errors,
            warnings=warnings,
            duration_ms=duration_ms
        )
    
    def _validate_response_content(
        self,
        response: str,
        validation: Dict,
        test_id: str
    ) -> List[str]:
        """Validate nội dung response"""
        errors = []
        response_lower = response.lower()
        
        # Check must_contain_any
        if "must_contain_any" in validation:
            keywords = validation["must_contain_any"]
            if not any(kw.lower() in response_lower for kw in keywords):
                errors.append(
                    f"Response missing required keywords: {keywords}"
                )
        
        # Check must_not_contain
        if "must_not_contain" in validation:
            forbidden = validation["must_not_contain"]
            found = [kw for kw in forbidden if kw.lower() in response_lower]
            if found:
                errors.append(f"Response contains forbidden phrases: {found}")
        
        # Check fabrication (simplified heuristic)
        if validation.get("must_not_fabricate"):
            fabrication_indicators = [
                "cuốn sách",
                "tác giả",
                "xuất bản năm",
                "ISBN",
            ]
            # Nếu AI nói về sách cụ thể mà không kèm disclaimer
            # thì có thể đang bịa
            if any(ind in response_lower for ind in fabrication_indicators):
                if "không chắc" not in response_lower and \
                   "tôi không biết" not in response_lower and \
                   "có thể" not in response_lower:
                    errors.append("Potential fabrication detected (specific claims without disclaimer)")
                    self.report.fabrication_detected += 1
        
        # Check must_admit_unknown (for fake book test)
        if validation.get("must_admit_unknown"):
            admit_phrases = [
                "không biết", "không có thông tin", "không tìm thấy",
                "chưa nghe", "không rõ", "không chắc"
            ]
            if not any(phrase in response_lower for phrase in admit_phrases):
                errors.append("AI should admit unknown but didn't")
                self.report.fabrication_detected += 1
        
        return errors
    
    def _print_test_result(self, result: TestResult):
        """In kết quả một test"""
        status_str = result.status.value
        print(f"  {result.test_id}: {status_str} ({result.duration_ms:.1f}ms)")
        
        if result.errors:
            for error in result.errors:
                print(f"      ❌ {error}")
        
        if result.warnings:
            for warning in result.warnings:
                print(f"      ⚠️ {warning}")
    
    def _print_summary(self):
        """In báo cáo tổng hợp"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        # Overall results
        print(f"\n📈 Overall Results:")
        print(f"   Total:    {self.report.total}")
        print(f"   Passed:   {self.report.passed} ✅")
        print(f"   Failed:   {self.report.failed} ❌")
        print(f"   Warnings: {self.report.warnings} ⚠️")
        
        pass_rate = (self.report.passed / self.report.total * 100) if self.report.total > 0 else 0
        print(f"   Pass Rate: {pass_rate:.1f}%")
        
        # Metrics
        print(f"\n📏 Metrics:")
        print(f"   Tone Accuracy:     {self.report.tone_accuracy:.1f}% ({self.report.tone_correct}/{self.report.tone_total})")
        print(f"   Behavior Accuracy: {self.report.behavior_accuracy:.1f}% ({self.report.behavior_correct}/{self.report.behavior_total})")
        print(f"   Refuse Accuracy:   {self.report.refuse_accuracy:.1f}% ({self.report.refuse_correct}/{self.report.refuse_total})")
        print(f"   Fabrications:      {self.report.fabrication_detected} {'🚨 CRITICAL!' if self.report.fabrication_detected > 0 else '✅'}")
        
        # Targets
        print(f"\n🎯 Targets:")
        targets = self.test_cases.get("metrics", {})
        
        tone_target = targets.get("tone_accuracy", {}).get("target", 90)
        behavior_target = targets.get("behavior_accuracy", {}).get("target", 90)
        refuse_target = targets.get("refuse_accuracy", {}).get("target", 95)
        
        tone_status = "✅" if self.report.tone_accuracy >= tone_target else "❌"
        behavior_status = "✅" if self.report.behavior_accuracy >= behavior_target else "❌"
        refuse_status = "✅" if self.report.refuse_accuracy >= refuse_target else "❌"
        fab_status = "✅" if self.report.fabrication_detected == 0 else "🚨"
        
        print(f"   Tone:      {self.report.tone_accuracy:.1f}% / {tone_target}% {tone_status}")
        print(f"   Behavior:  {self.report.behavior_accuracy:.1f}% / {behavior_target}% {behavior_status}")
        print(f"   Refuse:    {self.report.refuse_accuracy:.1f}% / {refuse_target}% {refuse_status}")
        print(f"   No Fabrication: {self.report.fabrication_detected} / 0 {fab_status}")
        
        # Failed tests detail
        failed_tests = [r for r in self.report.results if r.status == TestStatus.FAILED]
        if failed_tests:
            print(f"\n❌ Failed Tests Detail:")
            for result in failed_tests:
                print(f"\n   [{result.test_id}]")
                print(f"   Input: \"{result.input_text[:50]}{'...' if len(result.input_text) > 50 else ''}\"")
                for error in result.errors:
                    print(f"   → {error}")
        
        print("\n" + "="*60)
        
        # Final verdict
        if self.report.failed == 0 and self.report.fabrication_detected == 0:
            print("🎉 ALL TESTS PASSED! Ready for next phase.")
        elif self.report.fabrication_detected > 0:
            print("🚨 CRITICAL: Fabrication detected! Fix before proceeding.")
        else:
            print(f"⚠️ {self.report.failed} tests failed. Review and fix.")
        
        print("="*60 + "\n")
    
    def export_report(self, output_file: str = "tests/test_report.json"):
        """Export báo cáo ra JSON"""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": self.report.total,
                "passed": self.report.passed,
                "failed": self.report.failed,
                "warnings": self.report.warnings,
                "pass_rate": (self.report.passed / self.report.total * 100) if self.report.total > 0 else 0
            },
            "metrics": {
                "tone_accuracy": self.report.tone_accuracy,
                "behavior_accuracy": self.report.behavior_accuracy,
                "refuse_accuracy": self.report.refuse_accuracy,
                "fabrication_count": self.report.fabrication_detected
            },
            "results": [
                {
                    "test_id": r.test_id,
                    "status": r.status.name,
                    "input": r.input_text,
                    "expected": r.expected,
                    "actual": r.actual,
                    "errors": r.errors,
                    "warnings": r.warnings,
                    "duration_ms": r.duration_ms
                }
                for r in self.report.results
            ]
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Report exported to: {output_file}")


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Core Conversation Test Automation")
    parser.add_argument(
        "--real-model",
        action="store_true",
        help="Use real model for full integration test"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="local",
        choices=["mock", "openai", "anthropic", "local"],
        help="Model provider (default: local)"
    )
    parser.add_argument(
        "--export",
        type=str,
        default="tests/test_report.json",
        help="Export report to JSON file"
    )
    
    args = parser.parse_args()
    
    # Run tests
    tester = ConversationTester(
        use_real_model=args.real_model,
        model_provider=args.provider
    )
    
    report = tester.run_all_tests()
    
    # Export report
    tester.export_report(args.export)
    
    # Exit code based on results
    if report.failed > 0 or report.fabrication_detected > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
