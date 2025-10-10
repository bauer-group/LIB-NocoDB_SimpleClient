# NocoDB API v2 to v3 Schema & Parameter Comparison

**Generated:** 2025-10-10 11:35:33

This report focuses on the detailed schema and parameter changes between v2 and v3.

## Record Operations Detailed Analysis

### List Records Query Parameters

#### v2 Query Parameters

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `fields` | No | string | Allows you to specify the fields that you wish to include in your API response. By default, all the fields are included in the response.

Example: `fields=field1,field2` will include only 'field1' and 'field2' in the API response.

Please note that it's essential not to include spaces between field names in the comma-separated list. |
| `sort` | No | string | Allows you to specify the fields by which you want to sort the records in your API response. By default, sorting is done in ascending order for the designated fields. To sort in descending order, add a '-' symbol before the field name.

Example: `sort=field1,-field2` will sort the records first by 'field1' in ascending order and then by 'field2' in descending order.

If `viewId` query parameter is also included, the sort included here will take precedence over any sorting configuration defined in the view.

Please note that it's essential not to include spaces between field names in the comma-separated list. |
| `where` | No | string | Enables you to define specific conditions for filtering records in your API response. Multiple conditions can be combined using logical operators such as 'and' and 'or'. Each condition consists of three parts: a field name, a comparison operator, and a value.

Example: `where=(field1,eq,value1)~and(field2,eq,value2)` will filter records where 'field1' is equal to 'value1' AND 'field2' is equal to 'value2'.

You can also use other comparison operators like 'ne' (not equal), 'gt' (greater than), 'lt' (less than), and more, to create complex filtering rules.

If `viewId` query parameter is also included, then the filters included here will be applied over the filtering configuration defined in the view.

Please remember to maintain the specified format, and do not include spaces between the different condition components |
| `offset` | No | integer | Enables you to control the pagination of your API response by specifying the number of records you want to skip from the beginning of the result set. The default value for this parameter is set to 0, meaning no records are skipped by default.

Example: `offset=25` will skip the first 25 records in your API response, allowing you to access records starting from the 26th position.

Please note that the 'offset' value represents the number of records to exclude, not an index value, so an offset of 25 will skip the first 25 records. |
| `limit` | No | integer | Enables you to set a limit on the number of records you want to retrieve in your API response. By default, your response includes all the available records, but by using this parameter, you can control the quantity you receive.

Example: `limit=100` will constrain your response to the first 100 records in the dataset. |
| `viewId` | No | string | ***View Identifier***. Allows you to fetch records that are currently visible within a specific view. API retrieves records in the order they are displayed if the SORT option is enabled within that view.

Additionally, if you specify a `sort` query parameter, it will take precedence over any sorting configuration defined in the view. If you specify a `where` query parameter, it will be applied over the filtering configuration defined in the view.

By default, all fields, including those that are disabled within the view, are included in the response. To explicitly specify which fields to include or exclude, you can use the `fields` query parameter to customize the output according to your requirements. |

#### v3 Query Parameters

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `fields` | No | None | Allows you to specify the fields that you wish to include from the linked records in your API response. By default, only Primary Key and associated display value field is included.

Example: `fields=["field1","field2"]` or `fields=field1,field2` will include only 'field1' and 'field2' in the API response. |
| `sort` | No | None | Allows you to specify the fields by which you want to sort the records in your API response. Accepts either an array of sort objects or a single sort object.

Each sort object must have a 'field' property specifying the field name and a 'direction' property with value 'asc' or 'desc'.

Example: `sort=[{"direction":"asc","field":"field_name"},{"direction":"desc","field":"another_field"}]` or `sort={"direction":"asc","field":"field_name"}`

If `viewId` query parameter is also included, the sort included here will take precedence over any sorting configuration defined in the view. |
| `where` | No | string | Enables you to define specific conditions for filtering records in your API response. Multiple conditions can be combined using logical operators such as 'and' and 'or'. Each condition consists of three parts: a field name, a comparison operator, and a value.

Example: `where=(field1,eq,value1)~and(field2,eq,value2)` will filter records where 'field1' is equal to 'value1' AND 'field2' is equal to 'value2'.

You can also use other comparison operators like 'neq' (not equal), 'gt' (greater than), 'lt' (less than), and more, to create complex filtering rules.

If `viewId` query parameter is also included, then the filters included here will be applied over the filtering configuration defined in the view.

Please remember to maintain the specified format, for further information on this please see [the documentation](https://nocodb.com/docs/product-docs/developer-resources/rest-apis#v3-where-query-parameter) |
| `page` | No | integer | Enables you to control the pagination of your API response by specifying the page number you want to retrieve. By default, the first page is returned. If you want to retrieve the next page, you can increment the page number by one.

Example: `page=2` will return the second page of records in the dataset. |
| `nestedPage` | No | integer | Enables you to control the pagination of your nested data (linked records) in API response by specifying the page number you want to retrieve. By default, the first page is returned. If you want to retrieve the next page, you can increment the page number by one.

Example: `page=2` will return the second page of nested data records in the dataset. |
| `pageSize` | No | integer | Enables you to set a limit on the number of records you want to retrieve in your API response. By default, your response includes all the available records, but by using this parameter, you can control the quantity you receive.

Example: `pageSize=100` will constrain your response to the first 100 records in the dataset. |
| `viewId` | No | string | ***View Identifier***. Allows you to fetch records that are currently visible within a specific view. API retrieves records in the order they are displayed if the SORT option is enabled within that view.

Additionally, if you specify a `sort` query parameter, it will take precedence over any sorting configuration defined in the view. If you specify a `where` query parameter, it will be applied over the filtering configuration defined in the view.

By default, all fields, including those that are disabled within the view, are included in the response. To explicitly specify which fields to include or exclude, you can use the `fields` query parameter to customize the output according to your requirements. |

#### Parameter Changes

**Removed:** `offset`, `limit`
**Added:** `nestedPage`, `page`, `pageSize`

### List Records Response Schema

#### v2 Response
```
- list: array<object> (required)
  // List of data objects
- pageInfo: unknown (required)
  // Paginated Info
```

#### v3 Response
```
$ref: #/components/schemas/DataListResponseV3
```

### Create Records Request Schema

#### v2 Request Body
```
Type: unknown
```

#### v3 Request Body
```
Type: unknown
```


## Table Operations Detailed Analysis

### Get Table Response Schema

#### v2 Response
```
$ref: #/components/schemas/Table
```

#### v3 Response
```
$ref: #/components/schemas/Table
```


---

## Key Schema Observations

### 1. Response Envelope Structure

Check if both versions use the same response envelope:
- v2: May use `{ list: [...], pageInfo: {...} }`
- v3: May use different structure

### 2. Error Response Format

Error responses may differ between versions:
```typescript
// v2 error format (typical)
{
  "msg": "Error message",
  "error": "ERROR_CODE"
}

// v3 error format (may differ)
{
  "message": "Error message",
  "statusCode": 400,
  "error": "Bad Request"
}
```

### 3. Pagination

Both versions should be checked for:
- Offset/limit based pagination
- Cursor-based pagination
- Page info structure

### 4. Field Names

Notable terminology changes:
- `columns` → `fields`
- Check if `Id` vs `id` (capitalization)
- Check timestamp field names
