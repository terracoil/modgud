# 🧭 Kinetic Layered Architecture (KLA)
> **ProjectVersion:** `v4.6.6` (2025‑11‑11)

---

## Overview

**Kinetic Layered Architecture (KLA)** organizes software around *motion* (**Active** layers) and *structure* (**Passive** layers).  
Active layers **do things**, responding kinetically to stimuli.  
Passive layers **are things**, defining structure and boundaries.

> **Active = does something (creates or propagates motion)**  
> **Passive = is something (defines or stabilizes motion)**

Every layer in KLA responds to something, but **only Active layers propagate kinetic motion**.  
Passive layers complete or define that motion structurally — they *react* but never *drive* flow.

---

## 🧱 Layer Model
| Icon  | Layer                                | Energy        | Stimulus Type                    | Responsibilities                                                                                                           | Depends On                            | Archetypes                                                                        |
|-------|--------------------------------------|---------------|----------------------------------|----------------------------------------------------------------------------------------------------------------------------|---------------------------------------|-----------------------------------------------------------------------------------|
| 🟨    | **Presentation (API/UI)**            | 🟢 **Active** | External (user, system, network) | Handles inputs, validates requests, triggers domain behavior through interfaces. Optionally wired via an `EnergyInverter`. | 🟦 Domain, 🟫 Foundation, ▶ Utilities | **Orchestrators, CLI handlers, Application Use Cases**                            |
| 🟪    | **Infrastructure**                   | 🟢 **Active** | Internal (domain contract call)  | Implements 🟦 Domain interfaces. Executes side effects like I/O, persistence, messaging, and external integration.         | 🟦 Domain, 🟫 Foundation, ▶ Utilities | **Repository Implementations, Service Implementations, Use Case Implementations** |
| 🟦    | **Domain (Interfaces Only)**         | ⚪ **Passive** | Conceptual (definition‑time)     | Declares the system’s contracts — repositories, services, and use case interfaces. Contains no logic or data.              | 🟫 Foundation, ▶ Utilities            | **Repository Interfaces, Service Interfaces, Use Case Interfaces**                |
| 🟫    | **Foundation (Shared Abstractions)** | ⚪ **Passive** | Structural (composition‑time)    | Defines immutable data — entities, contexts, enums, constants, exceptions, and shared models.                              | ▶ Utilities                           | **Entities, Contexts, Models, Enums, Exceptions**                                 |
| ▶     | **Utilities (Cross‑cutting)**        | ⚪ **Passive** | Functional (call‑time)           | Stateless helpers accessible to all layers. Perform computations but never drive control flow.                             | —                                     | **Helpers, Validators, Formatters**                                               |

---

## 🧩 Archetypes
| Archetype                     | Description                                                                                                                   | Interface (Layer) | Implementation (Layer)            | Naming(interface)                                   | Naming(implementation)                             | Notes                                                                                                                                  |
|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------|-------------------|-----------------------------------|-----------------------------------------------------|----------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| **Definition**                | Immutable, reusable structural abstraction.                                                                                   | —                 | 🟫Foundation                      | n/a                                                 | `FooEntity`, `FooModel`, `FooEnum`, `FooException` | Passive objects only — no behavior.  Enums, Entities, Models, Exceptions, Constants                                                    |
| **Context**                   | Immutable structure encapsulating runtime or workflow state. Passed across layers to provide consistent execution context.    | —                 | 🟫Foundation                      | n/a                                                 | `GenerationContext`, `TenantContext`               | Describes *where* motion occurs — shared, read-only data.                                                                              |
| **Repository Interface**      | Interface defines persistence or retrieval operations for entities. Implementation has real persistence logic (MyBatis, etc.) | 🟦 Domain         | 🟪Infrastructure                  | `FooRepositoryProtocol` or `FooRepositoryInterface` | `FooRepository`, `TenantRepository`                | Interface Defines how entities are accessed or persisted, Implementation executes SQL or storage logic and maps entities to data model |
| **Repository Implementation** | Real persistence logic using Quarkus MyBatis or similar frameworks.                                                           | —                 | 🟪Infrastructure                  | `FooRepository`                                     |                                                    | Executes SQL or storage logic and converts between data forms and entities.                                                            |
| **Service**                   | Reusable capability provided by the system (e.g., rendering, networking).                                                     | 🟦 Domain         | 🟪Infrastructure                  | `FooServiceInterface` or `FooServiceProtocol`       | `FooService`                                       | Defines what can be done (interface) and how (implementation).                                                                         |
| **Use Case**                  | Represents a single behavioral intention. Performs one directed action in response to stimuli.                                | 🟦 Domain         | 🟨Presentation / 🟪Infrastructure | `FooUseCaseProtocol`or `FooUseCaseInterface`        | `FooUseCase`                                       | Interfaces optional for single‑use Presentation workflows.                                                                             |
| **Orchestrator**              | Coordinates multiple use cases into workflows.                                                                                | —                 | 🟨Presentation                    | n/a                                                 | `FooOrchestrator`                                  | Entry‑point logic only; no business rules.                                                                                             |
| **Utility**                   | Stateless helper or formatter.                                                                                                | —                 | ▶ Utilities                       | n/a                                                 | `StringUtils`, `PathHelper`                        | Framework‑agnostic, pure computation.                                                                                                  |

---

## Naming Conventions 
* ALL interfaces should be named with the suffix `Protocol` or `Interface`:
  * Repositories: `FooRepositoryProtocol` or `FooServiceInterface`
  * Use Cases: `FooUseCaseProtocol` or `FooUseCaseInterface`
  * Services: `FooServiceProtocol` or `FooServiceInterface`
  * Other: `FooBarThingyProtocol or FooBarThingyInterface`
* ALL implementations of interfaces should be named with any suffix, other than for its archetype:
  * Repositories: `FooRepository`
  * Use Cases: `FooUseCase`
  * Services: `FooService`
  * Other: `FooBarThingy`

---

## 🧩 Use Case Guidelines

KLA draws a clear distinction between **use cases (interfaces and implementations)** and **use case orchestration**.  
Both are *active*, but they operate at different levels of intent and motion.

- ➡️ The **use case** performs a *single, bounded, directed action.*  
- ➡️ The **orchestration** coordinates *multiple use cases* into a *business workflow.*
- ➡️ Services are reusable capabilities (always need interfaces)
- ➡️ Use Cases are atomic business behaviors (interfaces are optional unless there are multiple use cases implementing the same interface/protocol)
- ➡️ Use Cases _can_ use services, Services should NEVER use cases.  If it looks like a service needs to use a use_case, it is an `Orchestrator`.
- ➡️ Use Cases should not WRITE to anything (files, databases, etc).  They can accept a service to do so, or an orchestrator using the use case can do the writing (preferred for non-trivial cases).


Use cases represent **system intentions** — atomic units of business behavior.  
Each use case has an interface (optional for Presentation‑specific ones) and an implementation that executes the behavior.

| Aspect                  | Use Case Interface                   | Use Case Implementation                                         | Use Case Orchestration                       |
|-------------------------|--------------------------------------|-----------------------------------------------------------------|----------------------------------------------|
| **Scope**               | Defines what the use case does.      | Executes one directed action.                                   | Coordinates multiple use cases.              |
| **Responsibility**      | Exposes the contract (input/output). | Performs the actual work through services and domain protocols. | Manages overall workflows.                   |
| **Layer**               | 🟦 Domain                            | 🟩 Presentation or 🟪 Infrastructure                            | 🟩 Presentation (presentation/orchestration) |
| **Interface Optional?** | ✅ Yes, if Presentation‑only          | ❌ No, when reused or infrastructural                            | N/A                                          |
| **Example**             | `FooUseCaseProtocol`                 | `FooUseCase`                                                    | `FooOrchestrator`                            |

## 🧩 Contexts in KLA

**Contexts** are immutable, framework‑neutral objects that capture the *state, parameters, and conditions* of a particular execution flow.  
They make motion explicit across layers without introducing coupling.

> **Contexts describe “where and under what conditions” motion occurs — they do not perform motion themselves.**

### Key Traits
- **Immutable:** Once created, never mutated.  
- **Passive:** Contain no methods that cause side effects.  
- **Cross‑layer:** Shared between orchestrators, use cases, and repositories.  
- **Serializable:** Easy to log, cache, or transmit.  
- **Simple:** Often implemented as Java records or Python dataclasses.

### Example — Python
```python
# 🟫 infrastructure/context/generation_context.py
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass(frozen=True)
class GenerationContext:
    project_name: str
    group_id: str
    artifact_id: str
    services: List[str]
    generated_at: datetime
```

### Example — Java
```java
// 🟫 foundation/context/GenerationContext.java
package com.example.foundation.context;

import java.time.Instant;
import java.util.List;

public record GenerationContext(
    String projectName,
    String groupId,
    String artifactId,
    List<String> services,
    Instant generatedAt
) {}
```

Contexts travel through orchestrators and use cases like this:
```java
// 🟨 presentation/orchestration/ProjectOrchestrator.java
public class ProjectOrchestrator {
    private final GenerateCodeUseCase generateCode;

    public ProjectOrchestrator(GenerateCodeUseCase generateCode) {
        this.generateCode = generateCode;
    }

    public void execute(GenerationContext context) {
        generateCode.run(context);
    }
}
```

---

## 🧩 Repository Example (Java 21 + Quarkus MyBatis)

Below shows a repository using POJOs as Entities from 🟫 Foundation.  
The 🟦 Domain defines the contract, and 🟪 Infrastructure provides the implementation.

```java
// 🟦 domain/repository/UserRepositoryInterface.java
package com.example.domain.repository;
import com.example.foundation.entities.UserEntity;
import java.util.List;

public interface UserRepositoryInterface {
    List<UserEntity> findAll();
    UserEntity findById(Long id);
    void insert(UserEntity user);
}
```

```java
// 🟫 foundation/entities/UserEntity.java
package com.example.foundation.entities;

public record UserEntity(Long id, String username, String email) {}
```

```java
// 🟪 infrastructure/repository/UserRepository.java
package com.example.infrastructure.repository;

import com.example.domain.repository.UserRepository;
import com.example.foundation.entities.UserEntity;
import jakarta.enterprise.context.ApplicationScoped;
import org.apache.ibatis.annotations.*;

import java.util.List;

@ApplicationScoped
@Mapper
public interface UserRepository extends UserRepositoryInterface {

    @Select("SELECT id, username, email FROM users")
    List<UserEntity> findAll();

    @Select("SELECT id, username, email FROM users WHERE id = #{id}")
    UserEntity findById(Long id);

    @Insert("INSERT INTO users (username, email) VALUES (#{username}, #{email})")
    void insert(UserEntity user);
}
```

This pattern keeps the repository contract pure in the Domain and the actual persistence logic in Infrastructure, using immutable POJOs for entity exchange.

---

## ⚙️ Dependency Matrix

| From → To | 🟨 Presentation | 🟪 Infrastructure | 🟦 Domain | 🟫 Foundation | ▶ Utilities | Description |
|------------|----------------|------------------|-----------|---------------|-------------|--------------|
| 🟨 **Presentation (Active)** | — | ⚙️ *Injects only* | ✅ Uses domain interfaces | ✅ Reads entities, contexts | ✅ Uses helpers | Top kinetic layer; triggers motion. |
| 🟪 **Infrastructure (Active)** | ✖️ | — | ✅ Implements domain interfaces | ✅ Uses entities, contexts | ✅ Uses utilities | Performs persistence and integrations. |
| 🟦 **Domain (Passive)** | ✖️ | ✖️ | — | ✅ Uses entities, contexts | ✅ Uses utilities | Defines contracts, unaware of implementations. |
| 🟫 **Foundation (Passive)** | ✖️ | ✖️ | ✖️ | — | ✅ Uses utilities | Defines immutable structures only. |
| ▶ **Utilities (Passive)** | ✖️ | ✖️ | ✖️ | ✖️ | — | Cross‑cutting helpers. |

✅ = Allowed dependency  
✖️ = Forbidden dependency  

---

## 💡 Key Takeaways
✅ **Definitions** express structure and contain Entities, Enums, Exceptions, and Models.
✅ **Entities** define what *is*; **Contexts** define *where and when*.  
✅ **Repositories** bridge between Storage (e.g., database) and Entities (and other definitions as needed).
✅ **Services** define reusable capabilities; Interfaces are defined in **🟦Domain**, Implementations are defined in **🟪Infrastructure**.
✅ **Domain** contains only *interfaces*, describing *what can happen*.  
✅ **Infrastructure** realizes motion — persistence, I/O, external calls.  
✅ **Foundation** is immutable and framework‑agnostic.  
✅ **EnergyInverter** provides explicit wiring for kinetic flow.
✅ **Active layers** depend only on Passive contracts — never the reverse.
✅ **Utilities** remain pure and stateless.

---

## 🔚 Conclusion  
- **Entities & Contexts** live in 🟫 Foundation as immutable structure.  
- **Domain** defines interfaces — never behavior.  
- **Infrastructure** enacts real-world motion.  
- **Presentation** triggers and orchestrates flow.  

> _Active performs. Passive defines. Contexts stabilize the field of motion._  
> _Explicit > Implicit. Constructor > Container._
