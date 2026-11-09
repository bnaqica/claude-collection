package {{PACKAGE}}.config;

import {{PACKAGE}}.dto.ApiAuditEntry;
import {{PACKAGE}}.service.ApiAuditService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Set;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.ContentCachingRequestWrapper;

/**
 * Records every POST, PUT and DELETE in {@code audit.api_audit}, whether it succeeded or not.
 *
 * <p>{@link ApiAuditFilterConfig} runs this ahead of the Spring Security filter chain, so requests rejected by
 * security are audited too. That is also why the token is read here: the security context has been cleared by
 * the time the chain returns.
 */
@Slf4j
@RequiredArgsConstructor
public class ApiAuditFilter extends OncePerRequestFilter {

    private static final Set<String> AUDITED_METHODS = Set.of("POST", "PUT", "DELETE");
    private static final String BEARER_PREFIX = "Bearer ";
    private static final String ANONYMOUS = "anonymous";
    private static final int MAX_PAYLOAD_BYTES = 1_048_576;

    private final ApiAuditService auditService;
    private final JwtDecoder jwtDecoder;

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !AUDITED_METHODS.contains(request.getMethod());
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        ContentCachingRequestWrapper wrapped = new ContentCachingRequestWrapper(request, MAX_PAYLOAD_BYTES);
        boolean threw = true;
        try {
            chain.doFilter(wrapped, response);
            threw = false;
        } finally {
            audit(wrapped, response, threw);
        }
    }

    private void audit(ContentCachingRequestWrapper request, HttpServletResponse response, boolean threw) {
        try {
            int status = threw ? HttpServletResponse.SC_INTERNAL_SERVER_ERROR : response.getStatus();
            auditService.record(ApiAuditEntry.builder()
                    .apiPath(request.getRequestURI())
                    .action(request.getMethod())
                    .requestPayload(payload(request))
                    .performedBy(performedBy(request))
                    .responseStatus(status)
                    .success(status < HttpServletResponse.SC_BAD_REQUEST)
                    .build());
        } catch (RuntimeException | IOException ex) {
            // The request has already been handled; a failed audit write must not change its outcome
            log.error("Failed to audit {} {}", request.getMethod(), request.getRequestURI(), ex);
        }
    }

    private String payload(ContentCachingRequestWrapper request) throws IOException {
        if (request.getContentAsByteArray().length == 0) {
            // Security rejected the request before anything read the body
            request.getInputStream().readAllBytes();
        }
        return new String(request.getContentAsByteArray(), StandardCharsets.UTF_8);
    }

    private String performedBy(HttpServletRequest request) {
        String header = request.getHeader(HttpHeaders.AUTHORIZATION);
        if (header == null || !header.startsWith(BEARER_PREFIX)) {
            return ANONYMOUS;
        }
        try {
            return jwtDecoder.decode(header.substring(BEARER_PREFIX.length())).getClaimAsString("preferred_username");
        } catch (RuntimeException ex) {
            return ANONYMOUS; // invalid or expired token, or the issuer can't be reached
        }
    }
}
