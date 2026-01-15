"""
Test import for quality_validator library component.

Verifies that the quality_validator component was deployed correctly
and can be imported and used.
"""

import sys
from pathlib import Path

# Add backend to path for import
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))


def test_import_quality_validator():
    """Test that quality_validator can be imported."""
    from library.components.validation.quality_validator import (
        QualityValidator,
        QualityClaim,
        QualityValidationResult,
        Violation,
        AnalysisResult,
        Severity,
        EvidenceQuality,
        RiskLevel,
    )

    # Verify classes are importable
    assert QualityValidator is not None
    assert QualityClaim is not None
    assert QualityValidationResult is not None
    assert Violation is not None
    assert AnalysisResult is not None


def test_quality_validator_basic_usage():
    """Test basic QualityValidator functionality."""
    from library.components.validation.quality_validator import QualityValidator

    # Create validator with default config
    validator = QualityValidator()

    # Add a violation
    violation = validator.add_violation(
        rule_id="TEST-001",
        message="Test violation",
        file="test_file.py",
        line=10,
        severity="medium",
        category="test",
    )

    assert violation is not None
    assert violation.rule_id == "TEST-001"
    assert violation.severity == "medium"

    # Check metrics
    metrics = validator.get_metrics()
    assert metrics["total_violations"] == 1
    assert metrics["severity_counts"]["medium"] == 1

    # Check gate
    assert validator.check_gate(fail_on="critical") is True
    assert validator.check_gate(fail_on="high") is True


def test_quality_validator_analysis():
    """Test QualityValidator analysis functionality."""
    from library.components.validation.quality_validator import QualityValidator

    validator = QualityValidator()

    # Add violations of different severities
    validator.add_violation("RULE-1", "Critical issue", "file1.py", 1, severity="critical")
    validator.add_violation("RULE-2", "High issue", "file2.py", 2, severity="high")
    validator.add_violation("RULE-3", "Medium issue", "file3.py", 3, severity="medium")

    # Run analysis
    result = validator.analyze(fail_on="critical", project_path="test-project")

    assert result is not None
    assert len(result.violations) == 3
    assert result.overall_score < 100.0  # Should have penalties
    assert result.quality_gate_passed is False  # Has critical violation


def test_severity_enum():
    """Test Severity enum values."""
    from library.components.validation.quality_validator import Severity

    assert Severity.CRITICAL.value == "critical"
    assert Severity.HIGH.value == "high"
    assert Severity.MEDIUM.value == "medium"
    assert Severity.LOW.value == "low"
    assert Severity.INFO.value == "info"


if __name__ == "__main__":
    print("Running quality_validator import tests...")

    test_import_quality_validator()
    print("[PASS] test_import_quality_validator")

    test_quality_validator_basic_usage()
    print("[PASS] test_quality_validator_basic_usage")

    test_quality_validator_analysis()
    print("[PASS] test_quality_validator_analysis")

    test_severity_enum()
    print("[PASS] test_severity_enum")

    print("\nAll tests passed! Quality validator component deployed successfully.")
