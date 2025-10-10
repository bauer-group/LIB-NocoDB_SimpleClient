# NocoDB API v2 to v3 Comprehensive Comparison Report

**Generated:** 2025-10-10 11:21:10

## Executive Summary

### Meta API Changes
- **Removed Endpoints:** 137
- **New Endpoints:** 10
- **Potentially Renamed:** 0
- **Unchanged:** 0

### Data API Changes
- **Removed Endpoints:** 10
- **New Endpoints:** 36
- **Potentially Renamed:** 0
- **Unchanged:** 0

---

## Meta API: v2 → v3 Differences

### Removed Endpoints

#### Authentication

| Method | Path | Summary |
|--------|------|---------|
| `GET` | `/api/v2/auth/user/me` | Get User Info |
| `POST` | `/api/v2/auth/email/validate/{token}` | Verify Email |
| `POST` | `/api/v2/auth/password/change` | Change Password |
| `POST` | `/api/v2/auth/password/forgot` | Forget Password |
| `POST` | `/api/v2/auth/password/reset/{token}` | Reset Password |
| `POST` | `/api/v2/auth/token/refresh` | Refresh Token |
| `POST` | `/api/v2/auth/token/validate/{token}` | Verify Reset Token |
| `POST` | `/api/v2/auth/user/signin` | Signin |
| `POST` | `/api/v2/auth/user/signout` | Signout |
| `POST` | `/api/v2/auth/user/signup` | Signup |

#### Column/Field Operations

| Method | Path | Summary |
|--------|------|---------|
| `DELETE` | `/api/v2/meta/columns/{columnId}` | Delete Column |
| `GET` | `/api/v2/meta/columns/{columnId}` | Get Column Metadata |
| `GET` | `/api/v2/meta/views/{viewId}/columns` | List View Columns |
| `PATCH` | `/api/v2/meta/columns/{columnId}` | Update Column |
| `PATCH` | `/api/v2/meta/views/{viewId}/columns/{columnId}` | Update View Column |
| `POST` | `/api/v2/meta/columns/{columnId}/primary` | Create Primary Value |
| `POST` | `/api/v2/meta/views/{viewId}/columns` | Create Column in View |

#### File Operations

| Method | Path | Summary |
|--------|------|---------|
| `POST` | `/api/v2/storage/upload` | Attachment Upload |

#### Meta Operations

| Method | Path | Summary |
|--------|------|---------|
| `DELETE` | `/api/v2/meta/bases/{baseId}` | Delete Base |
| `DELETE` | `/api/v2/meta/bases/{baseId}/api-tokens/{tokenId}` | Delete API Token |
| `DELETE` | `/api/v2/meta/bases/{baseId}/shared` | Delete Base Shared Base |
| `DELETE` | `/api/v2/meta/bases/{baseId}/sources/{sourceId}` | Delete Source |
| `DELETE` | `/api/v2/meta/bases/{baseId}/sources/{sourceId}/share/erd` |  |
| `DELETE` | `/api/v2/meta/bases/{baseId}/users/{userId}` | Delete Base User |
| `DELETE` | `/api/v2/meta/cache` | Delete Cache |
| `DELETE` | `/api/v2/meta/comment/{commentId}` | Delete Comment |
| `DELETE` | `/api/v2/meta/filters/{filterId}` | Delete Filter |
| `DELETE` | `/api/v2/meta/sorts/{sortId}` | Delete Sort |
| `DELETE` | `/api/v2/meta/workspaces/{workspaceId}` | Delete workspace ☁ |
| `DELETE` | `/api/v2/meta/workspaces/{workspaceId}/users/{userId}` | Delete workspace user ☁ |
| `GET` | `/api/v2/meta/bases/` | List Bases (OSS) |
| `GET` | `/api/v2/meta/bases/{baseId}` | Get Base Schema |
| `GET` | `/api/v2/meta/bases/{baseId}/api-tokens` | List API Tokens in Base |
| `GET` | `/api/v2/meta/bases/{baseId}/cost` | Base Cost |
| `GET` | `/api/v2/meta/bases/{baseId}/has-empty-or-null-filters` | List Empty & Null Filter |
| `GET` | `/api/v2/meta/bases/{baseId}/info` | Get Base info |
| `GET` | `/api/v2/meta/bases/{baseId}/meta-diff` | Meta Diff |
| `GET` | `/api/v2/meta/bases/{baseId}/meta-diff/{sourceId}` | Source Meta Diff |
| `GET` | `/api/v2/meta/bases/{baseId}/shared` | Get Base Shared Base |
| `GET` | `/api/v2/meta/bases/{baseId}/sources/` | List Sources |
| `GET` | `/api/v2/meta/bases/{baseId}/sources/{sourceId}` | Get Source Schema |
| `GET` | `/api/v2/meta/bases/{baseId}/users` | List Base Users |
| `GET` | `/api/v2/meta/bases/{baseId}/visibility-rules` | Get UI ACL |
| `GET` | `/api/v2/meta/cache` | Get Cache |
| `GET` | `/api/v2/meta/comments` | List Comments |
| `GET` | `/api/v2/meta/comments/count` | Count Comments |
| `GET` | `/api/v2/meta/filters/{filterGroupId}/children` | Get Filter Group Children |
| `GET` | `/api/v2/meta/filters/{filterId}` | Get Filter Metadata |
| `GET` | `/api/v2/meta/forms/{formViewId}` | Get Form View Metadata |
| `GET` | `/api/v2/meta/galleries/{galleryViewId}` | Get Gallery View Metadata |
| `GET` | `/api/v2/meta/grids/{gridId}/grid-columns` | List Grid View Columns |
| `GET` | `/api/v2/meta/kanbans/{kanbanViewId}` | Get Kanban View Metadata |
| `GET` | `/api/v2/meta/maps/{mapViewId}` | Get Map View |
| `GET` | `/api/v2/meta/nocodb/info` | Get App Info |
| `GET` | `/api/v2/meta/sorts/{sortId}` | Get Sort Metadata |
| `GET` | `/api/v2/meta/workspaces` | List workspaces ☁ |
| `GET` | `/api/v2/meta/workspaces/{workspaceId}` | Read workspace ☁ |
| `GET` | `/api/v2/meta/workspaces/{workspaceId}/bases` | List Bases |
| `GET` | `/api/v2/meta/workspaces/{workspaceId}/users` | Workspace users list ☁ |
| `GET` | `/api/v2/meta/workspaces/{workspaceId}/users/{userId}` | Workspace user read ☁ |
| `PATCH` | `/api/v2/meta/bases/{baseId}` | Update Base |
| `PATCH` | `/api/v2/meta/bases/{baseId}/shared` | Update Base Shared Base |
| `PATCH` | `/api/v2/meta/bases/{baseId}/sources/{sourceId}` | Update Source |
| `PATCH` | `/api/v2/meta/bases/{baseId}/user` | Base user meta update |
| `PATCH` | `/api/v2/meta/bases/{baseId}/users/{userId}` | Update Base User |
| `PATCH` | `/api/v2/meta/comment/{commentId}` | Update Comment |
| `PATCH` | `/api/v2/meta/filters/{filterId}` | Update Filter |
| `PATCH` | `/api/v2/meta/form-columns/{formViewColumnId}` | Update Form View Column |
| `PATCH` | `/api/v2/meta/forms/{formViewId}` | Update Form View |
| `PATCH` | `/api/v2/meta/galleries/{galleryViewId}` | Update Gallery View |
| `PATCH` | `/api/v2/meta/grid-columns/{columnId}` | Update Grid View Column |
| `PATCH` | `/api/v2/meta/grids/{viewId}` | Update Grid View |
| `PATCH` | `/api/v2/meta/kanbans/{kanbanViewId}` | Update Kanban View |
| `PATCH` | `/api/v2/meta/maps/{mapViewId}` | Update Map View |
| `PATCH` | `/api/v2/meta/sorts/{sortId}` | Update Sort |
| `PATCH` | `/api/v2/meta/user/profile` | Update User Profile |
| `PATCH` | `/api/v2/meta/workspaces/{workspaceId}` | Update workspace ☁ |
| `PATCH` | `/api/v2/meta/workspaces/{workspaceId}/users/{userId}` | Update workspace user ☁ |
| `POST` | `/api/v2/meta/axiosRequestMake` | Axios Request |
| `POST` | `/api/v2/meta/bases/` | Create Base (OSS) |
| `POST` | `/api/v2/meta/bases/{baseId}/api-tokens` | Create API Token |
| `POST` | `/api/v2/meta/bases/{baseId}/meta-diff` | Sync Meta |
| `POST` | `/api/v2/meta/bases/{baseId}/meta-diff/{sourceId}` | Synchronise Source Meta |
| `POST` | `/api/v2/meta/bases/{baseId}/shared` | Create Base Shared Base |
| `POST` | `/api/v2/meta/bases/{baseId}/sources/` | Create Source |
| `POST` | `/api/v2/meta/bases/{baseId}/sources/{sourceId}/share/erd` | share ERD view |
| `POST` | `/api/v2/meta/bases/{baseId}/users` | Create Base User |
| `POST` | `/api/v2/meta/bases/{baseId}/users/{userId}/resend-invite` | Resend User Invitation |
| `POST` | `/api/v2/meta/bases/{baseId}/visibility-rules` | Create UI ACL |
| `POST` | `/api/v2/meta/comments` | Add Comment |
| `POST` | `/api/v2/meta/connection/test` | Test DB Connection |
| `POST` | `/api/v2/meta/duplicate/{baseId}` | Duplicate Base |
| `POST` | `/api/v2/meta/duplicate/{baseId}/{sourceId}` | Duplicate Base Source |
| `POST` | `/api/v2/meta/workspaces` | Create workspaces ☁ |
| `POST` | `/api/v2/meta/workspaces/{workspaceId}/bases` | Create Base |
| `POST` | `/api/v2/meta/workspaces/{workspaceId}/invitations` | Workspace user invite ☁ |

#### Other

| Method | Path | Summary |
|--------|------|---------|
| `POST` | `/api/v2/export/{viewId}/{exportAs}` | Trigger export as job |
| `POST` | `/api/v2/jobs/{baseId}` | Get Jobs |

#### Table Operations

| Method | Path | Summary |
|--------|------|---------|
| `DELETE` | `/api/v2/meta/tables/{tableId}` | Delete Table |
| `GET` | `/api/v2/meta/bases/{baseId}/tables` | List Tables |
| `GET` | `/api/v2/meta/bases/{baseId}/{sourceId}/tables` | List Tables |
| `GET` | `/api/v2/meta/tables/{tableId}` | Get Table Metadata |
| `GET` | `/api/v2/meta/tables/{tableId}/columns/hash` | Get columns hash for table |
| `GET` | `/api/v2/meta/tables/{tableId}/hooks` | List Table Hooks |
| `GET` | `/api/v2/meta/tables/{tableId}/hooks/samplePayload/{operation}/{version}` | Get Sample Hook Payload |
| `GET` | `/api/v2/meta/tables/{tableId}/share` | List Shared Views |
| `GET` | `/api/v2/meta/tables/{tableId}/views` | List Views |
| `PATCH` | `/api/v2/meta/tables/{tableId}` | Update Table |
| `POST` | `/api/v2/meta/bases/{baseId}/tables` | Create Table |
| `POST` | `/api/v2/meta/bases/{baseId}/{sourceId}/tables` | Create Table |
| `POST` | `/api/v2/meta/duplicate/{baseId}/table/{tableId}` | Duplicate Table |
| `POST` | `/api/v2/meta/tables/{tableId}/columns` | Create Column |
| `POST` | `/api/v2/meta/tables/{tableId}/columns/bulk` | Bulk create-update-delete columns |
| `POST` | `/api/v2/meta/tables/{tableId}/forms` | Create Form View |
| `POST` | `/api/v2/meta/tables/{tableId}/galleries` | Create Gallery View |
| `POST` | `/api/v2/meta/tables/{tableId}/grids` | Create Grid View |
| `POST` | `/api/v2/meta/tables/{tableId}/hooks` | Create Table Hook |
| `POST` | `/api/v2/meta/tables/{tableId}/hooks/test` | Test Hook |
| `POST` | `/api/v2/meta/tables/{tableId}/kanbans` | Create Kanban View |
| `POST` | `/api/v2/meta/tables/{tableId}/maps` | Create Map View |
| `POST` | `/api/v2/meta/tables/{tableId}/reorder` | Reorder Table |

#### View Operations

| Method | Path | Summary |
|--------|------|---------|
| `DELETE` | `/api/v2/meta/views/{viewId}` | Delete View |
| `DELETE` | `/api/v2/meta/views/{viewId}/share` | Delete Shared View |
| `GET` | `/api/v2/meta/views/{viewId}/filters` | List View Filters |
| `GET` | `/api/v2/meta/views/{viewId}/sorts` | List View Sorts |
| `PATCH` | `/api/v2/meta/views/{viewId}` | Update View |
| `PATCH` | `/api/v2/meta/views/{viewId}/share` | Update Shared View |
| `POST` | `/api/v2/meta/views/{viewId}/filters` | Create View Filter |
| `POST` | `/api/v2/meta/views/{viewId}/hide-all` | Hide All Columns In View |
| `POST` | `/api/v2/meta/views/{viewId}/share` | Create Shared View |
| `POST` | `/api/v2/meta/views/{viewId}/show-all` | Show All Columns In View |
| `POST` | `/api/v2/meta/views/{viewId}/sorts` | Create View Sort |

#### Webhook Operations

| Method | Path | Summary |
|--------|------|---------|
| `DELETE` | `/api/v2/meta/hooks/{hookId}` | Delete Table Hook |
| `GET` | `/api/v2/meta/hooks/{hookId}/filters` | Get Table Hook Filter |
| `GET` | `/api/v2/meta/hooks/{hookId}/logs` | List Hook Logs |
| `PATCH` | `/api/v2/meta/hooks/{hookId}` | Update Table Hook |
| `POST` | `/api/v2/meta/hooks/{hookId}/filters` | Create Table Hook Filter |

### New Endpoints

#### Record Operations

| Method | Path | Summary |
|--------|------|---------|
| `DELETE` | `/api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | Unlink Records |
| `DELETE` | `/api/v3/data/{baseId}/{tableId}/records` | Delete Table Records |
| `GET` | `/api/v3/data/{baseId}/{tableId}/count` | Count Table Records |
| `GET` | `/api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | List Linked Records |
| `GET` | `/api/v3/data/{baseId}/{tableId}/records` | List Table Records |
| `GET` | `/api/v3/data/{baseId}/{tableId}/records/{recordId}` | Read Table Record |
| `PATCH` | `/api/v3/data/{baseId}/{tableId}/records` | Update Table Records |
| `POST` | `/api/v3/data/{baseId}/{modelId}/records/{recordId}/fields/{fieldId}/upload` | Upload Attachment to Cell |
| `POST` | `/api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | Link Records |
| `POST` | `/api/v3/data/{baseId}/{tableId}/records` | Create Table Records |

---

## Data API: v2 → v3 Differences

### Removed Endpoints

#### File Operations

| Method | Path | Summary |
|--------|------|---------|
| `POST` | `/api/v2/storage/upload` | Attachment Upload |

#### Table Operations

| Method | Path | Summary |
|--------|------|---------|
| `DELETE` | `/api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | Unlink Records |
| `DELETE` | `/api/v2/tables/{tableId}/records` | Delete Table Records |
| `GET` | `/api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | List Linked Records |
| `GET` | `/api/v2/tables/{tableId}/records` | List Table Records |
| `GET` | `/api/v2/tables/{tableId}/records/count` | Count Table Records |
| `GET` | `/api/v2/tables/{tableId}/records/{recordId}` | Read Table Record |
| `PATCH` | `/api/v2/tables/{tableId}/records` | Update Table Records |
| `POST` | `/api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}` | Link Records |
| `POST` | `/api/v2/tables/{tableId}/records` | Create Table Records |

### New Endpoints

#### Column/Field Operations

| Method | Path | Summary |
|--------|------|---------|
| `DELETE` | `/api/v3/meta/bases/{baseId}/fields/{fieldId}` | Delete field |
| `GET` | `/api/v3/meta/bases/{baseId}/fields/{fieldId}` | Get field |
| `PATCH` | `/api/v3/meta/bases/{baseId}/fields/{fieldId}` | Update field |

#### Meta Operations

| Method | Path | Summary |
|--------|------|---------|
| `DELETE` | `/api/v3/meta/bases/{baseId}` | Delete base |
| `DELETE` | `/api/v3/meta/bases/{base_id}/members` | Delete base members |
| `DELETE` | `/api/v3/meta/workspaces/{workspaceId}/members` | Delete workspace members |
| `GET` | `/api/v3/meta/bases/{baseId}` | Get base meta |
| `GET` | `/api/v3/meta/bases/{baseId}?include[]=members` | List base members |
| `GET` | `/api/v3/meta/workspaces/{workspaceId}/bases` | List bases |
| `GET` | `/api/v3/meta/workspaces/{workspaceId}?include[]=members` | List workspace members |
| `PATCH` | `/api/v3/meta/bases/{baseId}` | Update base |
| `PATCH` | `/api/v3/meta/bases/{base_id}/members` | Update base members |
| `PATCH` | `/api/v3/meta/workspaces/{workspaceId}/members` | Update workspace members |
| `POST` | `/api/v3/meta/bases/{base_id}/members` | Invite base members |
| `POST` | `/api/v3/meta/workspaces/{workspaceId}/bases` | Create base |
| `POST` | `/api/v3/meta/workspaces/{workspaceId}/members` | Add workspace members |

#### Table Operations

| Method | Path | Summary |
|--------|------|---------|
| `DELETE` | `/api/v3/meta/bases/{baseId}/tables/{tableId}` | Delete table |
| `GET` | `/api/v3/meta/bases/{baseId}/tables/{tableId}` | Get table schema |
| `GET` | `/api/v3/meta/bases/{baseId}/tables/{tableId}/views` | List views |
| `GET` | `/api/v3/meta/bases/{base_id}/tables` | List tables |
| `PATCH` | `/api/v3/meta/bases/{baseId}/tables/{tableId}` | Update table |
| `POST` | `/api/v3/meta/bases/{baseId}/tables/{tableId}/fields` | Create field |
| `POST` | `/api/v3/meta/bases/{baseId}/tables/{tableId}/views` | Create view |
| `POST` | `/api/v3/meta/bases/{base_id}/tables` | Create table |

#### View Operations

| Method | Path | Summary |
|--------|------|---------|
| `DELETE` | `/api/v3/meta/bases/{baseId}/views/{viewId}` | Delete view |
| `DELETE` | `/api/v3/meta/bases/{baseId}/views/{viewId}/filters` | Delete filter |
| `DELETE` | `/api/v3/meta/bases/{baseId}/views/{viewId}/sorts` | Delete sort |
| `GET` | `/api/v3/meta/bases/{baseId}/views/{viewId}` | Get view schema |
| `GET` | `/api/v3/meta/bases/{baseId}/views/{viewId}/filters` | List view filters |
| `GET` | `/api/v3/meta/bases/{baseId}/views/{viewId}/sorts` | List view sorts |
| `PATCH` | `/api/v3/meta/bases/{baseId}/views/{viewId}` | Update view |
| `PATCH` | `/api/v3/meta/bases/{baseId}/views/{viewId}/filters` | Update filter |
| `PATCH` | `/api/v3/meta/bases/{baseId}/views/{viewId}/sorts` | Update sort |
| `POST` | `/api/v3/meta/bases/{baseId}/views/{viewId}/filters` | Create filter |
| `POST` | `/api/v3/meta/bases/{baseId}/views/{viewId}/sorts` | Add sort |
| `PUT` | `/api/v3/meta/bases/{baseId}/views/{viewId}/filters` | Replace filter |

---

## Breaking Changes Summary

These changes will require code modifications:

### Meta API Breaking Changes
#### Authentication
- **Removed:** `GET /api/v2/auth/user/me`
- **Removed:** `POST /api/v2/auth/email/validate/{token}`
- **Removed:** `POST /api/v2/auth/password/change`
- **Removed:** `POST /api/v2/auth/password/forgot`
- **Removed:** `POST /api/v2/auth/password/reset/{token}`
- **Removed:** `POST /api/v2/auth/token/refresh`
- **Removed:** `POST /api/v2/auth/token/validate/{token}`
- **Removed:** `POST /api/v2/auth/user/signin`
- **Removed:** `POST /api/v2/auth/user/signout`
- **Removed:** `POST /api/v2/auth/user/signup`

#### Column/Field Operations
- **Removed:** `DELETE /api/v2/meta/columns/{columnId}`
- **Removed:** `GET /api/v2/meta/columns/{columnId}`
- **Removed:** `GET /api/v2/meta/views/{viewId}/columns`
- **Removed:** `PATCH /api/v2/meta/columns/{columnId}`
- **Removed:** `PATCH /api/v2/meta/views/{viewId}/columns/{columnId}`
- **Removed:** `POST /api/v2/meta/columns/{columnId}/primary`
- **Removed:** `POST /api/v2/meta/views/{viewId}/columns`

#### File Operations
- **Removed:** `POST /api/v2/storage/upload`

#### Meta Operations
- **Removed:** `DELETE /api/v2/meta/bases/{baseId}`
- **Removed:** `DELETE /api/v2/meta/bases/{baseId}/api-tokens/{tokenId}`
- **Removed:** `DELETE /api/v2/meta/bases/{baseId}/shared`
- **Removed:** `DELETE /api/v2/meta/bases/{baseId}/sources/{sourceId}`
- **Removed:** `DELETE /api/v2/meta/bases/{baseId}/sources/{sourceId}/share/erd`
- **Removed:** `DELETE /api/v2/meta/bases/{baseId}/users/{userId}`
- **Removed:** `DELETE /api/v2/meta/cache`
- **Removed:** `DELETE /api/v2/meta/comment/{commentId}`
- **Removed:** `DELETE /api/v2/meta/filters/{filterId}`
- **Removed:** `DELETE /api/v2/meta/sorts/{sortId}`
- **Removed:** `DELETE /api/v2/meta/workspaces/{workspaceId}`
- **Removed:** `DELETE /api/v2/meta/workspaces/{workspaceId}/users/{userId}`
- **Removed:** `GET /api/v2/meta/bases/`
- **Removed:** `GET /api/v2/meta/bases/{baseId}`
- **Removed:** `GET /api/v2/meta/bases/{baseId}/api-tokens`
- **Removed:** `GET /api/v2/meta/bases/{baseId}/cost`
- **Removed:** `GET /api/v2/meta/bases/{baseId}/has-empty-or-null-filters`
- **Removed:** `GET /api/v2/meta/bases/{baseId}/info`
- **Removed:** `GET /api/v2/meta/bases/{baseId}/meta-diff`
- **Removed:** `GET /api/v2/meta/bases/{baseId}/meta-diff/{sourceId}`
- **Removed:** `GET /api/v2/meta/bases/{baseId}/shared`
- **Removed:** `GET /api/v2/meta/bases/{baseId}/sources/`
- **Removed:** `GET /api/v2/meta/bases/{baseId}/sources/{sourceId}`
- **Removed:** `GET /api/v2/meta/bases/{baseId}/users`
- **Removed:** `GET /api/v2/meta/bases/{baseId}/visibility-rules`
- **Removed:** `GET /api/v2/meta/cache`
- **Removed:** `GET /api/v2/meta/comments`
- **Removed:** `GET /api/v2/meta/comments/count`
- **Removed:** `GET /api/v2/meta/filters/{filterGroupId}/children`
- **Removed:** `GET /api/v2/meta/filters/{filterId}`
- **Removed:** `GET /api/v2/meta/forms/{formViewId}`
- **Removed:** `GET /api/v2/meta/galleries/{galleryViewId}`
- **Removed:** `GET /api/v2/meta/grids/{gridId}/grid-columns`
- **Removed:** `GET /api/v2/meta/kanbans/{kanbanViewId}`
- **Removed:** `GET /api/v2/meta/maps/{mapViewId}`
- **Removed:** `GET /api/v2/meta/nocodb/info`
- **Removed:** `GET /api/v2/meta/sorts/{sortId}`
- **Removed:** `GET /api/v2/meta/workspaces`
- **Removed:** `GET /api/v2/meta/workspaces/{workspaceId}`
- **Removed:** `GET /api/v2/meta/workspaces/{workspaceId}/bases`
- **Removed:** `GET /api/v2/meta/workspaces/{workspaceId}/users`
- **Removed:** `GET /api/v2/meta/workspaces/{workspaceId}/users/{userId}`
- **Removed:** `PATCH /api/v2/meta/bases/{baseId}`
- **Removed:** `PATCH /api/v2/meta/bases/{baseId}/shared`
- **Removed:** `PATCH /api/v2/meta/bases/{baseId}/sources/{sourceId}`
- **Removed:** `PATCH /api/v2/meta/bases/{baseId}/user`
- **Removed:** `PATCH /api/v2/meta/bases/{baseId}/users/{userId}`
- **Removed:** `PATCH /api/v2/meta/comment/{commentId}`
- **Removed:** `PATCH /api/v2/meta/filters/{filterId}`
- **Removed:** `PATCH /api/v2/meta/form-columns/{formViewColumnId}`
- **Removed:** `PATCH /api/v2/meta/forms/{formViewId}`
- **Removed:** `PATCH /api/v2/meta/galleries/{galleryViewId}`
- **Removed:** `PATCH /api/v2/meta/grid-columns/{columnId}`
- **Removed:** `PATCH /api/v2/meta/grids/{viewId}`
- **Removed:** `PATCH /api/v2/meta/kanbans/{kanbanViewId}`
- **Removed:** `PATCH /api/v2/meta/maps/{mapViewId}`
- **Removed:** `PATCH /api/v2/meta/sorts/{sortId}`
- **Removed:** `PATCH /api/v2/meta/user/profile`
- **Removed:** `PATCH /api/v2/meta/workspaces/{workspaceId}`
- **Removed:** `PATCH /api/v2/meta/workspaces/{workspaceId}/users/{userId}`
- **Removed:** `POST /api/v2/meta/axiosRequestMake`
- **Removed:** `POST /api/v2/meta/bases/`
- **Removed:** `POST /api/v2/meta/bases/{baseId}/api-tokens`
- **Removed:** `POST /api/v2/meta/bases/{baseId}/meta-diff`
- **Removed:** `POST /api/v2/meta/bases/{baseId}/meta-diff/{sourceId}`
- **Removed:** `POST /api/v2/meta/bases/{baseId}/shared`
- **Removed:** `POST /api/v2/meta/bases/{baseId}/sources/`
- **Removed:** `POST /api/v2/meta/bases/{baseId}/sources/{sourceId}/share/erd`
- **Removed:** `POST /api/v2/meta/bases/{baseId}/users`
- **Removed:** `POST /api/v2/meta/bases/{baseId}/users/{userId}/resend-invite`
- **Removed:** `POST /api/v2/meta/bases/{baseId}/visibility-rules`
- **Removed:** `POST /api/v2/meta/comments`
- **Removed:** `POST /api/v2/meta/connection/test`
- **Removed:** `POST /api/v2/meta/duplicate/{baseId}`
- **Removed:** `POST /api/v2/meta/duplicate/{baseId}/{sourceId}`
- **Removed:** `POST /api/v2/meta/workspaces`
- **Removed:** `POST /api/v2/meta/workspaces/{workspaceId}/bases`
- **Removed:** `POST /api/v2/meta/workspaces/{workspaceId}/invitations`

#### Other
- **Removed:** `POST /api/v2/export/{viewId}/{exportAs}`
- **Removed:** `POST /api/v2/jobs/{baseId}`

#### Table Operations
- **Removed:** `DELETE /api/v2/meta/tables/{tableId}`
- **Removed:** `GET /api/v2/meta/bases/{baseId}/tables`
- **Removed:** `GET /api/v2/meta/bases/{baseId}/{sourceId}/tables`
- **Removed:** `GET /api/v2/meta/tables/{tableId}`
- **Removed:** `GET /api/v2/meta/tables/{tableId}/columns/hash`
- **Removed:** `GET /api/v2/meta/tables/{tableId}/hooks`
- **Removed:** `GET /api/v2/meta/tables/{tableId}/hooks/samplePayload/{operation}/{version}`
- **Removed:** `GET /api/v2/meta/tables/{tableId}/share`
- **Removed:** `GET /api/v2/meta/tables/{tableId}/views`
- **Removed:** `PATCH /api/v2/meta/tables/{tableId}`
- **Removed:** `POST /api/v2/meta/bases/{baseId}/tables`
- **Removed:** `POST /api/v2/meta/bases/{baseId}/{sourceId}/tables`
- **Removed:** `POST /api/v2/meta/duplicate/{baseId}/table/{tableId}`
- **Removed:** `POST /api/v2/meta/tables/{tableId}/columns`
- **Removed:** `POST /api/v2/meta/tables/{tableId}/columns/bulk`
- **Removed:** `POST /api/v2/meta/tables/{tableId}/forms`
- **Removed:** `POST /api/v2/meta/tables/{tableId}/galleries`
- **Removed:** `POST /api/v2/meta/tables/{tableId}/grids`
- **Removed:** `POST /api/v2/meta/tables/{tableId}/hooks`
- **Removed:** `POST /api/v2/meta/tables/{tableId}/hooks/test`
- **Removed:** `POST /api/v2/meta/tables/{tableId}/kanbans`
- **Removed:** `POST /api/v2/meta/tables/{tableId}/maps`
- **Removed:** `POST /api/v2/meta/tables/{tableId}/reorder`

#### View Operations
- **Removed:** `DELETE /api/v2/meta/views/{viewId}`
- **Removed:** `DELETE /api/v2/meta/views/{viewId}/share`
- **Removed:** `GET /api/v2/meta/views/{viewId}/filters`
- **Removed:** `GET /api/v2/meta/views/{viewId}/sorts`
- **Removed:** `PATCH /api/v2/meta/views/{viewId}`
- **Removed:** `PATCH /api/v2/meta/views/{viewId}/share`
- **Removed:** `POST /api/v2/meta/views/{viewId}/filters`
- **Removed:** `POST /api/v2/meta/views/{viewId}/hide-all`
- **Removed:** `POST /api/v2/meta/views/{viewId}/share`
- **Removed:** `POST /api/v2/meta/views/{viewId}/show-all`
- **Removed:** `POST /api/v2/meta/views/{viewId}/sorts`

#### Webhook Operations
- **Removed:** `DELETE /api/v2/meta/hooks/{hookId}`
- **Removed:** `GET /api/v2/meta/hooks/{hookId}/filters`
- **Removed:** `GET /api/v2/meta/hooks/{hookId}/logs`
- **Removed:** `PATCH /api/v2/meta/hooks/{hookId}`
- **Removed:** `POST /api/v2/meta/hooks/{hookId}/filters`

### Data API Breaking Changes
#### File Operations
- **Removed:** `POST /api/v2/storage/upload`

#### Table Operations
- **Removed:** `DELETE /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}`
- **Removed:** `DELETE /api/v2/tables/{tableId}/records`
- **Removed:** `GET /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}`
- **Removed:** `GET /api/v2/tables/{tableId}/records`
- **Removed:** `GET /api/v2/tables/{tableId}/records/count`
- **Removed:** `GET /api/v2/tables/{tableId}/records/{recordId}`
- **Removed:** `PATCH /api/v2/tables/{tableId}/records`
- **Removed:** `POST /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}`
- **Removed:** `POST /api/v2/tables/{tableId}/records`

---

## Implementation Recommendations

### Version Detection Strategy
```typescript
// Detect API version from server response
async function detectApiVersion(baseUrl: string): Promise<'v2' | 'v3'> {
  // Check for v3-specific endpoints or response structures
  // Implementation depends on specific differences found
}
```

### Adapter Pattern
```typescript
interface ApiAdapter {
  getTables(baseId: string): Promise<Table[]>;
  getRecords(tableId: string, params?: QueryParams): Promise<Record[]>;
  // ... other methods
}

class ApiV2Adapter implements ApiAdapter { /* ... */ }
class ApiV3Adapter implements ApiAdapter { /* ... */ }
```

### Migration Priority
1. **High Priority**: Endpoints used frequently (record CRUD, table listing)
2. **Medium Priority**: View operations, link management
3. **Low Priority**: Advanced features, admin operations
