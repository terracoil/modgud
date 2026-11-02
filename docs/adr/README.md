**Parent**: [📚 Documentation Hub](../README.md) | [🌉 Main README](../../README.md) | [📖 API Reference](../api-reference.md)

# Architecture Decision Records

<img src="https://github.com/terracoil/modgud/raw/main/docs/modgud-github.jpg" alt="Modgud" title="Modgud" width="300"/>

---

Architecture Decision Records for modgud: the decisions that would otherwise live in someone's memory, written down while that memory still exists. A dated **Update** note at the top of an ADR means the code moved on and the record says how.

## What are ADRs?

Short documents that record one decision each: the context, the choice, the consequences, and what was rejected. They exist so the next person can disagree with the reasoning instead of guessing at it.

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](./ADR-001-implicit-return-transformation-approach.md) | Implicit Return Transformation Approach | Accepted | 2025-10-26 |
| [ADR-002](./ADR-002-guard-pattern-design-rationale.md) | Guard Pattern Design Rationale | Accepted | 2025-10-26 |
| [ADR-003](./ADR-003-registry-system-architecture.md) | Registry System Architecture | Accepted | 2025-10-26 |
| [ADR-004](./ADR-004-public-facade-and-api-tiers.md) | Public Facade and API Tiers | Accepted | 2026-11-02 |
| [ADR-005](./ADR-005-idunn-ports-and-adapters.md) | Idunn Ports and Adapters | Accepted | 2026-11-02 |

## ADR Format

Each ADR follows this standard format:

- **Status**: Current status (Proposed, Accepted, Deprecated, Superseded)
- **Context**: What problem are we solving and why?
- **Decision**: What architectural decision was made?
- **Consequences**: What are the positive and negative impacts?
- **Alternatives Considered**: What other options were evaluated?

## Contributing

When adding a new ADR:

1. Create a new file named `ADR-NNN-brief-description.md`
2. Follow the standard format shown in existing ADRs
3. Update this README index with the new ADR
4. Link to related ADRs where appropriate

## References

- [Michael Nygard's ADR template](https://github.com/joelparkerhenderson/architecture-decision-record)
- [Thoughtworks ADR guide](https://www.thoughtworks.com/en-us/insights/blog/architecture/demystifying-architecture-decision-records)