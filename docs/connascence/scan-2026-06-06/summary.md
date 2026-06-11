# Connascence Scan Summary

- Project: `agentic-commerce-arc`
- Path: `D:\Projects\agentic-commerce-arc`
- Git branch: `main`
- Git commit: `cca999500ad5edc97dced30e2c7f7666dc41ed2b`
- Dirty before scan: `True`
- Scan succeeded: `True`
- Python files staged: `39`

## Commands Run
- `C:\Python312\python.exe -m analyzer C:\Users\17175\Desktop\_SCRATCH\connascence-portfolio-scan-2026-06-06\raw-results\agentic-commerce-arc\mirror --format json --output C:\Users\17175\Desktop\_SCRATCH\connascence-portfolio-scan-2026-06-06\raw-results\agentic-commerce-arc\connascence.raw.json --no-duplication --compliance-threshold 0 --max-god-objects 999999` (exit 0)
- `connascence_portfolio_runner.py generate-sarif-from-json D:\Projects\agentic-commerce-arc\docs\connascence\scan-2026-06-06\connascence.json` (exit 0)
- `C:\Python312\python.exe -m analyzer.ast_engine --path C:\Users\17175\Desktop\_SCRATCH\connascence-portfolio-scan-2026-06-06\raw-results\agentic-commerce-arc\mirror --analyzer god_object --output C:\Users\17175\Desktop\_SCRATCH\connascence-portfolio-scan-2026-06-06\raw-results\agentic-commerce-arc\god-object.raw.json` (exit 0)

## Counts By Severity

- low: 1691
- medium: 248
- high: 11
- critical: 7

## Counts By Type

- connascence_of_meaning: 1518
- CoV: 184
- connascence_of_type: 82
- connascence_of_convention: 81
- CoP: 42
- connascence_of_execution: 20
- connascence_of_algorithm: 17
- god_object: 5
- connascence_of_timing: 5
- CoA: 3

## Top Files

- `D:\Projects\agentic-commerce-arc\backend\agent.py`: 388
- `D:\Projects\agentic-commerce-arc\backend\library\components\validation\quality_validator\quality_validator.py`: 279
- `D:\Projects\agentic-commerce-arc\submission\create_pdf.py`: 183
- `D:\Projects\agentic-commerce-arc\backend\main.py`: 179
- `D:\Projects\agentic-commerce-arc\contracts\lib\forge-std\scripts\vm.py`: 127
- `D:\Projects\agentic-commerce-arc\contracts\lib\openzeppelin-contracts\lib\forge-std\scripts\vm.py`: 127
- `D:\Projects\agentic-commerce-arc\backend\blockchain.py`: 107
- `D:\Projects\agentic-commerce-arc\backend\tools\price_compare.py`: 97
- `D:\Projects\agentic-commerce-arc\lib\library\metric_collector\collector.py`: 97
- `D:\Projects\agentic-commerce-arc\backend\models\schemas.py`: 89

## Top 10 Actionable Findings

1. `D:\Projects\agentic-commerce-arc\contracts\lib\openzeppelin-contracts\lib\forge-std\scripts\vm.py:409` - Class 'CheatcodesPrinter' is a God Object (business_logic context): Method count (26) exceeds business_logic threshold (15); Business logic class violates Single Responsibility Principle
2. `D:\Projects\agentic-commerce-arc\contracts\lib\forge-std\scripts\vm.py:408` - Class 'CheatcodesPrinter' is a God Object (business_logic context): Method count (26) exceeds business_logic threshold (15); Business logic class violates Single Responsibility Principle
3. `D:\Projects\agentic-commerce-arc\backend\library\components\validation\spec_validation\spec_validation.py:930` - Class 'ImplementationPlanValidator' is a God Object (test context): Very low cohesion (0.29)
4. `D:\Projects\agentic-commerce-arc\backend\library\components\validation\quality_validator\quality_validator.py:297` - Class 'QualityValidator' is a God Object: 21 methods, ~565 lines
5. `D:\Projects\agentic-commerce-arc\backend\agent.py:137` - Class 'CommerceAgent' is a God Object (business_logic context): Lines of code (620) exceeds business_logic threshold (300); Low cohesion (0.12) in business logic class; Business logic class violates Single Responsibility Principle
6. `D:\Projects\agentic-commerce-arc\contracts\lib\openzeppelin-contracts\lib\forge-std\scripts\vm.py:426` - Function '__init__' has 11 positional parameters (threshold: 3)
7. `D:\Projects\agentic-commerce-arc\backend\library\components\validation\quality_validator\quality_validator.py:362` - Function 'add_violation' has 11 positional parameters (threshold: 3)
8. `D:\Projects\agentic-commerce-arc\backend\main.py:192` - Excessive global state coupling: 1 global assignments, 48 stateful variables
9. `D:\Projects\agentic-commerce-arc\backend\database.py:44` - Excessive global state coupling: 2 global assignments, 7 stateful variables
10. `D:\Projects\agentic-commerce-arc\backend\auth.py:266` - Excessive global state coupling: 1 global assignments, 21 stateful variables

## Tool Limitations

- Connascence currently analyzes Python files only; non-Python coupling is not covered.
- Source-bearing fields and literal values were stripped or redacted before writing artifacts.
- Excluded directories and sensitive data patterns were not staged into the scan mirror.

## Next Cleanup Recommendations

### 1. Quick Wins
- Add type annotations at public function boundaries with the highest CoT counts.
- Replace repeated or magic literals with named constants or configuration keys.

### 2. Medium Refactors
- Convert high-parameter functions to keyword-only APIs or parameter objects.
- Split complex functions and consolidate duplicated algorithmic branches.
- Start with the top files by violation count and keep each change behavior-preserving.

### 3. Large Architectural Work
- Split god objects into cohesive classes around stable domain responsibilities.
- Use module or service boundaries to isolate recurring high-count hotspots.
