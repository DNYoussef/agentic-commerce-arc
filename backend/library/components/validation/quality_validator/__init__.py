"""
Quality Validator - Evidence-Based Quality Gate System

Provides threshold-based confidence scoring and pass/fail quality gate logic.
Extracted from Connascence Analyzer unified quality gate system.

Usage:
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

    # Basic usage
    validator = QualityValidator()
    validator.add_violation("RULE-001", "Issue found", "file.py", 10, severity="high")
    result = validator.analyze()
    print(f"Gate passed: {result.quality_gate_passed}")
"""

from .quality_validator import (
    QualityValidator,
    QualityClaim,
    QualityValidationResult,
    ValidationResult,
    Violation,
    AnalysisResult,
    Severity,
    EvidenceQuality,
    RiskLevel,
)

__all__ = [
    "QualityValidator",
    "QualityClaim",
    "QualityValidationResult",
    "ValidationResult",
    "Violation",
    "AnalysisResult",
    "Severity",
    "EvidenceQuality",
    "RiskLevel",
]
