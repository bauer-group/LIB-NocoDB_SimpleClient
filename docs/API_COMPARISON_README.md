# NocoDB API v2 to v3 Comparison Documentation

This directory contains comprehensive analysis and migration guides for the NocoDB API v2 to v3 transition.

## 📚 Documentation Index

### 1. **Quick Start: Migration Guide** ⭐
**File:** [`API_V2_V3_MIGRATION_GUIDE.md`](./API_V2_V3_MIGRATION_GUIDE.md)

**Use this if you need:** Practical migration steps, code examples, and quick reference tables.

**Contents:**
- Critical breaking changes by priority
- Code migration examples for most-used endpoints
- Implementation strategies (adapter pattern, query parameter conversion)
- Base ID resolution strategies
- Testing checklist
- Common pitfalls and solutions
- Quick reference tables
- Timeline estimates and risk assessment

**Best for:** Developers actively migrating code from v2 to v3.

---

### 2. **Comprehensive Comparison Report**
**File:** [`NOCODB_API_V2_V3_COMPARISON.md`](./NOCODB_API_V2_V3_COMPARISON.md)

**Use this if you need:** Deep understanding of all architectural changes and endpoint differences.

**Contents:**
- Executive summary with statistics
- Major architectural changes explained
- Complete list of removed endpoints (137 from Meta API)
- Complete list of new endpoints (36 in Data API)
- Critical breaking changes tables
- Migration path analysis
- Detailed implementation strategy
- Version detection code
- Base ID resolver implementation

**Best for:** Architects planning the migration strategy and understanding scope.

---

### 3. **Schema & Parameter Analysis**
**File:** [`NOCODB_API_SCHEMA_COMPARISON.md`](./NOCODB_API_SCHEMA_COMPARISON.md)

**Use this if you need:** Detailed query parameter and response schema changes.

**Contents:**
- Query parameter comparison for list records
- Pagination changes (offset/limit → page/pageSize)
- Sort format changes (string → JSON)
- Response schema structures
- Error response format differences
- Field naming conventions

**Best for:** Developers implementing query parameter conversion and response parsing.

---

### 4. **Initial Comparison Report**
**File:** [`API_COMPARISON_V2_V3.md`](./API_COMPARISON_V2_V3.md)

**Use this if you need:** High-level overview and endpoint categorization.

**Contents:**
- Statistics (endpoints removed/added)
- Endpoints categorized by type (Table, Record, View, etc.)
- Basic breaking changes summary
- Simple implementation recommendations

**Best for:** Initial assessment and presenting to stakeholders.

---

## 🚀 Quick Navigation by Use Case

### "I need to understand what changed"
→ Start with [`NOCODB_API_V2_V3_COMPARISON.md`](./NOCODB_API_V2_V3_COMPARISON.md) (Section: Executive Summary)

### "I need to migrate record operations"
→ Go to [`API_V2_V3_MIGRATION_GUIDE.md`](./API_V2_V3_MIGRATION_GUIDE.md) (Section: Most Used Endpoints)

### "I need to understand pagination changes"
→ Go to [`NOCODB_API_SCHEMA_COMPARISON.md`](./NOCODB_API_SCHEMA_COMPARISON.md) (Section: List Records Query Parameters)

### "I need implementation code examples"
→ Go to [`API_V2_V3_MIGRATION_GUIDE.md`](./API_V2_V3_MIGRATION_GUIDE.md) (Section: Implementation Strategy)

### "I need to handle baseId resolution"
→ Go to [`API_V2_V3_MIGRATION_GUIDE.md`](./API_V2_V3_MIGRATION_GUIDE.md) (Section: Base ID Resolution)

### "I need a complete list of endpoint changes"
→ Go to [`NOCODB_API_V2_V3_COMPARISON.md`](./NOCODB_API_V2_V3_COMPARISON.md) (Sections: Removed/New Endpoints)

---

## ⚠️ Critical Findings Summary

### 1. API File Role Reversal
**v2 and v3 have INVERTED their API file definitions!**

- v2's "Meta API" (137 endpoints) = v3's "Data API" (36 endpoints)
- v2's "Data API" (10 endpoints) = v3's "Meta API" (10 endpoints)

This is NOT just naming - you must load the opposite file for equivalent operations.

### 2. Base ID Now Required
**100% of endpoints now require `baseId` in the path.**

```diff
- /api/v2/tables/{tableId}/records
+ /api/v3/data/{baseId}/{tableId}/records
```

### 3. Pagination Redesigned
**Complete breaking change in pagination.**

| v2 | v3 |
|----|-----|
| `offset=50&limit=25` | `page=3&pageSize=25` |

### 4. Sort Format Changed
**String format replaced with JSON.**

```diff
- sort=field1,-field2
+ sort=[{"direction":"asc","field":"field1"},{"direction":"desc","field":"field2"}]
```

### 5. Terminology Changes
- `columns` → `fields`
- `columnId` → `fieldId`
- `ne` operator → `neq` operator

---

## 📊 Statistics

| Metric | v2 | v3 | Change |
|--------|----|----|--------|
| **Meta API Endpoints** | 137 | 10 | -93% |
| **Data API Endpoints** | 10 | 36 | +260% |
| **Total Endpoints** | 147 | 46 | -69% |
| **Breaking Changes** | - | 147 | 100% |

---

## 🔍 Source OpenAPI Files

All analysis is based on these OpenAPI specification files:

- **v2 Meta API:** `docs/nocodb-openapi-meta.json` (137 endpoints)
- **v2 Data API:** `docs/nocodb-openapi-data.json` (10 endpoints)
- **v3 Meta API:** `docs/nocodb-openapi-meta-v3.json` (10 endpoints)
- **v3 Data API:** `docs/nocodb-openapi-data-v3.json` (36 endpoints)

---

## 🛠️ Analysis Scripts

The following Python scripts were used to generate these reports:

1. **`analyze_api_diff.py`** - Basic endpoint comparison
2. **`analyze_api_detailed.py`** - Comprehensive analysis with migration examples
3. **`analyze_schemas.py`** - Query parameter and schema analysis

---

## ⏱️ Estimated Migration Timeline

| Phase | Duration |
|-------|----------|
| Analysis & Planning | 1-2 weeks |
| Implementation | 2-3 weeks |
| Testing | 2 weeks |
| Deployment | 1 week |
| **Total** | **6-8 weeks** |

---

## 🎯 Recommended Reading Order

### For Developers:
1. [`API_V2_V3_MIGRATION_GUIDE.md`](./API_V2_V3_MIGRATION_GUIDE.md) - Start here
2. [`NOCODB_API_SCHEMA_COMPARISON.md`](./NOCODB_API_SCHEMA_COMPARISON.md) - For parameter details
3. [`NOCODB_API_V2_V3_COMPARISON.md`](./NOCODB_API_V2_V3_COMPARISON.md) - For complete reference

### For Architects:
1. [`NOCODB_API_V2_V3_COMPARISON.md`](./NOCODB_API_V2_V3_COMPARISON.md) - Start here
2. [`API_V2_V3_MIGRATION_GUIDE.md`](./API_V2_V3_MIGRATION_GUIDE.md) - For implementation strategy
3. [`API_COMPARISON_V2_V3.md`](./API_COMPARISON_V2_V3.md) - For stakeholder presentation

### For QA/Testing:
1. [`API_V2_V3_MIGRATION_GUIDE.md`](./API_V2_V3_MIGRATION_GUIDE.md) - Testing checklist section
2. [`NOCODB_API_SCHEMA_COMPARISON.md`](./NOCODB_API_SCHEMA_COMPARISON.md) - Parameter validation

---

## 📝 Document Versions

All documents were generated on: **2025-10-10**

Based on OpenAPI specifications from the `docs/` directory.

---

## 🤝 Contributing

If you find discrepancies or need additional analysis:
1. Check the source OpenAPI files first
2. Run the analysis scripts to regenerate reports
3. Submit findings with specific endpoint examples

---

## ⚖️ License

These documentation files are part of the NocoDB_SimpleClient project.

---

**Quick Links:**
- [Migration Guide](./API_V2_V3_MIGRATION_GUIDE.md) | [Full Comparison](./NOCODB_API_V2_V3_COMPARISON.md) | [Schema Analysis](./NOCODB_API_SCHEMA_COMPARISON.md)
