package {{PACKAGE}}.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;
import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/** One POST, PUT or DELETE request. Append-only. */
@Entity
@Table(schema = "audit", name = "api_audit")
@Getter
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED) // for JPA
@AllArgsConstructor
public class ApiAudit {

    @Id
    private UUID id;

    @Column(name = "api_path", nullable = false)
    private String apiPath;

    @Column(nullable = false)
    private String action;

    @Column(name = "request_payload")
    private String requestPayload;

    @Column(name = "performed_by", nullable = false)
    private String performedBy;

    @Column(name = "response_status", nullable = false)
    private int responseStatus;

    @Column(nullable = false)
    private boolean success;

    @Column(name = "occurred_at", nullable = false)
    private Instant occurredAt;
}
