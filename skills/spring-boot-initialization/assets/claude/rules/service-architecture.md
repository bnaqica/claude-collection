---
paths:
  - "src/**"
---

# Service architecture

## Call flow

```
CRUD:     @RestController -> CRUD @Service interface -> CRUD implementation -> @Repository -> DB
Action:   @RestController -> action @Service -> CRUD @Service interface -> ...
Listener: listener -> @Service
```

- Every database table (or MongoDB collection) has a CRUD `@RestController` in `api`.
  The one exception is the audit table, which is append-only and is never updated or deleted through an API.
- The service injected into a `@RestController` has an interface and an implementation:
  `CustomerService` and `CustomerServiceImpl`, both in `service`.
- The CRUD service implementation is the only caller of its `@Repository`. Nothing else touches a repository.
- An action API (anything other than CRUD) goes to its own service, which changes data only by calling
  the CRUD `@Service` interface. Dependencies point one way, from action to CRUD, so there are no cycles;
  a CRUD service never calls an action service.

## No logic in the edges

- **Controllers (`api`)** hold the contract only: route, parameters, validation annotations, and the call to the service.
- **Listeners (`listener`)** receive the event and pass it to a service. Parsing, filtering and decisions belong in the service.
- **Clients (`client`)** are contracts only: declarative `@HttpExchange` interfaces. Wiring goes in `config`,
  error translation in `exception`, and anything else around a call in a service.

## Mapping

Map by hand with the builder pattern (`@Builder` on records and entities). Mapping happens in the service
implementation, so controllers receive DTOs and never see an entity. Don't add mapping libraries such as MapStruct.

## Security

Every API call requires a Keycloak bearer token; the service is an OAuth2 resource server that validates it.
Only the health check is open, and only the `local` profile may turn authentication off, for development without Keycloak.

## PostgreSQL schemas and audit

These apply to services that use PostgreSQL.

- Never use the `public` schema. That includes the Flyway history table.
- The main schema is named after the service, with hyphens as underscores (`order-service` becomes `order_service`),
  and holds the service's ERD.
- A service that integrates with a third party also has a `<service_name>_integration` schema (`order_service_integration`)
  for that integration's own tables, so they stay separate from the ERD. Name the schema in `@Table(schema = ...)`.
- The `audit` schema holds `audit.api_audit`, with one row for every POST, PUT and DELETE request:
  - the API called and the action (the HTTP method)
  - the request payload
  - the person who made the change, from the token (`anonymous` if there is no valid token)
  - whether it succeeded, and the response status
- Requests that fail are audited too, including those rejected by security (401 and 403).
  So auditing runs outside the Spring Security filter chain.
- Audit rows are append-only.
