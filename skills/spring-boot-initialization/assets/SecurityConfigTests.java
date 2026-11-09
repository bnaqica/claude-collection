package {{PACKAGE}}.config;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

/** A 404 here means the request got past security; this slice has no controllers or actuator. */
@WebMvcTest(useDefaultFilters = false) // no controllers, so this keeps working as the service grows
@Import(SecurityConfig.class)
class SecurityConfigTests {

    private final MockMvc mockMvc;

    @MockitoBean
    private JwtDecoder jwtDecoder;

    SecurityConfigTests(@Autowired MockMvc mockMvc) {
        this.mockMvc = mockMvc;
    }

    @Test
    void rejectsRequestWithoutToken() throws Exception {
        mockMvc.perform(get("/anything")).andExpect(status().isUnauthorized());
    }

    @Test
    void acceptsRequestWithToken() throws Exception {
        mockMvc.perform(get("/anything").with(jwt())).andExpect(status().isNotFound());
    }

    @Test
    void healthCheckIsPublic() throws Exception {
        mockMvc.perform(get("/actuator/health")).andExpect(status().isNotFound());
    }
}
