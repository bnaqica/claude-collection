package {{PACKAGE}}.config;

import static org.springframework.security.config.Customizer.withDefaults;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;

/**
 * Every endpoint needs a valid JWT from {@code JWT_ISSUER_URI}, except the health check. CSRF protection is off
 * because requests carry a bearer token and there are no sessions or cookies.
 */
@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    @Profile("!local")
    SecurityFilterChain securedFilterChain(HttpSecurity http) throws Exception {
        return http.csrf(AbstractHttpConfigurer::disable)
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(requests -> requests.requestMatchers("/actuator/health/**")
                        .permitAll()
                        .anyRequest()
                        .authenticated())
                .oauth2ResourceServer(server -> server.jwt(withDefaults()))
                .build();
    }

    /** No authentication in the {@code local} profile, so the API and Swagger UI work without an identity provider. */
    @Bean
    @Profile("local")
    SecurityFilterChain localFilterChain(HttpSecurity http) throws Exception {
        return http.csrf(AbstractHttpConfigurer::disable)
                .authorizeHttpRequests(requests -> requests.anyRequest().permitAll())
                .build();
    }
}
