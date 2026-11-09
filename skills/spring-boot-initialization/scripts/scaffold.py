#!/usr/bin/env python3
"""Scaffold a Spring Boot service with the standard package layout.

Never overwrites: a file that already exists is left alone and reported as skipped,
so this is safe to re-run or to point at an existing repository.
"""
import argparse
import re
import shutil
import stat
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

PACKAGES = {
    "api": "REST controllers. No logic: the contract only, passing each call to a {@code service}.",
    "service": "Business logic. CRUD services have an interface and an implementation; action services call the CRUD interfaces.",
    "repository": "Spring Data repositories. Called only from CRUD service implementations.",
    "dto.event": "Objects sent via events.",
    "dto.response": "Objects returned by the REST API.",
    "dto.request": "Request bodies received by the REST API.",
    "entity": "Database entities and the enums they persist.",
    "processors": "Additional processing that doesn't belong in a {@code service} class.",
    "listener": "Event listeners. No logic: receive the event and pass it to a {@code service}.",
    "publisher": "Event publishers.",
    "config": "Spring configuration and {@code @ConfigurationProperties}.",
    "exception": "The {@code @RestControllerAdvice}, custom exceptions, and handling of REST client errors.",
    "client": "Third-party API contracts. No logic: declarative interfaces only.",
}

MAIN_DEPS = {
    "postgres": [
        "implementation 'org.springframework.boot:spring-boot-starter-data-jpa'",
        "implementation 'org.springframework.boot:spring-boot-starter-flyway'",
        "implementation 'org.flywaydb:flyway-database-postgresql'",
        "runtimeOnly 'org.postgresql:postgresql'",
        "// Starts compose.yaml during `./gradlew bootRun`; left out of the jar and the tests",
        "developmentOnly 'org.springframework.boot:spring-boot-docker-compose'",
    ],
    "mongodb": [
        "implementation 'org.springframework.boot:spring-boot-starter-data-mongodb'",
        "// Flyway native connector for MongoDB (JSON migrations in src/main/resources/db/migration)",
        "implementation 'org.flywaydb:flyway-core'",
        "implementation 'org.flywaydb:flyway-database-nc-mongodb'",
        "// The native-connector \"migrate\" verb and migration scanners aren't in Spring Boot's BOM,",
        "// so pin them to the Flyway version Boot manages",
        "implementation \"org.flywaydb:flyway-verb-migrate:${dependencyManagement.importedProperties['flyway.version']}\"",
        "implementation \"org.flywaydb:flyway-nc-scanners:${dependencyManagement.importedProperties['flyway.version']}\"",
        "// Starts compose.yaml during `./gradlew bootRun`; left out of the jar and the tests",
        "developmentOnly 'org.springframework.boot:spring-boot-docker-compose'",
    ],
    "none": [],
}
TEST_DEPS = {
    "postgres": [
        "testImplementation 'org.springframework.boot:spring-boot-starter-data-jpa-test'",
        "testImplementation 'org.springframework.boot:spring-boot-starter-flyway-test'",
        "testImplementation 'org.springframework.boot:spring-boot-testcontainers'",
        "testImplementation 'org.testcontainers:testcontainers-junit-jupiter'",
        "testImplementation 'org.testcontainers:testcontainers-postgresql'",
    ],
    "mongodb": [
        "testImplementation 'org.springframework.boot:spring-boot-starter-data-mongodb-test'",
        "testImplementation 'org.springframework.boot:spring-boot-testcontainers'",
        "testImplementation 'org.testcontainers:testcontainers-junit-jupiter'",
        "testImplementation 'org.testcontainers:testcontainers-mongodb'",
    ],
    "none": [],
}
STACK = {
    "postgres": "PostgreSQL, Flyway, JUnit, Testcontainers, ",
    "mongodb": "MongoDB, Flyway, JUnit, Testcontainers, ",
    "none": "JUnit, ",
}
# Assets that differ by database: the folder they live in under assets/
DB_ASSET_DIR = {"postgres": "", "mongodb": "mongodb/"}
DB_DISPLAY_NAME = {"postgres": "PostgreSQL", "mongodb": "MongoDB"}
DEFAULT_PACKAGE_PREFIX = "com.bnaqica"
JAVA_RESERVED_WORDS = set("""
    abstract assert boolean break byte case catch char class const continue default do double else enum extends
    false final finally float for goto if implements import instanceof int interface long native new null package
    private protected public return short static strictfp super switch synchronized this throw throws transient
    true try void volatile while
""".split())
POSTGRES_AUDIT_CLASSES = {
    "ApiAudit": "entity",
    "ApiAuditRepository": "repository",
    "ApiAuditEntry": "dto",
    "ApiAuditService": "service",
    "ApiAuditServiceImpl": "service",
    "ApiAuditFilter": "config",
    "ApiAuditFilterConfig": "config",
}
KAFKA_MAIN = "implementation 'org.springframework.boot:spring-boot-starter-kafka'"
KAFKA_TEST = "testImplementation 'org.springframework.boot:spring-boot-starter-kafka-test'"


def application_yml(name, port, db, kafka, integration):
    y = f"""# Defaults for every environment. Values come from environment variables so the
# same image runs anywhere; the `local` profile fills them in for local development.
server:
  port: {port}

spring:
  application:
    name: {name}
"""
    if db == "postgres":
        schema = name.replace("-", "_")
        schemas = ",".join([schema, "audit", *([f"{schema}_integration"] if integration else [])])
        y += f"""  datasource:
    url: ${{DB_URL}}
    username: ${{DB_USERNAME}}
    password: ${{DB_PASSWORD}}
  jpa:
    open-in-view: false
    hibernate:
      ddl-auto: validate   # Flyway owns the schema
    properties:
      hibernate:
        default_schema: {schema}
  flyway:
    enabled: true
    locations: classpath:db/migration
    default-schema: {schema}   # never the public schema
    schemas: {schemas}
"""
    if db == "mongodb":
        y += """  mongodb:
    uri: ${MONGODB_URI}
    representation:
      uuid: standard
"""
    if kafka:
        y += f"""  kafka:
    bootstrap-servers: ${{KAFKA_BOOTSTRAP_SERVERS}}
    consumer:
      group-id: {name}
      auto-offset-reset: earliest
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.apache.kafka.common.serialization.StringSerializer
      acks: all
      properties:
        enable.idempotence: true
"""
    return y + """  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: ${JWT_ISSUER_URI}

management:
  endpoints:
    web:
      exposure:
        include: health,info

# API docs are only switched on by the `local` profile
springdoc:
  api-docs:
    enabled: false
  swagger-ui:
    enabled: false
"""


def application_local_yml(name, db, kafka):
    snake = name.replace("-", "_")
    body = ""
    if db == "postgres":
        body += f"""  # During `./gradlew bootRun` the connection comes from compose.yaml and these values aren't used.
  # They apply when the application is started some other way against a Postgres on port 5432.
  datasource:
    url: jdbc:postgresql://localhost:5432/{snake}_db
    username: {snake}_local
    password: local
"""
    if db == "mongodb":
        body += f"""  # During `./gradlew bootRun` the connection comes from compose.yaml and this value isn't used.
  # It applies when the application is started some other way against a MongoDB on port 27017.
  mongodb:
    uri: mongodb://{snake}_local:local@localhost:27017/{snake}_db?authSource={snake}_db
"""
    if kafka:
        body += "  kafka:\n    bootstrap-servers: localhost:9092\n"
    head = "# Settings for running on a developer machine. This profile also turns off authentication.\n"
    body += """  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: http://localhost:9999/local-issuer   # required at startup, but unused with authentication off
"""
    return head + "spring:\n" + body + """springdoc:
  api-docs:
    enabled: true
  swagger-ui:
    enabled: true
"""


def env_table(db, kafka):
    rows = []
    if db == "postgres":
        rows += [("DB_URL", "JDBC URL of the database"), ("DB_USERNAME", "Database user"), ("DB_PASSWORD", "Database password")]
    if db == "mongodb":
        rows += [("MONGODB_URI", "MongoDB connection string")]
    if kafka:
        rows += [("KAFKA_BOOTSTRAP_SERVERS", "Kafka brokers")]
    rows += [("JWT_ISSUER_URI", "Issuer whose JWTs this service accepts")]
    return "".join(f"| `{name}` | {purpose} |\n" for name, purpose in rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", required=True, type=Path, help="repository directory (created if missing)")
    ap.add_argument("--name", required=True, help="service name, kebab-case, e.g. order-service")
    ap.add_argument("--package", help=f"base package (default: {DEFAULT_PACKAGE_PREFIX}.<name without hyphens>)")
    ap.add_argument("--port", type=int, default=8080, help="server port (default: 8080)")
    ap.add_argument("--db", required=True, choices=sorted(MAIN_DEPS), help="database the service uses")
    ap.add_argument("--integration", action="store_true", help="postgres only: add a <service_name>_integration schema for a third-party integration")
    ap.add_argument("--kafka", action="store_true")
    a = ap.parse_args()

    if not re.fullmatch(r"[a-z][a-z0-9-]*", a.name):
        sys.exit("--name must be kebab-case")
    if a.integration and a.db != "postgres":
        sys.exit("--integration adds a PostgreSQL schema, so it needs --db postgres")
    if a.package is None:
        a.package = f"{DEFAULT_PACKAGE_PREFIX}.{a.name.replace('-', '')}"
    if not re.fullmatch(r"[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*)+", a.package):
        sys.exit("--package must be a lowercase Java package with at least two segments")
    reserved = JAVA_RESERVED_WORDS.intersection(a.package.split("."))
    if reserved:
        sys.exit(f"package {a.package} contains the Java reserved word '{sorted(reserved)[0]}'; choose another name or pass --package")

    main_class = "".join(w.capitalize() for w in a.name.split("-")) + "Application"
    package_path = a.package.replace(".", "/")
    deps = [*MAIN_DEPS[a.db], *([KAFKA_MAIN] if a.kafka else [])]
    test_deps = [*TEST_DEPS[a.db], *([KAFKA_TEST] if a.kafka else [])]
    uses_testcontainers = a.db in DB_ASSET_DIR
    tokens = {
        "NAME": a.name,
        "PACKAGE": a.package,
        "PACKAGE_PATH": package_path,
        "GROUP": a.package.rsplit(".", 1)[0],
        "PORT": str(a.port),
        "MAIN_CLASS": main_class,
        "MAIN_DEPENDENCIES": "".join(f"    {d}\n" for d in deps),
        "TEST_DEPENDENCIES": "".join(f"    {d}\n" for d in test_deps),
        "SNAKE_NAME": a.name.replace("-", "_"),
        "STACK": STACK[a.db],
        "ENV_TABLE": env_table(a.db, a.kafka),
        "TEST_PREREQUISITE": "- Docker running, for the local database and the Testcontainers tests.\n" if uses_testcontainers else "",
        "TEST_CONVENTION": (
            f"- Database tests run against real {DB_DISPLAY_NAME[a.db]} through Testcontainers: `@Import(TestcontainersConfiguration.class)`.\n"
            "  Don't use an embedded database. Docker must be running for `./gradlew test`.\n"
            if uses_testcontainers else ""
        ),
    }
    created, skipped = [], []

    def fill(text):
        return re.sub(r"\{\{(\w+)\}\}", lambda m: tokens[m.group(1)], text)

    def write(rel, text):
        dest = a.dir / rel
        if dest.exists():
            skipped.append(rel)
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)
        created.append(rel)

    def asset(src, rel):
        write(rel, fill((ASSETS / src).read_text()))

    def copy_binary(src, rel, executable=False):
        dest = a.dir / rel
        if dest.exists():
            skipped.append(rel)
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ASSETS / src, dest)
        if executable:
            dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        created.append(rel)

    for f in ["build.gradle", "settings.gradle", "gradle.properties", "lombok.config", "CLAUDE.md", "README.md"]:
        asset(f, f)
    asset("gitignore", ".gitignore")
    asset("github/workflows/build.yml", ".github/workflows/build.yml")
    asset("github/dependabot.yml", ".github/dependabot.yml")
    asset("openspec-config.yaml", "openspec/config.yaml")

    copy_binary("wrapper/gradlew", "gradlew", executable=True)
    copy_binary("wrapper/gradlew.bat", "gradlew.bat")
    for f in ["gradle-wrapper.jar", "gradle-wrapper.properties"]:
        copy_binary(f"wrapper/gradle/wrapper/{f}", f"gradle/wrapper/{f}")

    for src in sorted((ASSETS / "claude").rglob("*")):
        if src.is_file():
            rel = src.relative_to(ASSETS / "claude")
            asset(f"claude/{rel}", f".claude/{rel}")
    hook = a.dir / ".claude/hooks/block-git-commit.sh"
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    java = f"src/main/java/{package_path}"
    write(f"{java}/{main_class}.java", f"""package {a.package};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class {main_class} {{

    public static void main(String[] args) {{
        SpringApplication.run({main_class}.class, args);
    }}
}}
""")
    # An existing repository keeps its own classes, and its build may not have the dependencies these need
    is_new_project = "build.gradle" in created
    if is_new_project:
        asset("SecurityConfig.java", f"{java}/config/SecurityConfig.java")
        asset("ClockConfig.java", f"{java}/config/ClockConfig.java")
        asset("GlobalExceptionHandler.java", f"{java}/exception/GlobalExceptionHandler.java")
        if a.db == "postgres":
            for cls, pkg in POSTGRES_AUDIT_CLASSES.items():
                asset(f"postgres/{cls}.java", f"{java}/{pkg}/{cls}.java")
            asset("postgres/V1__create_audit_table.sql", "src/main/resources/db/migration/V1__create_audit_table.sql")
    if a.db == "mongodb":
        asset("MongoFlywayConfig.java", f"{java}/config/MongoFlywayConfig.java")

    for pkg, desc in PACKAGES.items():
        folder = a.dir / java / pkg.replace(".", "/")
        if folder.is_dir() and any(p.suffix == ".java" and p.name != "package-info.java" for p in folder.iterdir()):
            continue  # already has real classes
        write(f"{java}/{pkg.replace('.', '/')}/package-info.java", f"/**\n * {desc}\n */\npackage {a.package}.{pkg};\n")

    if a.db != "none" and not (a.db == "postgres" and is_new_project):
        write("src/main/resources/db/migration/.gitkeep", "")
    write("src/main/resources/application.yml", application_yml(a.name, a.port, a.db, a.kafka, a.integration))
    write("src/main/resources/application-local.yml", application_local_yml(a.name, a.db, a.kafka))
    write("docs/README.md", f"# {a.name} documentation\n\nTODO: link the docs for this service here.\n")

    if is_new_project:
        test_java = f"src/test/java/{package_path}"
        asset("SecurityConfigTests.java", f"{test_java}/config/SecurityConfigTests.java")
        asset("test-application.yml", "src/test/resources/config/application.yml")
        if uses_testcontainers:
            db_assets = DB_ASSET_DIR[a.db]
            asset(f"{db_assets}compose.yaml", "compose.yaml")
            asset(f"{db_assets}TestcontainersConfiguration.java", f"{test_java}/TestcontainersConfiguration.java")
            asset("ApplicationTests.java", f"{test_java}/{main_class}Tests.java")
    else:
        print("build.gradle already exists, so security, error handling, Clock, compose and starter tests were not added")

    print(f"created {len(created)} files in {a.dir}")
    if skipped:
        print(f"skipped {len(skipped)} existing files:")
        for s in skipped:
            print(f"  {s}")


if __name__ == "__main__":
    main()
