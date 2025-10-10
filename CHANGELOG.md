# CHANGELOG

<!-- version list -->

## v1.3.0 (2025-10-10)

### Chores

- Add examples for bulk operations, configuration, link management, meta operations, and webhook
  automation
  ([`68a5fea`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/68a5fead697d1e302c16f2040176ff4b52df8049))

- Add scripts for comprehensive API comparison and schema analysis between NocoDB v2 and v3
  ([`dadf3a2`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/dadf3a214ccba58f74330e25fa4293ec7899b43c))

- Update AI issue summary workflow configuration
  ([`0cb801c`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/0cb801cfdc9a85c5c234009c851dae3e500c2a38))

### Documentation

- Update README.MD [automated]
  ([`904dfb7`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/904dfb79379020021a81398a353387d40b3305f5))

- Update README.MD [automated]
  ([`e8c28fb`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/e8c28fb87093b28fef4136506944b1e6754dfc82))

- Update README.MD [automated]
  ([`a37417c`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/a37417c5339e1fb384680a5808897d47a74ae610))

- Update SECURITY.MD [automated]
  ([`53ed8f0`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/53ed8f06657e355d7c8e3388907abe26e0a791e9))

- V3 OpenAPI Specifications
  ([`6059be4`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/6059be4bd37c4932265acca91ed02ad5435e971a))

### Features

- Add support for benchmark tests in run-all script and quick-test script
  ([`956b93f`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/956b93fe9dfd96e22db9808ebab67fbae25cca36))

- Enhance Client to support both API v2 and v3
  ([`9356b08`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/9356b084464d75fcd34d1ff0d73dacbf8ac9095f))

- Implement comprehensive support for NocoDB API v2 and v3, including automatic parameter conversion
  and backward compatibility
  ([`d7c359f`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/d7c359fc19aac96d6515baad0cbdd7fa6ab97d5e))

- Refactor parameter handling and type annotations in API client and resolver classes
  ([`9e1317d`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/9e1317d203a264b2632766d0a8ffd5d4f38c2a22))

- Update file upload paths for API v2 to use new endpoint structure
  ([`f0dea7c`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/f0dea7cf9bb8cf2d862bba1c50a9857be9f97d25))


## Unreleased

### Features

- **API Version Support**: Add seamless support for NocoDB API v2 and v3
  - Implement `api_version` parameter for client initialization (default: "v2")
  - Add automatic parameter conversion between v2 and v3 formats
    - Pagination: `offset/limit` (v2) ↔ `page/pageSize` (v3)
    - Sort: string format (v2) ↔ JSON array format (v3)
    - Operators: automatic conversion (e.g., `ne` → `neq`)
  - Implement `BaseIdResolver` with caching for v3 API base_id resolution
  - Add v2/v3 support to all Data API methods (14 methods)
  - Add v2/v3 support to all Meta API methods (29 methods)
  - Update `NocoDBTable` wrapper to support `base_id` parameter
  - Full backward compatibility maintained for existing v2 code

### Documentation

- Add comprehensive API Version Guide ([docs/API_VERSION_GUIDE.md](docs/API_VERSION_GUIDE.md))
- Add Data API v2/v3 usage examples ([examples/api_version_example.py](examples/api_version_example.py))
- Add Meta API v2/v3 usage examples ([examples/meta_api_version_example.py](examples/meta_api_version_example.py))
- Update README.template.md with API version support documentation
- Add OpenAPI v2 and v3 specification files to docs directory

### Tests

- Add 88 new unit tests for v2/v3 functionality
  - 52 tests for PathBuilder and QueryParamAdapter
  - 15 tests for BaseIdResolver
  - 21 integration tests for version switching
- Update existing tests for new `base_id` parameter
- All 454 tests passing with full coverage

## v1.2.0 (2025-10-09)

### Bug Fixes

- Aktualisiere die Logik zum Abrufen vorhandener Basen in den Integrationstests
  ([`181bafd`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/181bafd7a12a53544ef180674ff3a5b80d01ec70))

- Aktualisiere die Logik zur Entdeckung von Basen in den Integrationstests
  ([`931b6a3`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/931b6a3857add13fe19f153645d5fd5b34d2ee4a))

- Behebe Syntaxfehler bei der Token-Generierung
  ([`c12dbfc`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/c12dbfc15943c5f2a6dff35357908408433d7ae9))

- Entferne Docker SDK und Pillow Installation aus den Workflow-Schritten und füge sie als optionale
  Abhängigkeiten in pyproject.toml hinzu
  ([`b7220c4`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/b7220c400ad33086430f8651d585e62372f867b5))

- Entferne fehlerhafte API-Token-Generierung und verbessere Fehlerbehandlung
  ([`a700c42`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/a700c42dbfb11c87dec8e59f769bdbd749ac2e2e))

- Entferne ungenutzte Importe aus den Integrationstests
  ([`7aaebf4`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/7aaebf46d52aaa22e3fa417f5cea64d7d0317cc6))

- Entferne überflüssige Parameter bei der Token-Generierung
  ([`2b647d7`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/2b647d7a457317d72ad803ca647de95653a0431d))

- Refactor and enhance view management tests
  ([`9a2df88`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/9a2df8895bd91337ca9f94d4f07f7af5c8509332))

- Update repository links in CONTRIBUTING.md and pyproject.toml for consistency
  ([`04e6fa8`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/04e6fa8f1d87ac74916a469bfbd3b472de6fe608))

- Verbessere Container-Start- und Bereitstellungslogik für Integrationstests
  ([`10fc739`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/10fc739d8a637e9cb901f4ad46c34cb71368e6ed))

- Überprüfe die Verfügbarkeit von Docker anstelle der Einrichtung in den Workflow-Schritten
  ([`de35dcb`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/de35dcb3977afa217c0a7872e8d643b64c2063a0))

### Chores

- Entferne veraltete README-Datei für CI/CD-Setup
  ([`34bc6d4`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/34bc6d4eaadea638f1cfeb45633c17806aeb439d))

### Code Style

- Aktualisiere Workflow-Datei mit klaren Jobnamen für Tests und Performance
  ([`2114ad2`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/2114ad2befe5975926fb37eb783f42881bfce8cc))

- Füge Emojis zu den Jobnamen und Schritten in der Feature-Test-Workflow-Datei hinzu
  ([`28030a9`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/28030a936f572978fad46b3ac8d7f14be0d9a667))

### Documentation

- Add openapi specs.
  ([`f500885`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/f500885b5829bbabce86ead1ffccc0aa1d81e6f7))

- Aktualisiere Installationsanweisungen für spezifische Versionen und Branches
  ([`102ff49`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/102ff496570c8a8b2df6716bb71eb77f18d03427))

- Füge Installationsanweisungen für GitHub hinzu
  ([`cf5d115`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/cf5d1157bf3974c33e1359b08ef2daed9561bbe7))

- Korrigiere Verweise auf CHANGELOG.md in README.template und pyproject.toml
  ([`228cebd`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/228cebd7041a821666797c8b04de978ec6eb6cf2))

- Update README.MD [automated]
  ([`3ab12ac`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/3ab12accc5d3c27f7458d3a29307965997844082))

- Update README.MD [automated]
  ([`be114d5`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/be114d522ef220619a7fae0a40137296eca2659b))

- Update README.MD [automated]
  ([`025262d`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/025262d3af97b50d8832bd085386c64483fceede))

- Update README.MD [automated]
  ([`37dab1d`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/37dab1d76876d5710ce770cdb1e067fd8da1952c))

- Update README.MD [automated]
  ([`7f40be9`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/7f40be9cb08bf32acff1a36aebb98c673c1d4a44))

- Update SECURITY.MD [automated]
  ([`16e374e`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/16e374ea1dffa5053f565fbb2379d45e0dbcc746))

### Features

- Add bulk operations and view management for NocoDB
  ([`7362e71`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/7362e719078610bada97fd3b3321f1814ad0b470))

- Add comprehensive tests for NocoDB webhooks functionality
  ([`433c9c5`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/433c9c5615c09b0b14d5580a08dbeab1283c8e65))

- Add comprehensive tests for NocoDB webhooks functionality
  ([`6a4336b`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/6a4336b40b33d8e17eeb1df70ffa89823c80f662))

- Add Docker support for testing NocoDB Simple Client and enhance caching mechanism
  ([`a506140`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/a50614021b69566ab976f177b56c713c52be69f5))

- Add python-dotenv to development dependencies and improve Bandit security scan exclusions
  ([`6193afd`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/6193afdf65e74d727bd1a1aabf71e3a328307fae))

- Add unit tests for NocoDB Views and Webhooks functionality
  ([`22a7afa`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/22a7afadaf460cfd07590097a9814ef1361b038c))

- Add workspace and base management methods to NocoDBMetaClient
  ([`8315d7a`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/8315d7a57fed6fb7b5cf0726eaf6e95ae2de7a3a))

- Aktualisiere die list_bases-Methode zur Auflistung aller Basen ohne workspace_id
  ([`080a2b9`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/080a2b99cfa54f65bb93b2e978a5dfbf4097f955))

- Aktualisiere Konfiguration und Umgebungsvariablen für nocodb-config.json zur Vereinheitlichung der
  Variablennamen
  ([`6a3e298`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/6a3e298f7311b00b3bd8b0128af4bb3706de191f))

- Aktualisiere Konfigurationsladefunktion zur Unterstützung von nocodb-config.json und entferne
  veraltete .env-Datei
  ([`877edcb`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/877edcb00b58e7b248a4824df465afa55b3522ba))

- Aktualisiere NocoDB-Client und Tests für API v2 Array-Antworten bei CRUD-Operationen
  ([`6d54860`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/6d5486021c438c6299343d05813e892de9bc39a1))

- Aktualisiere NocoDB-Client und Tests für API v2, um die Rückgabe von Objekten anstelle von Arrays
  zu berücksichtigen
  ([`67ae670`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/67ae670a825d23c12461de46f5db2edeca03fc7e))

- Aktualisiere NocoDBMetaClient zur Vererbung von NocoDBClient und passe Aufrufe in den
  Manager-Klassen an
  ([`908581d`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/908581db57e53c9d13c3afc66858c51d80f07653))

- Aktualisiere Pre-Commit-Konfiguration, um Tests von Hooks auszuschließen und die Python-Version zu
  ändern
  ([`d37bcf3`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/d37bcf336b4c88c06e417258ff99a799f6a76e16))

- Aktualisiere Test für Dateioperationen, um Upload und Download zu unterstützen
  ([`9cf5d8b`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/9cf5d8b28b704b998d19283162da7baac30596a8))

- Aktualisiere Tests für NocoDBTable, um spezifische Argumente für Mock-Methoden zu überprüfen
  ([`3856392`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/3856392413091a4d65cb49ae7fed9b2ada90f549))

- Aktualisiere Token-Generierung und verbessere Umgebungsdateien für CI/CD
  ([`e0dc9f9`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/e0dc9f973d830b1f2b0ea0258978166c76937da8))

- Enhance GitHub Actions workflow with descriptive step names and improve cache handling
  ([`458853e`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/458853e6b2a91823c0ac8d14b8104ab28422278d))

- Entferne die Standardgröße für die maximale Dateigröße im FileManager
  ([`9b63ba0`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/9b63ba06faeb474d04955b42b34d7864dedefb52))

- Entferne Docker-Testskripte und zugehörige Docker-Konfiguration
  ([`336cd2b`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/336cd2bb649c3a706fadde6cdc4e409d2e50ed5c))

- Entferne veraltete Analyse der API-Antwortformate aus der Dokumentation
  ([`fcb9940`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/fcb9940152a9d7d934120c351a7c21f5a628a6bd))

- Entferne überflüssige ID-Spalte aus der Tabellendefinition in Integrationstests
  ([`23ae951`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/23ae951d36c3369ec55129b96ed3471ca745d188))

- Erweitere Integrationstests um dynamische Tabellenverwaltung und verbessere Fehlerbehandlung
  ([`187cf39`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/187cf39ff74c93c5667e9e6119a7b2c316ed378e))

- Erweitere NocoDB Gesundheitsprüfung um Authentifizierungs-API-Überprüfung
  ([`491942e`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/491942e821f5e3c67ad719cc7e17febcc817e290))

- Füge Integrationstests für nocodb-simple-client hinzu
  ([`05448a5`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/05448a5255c9345409253c4289efb24100811f1a))

- Füge NocoDBMetaClient hinzu und verbessere Tests für asynchrone Client-Funktionalität
  ([`1957546`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/195754625e31ca91d1284a3d54eb51301db5774a))

- Füge Unterstützung für asynchrone Tests mit pytest-asyncio hinzu
  ([`9f0bf0e`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/9f0bf0eb8217fb7cc2359967e54ec91f5e04f054))

- Füge Unterstützung für workflow_dispatch und workflow_call in die Feature-Test-Workflow-Datei
  hinzu
  ([`591836b`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/591836be4350985d59529dc9a63db184b885fcee))

- Implement workspace and base operations tests in NocoDBMetaClient
  ([`e719e21`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/e719e2192c68a6c624f92d6de77dea5f5b9ade34))

- Integrationstests für Python-managed NocoDB-Instanz optimiert und Docker-Setup hinzugefügt
  ([`7ce9aaa`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/7ce9aaa8d887c4735ed5053029ec5fc4f30bba82))

- Reduziere die maximale Dateigröße auf 50MB im FileManager
  ([`cb8a663`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/cb8a663bda9241315757938d794a53f4e2bf920a))

- Refactor async client tests to use NocoDBConfig for configuration management
  ([`c4b6f73`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/c4b6f737dc20eb4b986de7fb3a12a90498282245))

- Refactor tests and add new test cases for NocoDB Meta Client and Views
  ([`0afa9fe`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/0afa9fe6d5578739f8bdf26b0fcfbc69dd37be59))

- Verbessere Docker-Setup und Warte-Logik für NocoDB-Container
  ([`7747ae2`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/7747ae229d8a32dc7354b50e8dd1fa14cc86b24f))

- Verbessere Fehlerbehandlung bei der Einfügeoperation für NocoDB-Client
  ([`d758cf1`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/d758cf17d7f375652ca3719ca6a7f6825fe966e4))

- Verbessere Fehlerbehandlung in Integrationstests für nicht vorhandene Datensätze
  ([`5b1f592`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/5b1f592f94971734cf1c4317e0194d31b8676e8f))

- Verbessere Fehlerbehandlung in NocoDB-Client und Integrationstests für ungültige Datensätze
  ([`11edc03`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/11edc032f50056d652b6e992b2b1bac938039dc0))

- Verbessere Fehlerbehandlung und Debugging für Token-Generierung und API-Verbindung
  ([`4a80d2b`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/4a80d2b5198fbe004ffe085ca0215e0e8d7e433c))

- Verbessere Fehlerbehandlung und Unterstützung für neue Cache-Konfigurationen in NocoDB
  ([`532ae91`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/532ae916549e3fc52b491b3002dcc28bd0689501))

- Verbessere Integrationstests mit Konfigurationsüberprüfung und optimiere Docker-Setup
  ([`d369f4c`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/d369f4c78a311458a19ebf2c10aa3e9bb37a5738))

- Verbessere Konfigurationsladefunktion und unterstütze neue Umgebungsvariablen für
  Integrationstests
  ([`1ad9718`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/1ad97184fc249c8fae15da25f6a453aa0c817ccb))

- Verbessere Protokollierung in den Integrationstests und aktualisiere die Tabellenstruktur für
  NocoDB 0.265.1+
  ([`a328535`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/a3285359fc2954b903b4103bc3c30c2445dd658a))

- Verbessere Token-Generierung durch Authentifizierung und verbessere Fehlerbehandlung
  ([`ed5786b`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/ed5786b0ba8a133dbdc2b8f90d915b0dd995e796))

- Verbessere Token-Generierung mit Basis-Authentifizierung und verbessere Fehlerbehandlung
  ([`2f9b022`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/2f9b022ad28ba9e6f85c4a51bdc20f8aa72e5645))

- Verbessere Typüberprüfungen und Fehlerbehandlung in der NocoDB-Client-Bibliothek
  ([`c24c622`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/c24c622f0ca58d7641aea4ba67201eb720a7e0bf))

- Vereinheitliche Variablennamen in Integrationstests für NocoDB-Client
  ([`5af424a`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/5af424a58decb1347552df3a326e0bb3f147b7ea))

### Refactoring

- Optimize webhook tests by simplifying assertions and updating method calls
  ([`f21fe5a`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/f21fe5a105344369ea3e7fc8a461cf6f0286827c))


## v1.1.1 (2025-09-01)

### Bug Fixes

- Aktualisiere CHANGELOG für Version 1.1.0 und entferne veraltete Einträge
  ([`3109991`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/3109991485cccfee67ca46d087c97d263364a46f))

- Entferne veraltete Versionseinträge aus dem CHANGELOG
  ([`36bb0c0`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/36bb0c09e9445fc8d920851e7aa2e32087c65a02))

- Korrigiere Dateinamen für CHANGELOG und README auf Großbuchstaben
  ([`f13ae97`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/f13ae974a0108e1fc68a5a471d35fe017571e066))

### Documentation

- Update README.MD [automated]
  ([`09d2565`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/09d256554d8fd8bf8b75087cf77f84cf654a0556))

- Update SECURITY.MD [automated]
  ([`10bfb1b`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/10bfb1ba2c4d2f961fbeae267e8e27da61f4ad91))


## v1.1.0 (2025-09-01)

### Bug Fixes

- Aktualisiere Versionsnummer im CHANGELOG auf v0.4.0
  ([`c5b164a`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/c5b164a7eba67d2238a72bde425ecc320bbedf6c))

- Füge fehlende Leerzeilen zwischen den Abschnitten im pyproject.toml hinzu
  ([`7394b31`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/7394b3132e3eeb72857e540afe6149d592b61b1a))

### Documentation

- Update README.MD [automated]
  ([`044c004`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/044c004249611cf623d8688c4662e33bafcde3e1))

- Update SECURITY.MD [automated]
  ([`fc8693d`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/fc8693d47fa824ba31467a19c373557a908eb01e))

### Features

- Füge CHANGELOG für Version 1.0.0 hinzu und strukturiere die Einträge
  ([`7163c07`](https://github.com/bauer-group/LIB-NocoDB_SimpleClient/commit/7163c071f6c545b82ba47ec3ecaeae071f78f36f))


## v1.0.0 (2025-09-01)

- Initial Release
