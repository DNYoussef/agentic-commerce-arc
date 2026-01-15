"""
Validation components package.

Contains reusable validation components:
- quality_validator: Evidence-based quality gate system
- spec_validation: Specification document validation framework
"""

# Re-export for convenience
from .quality_validator import QualityValidator
from .spec_validation import SpecValidator
