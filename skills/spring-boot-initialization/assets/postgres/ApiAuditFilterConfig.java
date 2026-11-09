package {{PACKAGE}}.config;

import {{PACKAGE}}.service.ApiAuditService;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.oauth2.jwt.JwtDecoder;

@Configuration
public class ApiAuditFilterConfig {

    /** One step ahead of the Spring Security filter chain, which runs at order -100. */
    private static final int BEFORE_SECURITY = -101;

    @Bean
    FilterRegistrationBean<ApiAuditFilter> apiAuditFilter(ApiAuditService auditService, JwtDecoder jwtDecoder) {
        FilterRegistrationBean<ApiAuditFilter> registration =
                new FilterRegistrationBean<>(new ApiAuditFilter(auditService, jwtDecoder));
        registration.setOrder(BEFORE_SECURITY);
        return registration;
    }
}
