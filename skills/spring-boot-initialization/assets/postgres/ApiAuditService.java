package {{PACKAGE}}.service;

import {{PACKAGE}}.dto.ApiAuditEntry;

public interface ApiAuditService {

    void record(ApiAuditEntry entry);
}
