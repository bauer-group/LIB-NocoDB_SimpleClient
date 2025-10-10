# NocoDB API v2 to v3 Migration Guide

**Executive Summary for Developers**

---

## Critical Discovery: API File Role Reversal

**The most important finding is that v2 and v3 have INVERTED their API file definitions:**

| Version | "Meta API" File | "Data API" File |
|---------|----------------|----------------|
| **v2** | Schema/Structure operations (137 endpoints) | Record CRUD operations (10 endpoints) |
| **v3** | Record CRUD operations (10 endpoints) | Schema/Structure operations (36 endpoints) |

**This means:**
- What was called "Meta API" in v2 is now called "Data API" in v3
- What was called "Data API" in v2 is now called "Meta API" in v3

**This is NOT just a naming change - you must load the opposite file for equivalent operations!**

---

## Breaking Changes by Priority

### 🔴 CRITICAL - Every endpoint requires baseId

**Impact:** 100% of code must change

All v3 paths now require `baseId` as a path parameter:

```diff
- GET /api/v2/tables/{tableId}/records
+ GET /api/v3/data/{baseId}/{tableId}/records

- GET /api/v2/meta/tables/{tableId}
+ GET /api/v3/meta/bases/{baseId}/tables/{tableId}
```

**Challenge:** v2 code often doesn't track baseId for each tableId.

**Solution:** Implement a baseId resolver or require baseId in all method signatures.

---

### 🔴 CRITICAL - Pagination completely changed

| Aspect | v2 | v3 | Breaking? |
|--------|----|----|-----------|
| **Offset** | `offset=25` | Removed - use `page` | ✅ YES |
| **Limit** | `limit=100` | `pageSize=100` | ✅ YES |
| **Page** | Not available | `page=2` | ✅ YES |
| **Nested Pagination** | Not available | `nestedPage=2` | ⚠️ NEW |

**Migration:**
```typescript
// v2
const params = { offset: 50, limit: 25 };

// v3 equivalent
const params = { page: 3, pageSize: 25 };  // page 3 = skip 50 records
```

---

### 🟡 MEDIUM - Query Parameter Changes

#### Sort Format Changed

**v2 - String format:**
```
sort=field1,-field2
```

**v3 - JSON format:**
```
sort=[{"direction":"asc","field":"field1"},{"direction":"desc","field":"field2"}]
```

#### Fields Format Enhanced

**v2:**
```
fields=field1,field2
```

**v3 - Array or string:**
```
fields=["field1","field2"]  OR  fields=field1,field2
```

#### Where Comparison Operators

| Operator | v2 | v3 | Changed? |
|----------|----|----|----------|
| Not equal | `ne` | `neq` | ✅ YES |
| Others | Same | Same | ❌ NO |

---

### 🔵 LOW - Terminology Changes

| v2 Term | v3 Term |
|---------|---------|
| column | field |
| columnId | fieldId |

---

## Most Used Endpoints Migration

### 1. List Records

```typescript
// v2
GET /api/v2/tables/{tableId}/records
  ?fields=field1,field2
  &sort=field1,-field2
  &where=(field1,eq,value)
  &offset=0
  &limit=100
  &viewId={viewId}

// v3
GET /api/v3/data/{baseId}/{tableId}/records
  ?fields=["field1","field2"]
  &sort=[{"direction":"asc","field":"field1"},{"direction":"desc","field":"field2"}]
  &where=(field1,eq,value)
  &page=1
  &pageSize=100
  &viewId={viewId}
```

**Required Changes:**
1. Add `baseId` to path
2. Change `offset/limit` to `page/pageSize`
3. Update `sort` format to JSON
4. Update `fields` format (optional - string still works)

---

### 2. Get Record

```typescript
// v2
GET /api/v2/tables/{tableId}/records/{recordId}

// v3
GET /api/v3/data/{baseId}/{tableId}/records/{recordId}
```

**Required Changes:**
1. Add `baseId` to path

---

### 3. Create Records

```typescript
// v2
POST /api/v2/tables/{tableId}/records
Body: { field1: value1, field2: value2 }

// v3
POST /api/v3/data/{baseId}/{tableId}/records
Body: (same structure - verify with testing)
```

**Required Changes:**
1. Add `baseId` to path
2. Verify request body structure hasn't changed

---

### 4. Update Records

```typescript
// v2
PATCH /api/v2/tables/{tableId}/records
Body: [{ Id: "rec123", field1: newValue }]

// v3
PATCH /api/v3/data/{baseId}/{tableId}/records
Body: (same structure - verify with testing)
```

**Required Changes:**
1. Add `baseId` to path
2. Verify request body structure (especially `Id` vs `id`)

---

### 5. Delete Records

```typescript
// v2
DELETE /api/v2/tables/{tableId}/records
Body: [{ Id: "rec123" }]

// v3
DELETE /api/v3/data/{baseId}/{tableId}/records
Body: (same structure - verify with testing)
```

**Required Changes:**
1. Add `baseId` to path

---

### 6. Count Records

```typescript
// v2
GET /api/v2/tables/{tableId}/records/count

// v3
GET /api/v3/data/{baseId}/{tableId}/count
```

**Required Changes:**
1. Add `baseId` to path
2. Path structure changed (`/count` not `/records/count`)

---

### 7. List Tables

```typescript
// v2
GET /api/v2/meta/bases/{baseId}/tables

// v3
GET /api/v3/meta/bases/{baseId}/tables
```

**Required Changes:**
1. Load from different OpenAPI file (now in "Data API" spec)
2. Path is the same

---

### 8. Get Table

```typescript
// v2
GET /api/v2/meta/tables/{tableId}

// v3
GET /api/v3/meta/bases/{baseId}/tables/{tableId}
```

**Required Changes:**
1. Add `baseId` to path
2. Load from different OpenAPI file

---

### 9. Link Records

```typescript
// v2
POST /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}
Body: { linkedRecordIds: ["rec1", "rec2"] }

// v3
POST /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}
Body: (verify structure)
```

**Required Changes:**
1. Add `baseId` to path
2. Path structure: removed `/records/` segment

---

### 10. Unlink Records

```typescript
// v2
DELETE /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}
Body: { linkedRecordIds: ["rec1"] }

// v3
DELETE /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}
Body: (verify structure)
```

**Required Changes:**
1. Add `baseId` to path
2. Path structure: removed `/records/` segment

---

## Implementation Strategy

### Option 1: Adapter Pattern (Recommended)

Create a unified interface with version-specific implementations:

```typescript
interface NocoDBRecordOperations {
  list(tableId: string, params?: QueryParams): Promise<RecordList>;
  get(tableId: string, recordId: string): Promise<Record>;
  create(tableId: string, data: RecordData[]): Promise<Record[]>;
  update(tableId: string, updates: RecordUpdate[]): Promise<Record[]>;
  delete(tableId: string, recordIds: string[]): Promise<void>;
}

class V2RecordOperations implements NocoDBRecordOperations {
  async list(tableId: string, params?: QueryParams) {
    // Build v2 URL with offset/limit
    const url = `${this.baseUrl}/api/v2/tables/${tableId}/records`;
    // Convert params to v2 format
    const v2Params = this.convertToV2Params(params);
    return this.fetch(url, v2Params);
  }
}

class V3RecordOperations implements NocoDBRecordOperations {
  constructor(private baseIdResolver: BaseIdResolver) {}

  async list(tableId: string, params?: QueryParams) {
    // Resolve baseId
    const baseId = await this.baseIdResolver.resolve(tableId);
    // Build v3 URL
    const url = `${this.baseUrl}/api/v3/data/${baseId}/${tableId}/records`;
    // Convert params to v3 format
    const v3Params = this.convertToV3Params(params);
    return this.fetch(url, v3Params);
  }

  private convertToV3Params(params?: QueryParams) {
    if (!params) return {};

    return {
      fields: params.fields,  // Already compatible
      sort: this.convertSortToV3(params.sort),
      where: params.where,  // Mostly compatible (check 'ne' → 'neq')
      page: params.page || Math.floor((params.offset || 0) / (params.limit || 25)) + 1,
      pageSize: params.pageSize || params.limit || 25,
      viewId: params.viewId
    };
  }

  private convertSortToV3(sort?: string | object[]): object[] | undefined {
    if (!sort) return undefined;
    if (Array.isArray(sort)) return sort;  // Already v3 format

    // Convert v2 string format to v3 object format
    // "field1,-field2" → [{"direction":"asc","field":"field1"},{"direction":"desc","field":"field2"}]
    return sort.split(',').map(field => {
      const desc = field.startsWith('-');
      return {
        direction: desc ? 'desc' : 'asc',
        field: desc ? field.slice(1) : field
      };
    });
  }
}
```

### Option 2: Query Parameter Adapter

Create middleware to convert query parameters:

```typescript
class QueryParamAdapter {
  convertToV3(v2Params: V2QueryParams): V3QueryParams {
    const { offset, limit, sort, where, ...rest } = v2Params;

    return {
      ...rest,
      page: offset !== undefined ? Math.floor(offset / (limit || 25)) + 1 : undefined,
      pageSize: limit,
      sort: typeof sort === 'string' ? this.convertSort(sort) : sort,
      where: where?.replace(/,ne,/g, ',neq,')  // Fix operator
    };
  }

  convertSort(sortString: string): SortObject[] {
    return sortString.split(',').map(field => {
      const desc = field.startsWith('-');
      return {
        direction: desc ? 'desc' : 'asc',
        field: desc ? field.slice(1) : field
      };
    });
  }
}
```

### Option 3: Base ID Resolution

Implement caching strategy for baseId lookup:

```typescript
class BaseIdResolver {
  private cache = new Map<string, string>();  // tableId → baseId
  private cacheTime = new Map<string, number>();
  private TTL = 3600000;  // 1 hour

  async resolve(tableId: string): Promise<string> {
    // Check cache
    const cached = this.cache.get(tableId);
    const cacheAge = Date.now() - (this.cacheTime.get(tableId) || 0);

    if (cached && cacheAge < this.TTL) {
      return cached;
    }

    // Fetch from API
    // Option A: If you have workspace/base context
    if (this.currentBaseId) {
      this.cache.set(tableId, this.currentBaseId);
      this.cacheTime.set(tableId, Date.now());
      return this.currentBaseId;
    }

    // Option B: Fetch table metadata (if available in v3)
    // This depends on whether there's a v3 endpoint that returns baseId for a tableId

    // Option C: Fetch all bases and build complete mapping
    await this.buildCompleteMapping();

    const baseId = this.cache.get(tableId);
    if (!baseId) {
      throw new Error(`Cannot resolve baseId for table ${tableId}`);
    }

    return baseId;
  }

  async buildCompleteMapping(): Promise<void> {
    const workspaces = await this.api.listWorkspaces();
    for (const workspace of workspaces) {
      const bases = await this.api.listBases(workspace.id);
      for (const base of bases) {
        const tables = await this.api.listTables(base.id);
        for (const table of tables) {
          this.cache.set(table.id, base.id);
          this.cacheTime.set(table.id, Date.now());
        }
      }
    }
  }

  // Call this whenever you fetch table metadata
  cacheMapping(tableId: string, baseId: string): void {
    this.cache.set(tableId, baseId);
    this.cacheTime.set(tableId, Date.now());
  }
}
```

---

## Testing Checklist

### Record Operations
- [ ] List records with all query parameters
- [ ] List records with pagination (verify page calculation)
- [ ] List records with sorting (verify JSON format)
- [ ] List records with filtering (verify 'neq' operator)
- [ ] Get single record
- [ ] Create single record
- [ ] Create multiple records
- [ ] Update single record
- [ ] Update multiple records
- [ ] Delete single record
- [ ] Delete multiple records
- [ ] Count records

### Table Operations
- [ ] List tables in base
- [ ] Get table schema
- [ ] Create table
- [ ] Update table
- [ ] Delete table

### Link Operations
- [ ] Link records
- [ ] Unlink records
- [ ] List linked records
- [ ] Verify path structure (no `/records/` segment)

### View Operations
- [ ] List views
- [ ] Get view
- [ ] List records with viewId
- [ ] Verify view filtering works
- [ ] Verify view sorting works

### Field Operations
- [ ] Get field (verify 'field' terminology)
- [ ] Create field
- [ ] Update field
- [ ] Delete field

### Error Handling
- [ ] Verify error response structure
- [ ] Test rate limiting
- [ ] Test authentication errors
- [ ] Test not found errors

### Pagination
- [ ] Verify page 1 returns first N records
- [ ] Verify page 2 returns next N records
- [ ] Verify pageSize works correctly
- [ ] Compare with v2 offset/limit results

---

## Common Pitfalls

### 1. Forgetting baseId
```typescript
// ❌ Will fail in v3
const url = `/api/v3/data/${tableId}/records`;

// ✅ Correct
const baseId = await resolver.resolve(tableId);
const url = `/api/v3/data/${baseId}/${tableId}/records`;
```

### 2. Using old pagination
```typescript
// ❌ v3 doesn't support offset/limit
const params = { offset: 25, limit: 100 };

// ✅ Use page/pageSize
const params = { page: 2, pageSize: 100 };
```

### 3. Using wrong sort format
```typescript
// ❌ String format may not work consistently in v3
const params = { sort: 'field1,-field2' };

// ✅ Use JSON format
const params = {
  sort: [
    { direction: 'asc', field: 'field1' },
    { direction: 'desc', field: 'field2' }
  ]
};
```

### 4. Using 'ne' instead of 'neq'
```typescript
// ❌ v3 uses 'neq' for not equal
where=(field1,ne,value)

// ✅ Correct operator
where=(field1,neq,value)
```

### 5. Loading from wrong OpenAPI file
```typescript
// ❌ v3 structure is inverted
// Don't assume "Meta API" has schema operations

// ✅ Check the actual endpoints in each file
// v3: Meta API = records, Data API = schema
```

---

## Quick Reference

### Path Changes Summary

| Operation | v2 Path | v3 Path |
|-----------|---------|---------|
| List Records | `/api/v2/tables/{tableId}/records` | `/api/v3/data/{baseId}/{tableId}/records` |
| Get Record | `/api/v2/tables/{tableId}/records/{id}` | `/api/v3/data/{baseId}/{tableId}/records/{id}` |
| Create | `/api/v2/tables/{tableId}/records` | `/api/v3/data/{baseId}/{tableId}/records` |
| Update | `/api/v2/tables/{tableId}/records` | `/api/v3/data/{baseId}/{tableId}/records` |
| Delete | `/api/v2/tables/{tableId}/records` | `/api/v3/data/{baseId}/{tableId}/records` |
| Count | `/api/v2/tables/{tableId}/records/count` | `/api/v3/data/{baseId}/{tableId}/count` |
| Link | `/api/v2/tables/{tableId}/links/{fieldId}/records/{id}` | `/api/v3/data/{baseId}/{tableId}/links/{fieldId}/{id}` |
| List Tables | `/api/v2/meta/bases/{baseId}/tables` | `/api/v3/meta/bases/{baseId}/tables` |
| Get Table | `/api/v2/meta/tables/{tableId}` | `/api/v3/meta/bases/{baseId}/tables/{tableId}` |

### Parameter Migration

| v2 | v3 | Notes |
|----|----|----|
| `offset=N` | `page=M` | page = floor(offset/pageSize) + 1 |
| `limit=N` | `pageSize=N` | Direct replacement |
| `sort=f1,-f2` | `sort=[{...}]` | Convert to JSON array |
| `where=(...,ne,...)` | `where=(...,neq,...)` | Operator change |

---

## Timeline Estimate

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Analysis** | 1 week | Review all endpoint usage, identify dependencies |
| **Architecture** | 1 week | Design adapter layer, base ID resolution |
| **Implementation** | 2-3 weeks | Implement v3 support, conversion utilities |
| **Testing** | 2 weeks | Integration tests, manual testing, edge cases |
| **Deployment** | 1 week | Feature flag, gradual rollout, monitoring |
| **Total** | **7-9 weeks** | For complete dual-version support |

---

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Base ID resolution fails | HIGH | MEDIUM | Cache baseId proactively, add fallbacks |
| Query parameter incompatibility | HIGH | MEDIUM | Comprehensive conversion layer, extensive testing |
| Response schema changes | MEDIUM | MEDIUM | Version-specific response parsers |
| Performance degradation | MEDIUM | LOW | Optimize base ID caching, benchmark both versions |
| Authentication incompatibility | HIGH | LOW | Verify token format early, test auth flows |

---

## Resources

- **Full Comparison Report:** `NOCODB_API_V2_V3_COMPARISON.md`
- **Schema Analysis:** `NOCODB_API_SCHEMA_COMPARISON.md`
- **OpenAPI Specs:**
  - v2 Meta: `docs/nocodb-openapi-meta.json`
  - v2 Data: `docs/nocodb-openapi-data.json`
  - v3 Meta: `docs/nocodb-openapi-meta-v3.json`
  - v3 Data: `docs/nocodb-openapi-data-v3.json`

---

## Conclusion

The v2 to v3 migration is a **major breaking change** requiring significant code modifications. The most critical changes are:

1. **baseId now required in all paths**
2. **Pagination completely redesigned** (offset/limit → page/pageSize)
3. **API file definitions inverted** (Meta ↔ Data)
4. **Sort format changed** to JSON
5. **Path structures modified** for several operations

**Recommendation:** Implement adapter pattern with automatic version detection to maintain backward compatibility while adding v3 support.

**Estimated Effort:** 7-9 weeks for complete implementation and testing.
