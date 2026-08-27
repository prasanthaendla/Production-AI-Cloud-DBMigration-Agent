# AWS SCT Assessment Report (Sample) — Oracle to Aurora PostgreSQL

## Summary
Schema: HR_PROD | Objects analyzed: 47 | Automatic conversion: 68% | Manual action required: 32%

## High-Complexity Findings

### 1. Sequence-based ID generation (trg_emp_id, emp_seq)
Oracle uses SEQUENCE + TRIGGER to emulate auto-increment. PostgreSQL supports
native IDENTITY columns (GENERATED ALWAYS AS IDENTITY) or SERIAL types, which
are simpler and don't require a trigger. Recommended action: replace the
sequence+trigger pattern with a native PostgreSQL IDENTITY column during
migration, rather than porting the trigger as-is.

### 2. ROWNUM pagination (top_10_earners view)
ROWNUM is evaluated before ORDER BY in Oracle, which is a common source of bugs
even in the original Oracle code. PostgreSQL has no ROWNUM; use LIMIT/OFFSET
or window functions (ROW_NUMBER() OVER (...)) instead. Manual rewrite required.

### 3. PACKAGE / PACKAGE BODY (payroll_pkg)
PostgreSQL has no package concept. AWS SCT will split package functions/procedures
into standalone functions within a schema, using naming conventions (e.g.,
payroll_pkg_calculate_bonus) to preserve logical grouping. Manual review needed
to confirm no naming collisions across split objects.

### 4. Exception handling (NO_DATA_FOUND)
Oracle's NO_DATA_FOUND maps to PostgreSQL's NO_DATA_FOUND exception under
PL/pgSQL, so this construct converts automatically in most cases — flagged
here only for awareness, not action.

## Risk Rating
Overall migration risk for this schema: **Medium** — no unsupported data types,
but several constructs need manual rewrite rather than automatic conversion.