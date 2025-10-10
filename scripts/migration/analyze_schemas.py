#!/usr/bin/env python3
"""
Analyze request/response schemas and query parameters between v2 and v3.
"""

import json


def load_openapi(filepath: str) -> dict:
    """Load OpenAPI JSON file."""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def extract_parameters(endpoint_spec: dict) -> dict[str, list[dict]]:
    """Extract query, path, and header parameters."""
    params = {"query": [], "path": [], "header": []}

    for param in endpoint_spec.get("parameters", []):
        param_type = param.get("in", "")
        if param_type in params:
            params[param_type].append(
                {
                    "name": param.get("name"),
                    "required": param.get("required", False),
                    "type": param.get("schema", {}).get("type"),
                    "description": param.get("description", ""),
                }
            )

    return params


def extract_request_schema(endpoint_spec: dict) -> dict:
    """Extract request body schema."""
    request_body = endpoint_spec.get("requestBody", {})
    content = request_body.get("content", {})
    json_content = content.get("application/json", {})
    return json_content.get("schema", {})


def extract_response_schema(endpoint_spec: dict, status_code: str = "200") -> dict:
    """Extract response schema for given status code."""
    responses = endpoint_spec.get("responses", {})
    response = responses.get(status_code, {})
    content = response.get("content", {})
    json_content = content.get("application/json", {})
    return json_content.get("schema", {})


def format_schema(schema: dict, indent: int = 0) -> list[str]:
    """Format schema for display."""
    lines = []
    prefix = "  " * indent

    if not schema:
        return [f"{prefix}(No schema)"]

    schema_type = schema.get("type", "unknown")

    if schema_type == "object":
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for prop_name, prop_schema in properties.items():
            req_marker = " (required)" if prop_name in required else ""
            prop_type = prop_schema.get("type", "unknown")
            description = prop_schema.get("description", "")

            if prop_type == "array":
                items = prop_schema.get("items", {})
                items_type = items.get("type", "unknown")
                lines.append(f"{prefix}- {prop_name}: {prop_type}<{items_type}>{req_marker}")
            else:
                lines.append(f"{prefix}- {prop_name}: {prop_type}{req_marker}")

            if description:
                lines.append(f"{prefix}  // {description}")

    elif schema_type == "array":
        items = schema.get("items", {})
        lines.append(f"{prefix}Array of:")
        lines.extend(format_schema(items, indent + 1))

    elif "$ref" in schema:
        ref = schema["$ref"]
        lines.append(f"{prefix}$ref: {ref}")

    else:
        lines.append(f"{prefix}Type: {schema_type}")

    return lines


def compare_record_operations(v2_spec: dict, v3_spec: dict) -> str:
    """Compare record operation details."""
    md = []

    md.append("## Record Operations Detailed Analysis")
    md.append("")

    # Find list records endpoints
    v2_list_records = None
    v3_list_records = None

    for path, methods in v2_spec.get("paths", {}).items():
        if "/tables/{tableId}/records" in path and "get" in methods:
            v2_list_records = methods["get"]
            break

    for path, methods in v3_spec.get("paths", {}).items():
        if "/data/{baseId}/{tableId}/records" in path and "get" in methods:
            v3_list_records = methods["get"]
            break

    if v2_list_records and v3_list_records:
        md.append("### List Records Query Parameters")
        md.append("")

        v2_params = extract_parameters(v2_list_records)
        v3_params = extract_parameters(v3_list_records)

        md.append("#### v2 Query Parameters")
        md.append("")
        if v2_params["query"]:
            md.append("| Parameter | Required | Type | Description |")
            md.append("|-----------|----------|------|-------------|")
            for param in v2_params["query"]:
                req = "Yes" if param["required"] else "No"
                md.append(
                    f"| `{param['name']}` | {req} | {param['type']} | {param['description']} |"
                )
        else:
            md.append("(No query parameters documented)")
        md.append("")

        md.append("#### v3 Query Parameters")
        md.append("")
        if v3_params["query"]:
            md.append("| Parameter | Required | Type | Description |")
            md.append("|-----------|----------|------|-------------|")
            for param in v3_params["query"]:
                req = "Yes" if param["required"] else "No"
                md.append(
                    f"| `{param['name']}` | {req} | {param['type']} | {param['description']} |"
                )
        else:
            md.append("(No query parameters documented)")
        md.append("")

        # Compare
        v2_param_names = {p["name"] for p in v2_params["query"]}
        v3_param_names = {p["name"] for p in v3_params["query"]}

        if v2_param_names != v3_param_names:
            md.append("#### Parameter Changes")
            md.append("")
            removed = v2_param_names - v3_param_names
            added = v3_param_names - v2_param_names

            if removed:
                md.append(f"**Removed:** {', '.join(f'`{p}`' for p in removed)}")
            if added:
                md.append(f"**Added:** {', '.join(f'`{p}`' for p in added)}")
            md.append("")

        # Response schema
        md.append("### List Records Response Schema")
        md.append("")

        v2_response = extract_response_schema(v2_list_records)
        v3_response = extract_response_schema(v3_list_records)

        md.append("#### v2 Response")
        md.append("```")
        md.extend(format_schema(v2_response))
        md.append("```")
        md.append("")

        md.append("#### v3 Response")
        md.append("```")
        md.extend(format_schema(v3_response))
        md.append("```")
        md.append("")

    # Create record
    v2_create = None
    v3_create = None

    for path, methods in v2_spec.get("paths", {}).items():
        if "/tables/{tableId}/records" in path and "post" in methods:
            v2_create = methods["post"]
            break

    for path, methods in v3_spec.get("paths", {}).items():
        if "/data/{baseId}/{tableId}/records" in path and "post" in methods:
            v3_create = methods["post"]
            break

    if v2_create and v3_create:
        md.append("### Create Records Request Schema")
        md.append("")

        v2_request = extract_request_schema(v2_create)
        v3_request = extract_request_schema(v3_create)

        md.append("#### v2 Request Body")
        md.append("```")
        md.extend(format_schema(v2_request))
        md.append("```")
        md.append("")

        md.append("#### v3 Request Body")
        md.append("```")
        md.extend(format_schema(v3_request))
        md.append("```")
        md.append("")

    return "\n".join(md)


def compare_table_operations(v2_spec: dict, v3_spec: dict) -> str:
    """Compare table operation details."""
    md = []

    md.append("## Table Operations Detailed Analysis")
    md.append("")

    # Get table endpoint
    v2_get_table = None
    v3_get_table = None

    for path, methods in v2_spec.get("paths", {}).items():
        if path == "/api/v2/meta/tables/{tableId}" and "get" in methods:
            v2_get_table = methods["get"]
            break

    for path, methods in v3_spec.get("paths", {}).items():
        if "/meta/bases/{baseId}/tables/{tableId}" in path and "get" in methods:
            v3_get_table = methods["get"]
            break

    if v2_get_table and v3_get_table:
        md.append("### Get Table Response Schema")
        md.append("")

        v2_response = extract_response_schema(v2_get_table)
        v3_response = extract_response_schema(v3_get_table)

        md.append("#### v2 Response")
        md.append("```")
        md.extend(format_schema(v2_response))
        md.append("```")
        md.append("")

        md.append("#### v3 Response")
        md.append("```")
        md.extend(format_schema(v3_response))
        md.append("```")
        md.append("")

    return "\n".join(md)


def generate_schema_report(v2_meta: dict, v3_meta: dict, v2_data: dict, v3_data: dict) -> str:
    """Generate schema comparison report."""
    md = []

    md.append("# NocoDB API v2 to v3 Schema & Parameter Comparison")
    md.append("")
    md.append(
        f"**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    md.append("")

    md.append("This report focuses on the detailed schema and parameter changes between v2 and v3.")
    md.append("")

    # Record operations (from data API specs)
    record_comparison = compare_record_operations(v2_data, v3_meta)
    md.append(record_comparison)
    md.append("")

    # Table operations (from meta API specs)
    table_comparison = compare_table_operations(v2_meta, v3_data)
    md.append(table_comparison)
    md.append("")

    md.append("---")
    md.append("")
    md.append("## Key Schema Observations")
    md.append("")
    md.append("### 1. Response Envelope Structure")
    md.append("")
    md.append("Check if both versions use the same response envelope:")
    md.append("- v2: May use `{ list: [...], pageInfo: {...} }`")
    md.append("- v3: May use different structure")
    md.append("")
    md.append("### 2. Error Response Format")
    md.append("")
    md.append("Error responses may differ between versions:")
    md.append("```typescript")
    md.append("// v2 error format (typical)")
    md.append("{")
    md.append('  "msg": "Error message",')
    md.append('  "error": "ERROR_CODE"')
    md.append("}")
    md.append("")
    md.append("// v3 error format (may differ)")
    md.append("{")
    md.append('  "message": "Error message",')
    md.append('  "statusCode": 400,')
    md.append('  "error": "Bad Request"')
    md.append("}")
    md.append("```")
    md.append("")
    md.append("### 3. Pagination")
    md.append("")
    md.append("Both versions should be checked for:")
    md.append("- Offset/limit based pagination")
    md.append("- Cursor-based pagination")
    md.append("- Page info structure")
    md.append("")
    md.append("### 4. Field Names")
    md.append("")
    md.append("Notable terminology changes:")
    md.append("- `columns` → `fields`")
    md.append("- Check if `Id` vs `id` (capitalization)")
    md.append("- Check timestamp field names")
    md.append("")

    return "\n".join(md)


def main():
    print("Loading OpenAPI specifications...")

    v2_meta = load_openapi("docs/nocodb-openapi-meta.json")
    v3_meta = load_openapi("docs/nocodb-openapi-meta-v3.json")
    v2_data = load_openapi("docs/nocodb-openapi-data.json")
    v3_data = load_openapi("docs/nocodb-openapi-data-v3.json")

    print("Analyzing schemas...")

    report = generate_schema_report(v2_meta, v3_meta, v2_data, v3_data)

    output_file = "NOCODB_API_SCHEMA_COMPARISON.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Schema comparison report generated: {output_file}")


if __name__ == "__main__":
    main()
