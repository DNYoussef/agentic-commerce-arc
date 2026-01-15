"""
Spec Validation - Specification Document Validation Framework

A generalized validation framework for specification documents including
JSON schemas, markdown documents, and implementation plans.

Provides:
- Configurable JSON schema validation
- Markdown section validation
- Implementation plan structure validation
- Extensible validator architecture with dependency injection

Usage:
    from library.components.validation.spec_validation import (
        SpecValidator,
        SpecValidationResult,
        ValidationSchema,
        BaseValidator,
    )

    # Basic usage with defaults
    validator = SpecValidator(spec_dir="/path/to/specs")
    results = validator.validate_all()

    # Check if valid
    if validator.is_valid():
        print("All validations passed!")

    # Get summary
    summary = validator.get_summary()
    print(f"Total errors: {summary['total_errors']}")
"""

from .spec_validation import (
    # Main validator class
    SpecValidator,
    # Result types
    SpecValidationResult,
    ValidationResult,
    # Schema configuration
    ValidationSchema,
    # Base classes for extension
    BaseValidator,
    Validatable,
    ValidatorFactory,
    # Individual validators
    PrereqsValidator,
    JSONFileValidator,
    ContextValidator,
    MarkdownDocumentValidator,
    SpecDocumentValidator,
    ImplementationPlanValidator,
    # Default schemas
    DEFAULT_SUBTASK_SCHEMA,
    DEFAULT_VERIFICATION_SCHEMA,
    DEFAULT_PHASE_SCHEMA,
    DEFAULT_IMPLEMENTATION_PLAN_SCHEMA,
    DEFAULT_CONTEXT_SCHEMA,
    DEFAULT_REQUIREMENTS_SCHEMA,
    DEFAULT_SPEC_REQUIRED_SECTIONS,
    DEFAULT_SPEC_RECOMMENDED_SECTIONS,
    # Utility functions
    validate_spec_directory,
    create_validator_from_config,
)

__all__ = [
    # Main validator class
    "SpecValidator",
    # Result types
    "SpecValidationResult",
    "ValidationResult",
    # Schema configuration
    "ValidationSchema",
    # Base classes for extension
    "BaseValidator",
    "Validatable",
    "ValidatorFactory",
    # Individual validators
    "PrereqsValidator",
    "JSONFileValidator",
    "ContextValidator",
    "MarkdownDocumentValidator",
    "SpecDocumentValidator",
    "ImplementationPlanValidator",
    # Default schemas
    "DEFAULT_SUBTASK_SCHEMA",
    "DEFAULT_VERIFICATION_SCHEMA",
    "DEFAULT_PHASE_SCHEMA",
    "DEFAULT_IMPLEMENTATION_PLAN_SCHEMA",
    "DEFAULT_CONTEXT_SCHEMA",
    "DEFAULT_REQUIREMENTS_SCHEMA",
    "DEFAULT_SPEC_REQUIRED_SECTIONS",
    "DEFAULT_SPEC_RECOMMENDED_SECTIONS",
    # Utility functions
    "validate_spec_directory",
    "create_validator_from_config",
]
