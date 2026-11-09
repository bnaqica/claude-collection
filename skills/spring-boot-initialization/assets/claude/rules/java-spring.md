---
paths:
  - "src/**/*.java"
  - "build.gradle"
  - "src/main/resources/**"
---

# Java and Spring Boot

- Java 25 language features are fine (records, pattern matching, `var` where the type is obvious).
- Spring Boot 4 uses **Jackson 3**: import `tools.jackson.databind.*`, not `com.fasterxml.jackson.databind.*`.
  (Annotations such as `@JsonProperty` still come from `com.fasterxml.jackson.annotation`.)
- Boot 4 test slices moved: `org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest`;
  mock beans with `@MockitoBean` (`org.springframework.test.context.bean.override.mockito`).
- Package layout is in `.claude/rules/package-structure.md`; call flow, mapping, security and database schemas are in
  `.claude/rules/service-architecture.md`; design principles are in `.claude/rules/design-principles.md`.
- Constructor injection only, via Lombok `@RequiredArgsConstructor` on `private final` fields.
  Write the constructor by hand only when it does more than assign fields. Inject `Clock` for anything time-based.
- Logging is SLF4J through Lombok `@Slf4j` (field `log`); never `System.out` or a hand-written `LoggerFactory` field.
  Use `{}` placeholders, not string concatenation, and pass the exception as the last argument.
  `info` for state changes (created, published, recorded), `debug` for skipped/ignored work, `error` for failures.
  Log ids, not personal data (names, email addresses).
- Lombok: `@Getter`, `@RequiredArgsConstructor`, `@Slf4j`, `@Builder` are fine. Prefer records for DTOs and events,
  and map between objects with `@Builder`, never a mapping library.
  No `@Data`, `@EqualsAndHashCode` or `@ToString` on JPA entities. Settings live in `lombok.config`.
- Errors from the API are `ProblemDetail` responses from the `@RestControllerAdvice`.
- New config goes in `application.yml` with an `${ENV_VAR}` placeholder, plus the local value in
  `application-local.yml`, plus a row in the README's environment table.
- Dependencies: versions come from the Spring Boot BOM. Only pin a version when the BOM doesn't manage it,
  and say why in a comment.
- Don't edit applied Flyway migrations; add `V<next>__<description>`.
- Every behaviour change gets a test. Run `./gradlew spotlessApply build` before saying you're done.
- The catch-all in `GlobalExceptionHandler` rethrows Spring Security exceptions. Keep that, or 401 and 403 become 500.
