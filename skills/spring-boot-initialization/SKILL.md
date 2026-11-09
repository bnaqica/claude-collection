---
name: spring-boot-initialization
description: Initialize a new Spring Boot microservice under com.bnaqica following SOLID, DRY, KISS and YAGNI, with CRUD and action service layering, Keycloak bearer tokens, a dedicated PostgreSQL service schema and audit schema, and the standard package layout (api, service, repository, dto/event, dto/response, entity, processors, listener, publisher, config, exception, client), Java 25, Spring Boot 4, Gradle, PostgreSQL, Flyway, JUnit, Testcontainers, Spring Security with JWT, OpenAPI docs, Spotless, JaCoCo, GitHub Actions, an OpenSpec and Superpowers development workflow, Lombok with SLF4J, Jib and a .claude folder with rules and hooks. Use this whenever the user wants to create, bootstrap, scaffold or start a Spring Boot service or Java microservice, even if they just say "new service" or "set up a Spring project". Also use it when they want to restructure an existing Spring Boot service into this package layout, or ask where a class belongs in one.
---

# Spring Boot initialization

Sets up a Spring Boot service so that every service looks the same: same packages, same build, same
Claude rules. The value is the consistency, so stick to the layout even for a small service.

## Package layout

Under the base package `com.bnaqica.<project>`, where `<project>` is the project name without hyphens
(for example `order-service` becomes `com.bnaqica.orderservice`):

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

How the layers relate:

- Controllers, listeners and clients have no logic. Controllers hold the contract and pass it to a service,
  listeners pass events to a service, and clients are contract-only interfaces.
- The service injected into a controller has an interface and an implementation. Only the CRUD implementation
  calls its `@Repository`.
- Every table has a CRUD controller in `api`, except the append-only audit table.
- Action APIs (anything other than CRUD) go to a service that calls the CRUD `@Service` interface. Dependencies
  point one way, from action to CRUD, so there are no cycles.
- Controllers never see entities: the service implementation maps with builders (`@Builder`), not a library such as MapStruct.
- REST client errors are translated in `exception`, so nothing above `client` depends on a REST client error type.
- All exceptions live in `exception`, including ones thrown by only one class.
- Tests mirror the package of the class they test.

The full rules are in `assets/claude/rules/service-architecture.md` and `design-principles.md`, which the scaffold
copies into each repo's `.claude/rules/`.

## PostgreSQL schemas and audit

Services on PostgreSQL never use the `public` schema. The main schema is named after the service (`order-service`
becomes `order_service`) and holds its ERD. The `audit` schema holds `audit.api_audit`, which records every POST, PUT
and DELETE: the API called, the action, the request payload, the person from the token, and whether it succeeded.
Requests that fail are recorded too, including ones rejected by security, so the audit filter runs ahead of the
Spring Security filter chain.

A service that integrates with a third party also gets a `<service_name>_integration` schema
(`order_service_integration`) for that integration's own tables. Schema names use underscores because a hyphen would
need quoting in every SQL statement. Flyway creates all of these schemas on its first run.

## MongoDB

A MongoDB service gets a `compose.yaml` for local development, Flyway migrations as JSON commands in `db/migration`
(run by `MongoFlywayConfig`), and a Testcontainers test. The Postgres schemas and audit table don't apply.

## Creating a new service

1. Ask for whichever of these the request doesn't already answer. Never assume or invent them:
   - The project name (kebab-case).
   - The database: PostgreSQL, MongoDB or none.
   - If PostgreSQL: does the service integrate with a third party?

   The rest have defaults, so only change them if the request or repo says otherwise: package
   `com.bnaqica.<project>`, no Kafka, and port 8080. If there are sibling services, use the next free port.

2. Run the scaffold script. It never overwrites an existing file.

   ```bash
   python3 <this-skill>/scripts/scaffold.py --dir <repo> --name order-service --db postgres
   ```

   `--db` is `postgres`, `mongodb` or `none`. Add `--integration` if a PostgreSQL service integrates with a third
   party. Add `--port 8084`, `--kafka` or `--package <package>` only to change a default.

   This creates the Gradle build and wrapper, `lombok.config`, the main class, `application.yml` and
   `application-local.yml`, every package with a `package-info.java`, `.claude/` (settings, never-commit hook,
   rules, code-reviewer agent), `CLAUDE.md`, `README.md`, `docs/`, a GitHub Actions build and Dependabot.
   It also generates `SecurityConfig` (JWT, turned off in the `local` profile), `GlobalExceptionHandler`
   (`ProblemDetail` errors), a `Clock` bean, and security tests. With `postgres` or `mongodb` it adds `compose.yaml`,
   which `bootRun` starts by itself, `db/migration` for Flyway, a Testcontainers configuration, and a JUnit test that
   starts the application against it. `postgres` also gets the service and `audit` schemas (and the integration
   schema with `--integration`), the audit table and the audit filter.

3. Fill in the `TODO` lines in `CLAUDE.md`, `README.md` and `docs/README.md` with what the service actually does.

4. Run `./gradlew build` and confirm it passes before writing features. With a database, Docker must be running
   for the tests. Read `references/boot4-notes.md` before writing code; it covers Spring Boot 4 changes and
   known traps.

5. If the workspace has a shared local-infrastructure repo (such as `local-docker`), add what the service needs:
   the database and user from `application-local.yml`, and any Kafka topics. To use it instead of `compose.yaml`,
   remove that file and the `spring-boot-docker-compose` dependency.

6. Run `openspec init --tools claude` in the repo. It adds `openspec/`, `.claude/commands/opsx/` and
   `.claude/skills/openspec-*`. It needs Node.js 22.12+ and `npm install -g @fission-ai/openspec@latest`. If either is
   missing, tell the developer what to install rather than installing it yourself.

7. Leave everything uncommitted for the developer to review. The hook blocks commits, and the developer
   wants to look at every file first.

## Development workflow

Generated services use OpenSpec for planning and Superpowers for execution. `assets/claude/rules/development-workflow.md`
connects them: features go through `/opsx:propose`, then `/opsx:apply`, which triggers
`superpowers:test-driven-development` through the guidance in `openspec/config.yaml`, and finish with `/opsx:archive`.
Code review goes through `superpowers:requesting-code-review`, using the `code-reviewer` agent because that skill's
commit comparison would be empty. The never-commit rule overrides any step in either tool that commits, and worktrees
aren't used because work stays uncommitted.

## Restructuring an existing service

1. If the repo has uncommitted work or no commits, copy `src` somewhere safe first, because a move can't be
   undone from git history.
2. Map every class to a package from the table and show that mapping if any choice is a judgment call.
   Common moves: `domain` splits into `entity` and `repository`; `event` splits into `dto.event`, `listener` and
   `publisher`; exceptions and controller advice go to `exception`; request and response records leave `api`.
3. Move the classes, update `package` lines and imports, and move tests to match.
4. Replace entities in controller signatures with `dto.response` objects, keeping the JSON fields the same
   unless asked otherwise. Move mapping and any other logic out of controllers, listeners and clients.
5. Run the scaffold script against the repo, passing its existing base package with `--package` and its `--port`
   and `--db`, to add `package-info.java` for the missing packages and any missing project files. It reports what
   it skipped.
6. Update anything that names the old packages: `CLAUDE.md`, `.claude/rules` path globs, agents and docs.
7. Run `./gradlew build` and report the test counts.

## Placeholder packages

A package with no classes holds only a `package-info.java` describing its purpose, because git doesn't track
empty folders. Delete that file when the first real class arrives.

## Code conventions

- Follow SOLID, DRY, KISS and YAGNI.
- Inject with Lombok `@RequiredArgsConstructor` on `private final` fields.
- Log with Lombok `@Slf4j` and `{}` placeholders. Log ids rather than names or email addresses.
- Prefer records for DTOs and events.
- Inject `Clock` for anything time-based.
- Schema changes are new Flyway migrations, never edits to applied ones.
- Tests use JUnit. Database tests run against the real database through Testcontainers, never an embedded one.
- Every endpoint needs a JWT except the health check; only the `local` profile turns authentication off.
- API docs are on only in the `local` profile.
- Code is formatted by Spotless; run `./gradlew spotlessApply` before building.
- API errors are `ProblemDetail` responses from the controller advice.
- Versions come from the Spring Boot BOM. Only pin one the BOM doesn't manage, with a comment saying why.
