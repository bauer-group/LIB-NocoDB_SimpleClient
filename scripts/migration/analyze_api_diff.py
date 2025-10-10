#!/usr/bin/env python3
"""
Comprehensive comparison of NocoDB API v2 vs v3 OpenAPI definitions.
Analyzes Meta and Data APIs for differences.
"""

import json
from collections import defaultdict


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


def normalize_path(path: str) -> str:
    """Normalize path for comparison by replacing parameter names."""
    import re

    # Replace {paramName} with {param}
    return re.sub(r"\{[^}]+\}", "{param}", path)


def compare_endpoints(v2_endpoints: dict, v3_endpoints: dict) -> dict:
    """Compare endpoints between v2 and v3."""
    v2_keys = set(v2_endpoints.keys())
    v3_keys = set(v3_endpoints.keys())

    # Find exact matches, new, and removed
    exact_matches = v2_keys & v3_keys
    removed = v2_keys - v3_keys
    new = v3_keys - v2_keys

    # Try to find renamed endpoints by comparing normalized paths
    v2_normalized = {normalize_path(ep): ep for ep in v2_keys}
    v3_normalized = {normalize_path(ep): ep for ep in v3_keys}

    potentially_renamed = []
    for v2_norm, v2_ep in v2_normalized.items():
        if v2_ep in removed and v2_norm in v3_normalized:
            v3_ep = v3_normalized[v2_norm]
            if v3_ep in new:
                potentially_renamed.append((v2_ep, v3_ep))

    return {
        "exact_matches": exact_matches,
        "removed": removed,
        "new": new,
        "potentially_renamed": potentially_renamed,
    }


def analyze_endpoint_changes(v2_spec: dict, v3_spec: dict) -> dict:
    """Analyze changes in a specific endpoint."""
    changes = {}

    # Compare parameters
    v2_params = {p.get("name"): p for p in v2_spec.get("parameters", [])}
    v3_params = {p.get("name"): p for p in v3_spec.get("parameters", [])}

    param_changes = {
        "removed": set(v2_params.keys()) - set(v3_params.keys()),
        "added": set(v3_params.keys()) - set(v2_params.keys()),
        "modified": [],
    }

    for param_name in set(v2_params.keys()) & set(v3_params.keys()):
        v2_p = v2_params[param_name]
        v3_p = v3_params[param_name]
        if v2_p != v3_p:
            param_changes["modified"].append({"name": param_name, "v2": v2_p, "v3": v3_p})

    if param_changes["removed"] or param_changes["added"] or param_changes["modified"]:
        changes["parameters"] = param_changes

    # Compare request body
    v2_body = v2_spec.get("requestBody", {})
    v3_body = v3_spec.get("requestBody", {})
    if v2_body != v3_body:
        changes["requestBody"] = {
            "v2": v2_body.get("content", {}).get("application/json", {}).get("schema", {}),
            "v3": v3_body.get("content", {}).get("application/json", {}).get("schema", {}),
        }

    # Compare responses
    v2_responses = v2_spec.get("responses", {})
    v3_responses = v3_spec.get("responses", {})
    if v2_responses != v3_responses:
        changes["responses"] = {"v2": v2_responses, "v3": v3_responses}

    # Compare security
    v2_security = v2_spec.get("security", [])
    v3_security = v3_spec.get("security", [])
    if v2_security != v3_security:
        changes["security"] = {"v2": v2_security, "v3": v3_security}

    return changes


def categorize_endpoint(endpoint: str) -> str:
    """Categorize endpoint by functionality."""
    path = endpoint.split(" ", 1)[1].lower()

    if "/tables" in path or "/table/" in path:
        return "Table Operations"
    elif "/records" in path or "/record/" in path or "/data/" in path:
        return "Record Operations"
    elif "/columns" in path or "/column/" in path or "/fields" in path:
        return "Column/Field Operations"
    elif "/views" in path or "/view/" in path:
        return "View Operations"
    elif "/links" in path or "/link/" in path or "/relations" in path:
        return "Link/Relation Operations"
    elif "/upload" in path or "/download" in path or "/files" in path:
        return "File Operations"
    elif "/hooks" in path or "/webhook" in path:
        return "Webhook Operations"
    elif "/meta" in path or "/schema" in path:
        return "Meta Operations"
    elif "/auth" in path or "/signin" in path or "/signup" in path:
        return "Authentication"
    elif "/bases" in path or "/base/" in path or "/projects" in path:
        return "Base/Project Operations"
    elif "/sources" in path or "/source/" in path:
        return "Data Source Operations"
    else:
        return "Other"


def generate_markdown_report(meta_analysis: dict, data_analysis: dict) -> str:
    """Generate comprehensive markdown report."""

    md = []
    md.append("# NocoDB API v2 to v3 Comprehensive Comparison Report")
    md.append("")
    md.append(
        f"**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    md.append("")

    # Executive Summary
    md.append("## Executive Summary")
    md.append("")

    meta_stats = {
        "removed": len(meta_analysis["comparison"]["removed"]),
        "new": len(meta_analysis["comparison"]["new"]),
        "renamed": len(meta_analysis["comparison"]["potentially_renamed"]),
        "unchanged": len(meta_analysis["comparison"]["exact_matches"]),
    }

    data_stats = {
        "removed": len(data_analysis["comparison"]["removed"]),
        "new": len(data_analysis["comparison"]["new"]),
        "renamed": len(data_analysis["comparison"]["potentially_renamed"]),
        "unchanged": len(data_analysis["comparison"]["exact_matches"]),
    }

    md.append("### Meta API Changes")
    md.append(f"- **Removed Endpoints:** {meta_stats['removed']}")
    md.append(f"- **New Endpoints:** {meta_stats['new']}")
    md.append(f"- **Potentially Renamed:** {meta_stats['renamed']}")
    md.append(f"- **Unchanged:** {meta_stats['unchanged']}")
    md.append("")

    md.append("### Data API Changes")
    md.append(f"- **Removed Endpoints:** {data_stats['removed']}")
    md.append(f"- **New Endpoints:** {data_stats['new']}")
    md.append(f"- **Potentially Renamed:** {data_stats['renamed']}")
    md.append(f"- **Unchanged:** {data_stats['unchanged']}")
    md.append("")

    # Meta API Detailed Analysis
    md.append("---")
    md.append("")
    md.append("## Meta API: v2 → v3 Differences")
    md.append("")

    md.extend(generate_api_section(meta_analysis))

    # Data API Detailed Analysis
    md.append("---")
    md.append("")
    md.append("## Data API: v2 → v3 Differences")
    md.append("")

    md.extend(generate_api_section(data_analysis))

    # Breaking Changes Summary
    md.append("---")
    md.append("")
    md.append("## Breaking Changes Summary")
    md.append("")
    md.append("These changes will require code modifications:")
    md.append("")

    md.append("### Meta API Breaking Changes")
    breaking_meta = categorize_breaking_changes(meta_analysis)
    for category, changes in sorted(breaking_meta.items()):
        if changes:
            md.append(f"#### {category}")
            for change in changes:
                md.append(f"- {change}")
            md.append("")

    md.append("### Data API Breaking Changes")
    breaking_data = categorize_breaking_changes(data_analysis)
    for category, changes in sorted(breaking_data.items()):
        if changes:
            md.append(f"#### {category}")
            for change in changes:
                md.append(f"- {change}")
            md.append("")

    # Recommendations
    md.append("---")
    md.append("")
    md.append("## Implementation Recommendations")
    md.append("")
    md.append("### Version Detection Strategy")
    md.append("```typescript")
    md.append("// Detect API version from server response")
    md.append("async function detectApiVersion(baseUrl: string): Promise<'v2' | 'v3'> {")
    md.append("  // Check for v3-specific endpoints or response structures")
    md.append("  // Implementation depends on specific differences found")
    md.append("}")
    md.append("```")
    md.append("")

    md.append("### Adapter Pattern")
    md.append("```typescript")
    md.append("interface ApiAdapter {")
    md.append("  getTables(baseId: string): Promise<Table[]>;")
    md.append("  getRecords(tableId: string, params?: QueryParams): Promise<Record[]>;")
    md.append("  // ... other methods")
    md.append("}")
    md.append("")
    md.append("class ApiV2Adapter implements ApiAdapter { /* ... */ }")
    md.append("class ApiV3Adapter implements ApiAdapter { /* ... */ }")
    md.append("```")
    md.append("")

    md.append("### Migration Priority")
    md.append("1. **High Priority**: Endpoints used frequently (record CRUD, table listing)")
    md.append("2. **Medium Priority**: View operations, link management")
    md.append("3. **Low Priority**: Advanced features, admin operations")
    md.append("")

    return "\n".join(md)


def generate_api_section(analysis: dict) -> list[str]:
    """Generate markdown section for an API."""
    md = []

    comparison = analysis["comparison"]
    v2_endpoints = analysis["v2_endpoints"]
    v3_endpoints = analysis["v3_endpoints"]

    # Group by category
    removed_by_category = defaultdict(list)
    new_by_category = defaultdict(list)

    for endpoint in sorted(comparison["removed"]):
        category = categorize_endpoint(endpoint)
        removed_by_category[category].append(endpoint)

    for endpoint in sorted(comparison["new"]):
        category = categorize_endpoint(endpoint)
        new_by_category[category].append(endpoint)

    # Removed Endpoints
    if comparison["removed"]:
        md.append("### Removed Endpoints")
        md.append("")
        for category in sorted(removed_by_category.keys()):
            md.append(f"#### {category}")
            md.append("")
            md.append("| Method | Path | Summary |")
            md.append("|--------|------|---------|")
            for endpoint in removed_by_category[category]:
                method, path = endpoint.split(" ", 1)
                summary = v2_endpoints[endpoint].get("summary", "N/A")
                md.append(f"| `{method}` | `{path}` | {summary} |")
            md.append("")

    # New Endpoints
    if comparison["new"]:
        md.append("### New Endpoints")
        md.append("")
        for category in sorted(new_by_category.keys()):
            md.append(f"#### {category}")
            md.append("")
            md.append("| Method | Path | Summary |")
            md.append("|--------|------|---------|")
            for endpoint in new_by_category[category]:
                method, path = endpoint.split(" ", 1)
                summary = v3_endpoints[endpoint].get("summary", "N/A")
                md.append(f"| `{method}` | `{path}` | {summary} |")
            md.append("")

    # Potentially Renamed
    if comparison["potentially_renamed"]:
        md.append("### Potentially Renamed/Restructured Endpoints")
        md.append("")
        md.append("| v2 Endpoint | v3 Endpoint |")
        md.append("|-------------|-------------|")
        for v2_ep, v3_ep in sorted(comparison["potentially_renamed"]):
            md.append(f"| `{v2_ep}` | `{v3_ep}` |")
        md.append("")

    return md


def categorize_breaking_changes(analysis: dict) -> dict[str, list[str]]:
    """Categorize breaking changes."""
    breaking = defaultdict(list)

    comparison = analysis["comparison"]

    # Removed endpoints are breaking
    for endpoint in sorted(comparison["removed"]):
        category = categorize_endpoint(endpoint)
        breaking[category].append(f"**Removed:** `{endpoint}`")

    # Renamed endpoints are breaking
    for v2_ep, v3_ep in comparison["potentially_renamed"]:
        category = categorize_endpoint(v2_ep)
        breaking[category].append(f"**Path Changed:** `{v2_ep}` → `{v3_ep}`")

    return breaking


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

    print("Comparing Meta API...")
    meta_comparison = compare_endpoints(meta_v2_endpoints, meta_v3_endpoints)

    print("Comparing Data API...")
    data_comparison = compare_endpoints(data_v2_endpoints, data_v3_endpoints)

    print("Generating report...")

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

    report = generate_markdown_report(meta_analysis, data_analysis)

    # Write report
    output_file = "API_COMPARISON_V2_V3.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nReport generated: {output_file}")
    print("\nQuick Stats:")
    print(f"Meta API: {len(meta_comparison['removed'])} removed, {len(meta_comparison['new'])} new")
    print(f"Data API: {len(data_comparison['removed'])} removed, {len(data_comparison['new'])} new")


if __name__ == "__main__":
    main()
