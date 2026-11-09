# Spring Boot 4 and Java 25 notes

Things that differ from Spring Boot 3, or that cost real debugging time. Read this before writing code
in a freshly scaffolded service.

## Starters and imports

- Starters are modular: `spring-boot-starter-webmvc`, `-kafka`, `-flyway`, `-data-mongodb`, and matching
  `-test` starters such as `spring-boot-starter-webmvc-test`.
- Jackson 3: import `tools.jackson.databind.*` and `tools.jackson.core.*`, using `JsonMapper`. Annotations
  such as `@JsonProperty` still come from `com.fasterxml.jackson.annotation`.
- `@WebMvcTest` is `org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest`.
- Mock beans with `@MockitoBean` from `org.springframework.test.context.bean.override.mockito`.
- Redis is still `spring.data.redis.*`, but MongoDB moved to `spring.mongodb.*`.

## Validation

To validate controller method parameters such as `@Min(1) @Max(200) int limit`, don't add `@Validated` to the
controller. Spring MVC's built-in method validation returns 400; `@Validated` raises an exception that
becomes a 500.

## Testing with PostgreSQL

- Import `TestcontainersConfiguration` into any test that touches the database. For a repository slice, combine it
  with `@DataJpaTest` from `org.springframework.boot.data.jpa.test.autoconfigure`; it uses the container as is.
- `@ServiceConnection` supplies the connection for the DataSource and Flyway, so tests don't need `DB_URL` and friends.
- Testcontainers 2 renamed things: artifacts are `testcontainers-postgresql` and `testcontainers-junit-jupiter`, and the
  class is `org.testcontainers.postgresql.PostgreSQLContainer`, which is no longer generic.
- Migrations run in every test context, so a bad migration fails the build rather than the deployment.

## Local PostgreSQL

- `spring-boot-docker-compose` starts `compose.yaml` during `bootRun` and overrides the `datasource` values.
- Jib must keep `configurationName = 'productionRuntimeClasspath'`. Without it the image contains
  `spring-boot-docker-compose` and fails at startup with "No Docker Compose file found".
- From `postgres:18` the volume mounts at `/var/lib/postgresql`. Mounting `/var/lib/postgresql/data` stops the container.

## Security

- The starters are `spring-boot-starter-security-oauth2-resource-server` and its `-test` counterpart.
- Startup fails if `JWT_ISSUER_URI` isn't set, which is why tests get a value from
  `src/test/resources/config/application.yml`. That location adds to the main `application.yml`; a file at
  `src/test/resources/application.yml` would replace it.
- The issuer is only contacted on the first token, so the application starts even if the value is wrong. Check it
  with a real token after deploying.
- A catch-all `@ExceptionHandler(Exception.class)` also catches security exceptions from `@PreAuthorize`, so it has
  to rethrow them.
- Controller slices need `@Import(SecurityConfig.class)` and a `@MockitoBean JwtDecoder`, and requests need
  `.with(jwt())`.

## MongoDB

- Set `spring.mongodb.representation.uuid: standard`, otherwise writing a `UUID` fails with
  "uuidRepresentation has not been specified".
- Spring Boot only auto-configures Flyway for JDBC, hence `MongoFlywayConfig`.
- Flyway needs all of `flyway-core`, `flyway-database-nc-mongodb`, `flyway-verb-migrate` and
  `flyway-nc-scanners`. Missing the verb gives a null `dataSource` NPE; missing the scanners gives
  "no migrations scanners loaded".
- `MongoFlywayConfig` takes `MongoConnectionDetails`, not the `spring.mongodb.uri` property, because Docker Compose and
  Testcontainers supply the connection that way and the property would still point at nothing.
- A Testcontainers test uses `org.testcontainers.mongodb.MongoDBContainer` from `testcontainers-mongodb`.
- A `.json` migration holds one command object. A JSON array fails, and only the first document in a
  multi-document file runs, so use one file per command.

## Kafka

- Send string JSON values and map them with `JsonMapper`. Don't put Java class names on the wire.
- Publish after the database commit using transaction synchronization, so consumers never see rolled-back data.
- Listeners must be idempotent on the event id, because delivery is at-least-once.
- Use a `DefaultErrorHandler` with `DeadLetterPublishingRecoverer` to `<topic>-dlq` and `FixedBackOff(1000, 3)`.
  Don't retry `JacksonException`, and log before sending to the DLQ, or failures disappear silently.
- `@KafkaListener` can't bind a YAML list property. Use a comma-separated string with
  `#{'${app.kafka.topics}'.split(',')}`.

## Lombok

- Spring Boot manages the version; don't pin one.
- On Java 25 every compile prints a `sun.misc.Unsafe` deprecation warning from Lombok. It's harmless.
- Never use `@Data`, `@EqualsAndHashCode` or `@ToString` on JPA entities. Use `@Getter`,
  `@NoArgsConstructor(access = AccessLevel.PROTECTED)` and `@AllArgsConstructor`.
- Records don't need Lombok; prefer them for DTOs.
