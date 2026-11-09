package {{PACKAGE}}.config;

import org.flywaydb.core.Flyway;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.mongodb.autoconfigure.MongoConnectionDetails;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Runs Flyway against MongoDB using Flyway's native MongoDB connector.
 *
 * <p>Spring Boot only auto-configures Flyway for a JDBC DataSource, so it is wired here by hand.
 * Migrations live in {@code src/main/resources/db/migration} as {@code V<n>__<description>.json};
 * each file holds exactly ONE MongoDB database command (as passed to {@code db.runCommand}).
 * Flyway only runs the first command in a file, so split multi-step changes into separate versions.
 */
@Configuration
@ConditionalOnProperty(prefix = "app.flyway", name = "enabled", havingValue = "true", matchIfMissing = true)
public class MongoFlywayConfig {

    @Bean(initMethod = "migrate")
    Flyway flyway(MongoConnectionDetails connectionDetails) {
        return Flyway.configure()
                // From the connection details, not the property, so Compose and Testcontainers connections work too
                .dataSource(connectionDetails.getConnectionString().getConnectionString(), null, null)
                .locations("classpath:db/migration")
                .sqlMigrationSuffixes(".json")
                // Standalone MongoDB has no multi-document transactions
                .executeInTransaction(false)
                .load();
    }
}
