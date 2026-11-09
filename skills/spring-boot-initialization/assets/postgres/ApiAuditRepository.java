package {{PACKAGE}}.repository;

import {{PACKAGE}}.entity.ApiAudit;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ApiAuditRepository extends JpaRepository<ApiAudit, UUID> {}
