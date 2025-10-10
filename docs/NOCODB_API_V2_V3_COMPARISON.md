# NocoDB API v2 to v3 Comprehensive Comparison Report

**Generated:** 2025-10-10 11:24:00

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Major Architectural Changes](#major-architectural-changes)
3. [Meta API Detailed Comparison](#meta-api-detailed-comparison)
4. [Data API Detailed Comparison](#data-api-detailed-comparison)
5. [Critical Breaking Changes](#critical-breaking-changes)
6. [Migration Path Analysis](#migration-path-analysis)
7. [Code Migration Examples](#code-migration-examples)
8. [Implementation Strategy](#implementation-strategy)

## Executive Summary

### Overview

NocoDB API v3 represents a **major architectural overhaul** compared to v2:

- **Meta API**: Dramatically simplified from 137 endpoints to 10 endpoints
- **Data API**: Expanded from 10 endpoints to 36 endpoints with more granular operations
- **Path Structure**: Complete restructuring - v2 paths do NOT directly map to v3
- **Terminology**: 'columns' → 'fields', simplified resource hierarchy

### Quick Stats

| API | v2 Endpoints | v3 Endpoints | Removed | New | Change |
|-----|--------------|--------------|---------|-----|--------|
| **Meta API** | 137 | 10 | 137 | 10 | -93% |
| **Data API** | 10 | 36 | 10 | 36 | +260% |

---

## Major Architectural Changes

### API Split Strategy

v3 introduces a clear separation of concerns:

#### v2 Architecture
```
Meta API (nocodb-openapi-meta.json):
  ├─ Authentication endpoints
  ├─ Base/Workspace management
  ├─ Table schema operations
  ├─ Column operations
  ├─ View operations
  ├─ Filter/Sort operations
  ├─ Webhook operations
  └─ Misc utilities

Data API (nocodb-openapi-data.json):
  ├─ Record CRUD (10 endpoints)
  └─ File upload
```

#### v3 Architecture
```
Meta API (nocodb-openapi-meta-v3.json):
  └─ Data operations ONLY (10 endpoints)
      ├─ Record CRUD
      ├─ Link operations
      └─ File upload

Data API (nocodb-openapi-data-v3.json):
  └─ Meta operations ONLY (36 endpoints)
      ├─ Base management
      ├─ Table schema
      ├─ Field operations (columns)
      ├─ View operations
      └─ Member management
```

**KEY INSIGHT: v2 and v3 have INVERTED their API definitions!**

- v2's 'Meta API' = v3's 'Data API' (schema/structure)
- v2's 'Data API' = v3's 'Meta API' (records/content)

### Path Structure Changes

#### v2 Path Patterns
```
Authentication:     /api/v2/auth/{operation}
Meta Operations:    /api/v2/meta/{resource}/{id}
Data Operations:    /api/v2/tables/{tableId}/records
Column Operations:  /api/v2/meta/columns/{columnId}
View Operations:    /api/v2/meta/views/{viewId}
```

#### v3 Path Patterns
```
Meta (Structure):   /api/v3/meta/bases/{baseId}/{resource}
Data (Records):     /api/v3/data/{baseId}/{tableId}/records
Field Operations:   /api/v3/meta/bases/{baseId}/fields/{fieldId}
View Operations:    /api/v3/meta/bases/{baseId}/views/{viewId}
Link Operations:    /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}
```

**KEY CHANGES:**

1. **baseId is now required** in all paths (was optional/implicit in v2)
2. **Resource hierarchy** is more explicit: `/bases/{baseId}/tables/{tableId}/...`
3. **Terminology change**: `columns` → `fields`
4. **Authentication endpoints removed** from OpenAPI specs (likely moved to separate service)

---

## Critical Breaking Changes

### 🔴 HIGH PRIORITY: Record Operations

**Most frequently used endpoints - requires immediate attention**

| Operation | v2 Endpoint | v3 Endpoint | Breaking Change |
|-----------|-------------|-------------|-----------------|
| List Records | `GET /api/v2/tables/{tableId}/records` | `GET /api/v3/data/{baseId}/{tableId}/records` | **baseId required** |
| Get Record | `GET /api/v2/tables/{tableId}/records/{recordId}` | `GET /api/v3/data/{baseId}/{tableId}/records/{recordId}` | **baseId required** |
| Create Records | `POST /api/v2/tables/{tableId}/records` | `POST /api/v3/data/{baseId}/{tableId}/records` | **baseId required** |
| Update Records | `PATCH /api/v2/tables/{tableId}/records` | `PATCH /api/v3/data/{baseId}/{tableId}/records` | **baseId required** |
| Delete Records | `DELETE /api/v2/tables/{tableId}/records` | `DELETE /api/v3/data/{baseId}/{tableId}/records` | **baseId required** |
| Count Records | `GET /api/v2/tables/{tableId}/records/count` | `GET /api/v3/data/{baseId}/{tableId}/count` | **path change + baseId** |

### 🟡 MEDIUM PRIORITY: Table & Schema Operations

| Operation | v2 Endpoint | v3 Endpoint | Breaking Change |
|-----------|-------------|-------------|-----------------|
| List Tables | `GET /api/v2/meta/bases/{baseId}/tables` | `GET /api/v3/meta/bases/{baseId}/tables` | **API file swap** |
| Get Table | `GET /api/v2/meta/tables/{tableId}` | `GET /api/v3/meta/bases/{baseId}/tables/{tableId}` | **baseId required in path** |
| Create Table | `POST /api/v2/meta/bases/{baseId}/tables` | `POST /api/v3/meta/bases/{baseId}/tables` | **API file swap** |
| Update Table | `PATCH /api/v2/meta/tables/{tableId}` | `PATCH /api/v3/meta/bases/{baseId}/tables/{tableId}` | **baseId required in path** |
| Delete Table | `DELETE /api/v2/meta/tables/{tableId}` | `DELETE /api/v3/meta/bases/{baseId}/tables/{tableId}` | **baseId required in path** |

### 🔵 LOW PRIORITY: Column/Field Operations

| Operation | v2 Endpoint | v3 Endpoint | Breaking Change |
|-----------|-------------|-------------|-----------------|
| Get Column | `GET /api/v2/meta/columns/{columnId}` | `GET /api/v3/meta/bases/{baseId}/fields/{fieldId}` | **terminology + path change** |
| Update Column | `PATCH /api/v2/meta/columns/{columnId}` | `PATCH /api/v3/meta/bases/{baseId}/fields/{fieldId}` | **terminology + path change** |
| Delete Column | `DELETE /api/v2/meta/columns/{columnId}` | `DELETE /api/v3/meta/bases/{baseId}/fields/{fieldId}` | **terminology + path change** |
| Create Column | `POST /api/v2/meta/tables/{tableId}/columns` | `POST /api/v3/meta/bases/{baseId}/tables/{tableId}/fields` | **terminology + baseId** |

### 🟣 CRITICAL: Link/Relation Operations

| Operation | v2 Endpoint | v3 Endpoint | Breaking Change |
|-----------|-------------|-------------|-----------------|
| List Links | `GET /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | `GET /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | **complete restructure** |
| Link Records | `POST /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | `POST /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | **complete restructure** |
| Unlink Records | `DELETE /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | `DELETE /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | **complete restructure** |

### 🔴 REMOVED: Authentication Endpoints

These endpoints are completely removed from v3 OpenAPI specs:

- `POST /api/v2/auth/user/signin`
- `POST /api/v2/auth/user/signup`
- `POST /api/v2/auth/user/signout`
- `GET /api/v2/auth/user/me`
- `POST /api/v2/auth/token/refresh`
- `POST /api/v2/auth/password/forgot`
- `POST /api/v2/auth/password/reset/{token}`
- `POST /api/v2/auth/password/change`

**Note:** These may still exist but are not documented in the provided v3 OpenAPI specs.

---

## Migration Path Analysis

### Phase 1: Base ID Resolution

The biggest structural change is that **baseId is required in all v3 paths**.

**Challenge:** v2 code often uses just `tableId` without explicitly tracking `baseId`.

**Solutions:**

1. **Cache baseId with tableId** when fetching table metadata
2. **Fetch baseId on demand** if not cached
3. **Require baseId** as a parameter in all client methods

### Phase 2: Endpoint Mapping

Create adapter layer to map v2 calls to v3:

```typescript
interface EndpointMapper {
  mapRecordsList(tableId: string): {
    v2: string;  // '/api/v2/tables/{tableId}/records'
    v3: string;  // '/api/v3/data/{baseId}/{tableId}/records'
  };
}
```

### Phase 3: Response Schema Adaptation

Response structures may have changed. Need to analyze:

- Field naming conventions
- Nested object structures
- Pagination formats
- Error response formats

---

## Code Migration Examples

### Example 1: List Records

**v2 Code:**
```typescript
async function getRecords(tableId: string, params?: QueryParams) {
  const response = await fetch(
    `${baseUrl}/api/v2/tables/${tableId}/records?${queryString}`,
    { headers: { 'xc-token': token } }
  );
  return response.json();
}
```

**v3 Code:**
```typescript
async function getRecords(
  baseId: string,  // ← NEW: baseId required
  tableId: string,
  params?: QueryParams
) {
  const response = await fetch(
    `${baseUrl}/api/v3/data/${baseId}/${tableId}/records?${queryString}`,
    { headers: { 'xc-token': token } }
  );
  return response.json();
}
```

### Example 2: Create Record

**v2 Code:**
```typescript
async function createRecord(tableId: string, data: Record<string, any>) {
  const response = await fetch(
    `${baseUrl}/api/v2/tables/${tableId}/records`,
    {
      method: 'POST',
      headers: {
        'xc-token': token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    }
  );
  return response.json();
}
```

**v3 Code:**
```typescript
async function createRecord(
  baseId: string,  // ← NEW: baseId required
  tableId: string,
  data: Record<string, any>
) {
  const response = await fetch(
    `${baseUrl}/api/v3/data/${baseId}/${tableId}/records`,
    {
      method: 'POST',
      headers: {
        'xc-token': token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    }
  );
  return response.json();
}
```

### Example 3: Get Table Schema

**v2 Code:**
```typescript
async function getTable(tableId: string) {
  const response = await fetch(
    `${baseUrl}/api/v2/meta/tables/${tableId}`,
    { headers: { 'xc-token': token } }
  );
  return response.json();
}
```

**v3 Code:**
```typescript
async function getTable(baseId: string, tableId: string) {
  const response = await fetch(
    // NOTE: This is in the 'Data API' file in v3, not 'Meta API'
    `${baseUrl}/api/v3/meta/bases/${baseId}/tables/${tableId}`,
    { headers: { 'xc-token': token } }
  );
  return response.json();
}
```

### Example 4: Link Records

**v2 Code:**
```typescript
async function linkRecords(
  tableId: string,
  linkFieldId: string,
  recordId: string,
  linkedRecordIds: string[]
) {
  const response = await fetch(
    `${baseUrl}/api/v2/tables/${tableId}/links/${linkFieldId}/records/${recordId}`,
    {
      method: 'POST',
      headers: {
        'xc-token': token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ linkedRecordIds })
    }
  );
  return response.json();
}
```

**v3 Code:**
```typescript
async function linkRecords(
  baseId: string,  // ← NEW: baseId required
  tableId: string,
  linkFieldId: string,
  recordId: string,
  linkedRecordIds: string[]
) {
  const response = await fetch(
    `${baseUrl}/api/v3/data/${baseId}/${tableId}/links/${linkFieldId}/${recordId}`,
    {
      method: 'POST',
      headers: {
        'xc-token': token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ linkedRecordIds })
    }
  );
  return response.json();
}
```

---

## Implementation Strategy

### 1. Dual-Version Support Architecture

**Recommended Approach:** Adapter Pattern with Version Detection

```typescript
// Core interface that both versions implement
interface NocoDBClient {
  // Record operations
  getRecords(tableId: string, params?: RecordQueryParams): Promise<RecordList>;
  getRecord(tableId: string, recordId: string): Promise<Record>;
  createRecords(tableId: string, records: RecordData[]): Promise<Record[]>;
  updateRecords(tableId: string, records: RecordUpdate[]): Promise<Record[]>;
  deleteRecords(tableId: string, recordIds: string[]): Promise<void>;

  // Table operations
  getTables(baseId: string): Promise<Table[]>;
  getTable(tableId: string): Promise<Table>;

  // Link operations
  linkRecords(tableId: string, linkFieldId: string, recordId: string, linkedIds: string[]): Promise<void>;
  unlinkRecords(tableId: string, linkFieldId: string, recordId: string, linkedIds: string[]): Promise<void>;
}

// Version-specific implementations
class NocoDBClientV2 implements NocoDBClient {
  // Implements v2 API paths
}

class NocoDBClientV3 implements NocoDBClient {
  // Implements v3 API paths
  // Requires baseId for all operations
}

// Factory with auto-detection
async function createNocoDBClient(config: ClientConfig): Promise<NocoDBClient> {
  const version = await detectApiVersion(config.baseUrl, config.token);
  return version === 'v3'
    ? new NocoDBClientV3(config)
    : new NocoDBClientV2(config);
}
```

### 2. Version Detection Strategy

```typescript
async function detectApiVersion(
  baseUrl: string,
  token: string
): Promise<'v2' | 'v3'> {
  // Option 1: Check for v3-specific endpoint
  try {
    const response = await fetch(
      `${baseUrl}/api/v3/meta/workspaces/`,
      { headers: { 'xc-token': token } }
    );
    if (response.ok) return 'v3';
  } catch (error) {
    // v3 endpoint doesn't exist
  }

  // Option 2: Check /api/v2/meta/nocodb/info for version
  try {
    const response = await fetch(
      `${baseUrl}/api/v2/meta/nocodb/info`,
      { headers: { 'xc-token': token } }
    );
    if (response.ok) {
      const info = await response.json();
      // Parse version string to determine API version
      return info.version?.startsWith('3.') ? 'v3' : 'v2';
    }
  } catch (error) {
    // Fallback to v2
  }

  // Default to v2 for backward compatibility
  return 'v2';
}
```

### 3. Base ID Resolution Strategy

Since v3 requires baseId everywhere, implement a resolution mechanism:

```typescript
class BaseIdResolver {
  private cache = new Map<string, string>();  // tableId -> baseId

  async getBaseIdForTable(tableId: string): Promise<string> {
    // Check cache first
    if (this.cache.has(tableId)) {
      return this.cache.get(tableId)!;
    }

    // Fetch all bases and tables to build mapping
    const workspaces = await this.listWorkspaces();
    for (const workspace of workspaces) {
      const bases = await this.listBases(workspace.id);
      for (const base of bases) {
        const tables = await this.listTables(base.id);
        for (const table of tables) {
          this.cache.set(table.id, base.id);
        }
      }
    }

    const baseId = this.cache.get(tableId);
    if (!baseId) {
      throw new Error(`Could not resolve baseId for tableId: ${tableId}`);
    }
    return baseId;
  }

  // Proactively cache when fetching table metadata
  cacheTableBase(tableId: string, baseId: string) {
    this.cache.set(tableId, baseId);
  }
}
```

### 4. Migration Checklist

#### Phase 1: Foundation (Week 1)
- [ ] Create unified client interface
- [ ] Implement version detection
- [ ] Set up base ID resolver
- [ ] Create v2 adapter implementation
- [ ] Write comprehensive tests

#### Phase 2: v3 Implementation (Week 2-3)
- [ ] Implement v3 adapter for record operations
- [ ] Implement v3 adapter for table operations
- [ ] Implement v3 adapter for link operations
- [ ] Implement v3 adapter for view operations
- [ ] Handle terminology changes (column → field)

#### Phase 3: Testing (Week 4)
- [ ] Integration tests against v2 server
- [ ] Integration tests against v3 server
- [ ] Performance benchmarks
- [ ] Error handling verification

#### Phase 4: Deployment (Week 5)
- [ ] Feature flag for v3 support
- [ ] Gradual rollout strategy
- [ ] Monitoring and alerting
- [ ] Documentation updates

### 5. Backward Compatibility Strategy

```typescript
interface ClientConfig {
  baseUrl: string;
  token: string;
  apiVersion?: 'v2' | 'v3' | 'auto';  // Default: 'auto'
  baseId?: string;  // Optional for v2, required for v3 if not using resolver
}

class NocoDBClientV3 implements NocoDBClient {
  private baseIdResolver: BaseIdResolver;

  async getRecords(tableId: string, params?: RecordQueryParams) {
    // Auto-resolve baseId if not provided
    const baseId = this.config.baseId ||
      await this.baseIdResolver.getBaseIdForTable(tableId);

    return this.fetchRecords(baseId, tableId, params);
  }
}
```

### 6. Key Considerations

1. **Performance Impact**
   - Base ID resolution adds overhead if not cached
   - Consider proactive caching during initialization

2. **Error Handling**
   - v3 may return different error structures
   - Normalize errors in adapter layer

3. **Rate Limiting**
   - Check if v3 has different rate limits
   - Implement appropriate retry logic

4. **Authentication**
   - v3 auth endpoints not in OpenAPI spec
   - Verify auth token format compatibility

5. **Query Parameters**
   - Validate that filter/sort syntax is compatible
   - Check pagination format (offset/limit vs cursor-based)

---

## Detailed Endpoint Mappings

### Record Operations Mapping

| Operation | v2 Path | v3 Path | Notes |
|-----------|---------|---------|-------|
| List | `/api/v2/tables/{tableId}/records` | `/api/v3/data/{baseId}/{tableId}/records` | Add baseId param |
| Get | `/api/v2/tables/{tableId}/records/{recordId}` | `/api/v3/data/{baseId}/{tableId}/records/{recordId}` | Add baseId param |
| Create | `/api/v2/tables/{tableId}/records` | `/api/v3/data/{baseId}/{tableId}/records` | Add baseId param |
| Update | `/api/v2/tables/{tableId}/records` | `/api/v3/data/{baseId}/{tableId}/records` | Add baseId param |
| Delete | `/api/v2/tables/{tableId}/records` | `/api/v3/data/{baseId}/{tableId}/records` | Add baseId param |
| Count | `/api/v2/tables/{tableId}/records/count` | `/api/v3/data/{baseId}/{tableId}/count` | Path structure changed |

### Table Operations Mapping

| Operation | v2 Path | v3 Path | Notes |
|-----------|---------|---------|-------|
| List | `/api/v2/meta/bases/{baseId}/tables` | `/api/v3/meta/bases/{baseId}/tables` | Now in 'Data API' spec |
| Get | `/api/v2/meta/tables/{tableId}` | `/api/v3/meta/bases/{baseId}/tables/{tableId}` | Add baseId to path |
| Create | `/api/v2/meta/bases/{baseId}/tables` | `/api/v3/meta/bases/{baseId}/tables` | Now in 'Data API' spec |
| Update | `/api/v2/meta/tables/{tableId}` | `/api/v3/meta/bases/{baseId}/tables/{tableId}` | Add baseId to path |
| Delete | `/api/v2/meta/tables/{tableId}` | `/api/v3/meta/bases/{baseId}/tables/{tableId}` | Add baseId to path |

### View Operations Mapping

| Operation | v2 Path | v3 Path | Notes |
|-----------|---------|---------|-------|
| List | `/api/v2/meta/tables/{tableId}/views` | `/api/v3/meta/bases/{baseId}/tables/{tableId}/views` | Add baseId to path |
| Get | `/api/v2/meta/views/{viewId}` (implicit) | `/api/v3/meta/bases/{baseId}/views/{viewId}` | Add baseId to path |
| Create | `/api/v2/meta/tables/{tableId}/grids` (etc) | `/api/v3/meta/bases/{baseId}/tables/{tableId}/views` | Unified view creation |
| Update | `/api/v2/meta/views/{viewId}` | `/api/v3/meta/bases/{baseId}/views/{viewId}` | Add baseId to path |
| Delete | `/api/v2/meta/views/{viewId}` | `/api/v3/meta/bases/{baseId}/views/{viewId}` | Add baseId to path |
| Filters | `/api/v2/meta/views/{viewId}/filters` | `/api/v3/meta/bases/{baseId}/views/{viewId}/filters` | Add baseId to path |
| Sorts | `/api/v2/meta/views/{viewId}/sorts` | `/api/v3/meta/bases/{baseId}/views/{viewId}/sorts` | Add baseId to path |

### Field/Column Operations Mapping

| Operation | v2 Path | v3 Path | Notes |
|-----------|---------|---------|-------|
| Get | `/api/v2/meta/columns/{columnId}` | `/api/v3/meta/bases/{baseId}/fields/{fieldId}` | Terminology change + baseId |
| Create | `/api/v2/meta/tables/{tableId}/columns` | `/api/v3/meta/bases/{baseId}/tables/{tableId}/fields` | Terminology change + baseId |
| Update | `/api/v2/meta/columns/{columnId}` | `/api/v3/meta/bases/{baseId}/fields/{fieldId}` | Terminology change + baseId |
| Delete | `/api/v2/meta/columns/{columnId}` | `/api/v3/meta/bases/{baseId}/fields/{fieldId}` | Terminology change + baseId |

### Link Operations Mapping

| Operation | v2 Path | v3 Path | Notes |
|-----------|---------|---------|-------|
| List | `/api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | `/api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | Complete restructure |
| Link | `/api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | `/api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | Complete restructure |
| Unlink | `/api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | `/api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | Complete restructure |

---

## Conclusion

The v2 to v3 migration represents a **major breaking change** that requires:

1. **Architectural refactoring** - Not just path changes, but structural changes
2. **Base ID management** - New requirement for all operations
3. **API file swap** - Meta/Data definitions inverted
4. **Terminology updates** - columns → fields
5. **Comprehensive testing** - All endpoints need verification

**Recommended Timeline:** 4-6 weeks for full implementation and testing

**Risk Level:** HIGH - This is not a simple version bump
