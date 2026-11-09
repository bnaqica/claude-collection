-- Flyway creates the schemas listed in spring.flyway.schemas before running this.
CREATE TABLE audit.api_audit (
    id              UUID PRIMARY KEY,
    api_path        VARCHAR(2048) NOT NULL,
    action          VARCHAR(10)   NOT NULL,
    request_payload TEXT,
    performed_by    VARCHAR(255)  NOT NULL,
    response_status INTEGER       NOT NULL,
    success         BOOLEAN       NOT NULL,
    occurred_at     TIMESTAMPTZ   NOT NULL
);

CREATE INDEX idx_api_audit_occurred_at ON audit.api_audit (occurred_at);
