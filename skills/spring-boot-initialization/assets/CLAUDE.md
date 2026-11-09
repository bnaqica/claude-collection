# CLAUDE.md — {{NAME}}

TODO: one or two sentences on what this service owns and does.

## Never commit

Claude does not commit, push, merge, rebase or open PRs in this repo — the developer reviews and commits
every change. A hook enforces this. See `.claude/rules/git-workflow.md`.

## Commands

```bash
./gradlew build            # compile, test, coverage report, formatting check
./gradlew spotlessApply    # format the code
./gradlew bootRun          # run with the `local` profile
./gradlew jibDockerBuild   # build the container image
```

## Stack

Java 25, Spring Boot 4.1, Gradle (wrapper), {{STACK}}Spring Security (JWT), springdoc, Spotless, JaCoCo, Lombok,
SLF4J, Jib. Port {{PORT}}.

## Layout

```
src/main/java/{{PACKAGE_PATH}}/
  {{MAIN_CLASS}}.java
  api/          REST controllers
  service/      business logic
  repository/   Spring Data repositories
  dto/event/    objects sent via events
  dto/response/ objects returned by the API
  dto/request/  request bodies received by the API
  entity/       database entities
  processors/   additional processing that can't be done in a service
  listener/     event listeners
  publisher/    event publishers
  config/       Spring configuration and @ConfigurationProperties
  exception/    @RestControllerAdvice, custom exceptions, REST client error handling
  client/       API calls to third parties
src/main/resources/
  application.yml          defaults; values from environment variables
  application-local.yml    local settings (profile `local`)
src/test/java/...          tests mirror the main package layout
```

## Conventions

- Constructor injection only, generated with Lombok `@RequiredArgsConstructor`; no field `@Autowired`.
- Log with Lombok `@Slf4j` (SLF4J, `{}` placeholders); never `System.out`.
- Tests mirror the main package and use JUnit. Unit-test services with Mockito; use `@WebMvcTest` for controllers.
{{TEST_CONVENTION}}- Every endpoint needs a JWT, except the health check. Only the `local` profile turns authentication off, so never
  activate it outside a developer machine.

## Workflow

Features start with `/opsx:propose`, not `superpowers:brainstorming`. `/opsx:apply` builds them with
`superpowers:test-driven-development`, and code review uses `superpowers:requesting-code-review`.
Finish with `/opsx:archive` after the developer has reviewed. See `.claude/rules/development-workflow.md`.

## More rules

`.claude/rules/` holds the detailed rules (git workflow, development workflow, design principles, package structure, service architecture, Java/Spring).
`.claude/agents/` holds review subagents.
