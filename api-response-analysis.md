# NocoDB API Response Formats Analysis

This document provides a comprehensive analysis of response formats for all critical CRUD operations in the NocoDB API.

---

## Data API (v2)

### 1. Create Single/Multiple Records

**Endpoint:** `POST /api/v2/tables/{tableId}/records`
**Operation ID:** `db-data-table-row-create`
**Response Type:** Array

**Response Structure:**
- Returns an array of objects
- Each object contains the ID of the created record
- Key field: `Id`

**Example Response:**
```json
[
  {
    "Id": 10
  },
  {
    "Id": 11
  }
]
```

---

### 2. Update Multiple Records (Bulk Update)

**Endpoint:** `PATCH /api/v2/tables/{tableId}/records`
**Operation ID:** `db-data-table-row-update`
**Response Type:** Array

**Response Structure:**
- Returns an array of objects
- Each object contains the ID of the updated record
- Key field: `Id`

**Example Response:**
```json
[
  {
    "Id": 6
  },
  {
    "Id": 7
  }
]
```

---

### 3. Get Single Record

**Endpoint:** `GET /api/v2/tables/{tableId}/records/{recordId}`
**Operation ID:** `db-data-table-row-read`
**Response Type:** Object

**Response Structure:**
- Returns a single object representing the record
- Contains all fields of the record
- Key fields include: `Id`, and all user-defined columns

**Example Response (truncated):**
```json
{
  "Id": 1,
  "SingleLineText": "David",
  "CreatedAt": "2023-10-16 08:27:59+00:00",
  "UpdatedAt": "2023-10-16 10:05:41+00:00",
  "Year": 2023,
  "URL": "www.google.com",
  "SingleSelect": "Jan",
  "Email": "a@b.com",
  "Duration": 74040,
  "Decimal": 23.658,
  "Currency": 23,
  "Barcode": "David",
  "JSON": {
    "name": "John Doe",
    "age": 30,
    "email": "johndoe@example.com",
    "isSubscribed": true,
    "address": {
      "street": "123 Main Street",
      "city": "Anytown",
      "zipCode": "12345"
    },
    "hobbies": [
      "Reading",
      "Hiking",
      "Cooking"
    ],
    "scores": {
      "math": 95,
      "science": 88,
      "history": 75
    }
  },
  "QRCode": "David",
  "Rollup": 3
}
  ...
}
```

**Key Field Names in Response:**
- `Id`
- `SingleLineText`
- `CreatedAt`
- `UpdatedAt`
- `Year`
- `URL`
- `SingleSelect`
- `Email`
- `Duration`
- `Decimal`
- `Currency`
- `Barcode`
- `JSON`
- `QRCode`
- `Rollup`
- `Date`
- `Time`
- `Rating`
- `Percent`
- `Formula`

---

### 4. List Records (Paginated)

**Endpoint:** `GET /api/v2/tables/{tableId}/records`
**Operation ID:** `db-data-table-row-list`
**Response Type:** Object

**Response Structure:**
- Returns an object with two main properties:
  - `list`: Array of record objects
  - `pageInfo`: Pagination metadata object

**Key Fields to Extract:**
- `list`: Contains the actual records
- `pageInfo.totalRows`: Total number of records
- `pageInfo.page`: Current page number
- `pageInfo.pageSize`: Number of records per page
- `pageInfo.isFirstPage`: Boolean indicating first page
- `pageInfo.isLastPage`: Boolean indicating last page

**Example Response (truncated):**
```json
{
  "list": [
    {
      "Id": 1,
      "SingleLineText": "David",
      "Year": 2023,
      "URL": "www.google.com",
      "SingleSelect": "Jan",
      "Email": "a@b.com",
      "Duration": 74040,
      "Decimal": 23.658,
      "Currency": 23,
      "JSON": {
        "name": "John Doe",
        "age": 30,
        "email": "johndoe@example.com",
        "isSubscribed": true,
        "address": {
          "street": "123 Main Street",
          "city": "Anytown",
          "zipCode": "12345"
        },
        "hobbies": [
          "Reading",
          "Hiking",
          "Cooking"
        ],
        "scores": {
          "math": 95,
          "science": 88,
          "history": 75
        }
      }
    }
  ],
  "pageInfo": {
    "totalRows": 5,
    "page": 1,
    "pageSize": 1,
    "isFirstPage": true,
    "isLastPage": false
  }
}
```

---

### 5. Delete Multiple Records (Bulk Delete)

**Endpoint:** `DELETE /api/v2/tables/{tableId}/records`
**Operation ID:** `db-data-table-row-delete`
**Response Type:** Array

**Response Structure:**
- Returns an array of objects
- Each object contains the ID of the deleted record
- Key field: `Id`

**Example Response:**
```json
[
  {
    "Id": 1
  },
  {
    "Id": 2
  }
]
```

---

## Meta API (v2)

### 6. List Bases

**Endpoint:** `GET /api/v2/meta/bases/`
**Operation ID:** `base-list`
**Response Type:** Object

**Response Structure:**
- Returns an object with two main properties:
  - `list`: Array of base objects
  - `pageInfo`: Pagination metadata object

**Key Fields to Extract:**
- `list`: Contains the actual bases
- Each base has: `id`, `title`, `description`, `color`, `sources`, etc.
- `pageInfo`: Same structure as data API pagination

**Example Response:**
```json
{
  "list": [
    {
      "sources": [
        {
          "alias": "string",
          "config": null,
          "created_at": "2023-03-01 14:27:36",
          "enabled": true,
          "id": "string",
          "inflection_column": "camelize",
          "inflection_table": "camelize",
          "is_meta": true,
          "order": 1,
          "base_id": "string",
          "type": "mysql2",
          "updated_at": "2023-03-01 14:27:36"
        }
      ],
      "color": "#24716E",
      "created_at": "2023-03-01 14:27:36",
      "deleted": true,
      "description": "This is my base description",
      "id": "p_124hhlkbeasewh",
      "is_meta": true,
      "meta": {},
      "order": 0,
      "prefix": "nc_vm5q__",
      "status": "string",
      "title": "my-base",
      "updated_at": "2023-03-01 14:27:36"
    }
  ],
  "pageInfo": {
    "isFirstPage": true,
    "isLastPage": true,
    "page": 1,
    "pageSize": 10,
    "totalRows": 1
  }
}
```

---

### 7. Create Base

**Endpoint:** `POST /api/v2/meta/bases/`
**Operation ID:** `base-create`
**Response Type:** Object

**Response Structure:**
- Returns a single base object
- Contains all base metadata including sources

**Key Fields in Response:**
- `id`: Base identifier
- `title`: Base name
- `description`: Base description
- `color`: Base color code
- `sources`: Array of data source configurations
- `created_at`, `updated_at`: Timestamps

**Example Response:**
```json
{
  "sources": [
    {
      "alias": "string",
      "config": null,
      "enabled": true,
      "id": "string",
      "inflection_column": "camelize",
      "inflection_table": "camelize",
      "is_meta": true,
      "order": 1,
      "base_id": "string",
      "type": "mysql2",
      "updated_at": "2023-03-01 14:27:36"
    }
  ],
  "color": "#24716E",
  "created_at": "2023-03-01 14:27:36",
  "deleted": true,
  "description": "This is my base description",
  "id": "p_124hhlkbeasewh",
  "is_meta": true,
  "meta": {},
  "order": 0,
  "prefix": "nc_vm5q__",
  "status": "string",
  "title": "my-base"
}
```

---

### 8. Get Base

**Endpoint:** `GET /api/v2/meta/bases/{baseId}`
**Operation ID:** `base-read`
**Response Type:** Object

**Response Structure:**
- Returns a single base object with full schema
- Contains all base metadata and configuration

**Example Response (truncated):**
```json
{
  "sources": [
    {
      "alias": "string",
      "config": null,
      "enabled": true,
      "id": "string",
      "inflection_column": "camelize",
      "inflection_table": "camelize",
      "is_meta": true,
      "order": 1,
      "base_id": "string",
      "type": "mysql2",
      "updated_at": "2023-03-01 14:27:36"
    }
  ],
  "color": "#24716E",
  "created_at": "2023-03-01 14:27:36",
  "deleted": true,
  "description": "This is my base description",
  "id": "p_124hhlkbeasewh",
  "is_meta": true,
  "meta": {},
  "order": 0,
  "prefix": "nc_vm5q__",
  "status": "string",
  "title": "my-base"
}
  ...
}
```

---

### 9. Update Base

**Endpoint:** `PATCH /api/v2/meta/bases/{baseId}`
**Operation ID:** `base-update`
**Response Type:** Primitive (number)

**Response Structure:**
- Returns a number (likely number of affected records)

**Example Response:**
```json
1
```

---

### 10. Delete Base

**Endpoint:** `DELETE /api/v2/meta/bases/{baseId}`
**Operation ID:** `base-delete`
**Response Type:** Primitive (boolean)

**Response Structure:**
- Returns a boolean indicating success

**Example Response:**
```json
true
```

---

### 11. Create Table

**Endpoint:** `POST /api/v2/meta/bases/{baseId}/tables`
**Operation ID:** `db-table-create`
**Response Type:** Object

**Response Structure:**
- Returns a table object with columns configuration
- Contains metadata for the created table

**Key Fields in Response:**
- `id`: Table identifier
- `table_name`: Internal table name
- `title`: Display title
- `source_id`: Associated data source
- `columns`: Array of column definitions

**Example Response (truncated):**
```json
{
  "source_id": "ds_g4ccx6e77h1dmi",
  "columns": "[{'ai': 0, 'au': 0, 'source_id': 'ds_g4ccx6e77h1dmi', 'cc': '', 'cdf': 'CURRENT_TIMESTAMP on update ...",
  "columnsById": "{'cl_c5knoi4xs4sfpt': {'ai': 0, 'au': 0, 'source_id': 'ds_g4ccx6e77h1dmi', 'cc': '', 'cdf': None, 'c...",
  "created_at": "2023-03-02 17:04:06",
  "deleted": null,
  "enabled": 1,
  "id": "md_rsu68aqjsbyqtl",
  "meta": null
}
  ...
}
```

---

### 12. Get Table Metadata

**Endpoint:** `GET /api/v2/meta/tables/{tableId}`
**Operation ID:** `db-table-read`
**Response Type:** Object

**Response Structure:**
- Returns complete table metadata
- Includes all column definitions, relationships, etc.

**Key Fields in Response:**
- `id`: Table identifier
- `table_name`: Internal table name
- `title`: Display title
- `columns`: Full column definitions
- `base_id`: Parent base identifier
- `source_id`: Data source identifier

**Example Response (truncated):**
```json
{
  "id": "md_rsu68aqjsbyqtl",
  "source_id": "ds_g4ccx6e77h1dmi",
  "base_id": "p_xm3thidrblw4n7",
  "table_name": "nc_vm5q___Table1",
  "title": "Table1",
  "type": "table",
  "meta": null,
  "schema": null,
  "enabled": 1,
  "mm": 0
}
  ...
}
```

---

### 13. Update Table

**Endpoint:** `PATCH /api/v2/meta/tables/{tableId}`
**Operation ID:** `db-table-update`
**Response Type:** Object

**Response Structure:**
- Returns a success message object

**Example Response:**
```json
{
  "msg": "The table has been updated successfully"
}
```

---

### 14. Delete Table

**Endpoint:** `DELETE /api/v2/meta/tables/{tableId}`
**Operation ID:** `db-table-delete`
**Response Type:** Primitive (boolean)

**Response Structure:**
- Returns a boolean indicating success

**Example Response:**
```json
true
```

---

## Summary

### Response Type Patterns

The NocoDB API uses three main response type patterns:

#### 1. Array Responses
Used for bulk operations that affect multiple records:
- **POST** /api/v2/tables/{tableId}/records - Create records
- **PATCH** /api/v2/tables/{tableId}/records - Update records
- **DELETE** /api/v2/tables/{tableId}/records - Delete records

Format: Array of objects with `Id` field
```json
[{"Id": 1}, {"Id": 2}]
```

#### 2. Paginated Object Responses
Used for list operations:
- **GET** /api/v2/tables/{tableId}/records - List records
- **GET** /api/v2/meta/bases/ - List bases

Format: Object with `list` array and `pageInfo` object
```json
{
  "list": [/* array of items */],
  "pageInfo": {
    "totalRows": 10,
    "page": 1,
    "pageSize": 25,
    "isFirstPage": true,
    "isLastPage": false
  }
}
```

#### 3. Single Object Responses
Used for operations on individual resources:
- **GET** /api/v2/tables/{tableId}/records/{recordId} - Get single record
- **POST** /api/v2/meta/bases/ - Create base
- **GET** /api/v2/meta/bases/{baseId} - Get base
- **POST** /api/v2/meta/bases/{baseId}/tables - Create table
- **GET** /api/v2/meta/tables/{tableId} - Get table

Format: Single object with all resource fields

#### 4. Primitive Responses
Used for simple success/failure or count operations:
- **DELETE** /api/v2/meta/bases/{baseId} - Returns `boolean`
- **DELETE** /api/v2/meta/tables/{tableId} - Returns `boolean`
- **PATCH** /api/v2/meta/bases/{baseId} - Returns `number`

#### 5. Message Object Responses
Used for operations that return status messages:
- **PATCH** /api/v2/meta/tables/{tableId} - Returns `{"msg": "..."}`

### Important Notes for Client Library Implementation

1. **Single Record Operations:**
   - There is NO `PATCH /api/v2/tables/{tableId}/records/{recordId}` endpoint
   - There is NO `DELETE /api/v2/tables/{tableId}/records/{recordId}` endpoint
   - To update/delete single records, use the bulk endpoints with a single-item array
   - The `{recordId}` path only supports GET operations

2. **Bulk Operations Always Return Arrays:**
   - POST, PATCH, and DELETE on `/api/v2/tables/{tableId}/records` return arrays
   - Even for single record operations, wrap the input in an array and expect an array response

3. **Pagination is Consistent:**
   - All list endpoints use the same `pageInfo` structure
   - Key fields: `totalRows`, `page`, `pageSize`, `isFirstPage`, `isLastPage`

4. **ID Field Naming:**
   - Records use `Id` (capital I)
   - Bases and tables use `id` (lowercase i)

5. **Delete Operations:**
   - Base delete returns `boolean`
   - Table delete returns `boolean`
   - Record delete returns `array of objects with Id`

6. **Update Operations:**
   - Base update returns `number`
   - Table update returns `object with msg`
   - Record update returns `array of objects with Id`

### Recommended Response Parsing Strategy

```typescript
// For list operations
interface PaginatedResponse<T> {
  list: T[];
  pageInfo: {
    totalRows: number;
    page: number;
    pageSize: number;
    isFirstPage: boolean;
    isLastPage: boolean;
  };
}

// For bulk record operations
interface RecordIdResponse {
  Id: number;
}

// For table update
interface MessageResponse {
  msg: string;
}
```

---

## Conclusion

This analysis covers all critical CRUD endpoints for the NocoDB API v2. The API follows consistent
patterns for different operation types, making it predictable for client library implementation.

**Key Takeaway:** Always check the response type before parsing:
- List operations: Check for 'list' and 'pageInfo' properties
- Bulk operations: Expect arrays with 'Id' fields
- Single resource operations: Expect complete objects
- Delete/Update operations: Check for boolean, number, or message objects
