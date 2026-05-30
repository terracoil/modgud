
# 🧭 KOA — Kinetic Oriented Architecture  
## Full Architecture Specification (v0.3.0)

This is the complete KOA specification including all content developed so far:
- Energy-first model  
- Color + icon + shape language  
- Segments + passive/active/dissipative archetypes  
- UsedBy/UserOf matrix  
- Box-art diagrams  
- Quarkus + MyBatis directory layout + code examples  
- YAML schema preview  
- Icon lexicon  

You can paste your diagrams (PNG/SVG/drawio) between sections.

---

# 1. KOA Ground — Architectural Invariants (⏚)

KOA is grounded (literally) on a set of invariants represented by the **Ground icon** (⏚).  
These invariants define the "field" in which all architectural energy moves:

- **Presentation never depends directly on Infrastructure.**
- **Domain/Foundation never depends on Presentation or Infrastructure.**
- **Constructor-only dependency injection (DI).**
- **Ports define allowed behaviors; Adapters implement them.**
- **Domain/Foundation is pure passive potential energy.**
- **Infrastructure is where dissipation (I/O) and kinetic logic lives.**

> **Ground = the anchor point for system behavior, invariants, and dependency rules.**

---

# 2. KOA Energy Model

KOA treats software action as **energy flow**.  
The four energies correspond to strict architectural roles:

## 2.1 Energy Palette

| Icon | Name                    | Color | Archetypes |
|------|-------------------------|--------|--------------|
| 🔋   | Potential Energy        | `#1F6F5F` (dark teal green) | Definitions, Entities, Contexts, Ports |
| ⚡   | Kinetic Energy          | `#264DFF` (deep kinetic blue) | UseCaseAdapters, ServiceAdapters, Orchestrators |
| 💧   | Dissipative Energy      | `#009FBF` (deep cyan) | RepositoryAdapters, ExternalAdapters |
| ⚙️   | Neutral/Utility Energy  | `#555555` (iron gray) | Utility helpers |

### What is I/O in KOA?
Any energy leaving the system boundary:
- DB reads/writes
- Message queues
- External HTTP/gRPC/GraphQL
- Filesystem
- Cache (externalized state)
- Cloud APIs (S3/GCS/Azure)
- OS pipes, sockets, system calls

All such dissipation is **cyan**.

---

# 3. Segments (Not Layers)

KOA uses **segments** to group energy types.

## 3.1 Presentation Segment (🟨 Yellow)
- Orchestrators (blue)
- App-facing UseCaseAdapters (blue)
- Resources/controllers

Speaks only to:
- Ports (green)
- Entities/Definitions/Contexts (green)
- Utilities (gray)

---

## 3.2 Ports Segment (Green Hexagons)
All Ports belong to the domain/foundation segment:
- UseCasePort
- ServicePort
- RepositoryPort
- ExternalPort

All **interfaces**, all **potential**, all **green**.

---

## 3.3 Infrastructure Segment (Slate Blue)
Contains:
- ⚡ Blue kinetic adapters (internal behavior)
- 💧 Cyan dissipative adapters (I/O)

Implements Ports.  
Zero upward dependency.

---

## 3.4 Domain/Foundation Segment (Slate Grey-Green)
An **upside-down trapezoid** representing stable bedrock.

Contains green passive items:
- Entities
- Definitions
- Contexts
- Ports
- Domain Errors / Domain Enums

No I/O. No framework. No DI annotations.

---

## 3.5 Cross-Cutting Utilities (Gray)
Diagonal wedge cutting across the whole system.

Contains:
- Logging
- String helpers
- Validation
- Crypto
- Small functional libraries

Never depends on application segments.

---

# 4. Archetypes: Color, Shape, Energy

| Archetype | Shape | Color | Icon | Energy |
|-----------|---------|--------|--------|-----------|
| Definition | Rounded rectangle | Green `#1F6F5F` | 🧱 📘 | 🔋 |
| Entity | Rounded rectangle | Green | 🌱 🌳 | 🔋 |
| Context | Rounded rectangle | Green | 🗺️ | 🔋 |
| Port | Hexagon | Green | 🔌 💠 | 🔋 |
| UseCaseAdapter | Octagon | Blue `#264DFF` | ⚡ ✨ | ⚡ |
| ServiceAdapter | Octagon | Blue | 🔥 ⚙️ | ⚡ |
| RepositoryAdapter | Cylinder | Cyan `#009FBF` | 💧 🗄️ | 💧 |
| ExternalAdapter | Parallelogram | Cyan | 🌊 📡 | 💧 |
| Orchestrator | Diamond | Blue | 🎛️ ⚡ | ⚡ |
| Utility | Slanted wedge | Gray `#555555` | 🧰 🔧 | ⚙️ |

---

# 5. UsedBy / UserOf Matrix

| UsedBy ↓ / UserOf → | Definition | Entity | Context | Port | Adapter | Orchestrator | Utility |
|---------------------|-----------|--------|---------|------|---------|--------------|---------|
| Definition          | ✅ | ✅ | ✅ | ⛔ | ⛔ | ⛔ | ✅ |
| Entity              | ✅ | ✅ | ✅ | ⛔ | ⛔ | ⛔ | ✅ |
| Context             | ✅ | ✅ | ✅ | ⛔ | ⛔ | ⛔ | ✅ |
| Port                | ✅ | ✅ | ✅ | ✅ | ⛔ | ⛔ | ✅ |
| Adapter             | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⛔ | ✅ |
| Orchestrator        | ✅ | ✅ | ✅ | ✅ | ⛔ | ⚠️ | ✅ |
| Utility             | ⛔ | ⛔ | ⛔ | ⛔ | ⛔ | ⛔ | ✅ |

Legend:  
- **Green → Gray allowed**  
- **Blue/Cyan → Green allowed**  
- **Green → Blue not allowed**

---

# 6. Box-Art Diagram (ASCII)

```
                              KOA GROUND (⏚)
                       (invariants, DI rules, boundaries)

             ┌─────────────────────────────────────────┐
             │            PRESENTATION  (🟨 Yellow)   │
             │   🎛️ Orchestrators                    │
             │   ⚡ UseCaseAdapters                    │
             └─────────────────┬──────────────────────┘
                               ▼
                       🔌💠 PORTS (Green Hexagons)

   ┌───────────────────────────┬───────────────────────────┐
   │    INFRASTRUCTURE (Slate Blue) 🛠️                    │
   │   ⚡ Blue KineticAdapters                               │
   │   💧 Cyan IO Adapters                                   │
   └──────────────────┬──────────────────────────────────────┘
                      ▼
             ┌───────────────────────────┐
             │ DOMAIN/FOUNDATION (Green) │
             │ upside trapezoid          │
             └───────────────────────────┘

─────────────────────────────────────────────────────────────
   UTILITIES (Gray) — diagonal wedge (🧰⚙️)
```

---

# 7. Quarkus + MyBatis KOA Layout (Full)

A complete directory layout for a KOA microservice using Quarkus (Jakarta) + MyBatis (no ORM):

```
src/
  main/
    java/
      com/example/users/
        app/
          presentation/
            UsersResource.java
            UsersOrchestrator.java
        domain/
          entities/
            UserEntity.java
          contexts/
            RequestContext.java
          ports/
            UserRepositoryPort.java
            ListUsersUseCasePort.java
        infrastructure/
          mybatis/
            mapper/
              UserMapper.java
            adapters/
              UserRepositoryAdapter.java
              ListUsersUseCaseAdapter.java
          external/
            # ExternalAdapters (if needed)
        util/
          # neutral helpers
    resources/
      mybatis/
        UserMapper.xml
      application.yml
```

---

# 8. Java Examples (Blue/Cyan/Green)

### 8.1 Domain Entities (Green)

```java
public record UserEntity(Long id, String username, String email) {}
```

### 8.2 Ports (Green Hexagons)

```java
public interface UserRepositoryPort {
    List<UserEntity> findAll();
    UserEntity findById(Long id);
    void save(UserEntity user);
}
```

### 8.3 MyBatis Mapper (I/O Cyan)

```java
@Mapper
public interface UserMapper {
    List<UserEntity> selectAll();
    UserEntity selectById(Long id);
    void insert(UserEntity user);
}
```

### 8.4 RepositoryAdapter (Cyan)

```java
@ApplicationScoped
public class UserRepositoryAdapter implements UserRepositoryPort {
    private final UserMapper mapper;
    @Inject UserRepositoryAdapter(UserMapper mapper) { this.mapper = mapper; }

    public List<UserEntity> findAll() { return mapper.selectAll(); }
    public UserEntity findById(Long id){ return mapper.selectById(id); }
    public void save(UserEntity user) { mapper.insert(user); }
}
```

### 8.5 UseCaseAdapter (Blue)

```java
@ApplicationScoped
public class ListUsersUseCaseAdapter implements ListUsersUseCasePort {
    private final UserRepositoryPort repo;
    @Inject ListUsersUseCaseAdapter(UserRepositoryPort repo){ this.repo = repo; }
    public List<UserEntity> listAllUsers(){ return repo.findAll(); }
}
```

---

# 9. Presentation / Orchestrator (Blue in Yellow Segment)

```java
@ApplicationScoped
public class UsersOrchestrator {
    private final ListUsersUseCasePort listUsers;
    @Inject UsersOrchestrator(ListUsersUseCasePort listUsers){ this.listUsers = listUsers; }
    public List<UserEntity> handleListUsers(){ return listUsers.listAllUsers(); }
}
```

```java
@Path("/users")
@RequestScoped
public class UsersResource {
    @Inject UsersOrchestrator orchestrator;
    @GET @Produces(MediaType.APPLICATION_JSON)
    public List<UserEntity> list(){ return orchestrator.handleListUsers(); }
}
```

---

# 10. YAML Schema (Preview)

```yaml
koa:
  version: 0.3.0
  energy_levels:
    potential:  { icon: "🔋", color: "#1F6F5F" }
    kinetic:    { icon: "⚡", color: "#264DFF" }
    dissipative:{ icon: "💧", color: "#009FBF" }
    neutral:    { icon: "⚙️", color: "#555555" }
  segments:
    - name: presentation
      color: "#FFC93C"
    - name: domain
      color: "#1E2A27"
    - name: infrastructure
      color: "#2E3A59"
```

---

# 11. Icon Lexicon (Concise)

### Favorites
✨ ⚡ 🔥 🌊 💧 🧱 📦 🧩 🧭 🗺️ 🎯 📐 🛠️ 🧰 🌱 🌳 💡 🧠 🔌 💠 🎛️ 🚦 🔧

### Categories (Selected)
- **Energy**: ✨ ⚡ 🔥 🌊 💧 🌀 🌪️ ☀️ 🌙  
- **Architecture**: 🧱 📐 🏗️ 🏛️ 🏢  
- **Flow**: 🧭 🛤️ 🔄 ♻️  
- **Components**: 🧩 📦 🔗 🎯  
- **Tools**: 🛠️ 🔧 ⚙️ 🎛️  
- **Concepts**: 💡 💭 🧠 📌 ℹ️  

---

# END OF DOCUMENT

