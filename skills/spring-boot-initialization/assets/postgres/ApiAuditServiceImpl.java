package {{PACKAGE}}.service;

import {{PACKAGE}}.dto.ApiAuditEntry;
import {{PACKAGE}}.entity.ApiAudit;
import {{PACKAGE}}.repository.ApiAuditRepository;
import java.time.Clock;
import java.time.Instant;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@RequiredArgsConstructor
@Service
public class ApiAuditServiceImpl implements ApiAuditService {

    private final ApiAuditRepository repository;
    private final Clock clock;

    @Override
    public void record(ApiAuditEntry entry) {
        repository.save(ApiAudit.builder()
                .id(UUID.randomUUID())
                .apiPath(entry.apiPath())
                .action(entry.action())
                .requestPayload(entry.requestPayload())
                .performedBy(entry.performedBy())
                .responseStatus(entry.responseStatus())
                .success(entry.success())
                .occurredAt(Instant.now(clock))
                .build());
    }
}
