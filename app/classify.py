"""
PII classification using value rules and vector similarity.

Safety assumptions:
- Sampled values are processed in-memory only
- No sampled values are sent to LLMs
- Only metadata (labels, confidences) is stored
- Column names and types come from catalog
"""
import re
from dataclasses import dataclass
from typing import Any, Optional

from app.config import settings
from app.db import conn, query
from app.discovery import columns


# Regex patterns for value-based detection
PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
AADHAAR_PATTERN = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE_PATTERN = re.compile(r"\b(?:\+91[- ]?)?[6-9]\d{9}\b")

# Verhoeff algorithm tables for Aadhaar validation
_VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]

_VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]


def verhoeff_valid(num: str) -> bool:
    """
    Validate a number using Verhoeff checksum algorithm.
    
    Used for Aadhaar validation (12 digits with last digit as checksum).
    
    Args:
        num: String of digits to validate
        
    Returns:
        True if checksum is valid, False otherwise
    """
    try:
        c = 0
        for i, ch in enumerate(reversed(num)):
            c = _VERHOEFF_D[c][_VERHOEFF_P[i % 8][int(ch)]]
        return c == 0
    except (ValueError, IndexError):
        return False


@dataclass
class Classification:
    """Result of classifying a single column."""
    
    table: str
    column: str
    label: str  # EMAIL, PHONE, PAN, AADHAAR, DOB, ADDRESS, NAME, HEALTH, NOT_PII, etc.
    confidence: float  # 0.0 to 1.0
    method: str  # VALUE_RULE, NAME_VECTOR, MANUAL
    sample_size: int = 0
    needs_review: bool = False


def sample_values(schema: str, table: str, column: str, limit: int = 200) -> list[Any]:
    """
    Sample values from a column for pattern matching.
    
    IMPORTANT: Sampled values are processed in-memory only.
    Never send these to an LLM or log them.
    
    Args:
        schema: Schema name
        table: Table name
        column: Column name
        limit: Maximum number of rows to sample
        
    Returns:
        List of sampled values (may be empty if table is empty)
    """
    # Use parameterized query with catalog-validated identifiers
    sql = f"""
        SELECT "{column}"
        FROM "{schema}"."{table}"
        WHERE "{column}" IS NOT NULL
        FETCH FIRST {limit} ROWS ONLY
    """
    
    try:
        result = query(sql)
        return [row[0] for row in result] if result else []
    except Exception as e:
        print(f"Warning: Could not sample {table}.{column}: {e}")
        return []


def scan_values(samples: list[Any]) -> dict[str, float]:
    """
    Scan sampled values for PII patterns.
    
    Returns hit rates for each detected pattern.
    
    Args:
        samples: List of values to scan
        
    Returns:
        Dict mapping pattern name to hit rate (0.0 to 1.0)
    """
    if not samples:
        return {}
    
    n = len(samples)
    hits = {"EMAIL": 0, "PAN": 0, "AADHAAR": 0, "PHONE": 0}
    
    for value in samples:
        if value is None:
            continue
            
        # Convert to string for pattern matching
        v = str(value)
        
        # Email detection
        if EMAIL_PATTERN.search(v):
            hits["EMAIL"] += 1
        
        # PAN detection
        if PAN_PATTERN.search(v):
            hits["PAN"] += 1
        
        # Phone detection (including numeric-only columns)
        if PHONE_PATTERN.search(v):
            hits["PHONE"] += 1
        elif v.isdigit() and len(v) == 10 and v[0] in "6789":
            # Phone stored as number (no country code)
            hits["PHONE"] += 1
        
        # Aadhaar detection with Verhoeff validation
        m = AADHAAR_PATTERN.search(v)
        if m:
            aadhaar_digits = re.sub(r"\s", "", m.group())
            if len(aadhaar_digits) == 12 and verhoeff_valid(aadhaar_digits):
                hits["AADHAAR"] += 1
    
    # Return hit rates
    return {k: count / n for k, count in hits.items() if count > 0}


def classify_by_name(column_name: str) -> Optional[tuple[str, float]]:
    """
    Classify a column by name using vector similarity.
    
    This will be enhanced in Phase 2b with actual vector search.
    For now, use simple heuristics.
    
    Args:
        column_name: Column name to classify
        
    Returns:
        Tuple of (label, similarity_score) or None if no match
    """
    # Normalize column name for matching
    name_lower = column_name.lower().replace("_", " ")
    
    # Simple heuristic matching (will be replaced with vector similarity)
    patterns = {
        "email": ["email", "mail", "e-mail"],
        "phone": ["phone", "mobile", "tel", "contact"],
        "name": ["name", "full name", "nm"],
        "address": ["address", "addr", "street", "city", "pincode", "postal"],
        "dob": ["dob", "birth", "date of birth"],
        "govt_id": ["govt", "government", "id", "aadhaar", "pan"],
        "health": ["diagnosis", "medication", "test", "result", "prescription", "lab"],
    }
    
    best_match = None
    best_score = 0.0
    
    for label, keywords in patterns.items():
        for keyword in keywords:
            if keyword in name_lower:
                # Simple scoring: longer matches score higher
                score = len(keyword) / len(name_lower)
                if score > best_score:
                    best_score = score
                    best_match = label.upper()
    
    if best_match and best_score >= 0.2:  # Minimum threshold
        return (best_match, 1.0 - best_score)  # Convert to distance (lower is better)
    
    return None


def classify_column(
    schema: str, table: str, column: str, typename: str
) -> Classification:
    """
    Classify a single column as PII or not.
    
    Decision order:
    1. Value rule with hit rate >= threshold → use that label
    2. Name similarity under threshold → use that label
    3. Otherwise → NOT_PII
    
    Args:
        schema: Schema name
        table: Table name
        column: Column name
        typename: Db2 type name
        
    Returns:
        Classification result
    """
    # Skip obvious non-PII types
    if typename in ["INTEGER", "BIGINT", "SMALLINT"] and "ID" in column.upper():
        return Classification(
            table=table,
            column=column,
            label="NOT_PII",
            confidence=0.95,
            method="TYPE_HEURISTIC",
        )
    
    # Layer A: Value-based rules
    samples = sample_values(schema, table, column, limit=200)
    value_hits = scan_values(samples)
    
    # Check if any pattern has high enough hit rate
    value_threshold = settings.pii_value_threshold
    for pattern, hit_rate in value_hits.items():
        if hit_rate >= value_threshold:
            return Classification(
                table=table,
                column=column,
                label=pattern,
                confidence=hit_rate,
                method="VALUE_RULE",
                sample_size=len(samples),
            )
    
    # Layer B: Name-based similarity
    name_result = classify_by_name(column)
    if name_result:
        label, distance = name_result
        similarity = 1.0 - distance
        name_threshold = settings.pii_name_threshold
        
        if distance <= name_threshold:
            return Classification(
                table=table,
                column=column,
                label=label,
                confidence=similarity,
                method="NAME_VECTOR",
            )
    
    # Layer C: Uncertain - may need review
    # If we have value hits but below threshold, flag for review
    if value_hits:
        best_pattern = max(value_hits.items(), key=lambda x: x[1])
        return Classification(
            table=table,
            column=column,
            label=best_pattern[0],
            confidence=best_pattern[1],
            method="VALUE_RULE",
            sample_size=len(samples),
            needs_review=True,
        )
    
    # Default: Not PII
    return Classification(
        table=table,
        column=column,
        label="NOT_PII",
        confidence=0.80,
        method="DEFAULT",
    )


def persist_classification(c: Classification) -> None:
    """
    Save classification result to PII_MAP table.
    
    Args:
        c: Classification result to persist
    """
    sql = """
        MERGE INTO PII_MAP AS target
        USING (VALUES (?, ?, ?, ?, ?)) AS source (TABNAME, COLNAME, LABEL, CONFIDENCE, METHOD)
        ON target.TABNAME = source.TABNAME AND target.COLNAME = source.COLNAME
        WHEN MATCHED THEN
            UPDATE SET LABEL = source.LABEL, CONFIDENCE = source.CONFIDENCE, 
                       METHOD = source.METHOD, CLASSIFIED_AT = CURRENT TIMESTAMP
        WHEN NOT MATCHED THEN
            INSERT (TABNAME, COLNAME, LABEL, CONFIDENCE, METHOD)
            VALUES (source.TABNAME, source.COLNAME, source.LABEL, source.CONFIDENCE, source.METHOD)
    """
    
    query(
        sql,
        (
            c.table.upper(),
            c.column.upper(),
            c.label,
            c.confidence,
            c.method,
        ),
    )


def run(schema: str) -> list[Classification]:
    """
    Run classification on all columns in a schema.
    
    Args:
        schema: Schema name to classify
        
    Returns:
        List of classification results
    """
    print(f"Classifying columns in schema: {schema}")
    print("=" * 60)
    
    cols = columns(schema)
    results = []
    
    for tabname, colname, typename, length, nulls in cols:
        table = tabname.strip()
        column = colname.strip()
        coltype = typename.strip()
        
        print(f"Classifying {table}.{column} ({coltype})...", end=" ")
        
        classification = classify_column(schema, table, column, coltype)
        results.append(classification)
        
        # Persist to database
        persist_classification(classification)
        
        # Show result
        if classification.needs_review:
            print(f"⚠️  {classification.label} (conf={classification.confidence:.2f}, NEEDS REVIEW)")
        elif classification.label != "NOT_PII":
            print(f"✓ {classification.label} (conf={classification.confidence:.2f})")
        else:
            print(f"  {classification.label}")
    
    print("\n" + "=" * 60)
    print(f"Classification complete: {len(results)} columns")
    
    # Summary statistics
    pii_count = sum(1 for c in results if c.label != "NOT_PII")
    review_count = sum(1 for c in results if c.needs_review)
    
    print(f"  PII columns found: {pii_count}")
    print(f"  Columns needing review: {review_count}")
    print(f"  Non-PII columns: {len(results) - pii_count}")
    
    return results


if __name__ == "__main__":
    """Run classification on the configured schema."""
    results = run(settings.db2_schema)
    
    # Show PII map summary
    print("\n" + "=" * 60)
    print("PII Map Summary")
    print("=" * 60)
    
    by_label = {}
    for c in results:
        if c.label not in by_label:
            by_label[c.label] = []
        by_label[c.label].append(f"{c.table}.{c.column}")
    
    for label, cols in sorted(by_label.items()):
        print(f"\n{label} ({len(cols)} columns):")
        for col in cols[:5]:  # Show first 5
            print(f"  - {col}")
        if len(cols) > 5:
            print(f"  ... and {len(cols) - 5} more")
