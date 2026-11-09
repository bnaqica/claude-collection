---
paths:
  - "src/**/*.java"
---

# Package structure

Every class lives under `{{PACKAGE}}` in one of these packages. Tests mirror the package of the class they test.

| Package | What goes in it |
|---|---|
| `api` | REST controllers |
| `service` | Business logic |
| `repository` | Spring Data repositories |
| `dto` | Data objects that aren't entities; internal ones (such as query projections) sit at the root |
| `dto.event` | Objects sent via events |
| `dto.response` | Objects returned by the API |
| `dto.request` | Request bodies received by the API |
| `entity` | Database entities and the enums they persist |
| `processors` | Additional processing that can't be done in a service |
| `listener` | Event listeners |
| `publisher` | Event publishers |
| `config` | Spring configuration and `@ConfigurationProperties` |
| `exception` | `@RestControllerAdvice`, custom exceptions, handling of REST client errors |
| `client` | API calls to third parties |

- Don't add other top-level packages.
- Controllers, listeners and clients hold no logic, and controllers never see entities.
  See `.claude/rules/service-architecture.md` for the call flow and mapping rules.
- Third-party API contracts go in `client`; REST client errors are translated in `exception`.
- Exceptions are never declared next to the code that throws them; they all go in `exception`.
- A package with no classes yet holds only a `package-info.java`. Delete that file once the package has real classes.
