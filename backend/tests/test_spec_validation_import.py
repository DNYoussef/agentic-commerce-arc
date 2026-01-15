"""
Test imports for spec_validation library component.

Verifies that the SpecValidator component was properly deployed from the library.
"""

import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))


def test_spec_validation_import():
    """Test that SpecValidator can be imported from the library."""
    from library.components.validation.spec_validation import SpecValidator
    assert SpecValidator is not None
    print("[PASS] SpecValidator imported successfully")


def test_spec_validation_result_import():
    """Test that SpecValidationResult can be imported."""
    from library.components.validation.spec_validation import SpecValidationResult
    assert SpecValidationResult is not None
    print("[PASS] SpecValidationResult imported successfully")


def test_validation_schema_import():
    """Test that ValidationSchema can be imported."""
    from library.components.validation.spec_validation import ValidationSchema
    assert ValidationSchema is not None
    print("[PASS] ValidationSchema imported successfully")


def test_base_validator_import():
    """Test that BaseValidator can be imported."""
    from library.components.validation.spec_validation import BaseValidator
    assert BaseValidator is not None
    print("[PASS] BaseValidator imported successfully")


def test_default_schemas_import():
    """Test that default schemas can be imported."""
    from library.components.validation.spec_validation import (
        DEFAULT_CONTEXT_SCHEMA,
        DEFAULT_IMPLEMENTATION_PLAN_SCHEMA,
        DEFAULT_SPEC_REQUIRED_SECTIONS,
    )
    assert DEFAULT_CONTEXT_SCHEMA is not None
    assert DEFAULT_IMPLEMENTATION_PLAN_SCHEMA is not None
    assert DEFAULT_SPEC_REQUIRED_SECTIONS is not None
    print("[PASS] Default schemas imported successfully")


def test_utility_functions_import():
    """Test that utility functions can be imported."""
    from library.components.validation.spec_validation import (
        validate_spec_directory,
        create_validator_from_config,
    )
    assert validate_spec_directory is not None
    assert create_validator_from_config is not None
    print("[PASS] Utility functions imported successfully")


def test_parent_package_import():
    """Test that SpecValidator can be imported from parent validation package."""
    from library.components.validation import SpecValidator
    assert SpecValidator is not None
    print("[PASS] SpecValidator imported from parent package successfully")


def test_spec_validator_instantiation():
    """Test that SpecValidator can be instantiated with a temp directory."""
    import tempfile
    from library.components.validation.spec_validation import SpecValidator

    with tempfile.TemporaryDirectory() as tmpdir:
        validator = SpecValidator(spec_dir=tmpdir)
        assert validator is not None
        assert validator.spec_dir == Path(tmpdir)
        print("[PASS] SpecValidator instantiated successfully")


def test_validation_schema_usage():
    """Test that ValidationSchema works correctly."""
    from library.components.validation.spec_validation import ValidationSchema

    schema = ValidationSchema(
        required_fields=["name", "version"],
        optional_fields=["description"],
    )

    # Test valid data
    errors, warnings = schema.validate_data({"name": "test", "version": "1.0"})
    assert len(errors) == 0, f"Expected no errors, got: {errors}"

    # Test invalid data (missing required field)
    errors, warnings = schema.validate_data({"name": "test"})
    assert len(errors) == 1, f"Expected 1 error, got: {errors}"
    assert "version" in errors[0]

    print("[PASS] ValidationSchema usage test passed")


def test_spec_validation_result_creation():
    """Test that SpecValidationResult can be created and used."""
    from library.components.validation.spec_validation import SpecValidationResult

    result = SpecValidationResult(
        valid=True,
        checkpoint="test_checkpoint",
        errors=[],
        warnings=["minor warning"],
        fixes=[],
        metadata={"test": True},
    )

    assert result.valid is True
    assert result.checkpoint == "test_checkpoint"
    assert len(result.warnings) == 1
    assert bool(result) is True

    # Test to_dict and from_dict
    result_dict = result.to_dict()
    restored = SpecValidationResult.from_dict(result_dict)
    assert restored.valid == result.valid
    assert restored.checkpoint == result.checkpoint

    print("[PASS] SpecValidationResult creation test passed")


if __name__ == "__main__":
    print("Running spec_validation import tests...\n")

    test_spec_validation_import()
    test_spec_validation_result_import()
    test_validation_schema_import()
    test_base_validator_import()
    test_default_schemas_import()
    test_utility_functions_import()
    test_parent_package_import()
    test_spec_validator_instantiation()
    test_validation_schema_usage()
    test_spec_validation_result_creation()

    print("\n" + "=" * 50)
    print("All spec_validation import tests passed!")
    print("=" * 50)
