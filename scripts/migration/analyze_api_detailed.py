#!/usr/bin/env python3
"""
Enhanced comprehensive comparison of NocoDB API v2 vs v3.
Includes detailed schema analysis, migration paths, and code examples.
"""

import json
import re


def load_openapi(filepath: str) -> dict:
    """Load OpenAPI JSON file."""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def get_endpoints(openapi: dict) -> dict[str, dict]:
    """Extract all endpoints from OpenAPI spec."""
    endpoints = {}
    paths = openapi.get("paths", {})
    for path, methods in paths.items():
        for method, spec in methods.items():
            if method.lower() in ["get", "post", "put", "patch", "delete", "head", "options"]:
                key = f"{method.upper()} {path}"
                endpoints[key] = {
                    "path": path,
                    "method": method.upper(),
                    "spec": spec,
                    "summary": spec.get("summary", ""),
                    "description": spec.get("description", ""),
                    "operationId": spec.get("operationId", ""),
                    "tags": spec.get("tags", []),
                    "parameters": spec.get("parameters", []),
                    "requestBody": spec.get("requestBody", {}),
                    "responses": spec.get("responses", {}),
                    "security": spec.get("security", []),
                }
    return endpoints


def extract_path_params(path: str) -> list[str]:
    """Extract parameter names from path."""
    return re.findall(r"\{([^}]+)\}", path)


def find_path_mapping(v2_path: str, v3_endpoints: dict) -> list[str]:
    """Find potential v3 path mappings for a v2 path."""
    v2_params = extract_path_params(v2_path)
    v2_parts = [p for p in v2_path.split("/") if p and not p.startswith("{")]

    candidates = []
    for v3_key, v3_data in v3_endpoints.items():
        v3_path = v3_data["path"]
        v3_params = extract_path_params(v3_path)
        v3_parts = [p for p in v3_path.split("/") if p and not p.startswith("{")]

        # Check if similar structure
        if len(v2_params) == len(v3_params):
            common_parts = set(v2_parts) & set(v3_parts)
            if len(common_parts) >= min(len(v2_parts), len(v3_parts)) * 0.5:
                candidates.append(v3_key)

    return candidates


def analyze_migration_path(v2_endpoint: str, v2_data: dict, v3_endpoints: dict) -> dict:
    """Analyze migration path from v2 to v3."""
    method, path = v2_endpoint.split(" ", 1)

    # Try to find direct v3 equivalent
    v3_candidates = find_path_mapping(path, v3_endpoints)

    migration = {
        "v2_endpoint": v2_endpoint,
        "v2_summary": v2_data.get("summary", ""),
        "v3_candidates": [],
        "migration_complexity": "unknown",
        "recommendations": [],
    }

    for candidate in v3_candidates:
        cand_method, cand_path = candidate.split(" ", 1)
        if cand_method == method:
            migration["v3_candidates"].append(candidate)

    if not migration["v3_candidates"]:
        migration["migration_complexity"] = "high"
        migration["recommendations"].append(
            "No direct v3 equivalent found. May require restructured approach."
        )
    elif len(migration["v3_candidates"]) == 1:
        migration["migration_complexity"] = "low"
        migration["recommendations"].append("Direct 1:1 mapping available with path changes.")
    else:
        migration["migration_complexity"] = "medium"
        migration["recommendations"].append(
            "Multiple potential mappings. Requires careful analysis."
        )

    return migration


def generate_detailed_markdown(meta_analysis: dict, data_analysis: dict) -> str:
    """Generate comprehensive markdown with detailed analysis."""

    md = []
    md.append("# NocoDB API v2 to v3 Comprehensive Comparison Report")
    md.append("")
    md.append(
        f"**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    md.append("")
    md.append("## Table of Contents")
    md.append("")
    md.append("1. [Executive Summary](#executive-summary)")
    md.append("2. [Major Architectural Changes](#major-architectural-changes)")
    md.append("3. [Meta API Detailed Comparison](#meta-api-detailed-comparison)")
    md.append("4. [Data API Detailed Comparison](#data-api-detailed-comparison)")
    md.append("5. [Critical Breaking Changes](#critical-breaking-changes)")
    md.append("6. [Migration Path Analysis](#migration-path-analysis)")
    md.append("7. [Code Migration Examples](#code-migration-examples)")
    md.append("8. [Implementation Strategy](#implementation-strategy)")
    md.append("")

    # Executive Summary
    md.append("## Executive Summary")
    md.append("")
    md.append("### Overview")
    md.append("")
    md.append("NocoDB API v3 represents a **major architectural overhaul** compared to v2:")
    md.append("")
    md.append("- **Meta API**: Dramatically simplified from 137 endpoints to 10 endpoints")
    md.append(
        "- **Data API**: Expanded from 10 endpoints to 36 endpoints with more granular operations"
    )
    md.append("- **Path Structure**: Complete restructuring - v2 paths do NOT directly map to v3")
    md.append("- **Terminology**: 'columns' → 'fields', simplified resource hierarchy")
    md.append("")

    meta_stats = {
        "removed": len(meta_analysis["comparison"]["removed"]),
        "new": len(meta_analysis["comparison"]["new"]),
    }

    data_stats = {
        "removed": len(data_analysis["comparison"]["removed"]),
        "new": len(data_analysis["comparison"]["new"]),
    }

    md.append("### Quick Stats")
    md.append("")
    md.append("| API | v2 Endpoints | v3 Endpoints | Removed | New | Change |")
    md.append("|-----|--------------|--------------|---------|-----|--------|")
    md.append(f"| **Meta API** | 137 | 10 | {meta_stats['removed']} | {meta_stats['new']} | -93% |")
    md.append(f"| **Data API** | 10 | 36 | {data_stats['removed']} | {data_stats['new']} | +260% |")
    md.append("")

    # Major Architectural Changes
    md.append("---")
    md.append("")
    md.append("## Major Architectural Changes")
    md.append("")
    md.append("### API Split Strategy")
    md.append("")
    md.append("v3 introduces a clear separation of concerns:")
    md.append("")
    md.append("#### v2 Architecture")
    md.append("```")
    md.append("Meta API (nocodb-openapi-meta.json):")
    md.append("  ├─ Authentication endpoints")
    md.append("  ├─ Base/Workspace management")
    md.append("  ├─ Table schema operations")
    md.append("  ├─ Column operations")
    md.append("  ├─ View operations")
    md.append("  ├─ Filter/Sort operations")
    md.append("  ├─ Webhook operations")
    md.append("  └─ Misc utilities")
    md.append("")
    md.append("Data API (nocodb-openapi-data.json):")
    md.append("  ├─ Record CRUD (10 endpoints)")
    md.append("  └─ File upload")
    md.append("```")
    md.append("")
    md.append("#### v3 Architecture")
    md.append("```")
    md.append("Meta API (nocodb-openapi-meta-v3.json):")
    md.append("  └─ Data operations ONLY (10 endpoints)")
    md.append("      ├─ Record CRUD")
    md.append("      ├─ Link operations")
    md.append("      └─ File upload")
    md.append("")
    md.append("Data API (nocodb-openapi-data-v3.json):")
    md.append("  └─ Meta operations ONLY (36 endpoints)")
    md.append("      ├─ Base management")
    md.append("      ├─ Table schema")
    md.append("      ├─ Field operations (columns)")
    md.append("      ├─ View operations")
    md.append("      └─ Member management")
    md.append("```")
    md.append("")
    md.append("**KEY INSIGHT: v2 and v3 have INVERTED their API definitions!**")
    md.append("")
    md.append("- v2's 'Meta API' = v3's 'Data API' (schema/structure)")
    md.append("- v2's 'Data API' = v3's 'Meta API' (records/content)")
    md.append("")

    # Path Structure Changes
    md.append("### Path Structure Changes")
    md.append("")
    md.append("#### v2 Path Patterns")
    md.append("```")
    md.append("Authentication:     /api/v2/auth/{operation}")
    md.append("Meta Operations:    /api/v2/meta/{resource}/{id}")
    md.append("Data Operations:    /api/v2/tables/{tableId}/records")
    md.append("Column Operations:  /api/v2/meta/columns/{columnId}")
    md.append("View Operations:    /api/v2/meta/views/{viewId}")
    md.append("```")
    md.append("")
    md.append("#### v3 Path Patterns")
    md.append("```")
    md.append("Meta (Structure):   /api/v3/meta/bases/{baseId}/{resource}")
    md.append("Data (Records):     /api/v3/data/{baseId}/{tableId}/records")
    md.append("Field Operations:   /api/v3/meta/bases/{baseId}/fields/{fieldId}")
    md.append("View Operations:    /api/v3/meta/bases/{baseId}/views/{viewId}")
    md.append("Link Operations:    /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}")
    md.append("```")
    md.append("")
    md.append("**KEY CHANGES:**")
    md.append("")
    md.append("1. **baseId is now required** in all paths (was optional/implicit in v2)")
    md.append("2. **Resource hierarchy** is more explicit: `/bases/{baseId}/tables/{tableId}/...`")
    md.append("3. **Terminology change**: `columns` → `fields`")
    md.append(
        "4. **Authentication endpoints removed** from OpenAPI specs (likely moved to separate service)"
    )
    md.append("")

    # Critical Breaking Changes
    md.append("---")
    md.append("")
    md.append("## Critical Breaking Changes")
    md.append("")
    md.append("### 🔴 HIGH PRIORITY: Record Operations")
    md.append("")
    md.append("**Most frequently used endpoints - requires immediate attention**")
    md.append("")
    md.append("| Operation | v2 Endpoint | v3 Endpoint | Breaking Change |")
    md.append("|-----------|-------------|-------------|-----------------|")
    md.append(
        "| List Records | `GET /api/v2/tables/{tableId}/records` | `GET /api/v3/data/{baseId}/{tableId}/records` | **baseId required** |"
    )
    md.append(
        "| Get Record | `GET /api/v2/tables/{tableId}/records/{recordId}` | `GET /api/v3/data/{baseId}/{tableId}/records/{recordId}` | **baseId required** |"
    )
    md.append(
        "| Create Records | `POST /api/v2/tables/{tableId}/records` | `POST /api/v3/data/{baseId}/{tableId}/records` | **baseId required** |"
    )
    md.append(
        "| Update Records | `PATCH /api/v2/tables/{tableId}/records` | `PATCH /api/v3/data/{baseId}/{tableId}/records` | **baseId required** |"
    )
    md.append(
        "| Delete Records | `DELETE /api/v2/tables/{tableId}/records` | `DELETE /api/v3/data/{baseId}/{tableId}/records` | **baseId required** |"
    )
    md.append(
        "| Count Records | `GET /api/v2/tables/{tableId}/records/count` | `GET /api/v3/data/{baseId}/{tableId}/count` | **path change + baseId** |"
    )
    md.append("")

    md.append("### 🟡 MEDIUM PRIORITY: Table & Schema Operations")
    md.append("")
    md.append("| Operation | v2 Endpoint | v3 Endpoint | Breaking Change |")
    md.append("|-----------|-------------|-------------|-----------------|")
    md.append(
        "| List Tables | `GET /api/v2/meta/bases/{baseId}/tables` | `GET /api/v3/meta/bases/{baseId}/tables` | **API file swap** |"
    )
    md.append(
        "| Get Table | `GET /api/v2/meta/tables/{tableId}` | `GET /api/v3/meta/bases/{baseId}/tables/{tableId}` | **baseId required in path** |"
    )
    md.append(
        "| Create Table | `POST /api/v2/meta/bases/{baseId}/tables` | `POST /api/v3/meta/bases/{baseId}/tables` | **API file swap** |"
    )
    md.append(
        "| Update Table | `PATCH /api/v2/meta/tables/{tableId}` | `PATCH /api/v3/meta/bases/{baseId}/tables/{tableId}` | **baseId required in path** |"
    )
    md.append(
        "| Delete Table | `DELETE /api/v2/meta/tables/{tableId}` | `DELETE /api/v3/meta/bases/{baseId}/tables/{tableId}` | **baseId required in path** |"
    )
    md.append("")

    md.append("### 🔵 LOW PRIORITY: Column/Field Operations")
    md.append("")
    md.append("| Operation | v2 Endpoint | v3 Endpoint | Breaking Change |")
    md.append("|-----------|-------------|-------------|-----------------|")
    md.append(
        "| Get Column | `GET /api/v2/meta/columns/{columnId}` | `GET /api/v3/meta/bases/{baseId}/fields/{fieldId}` | **terminology + path change** |"
    )
    md.append(
        "| Update Column | `PATCH /api/v2/meta/columns/{columnId}` | `PATCH /api/v3/meta/bases/{baseId}/fields/{fieldId}` | **terminology + path change** |"
    )
    md.append(
        "| Delete Column | `DELETE /api/v2/meta/columns/{columnId}` | `DELETE /api/v3/meta/bases/{baseId}/fields/{fieldId}` | **terminology + path change** |"
    )
    md.append(
        "| Create Column | `POST /api/v2/meta/tables/{tableId}/columns` | `POST /api/v3/meta/bases/{baseId}/tables/{tableId}/fields` | **terminology + baseId** |"
    )
    md.append("")

    md.append("### 🟣 CRITICAL: Link/Relation Operations")
    md.append("")
    md.append("| Operation | v2 Endpoint | v3 Endpoint | Breaking Change |")
    md.append("|-----------|-------------|-------------|-----------------|")
    md.append(
        "| List Links | `GET /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | `GET /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | **complete restructure** |"
    )
    md.append(
        "| Link Records | `POST /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | `POST /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | **complete restructure** |"
    )
    md.append(
        "| Unlink Records | `DELETE /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | `DELETE /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | **complete restructure** |"
    )
    md.append("")

    md.append("### 🔴 REMOVED: Authentication Endpoints")
    md.append("")
    md.append("These endpoints are completely removed from v3 OpenAPI specs:")
    md.append("")
    md.append("- `POST /api/v2/auth/user/signin`")
    md.append("- `POST /api/v2/auth/user/signup`")
    md.append("- `POST /api/v2/auth/user/signout`")
    md.append("- `GET /api/v2/auth/user/me`")
    md.append("- `POST /api/v2/auth/token/refresh`")
    md.append("- `POST /api/v2/auth/password/forgot`")
    md.append("- `POST /api/v2/auth/password/reset/{token}`")
    md.append("- `POST /api/v2/auth/password/change`")
    md.append("")
    md.append(
        "**Note:** These may still exist but are not documented in the provided v3 OpenAPI specs."
    )
    md.append("")

    # Migration Path Analysis
    md.append("---")
    md.append("")
    md.append("## Migration Path Analysis")
    md.append("")
    md.append("### Phase 1: Base ID Resolution")
    md.append("")
    md.append("The biggest structural change is that **baseId is required in all v3 paths**.")
    md.append("")
    md.append(
        "**Challenge:** v2 code often uses just `tableId` without explicitly tracking `baseId`."
    )
    md.append("")
    md.append("**Solutions:**")
    md.append("")
    md.append("1. **Cache baseId with tableId** when fetching table metadata")
    md.append("2. **Fetch baseId on demand** if not cached")
    md.append("3. **Require baseId** as a parameter in all client methods")
    md.append("")

    md.append("### Phase 2: Endpoint Mapping")
    md.append("")
    md.append("Create adapter layer to map v2 calls to v3:")
    md.append("")
    md.append("```typescript")
    md.append("interface EndpointMapper {")
    md.append("  mapRecordsList(tableId: string): {")
    md.append("    v2: string;  // '/api/v2/tables/{tableId}/records'")
    md.append("    v3: string;  // '/api/v3/data/{baseId}/{tableId}/records'")
    md.append("  };")
    md.append("}")
    md.append("```")
    md.append("")

    md.append("### Phase 3: Response Schema Adaptation")
    md.append("")
    md.append("Response structures may have changed. Need to analyze:")
    md.append("")
    md.append("- Field naming conventions")
    md.append("- Nested object structures")
    md.append("- Pagination formats")
    md.append("- Error response formats")
    md.append("")

    # Code Migration Examples
    md.append("---")
    md.append("")
    md.append("## Code Migration Examples")
    md.append("")

    md.append("### Example 1: List Records")
    md.append("")
    md.append("**v2 Code:**")
    md.append("```typescript")
    md.append("async function getRecords(tableId: string, params?: QueryParams) {")
    md.append("  const response = await fetch(")
    md.append("    `${baseUrl}/api/v2/tables/${tableId}/records?${queryString}`,")
    md.append("    { headers: { 'xc-token': token } }")
    md.append("  );")
    md.append("  return response.json();")
    md.append("}")
    md.append("```")
    md.append("")
    md.append("**v3 Code:**")
    md.append("```typescript")
    md.append("async function getRecords(")
    md.append("  baseId: string,  // ← NEW: baseId required")
    md.append("  tableId: string,")
    md.append("  params?: QueryParams")
    md.append(") {")
    md.append("  const response = await fetch(")
    md.append("    `${baseUrl}/api/v3/data/${baseId}/${tableId}/records?${queryString}`,")
    md.append("    { headers: { 'xc-token': token } }")
    md.append("  );")
    md.append("  return response.json();")
    md.append("}")
    md.append("```")
    md.append("")

    md.append("### Example 2: Create Record")
    md.append("")
    md.append("**v2 Code:**")
    md.append("```typescript")
    md.append("async function createRecord(tableId: string, data: Record<string, any>) {")
    md.append("  const response = await fetch(")
    md.append("    `${baseUrl}/api/v2/tables/${tableId}/records`,")
    md.append("    {")
    md.append("      method: 'POST',")
    md.append("      headers: {")
    md.append("        'xc-token': token,")
    md.append("        'Content-Type': 'application/json'")
    md.append("      },")
    md.append("      body: JSON.stringify(data)")
    md.append("    }")
    md.append("  );")
    md.append("  return response.json();")
    md.append("}")
    md.append("```")
    md.append("")
    md.append("**v3 Code:**")
    md.append("```typescript")
    md.append("async function createRecord(")
    md.append("  baseId: string,  // ← NEW: baseId required")
    md.append("  tableId: string,")
    md.append("  data: Record<string, any>")
    md.append(") {")
    md.append("  const response = await fetch(")
    md.append("    `${baseUrl}/api/v3/data/${baseId}/${tableId}/records`,")
    md.append("    {")
    md.append("      method: 'POST',")
    md.append("      headers: {")
    md.append("        'xc-token': token,")
    md.append("        'Content-Type': 'application/json'")
    md.append("      },")
    md.append("      body: JSON.stringify(data)")
    md.append("    }")
    md.append("  );")
    md.append("  return response.json();")
    md.append("}")
    md.append("```")
    md.append("")

    md.append("### Example 3: Get Table Schema")
    md.append("")
    md.append("**v2 Code:**")
    md.append("```typescript")
    md.append("async function getTable(tableId: string) {")
    md.append("  const response = await fetch(")
    md.append("    `${baseUrl}/api/v2/meta/tables/${tableId}`,")
    md.append("    { headers: { 'xc-token': token } }")
    md.append("  );")
    md.append("  return response.json();")
    md.append("}")
    md.append("```")
    md.append("")
    md.append("**v3 Code:**")
    md.append("```typescript")
    md.append("async function getTable(baseId: string, tableId: string) {")
    md.append("  const response = await fetch(")
    md.append("    // NOTE: This is in the 'Data API' file in v3, not 'Meta API'")
    md.append("    `${baseUrl}/api/v3/meta/bases/${baseId}/tables/${tableId}`,")
    md.append("    { headers: { 'xc-token': token } }")
    md.append("  );")
    md.append("  return response.json();")
    md.append("}")
    md.append("```")
    md.append("")

    md.append("### Example 4: Link Records")
    md.append("")
    md.append("**v2 Code:**")
    md.append("```typescript")
    md.append("async function linkRecords(")
    md.append("  tableId: string,")
    md.append("  linkFieldId: string,")
    md.append("  recordId: string,")
    md.append("  linkedRecordIds: string[]")
    md.append(") {")
    md.append("  const response = await fetch(")
    md.append("    `${baseUrl}/api/v2/tables/${tableId}/links/${linkFieldId}/records/${recordId}`,")
    md.append("    {")
    md.append("      method: 'POST',")
    md.append("      headers: {")
    md.append("        'xc-token': token,")
    md.append("        'Content-Type': 'application/json'")
    md.append("      },")
    md.append("      body: JSON.stringify({ linkedRecordIds })")
    md.append("    }")
    md.append("  );")
    md.append("  return response.json();")
    md.append("}")
    md.append("```")
    md.append("")
    md.append("**v3 Code:**")
    md.append("```typescript")
    md.append("async function linkRecords(")
    md.append("  baseId: string,  // ← NEW: baseId required")
    md.append("  tableId: string,")
    md.append("  linkFieldId: string,")
    md.append("  recordId: string,")
    md.append("  linkedRecordIds: string[]")
    md.append(") {")
    md.append("  const response = await fetch(")
    md.append("    `${baseUrl}/api/v3/data/${baseId}/${tableId}/links/${linkFieldId}/${recordId}`,")
    md.append("    {")
    md.append("      method: 'POST',")
    md.append("      headers: {")
    md.append("        'xc-token': token,")
    md.append("        'Content-Type': 'application/json'")
    md.append("      },")
    md.append("      body: JSON.stringify({ linkedRecordIds })")
    md.append("    }")
    md.append("  );")
    md.append("  return response.json();")
    md.append("}")
    md.append("```")
    md.append("")

    # Implementation Strategy
    md.append("---")
    md.append("")
    md.append("## Implementation Strategy")
    md.append("")

    md.append("### 1. Dual-Version Support Architecture")
    md.append("")
    md.append("**Recommended Approach:** Adapter Pattern with Version Detection")
    md.append("")
    md.append("```typescript")
    md.append("// Core interface that both versions implement")
    md.append("interface NocoDBClient {")
    md.append("  // Record operations")
    md.append("  getRecords(tableId: string, params?: RecordQueryParams): Promise<RecordList>;")
    md.append("  getRecord(tableId: string, recordId: string): Promise<Record>;")
    md.append("  createRecords(tableId: string, records: RecordData[]): Promise<Record[]>;")
    md.append("  updateRecords(tableId: string, records: RecordUpdate[]): Promise<Record[]>;")
    md.append("  deleteRecords(tableId: string, recordIds: string[]): Promise<void>;")
    md.append("  ")
    md.append("  // Table operations")
    md.append("  getTables(baseId: string): Promise<Table[]>;")
    md.append("  getTable(tableId: string): Promise<Table>;")
    md.append("  ")
    md.append("  // Link operations")
    md.append(
        "  linkRecords(tableId: string, linkFieldId: string, recordId: string, linkedIds: string[]): Promise<void>;"
    )
    md.append(
        "  unlinkRecords(tableId: string, linkFieldId: string, recordId: string, linkedIds: string[]): Promise<void>;"
    )
    md.append("}")
    md.append("")
    md.append("// Version-specific implementations")
    md.append("class NocoDBClientV2 implements NocoDBClient {")
    md.append("  // Implements v2 API paths")
    md.append("}")
    md.append("")
    md.append("class NocoDBClientV3 implements NocoDBClient {")
    md.append("  // Implements v3 API paths")
    md.append("  // Requires baseId for all operations")
    md.append("}")
    md.append("")
    md.append("// Factory with auto-detection")
    md.append("async function createNocoDBClient(config: ClientConfig): Promise<NocoDBClient> {")
    md.append("  const version = await detectApiVersion(config.baseUrl, config.token);")
    md.append("  return version === 'v3' ")
    md.append("    ? new NocoDBClientV3(config)")
    md.append("    : new NocoDBClientV2(config);")
    md.append("}")
    md.append("```")
    md.append("")

    md.append("### 2. Version Detection Strategy")
    md.append("")
    md.append("```typescript")
    md.append("async function detectApiVersion(")
    md.append("  baseUrl: string,")
    md.append("  token: string")
    md.append("): Promise<'v2' | 'v3'> {")
    md.append("  // Option 1: Check for v3-specific endpoint")
    md.append("  try {")
    md.append("    const response = await fetch(")
    md.append("      `${baseUrl}/api/v3/meta/workspaces/`,")
    md.append("      { headers: { 'xc-token': token } }")
    md.append("    );")
    md.append("    if (response.ok) return 'v3';")
    md.append("  } catch (error) {")
    md.append("    // v3 endpoint doesn't exist")
    md.append("  }")
    md.append("  ")
    md.append("  // Option 2: Check /api/v2/meta/nocodb/info for version")
    md.append("  try {")
    md.append("    const response = await fetch(")
    md.append("      `${baseUrl}/api/v2/meta/nocodb/info`,")
    md.append("      { headers: { 'xc-token': token } }")
    md.append("    );")
    md.append("    if (response.ok) {")
    md.append("      const info = await response.json();")
    md.append("      // Parse version string to determine API version")
    md.append("      return info.version?.startsWith('3.') ? 'v3' : 'v2';")
    md.append("    }")
    md.append("  } catch (error) {")
    md.append("    // Fallback to v2")
    md.append("  }")
    md.append("  ")
    md.append("  // Default to v2 for backward compatibility")
    md.append("  return 'v2';")
    md.append("}")
    md.append("```")
    md.append("")

    md.append("### 3. Base ID Resolution Strategy")
    md.append("")
    md.append("Since v3 requires baseId everywhere, implement a resolution mechanism:")
    md.append("")
    md.append("```typescript")
    md.append("class BaseIdResolver {")
    md.append("  private cache = new Map<string, string>();  // tableId -> baseId")
    md.append("  ")
    md.append("  async getBaseIdForTable(tableId: string): Promise<string> {")
    md.append("    // Check cache first")
    md.append("    if (this.cache.has(tableId)) {")
    md.append("      return this.cache.get(tableId)!;")
    md.append("    }")
    md.append("    ")
    md.append("    // Fetch all bases and tables to build mapping")
    md.append("    const workspaces = await this.listWorkspaces();")
    md.append("    for (const workspace of workspaces) {")
    md.append("      const bases = await this.listBases(workspace.id);")
    md.append("      for (const base of bases) {")
    md.append("        const tables = await this.listTables(base.id);")
    md.append("        for (const table of tables) {")
    md.append("          this.cache.set(table.id, base.id);")
    md.append("        }")
    md.append("      }")
    md.append("    }")
    md.append("    ")
    md.append("    const baseId = this.cache.get(tableId);")
    md.append("    if (!baseId) {")
    md.append("      throw new Error(`Could not resolve baseId for tableId: ${tableId}`);")
    md.append("    }")
    md.append("    return baseId;")
    md.append("  }")
    md.append("  ")
    md.append("  // Proactively cache when fetching table metadata")
    md.append("  cacheTableBase(tableId: string, baseId: string) {")
    md.append("    this.cache.set(tableId, baseId);")
    md.append("  }")
    md.append("}")
    md.append("```")
    md.append("")

    md.append("### 4. Migration Checklist")
    md.append("")
    md.append("#### Phase 1: Foundation (Week 1)")
    md.append("- [ ] Create unified client interface")
    md.append("- [ ] Implement version detection")
    md.append("- [ ] Set up base ID resolver")
    md.append("- [ ] Create v2 adapter implementation")
    md.append("- [ ] Write comprehensive tests")
    md.append("")
    md.append("#### Phase 2: v3 Implementation (Week 2-3)")
    md.append("- [ ] Implement v3 adapter for record operations")
    md.append("- [ ] Implement v3 adapter for table operations")
    md.append("- [ ] Implement v3 adapter for link operations")
    md.append("- [ ] Implement v3 adapter for view operations")
    md.append("- [ ] Handle terminology changes (column → field)")
    md.append("")
    md.append("#### Phase 3: Testing (Week 4)")
    md.append("- [ ] Integration tests against v2 server")
    md.append("- [ ] Integration tests against v3 server")
    md.append("- [ ] Performance benchmarks")
    md.append("- [ ] Error handling verification")
    md.append("")
    md.append("#### Phase 4: Deployment (Week 5)")
    md.append("- [ ] Feature flag for v3 support")
    md.append("- [ ] Gradual rollout strategy")
    md.append("- [ ] Monitoring and alerting")
    md.append("- [ ] Documentation updates")
    md.append("")

    md.append("### 5. Backward Compatibility Strategy")
    md.append("")
    md.append("```typescript")
    md.append("interface ClientConfig {")
    md.append("  baseUrl: string;")
    md.append("  token: string;")
    md.append("  apiVersion?: 'v2' | 'v3' | 'auto';  // Default: 'auto'")
    md.append("  baseId?: string;  // Optional for v2, required for v3 if not using resolver")
    md.append("}")
    md.append("")
    md.append("class NocoDBClientV3 implements NocoDBClient {")
    md.append("  private baseIdResolver: BaseIdResolver;")
    md.append("  ")
    md.append("  async getRecords(tableId: string, params?: RecordQueryParams) {")
    md.append("    // Auto-resolve baseId if not provided")
    md.append("    const baseId = this.config.baseId || ")
    md.append("      await this.baseIdResolver.getBaseIdForTable(tableId);")
    md.append("    ")
    md.append("    return this.fetchRecords(baseId, tableId, params);")
    md.append("  }")
    md.append("}")
    md.append("```")
    md.append("")

    md.append("### 6. Key Considerations")
    md.append("")
    md.append("1. **Performance Impact**")
    md.append("   - Base ID resolution adds overhead if not cached")
    md.append("   - Consider proactive caching during initialization")
    md.append("")
    md.append("2. **Error Handling**")
    md.append("   - v3 may return different error structures")
    md.append("   - Normalize errors in adapter layer")
    md.append("")
    md.append("3. **Rate Limiting**")
    md.append("   - Check if v3 has different rate limits")
    md.append("   - Implement appropriate retry logic")
    md.append("")
    md.append("4. **Authentication**")
    md.append("   - v3 auth endpoints not in OpenAPI spec")
    md.append("   - Verify auth token format compatibility")
    md.append("")
    md.append("5. **Query Parameters**")
    md.append("   - Validate that filter/sort syntax is compatible")
    md.append("   - Check pagination format (offset/limit vs cursor-based)")
    md.append("")

    md.append("---")
    md.append("")
    md.append("## Detailed Endpoint Mappings")
    md.append("")

    # Generate detailed mapping tables
    md.extend(generate_mapping_tables())

    md.append("---")
    md.append("")
    md.append("## Conclusion")
    md.append("")
    md.append("The v2 to v3 migration represents a **major breaking change** that requires:")
    md.append("")
    md.append("1. **Architectural refactoring** - Not just path changes, but structural changes")
    md.append("2. **Base ID management** - New requirement for all operations")
    md.append("3. **API file swap** - Meta/Data definitions inverted")
    md.append("4. **Terminology updates** - columns → fields")
    md.append("5. **Comprehensive testing** - All endpoints need verification")
    md.append("")
    md.append("**Recommended Timeline:** 4-6 weeks for full implementation and testing")
    md.append("")
    md.append("**Risk Level:** HIGH - This is not a simple version bump")
    md.append("")

    return "\n".join(md)


def generate_mapping_tables() -> list[str]:
    """Generate detailed mapping tables."""
    md = []

    md.append("### Record Operations Mapping")
    md.append("")
    md.append("| Operation | v2 Path | v3 Path | Notes |")
    md.append("|-----------|---------|---------|-------|")
    md.append(
        "| List | `/api/v2/tables/{tableId}/records` | `/api/v3/data/{baseId}/{tableId}/records` | Add baseId param |"
    )
    md.append(
        "| Get | `/api/v2/tables/{tableId}/records/{recordId}` | `/api/v3/data/{baseId}/{tableId}/records/{recordId}` | Add baseId param |"
    )
    md.append(
        "| Create | `/api/v2/tables/{tableId}/records` | `/api/v3/data/{baseId}/{tableId}/records` | Add baseId param |"
    )
    md.append(
        "| Update | `/api/v2/tables/{tableId}/records` | `/api/v3/data/{baseId}/{tableId}/records` | Add baseId param |"
    )
    md.append(
        "| Delete | `/api/v2/tables/{tableId}/records` | `/api/v3/data/{baseId}/{tableId}/records` | Add baseId param |"
    )
    md.append(
        "| Count | `/api/v2/tables/{tableId}/records/count` | `/api/v3/data/{baseId}/{tableId}/count` | Path structure changed |"
    )
    md.append("")

    md.append("### Table Operations Mapping")
    md.append("")
    md.append("| Operation | v2 Path | v3 Path | Notes |")
    md.append("|-----------|---------|---------|-------|")
    md.append(
        "| List | `/api/v2/meta/bases/{baseId}/tables` | `/api/v3/meta/bases/{baseId}/tables` | Now in 'Data API' spec |"
    )
    md.append(
        "| Get | `/api/v2/meta/tables/{tableId}` | `/api/v3/meta/bases/{baseId}/tables/{tableId}` | Add baseId to path |"
    )
    md.append(
        "| Create | `/api/v2/meta/bases/{baseId}/tables` | `/api/v3/meta/bases/{baseId}/tables` | Now in 'Data API' spec |"
    )
    md.append(
        "| Update | `/api/v2/meta/tables/{tableId}` | `/api/v3/meta/bases/{baseId}/tables/{tableId}` | Add baseId to path |"
    )
    md.append(
        "| Delete | `/api/v2/meta/tables/{tableId}` | `/api/v3/meta/bases/{baseId}/tables/{tableId}` | Add baseId to path |"
    )
    md.append("")

    md.append("### View Operations Mapping")
    md.append("")
    md.append("| Operation | v2 Path | v3 Path | Notes |")
    md.append("|-----------|---------|---------|-------|")
    md.append(
        "| List | `/api/v2/meta/tables/{tableId}/views` | `/api/v3/meta/bases/{baseId}/tables/{tableId}/views` | Add baseId to path |"
    )
    md.append(
        "| Get | `/api/v2/meta/views/{viewId}` (implicit) | `/api/v3/meta/bases/{baseId}/views/{viewId}` | Add baseId to path |"
    )
    md.append(
        "| Create | `/api/v2/meta/tables/{tableId}/grids` (etc) | `/api/v3/meta/bases/{baseId}/tables/{tableId}/views` | Unified view creation |"
    )
    md.append(
        "| Update | `/api/v2/meta/views/{viewId}` | `/api/v3/meta/bases/{baseId}/views/{viewId}` | Add baseId to path |"
    )
    md.append(
        "| Delete | `/api/v2/meta/views/{viewId}` | `/api/v3/meta/bases/{baseId}/views/{viewId}` | Add baseId to path |"
    )
    md.append(
        "| Filters | `/api/v2/meta/views/{viewId}/filters` | `/api/v3/meta/bases/{baseId}/views/{viewId}/filters` | Add baseId to path |"
    )
    md.append(
        "| Sorts | `/api/v2/meta/views/{viewId}/sorts` | `/api/v3/meta/bases/{baseId}/views/{viewId}/sorts` | Add baseId to path |"
    )
    md.append("")

    md.append("### Field/Column Operations Mapping")
    md.append("")
    md.append("| Operation | v2 Path | v3 Path | Notes |")
    md.append("|-----------|---------|---------|-------|")
    md.append(
        "| Get | `/api/v2/meta/columns/{columnId}` | `/api/v3/meta/bases/{baseId}/fields/{fieldId}` | Terminology change + baseId |"
    )
    md.append(
        "| Create | `/api/v2/meta/tables/{tableId}/columns` | `/api/v3/meta/bases/{baseId}/tables/{tableId}/fields` | Terminology change + baseId |"
    )
    md.append(
        "| Update | `/api/v2/meta/columns/{columnId}` | `/api/v3/meta/bases/{baseId}/fields/{fieldId}` | Terminology change + baseId |"
    )
    md.append(
        "| Delete | `/api/v2/meta/columns/{columnId}` | `/api/v3/meta/bases/{baseId}/fields/{fieldId}` | Terminology change + baseId |"
    )
    md.append("")

    md.append("### Link Operations Mapping")
    md.append("")
    md.append("| Operation | v2 Path | v3 Path | Notes |")
    md.append("|-----------|---------|---------|-------|")
    md.append(
        "| List | `/api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | `/api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | Complete restructure |"
    )
    md.append(
        "| Link | `/api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | `/api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | Complete restructure |"
    )
    md.append(
        "| Unlink | `/api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | `/api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | Complete restructure |"
    )
    md.append("")

    return md


def main():
    print("Loading OpenAPI specifications...")

    # Load files
    meta_v2 = load_openapi("docs/nocodb-openapi-meta.json")
    meta_v3 = load_openapi("docs/nocodb-openapi-meta-v3.json")
    data_v2 = load_openapi("docs/nocodb-openapi-data.json")
    data_v3 = load_openapi("docs/nocodb-openapi-data-v3.json")

    print("Extracting endpoints...")

    # Extract endpoints
    meta_v2_endpoints = get_endpoints(meta_v2)
    meta_v3_endpoints = get_endpoints(meta_v3)
    data_v2_endpoints = get_endpoints(data_v2)
    data_v3_endpoints = get_endpoints(data_v3)

    print(
        f"Meta API - v2: {len(meta_v2_endpoints)} endpoints, v3: {len(meta_v3_endpoints)} endpoints"
    )
    print(
        f"Data API - v2: {len(data_v2_endpoints)} endpoints, v3: {len(data_v3_endpoints)} endpoints"
    )

    print("Analyzing differences...")

    # Simple comparison
    meta_comparison = {
        "removed": set(meta_v2_endpoints.keys()) - set(meta_v3_endpoints.keys()),
        "new": set(meta_v3_endpoints.keys()) - set(meta_v2_endpoints.keys()),
    }

    data_comparison = {
        "removed": set(data_v2_endpoints.keys()) - set(data_v3_endpoints.keys()),
        "new": set(data_v3_endpoints.keys()) - set(data_v2_endpoints.keys()),
    }

    meta_analysis = {
        "comparison": meta_comparison,
        "v2_endpoints": meta_v2_endpoints,
        "v3_endpoints": meta_v3_endpoints,
    }

    data_analysis = {
        "comparison": data_comparison,
        "v2_endpoints": data_v2_endpoints,
        "v3_endpoints": data_v3_endpoints,
    }

    print("Generating comprehensive report...")

    report = generate_detailed_markdown(meta_analysis, data_analysis)

    # Write report
    output_file = "NOCODB_API_V2_V3_COMPARISON.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✓ Comprehensive report generated: {output_file}")
    print("\nSummary:")
    print(
        f"  Meta API: {len(meta_comparison['removed'])} removed, {len(meta_comparison['new'])} new"
    )
    print(
        f"  Data API: {len(data_comparison['removed'])} removed, {len(data_comparison['new'])} new"
    )
    print(f"\nReport size: {len(report)} characters")


if __name__ == "__main__":
    main()
