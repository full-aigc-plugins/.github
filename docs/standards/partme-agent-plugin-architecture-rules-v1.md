# Partme Agent Plugin Architecture Rules v1

- **Policy ID:** PAPR-001
- **Status:** Active — Organization Architecture Policy (v1)
- **Scope:** All active Agent Plugin repositories in both `full-aigc-plugins` and `full-stack-plugins` (primarily `*-plugin` repos). Standalone native engines, CLI programs, core libraries and archived repositories are outside the mandatory plugin gate unless explicitly opted in.
- **Upstream:** [Agent Plugins Specification v1.0.0](https://agent-plugins.org/specification) and [Agent Skills Specification](https://agentskills.io/specification).
- **Principle:** **Skill-first · Harness-optional · Reuse-before-build · Explicit-execution · One-state-owner**.

This document is the **canonical policy**. Do not copy and edit diverging versions in individual plugin repositories. Each plugin's `AGENTS.md` must link to this document; CI uses the shared policy checker in the organization `.github` repository. Domain-specific OpenSpec contracts remain authoritative for domain behavior as long as they do not violate this organization-level architecture policy.

## 1. Normative versus Partme-specific rules

**Agent Plugins v1.0.0** requires a root `plugin.json`. Its two portable component types are **Skills** (immediate children of `skills/` containing `SKILL.md`) and **MCP servers** (optional root `mcp.json`). Missing `skills/` or `mcp.json` is **not** a specification error. Commands and Hooks are **client extensions**, not portable v1 components; do not declare them as standard top-level manifest fields. The official specification and its schemas remain normative for portability.

The rules below are **Partme organization policy**, not additional requirements imposed by the upstream standard.

## 2. Architectural responsibilities

| Component | Owns | Does not own by default |
|---|---|---|
| Agent Host | Intent interpretation, plan selection, Skill/tool choice, user interaction | Native editing engine |
| Manifest (`plugin.json`) | Identity, portable metadata and client extension metadata | Business implementation |
| Domain Skill | Task know-how, constraints, references, tool usage and verification instructions | Its own Agent Runtime |
| Client Command | User-visible explicit entry into a Skill, if supported | Duplicate domain executor |
| Client Hook | Bounded, host-supported lifecycle actions | Global orchestration or unconditional native process launch |
| MCP configuration | Discovery of concrete tools | Second copy of CLI business logic |
| Optional Harness Skill | Explicit *plugin-level* complex execution procedure, if justified | Mandatory path for every request |
| Optional `harness.py` | Small, deterministic validation/adaptation/dispatch/verification helper | Agent planner, generic scheduler, database platform |
| CLI / MCP / Native Runtime | Real side effects, domain operations, enforced permissions, durable execution identity as needed | LLM intent interpretation |
| Artifacts/receipts | Verifiable evidence of what happened | Assumed success inferred from agent text |

### R01 — Skills first

Design a new plugin around `plugin.json` and the smallest useful set of Skills. For each requested operation, first prefer the host's capabilities, an existing CLI/MCP, or a domain Skill. Adding a directory, script, service, or database is **not** inherently evidence of a better plugin.

### R02 — Harness is optional (NO mandatory Harness)

**Zero Harness Skills is valid.** A plugin must never create one merely to satisfy a template, tests, or CI. A normal Skill may call an existing CLI or MCP tool directly.

If the plugin **does need** plugin-level coordinated, deterministic behavior unavailable through ordinary Skills and existing tools, use **at most one** discoverable `skills/<plugin-or-domain>-harness/SKILL.md` with a name ending in `-harness`. The preferred canonical name is `<plugin.json:name>-harness`. Existing differing names should be migrated without breaking users; CI may warn during migration.

The Harness Skill may invoke `scripts/harness.py` **inside its own Skill folder** when Python is appropriate, or call an available MCP/CLI directly. Neither Python nor shell access is guaranteed in every host. `harness.py` is **optional**. Do **not** create an undiscoverable private Harness and assume Agent Hosts will invoke it automatically.

### R03 — Explicit invocation path

A runtime module is a product capability only when it has a documented, testable chain:

```text
User request → discovered Skill / supported client Command
             → Agent tool call (Shell, MCP, or other host tool)
             → actual CLI/MCP/script entry
             → real operation → verified artifact/receipt
```

A code file imported only by tests is **not** proof of a host-reachable feature. Show the actual entry in documentation and prove it in an appropriate real host. A Skill does not gain new tools merely by mentioning a script.

### R04 — Reuse before implementation

Before adding nontrivial executable logic, document: existing host capabilities, upstream/Fork CLI or MCP operations, missing functionality, chosen owner, and a reproducible test. No second native engine, second tool protocol, or replicated provider logic inside the plugin when the execution tool already owns it.

### R05 — One authoritative durable execution state

If cross-session tasks are needed, the component that actually owns execution should normally own task IDs, idempotency, cancellation, recovery, and canonical durable state. A Skill or helper may query and summarize this state but must not silently introduce another conflicting task ledger. `unknown` means reconcile before retrying a side-effecting operation.

### R06 — Safety at the real execution boundary

Skill instructions alone cannot enforce security. The CLI/MCP/runtime that performs the operation must enforce path restrictions, authorization, permission scopes and durable safety rules. No unchecked external actions, fabricated user approvals, made-up receipts, or blind retries. A user or host can still call a CLI directly; the plugin's `harness.py` is **not** a sandbox.

### R07 — Prefer lean client extensions

Commands forward user intent to Skills. Hooks respond to precisely documented host events, and do not silently start long-lived native processes or hijack every request. Client-specific files live in documented client namespaces / native compatibility directories; the root portable manifest stays portable.

### R08 — Deterministic helper scope

An optional `harness.py` may implement `doctor`, `capabilities`, `validate`, `run`, `verify`, and forwarding `status` / `reconcile` if the underlying tool supports them. Prefer JSON requests and results; normalize error states (`succeeded`, `failed`, `blocked`, `unknown`). Avoid inventing an Agent Planner, general-purpose task orchestration runtime, duplicate Controller/Worker pool, or persistence layer in every plugin.

### R09 — Keep runtime and user data separate

Do not store user assets, secrets, logs, mutable runtime state, or generated artifacts in the immutable plugin installation path. Respect the actual loaded Skill path. A stdio MCP subprocess may receive `PLUGIN_ROOT` and `PLUGIN_DATA` under the Agent Plugins specification; ordinary Skill-launched shell scripts must not assume these variables always exist.

### R10 — Original Fork and Skill ownership

Forked applications such as FilmCraft, PhotoCraft and EffectCraft remain **execution tools**, separate from `*-plugin` packaging and independent `full-aigc-skills` source repositories. Track licenses, pinned binaries, origin and version digests. Vendored Skill snapshots must not create an independently maintained second implementation of the original engine.

### R11 — Keep release claims evidence-bound

Manifest/schema validation, unit tests, installed-client discovery, actual model routing, native tool execution and artifact verification are distinct acceptance levels. Record `NOT_RUN` and partial coverage; never promote static validation to live compatibility or creative acceptance.

### R12 — Migration must preserve behavior

When reducing an existing `src/harness`, Controller, ledger, or database, first trace consumers and determine whether any real execution/safety guarantee depends on it. Migrate callers and test parity before deletion. Mark legacy private executors as **review required**, not dead code solely because their name is unfamiliar.

## 3. Allowed layouts

**Type A — Skills-only:** `plugin.json` + optional `skills/*/SKILL.md`.

**Type B — Skills + CLI/MCP:** `plugin.json`, Skills, optional `mcp.json`, possibly small adapters; preferred for most editor/service wrappers.

**Type C — Optional Harness:** Type A/B plus **at most one** discoverable `skills/*-harness/SKILL.md`, and optional `skills/*-harness/scripts/harness.py`. Only use when a specific execution constraint justifies it.

```text
my-plugin/
├── plugin.json
├── skills/
│   ├── my-plugin-use/SKILL.md
│   ├── my-plugin-export/SKILL.md
│   └── my-plugin-harness/          # OPTIONAL — do not create by default
│       ├── SKILL.md
│       └── scripts/harness.py     # OPTIONAL
├── mcp.json                       # OPTIONAL
├── <client-extension>/            # OPTIONAL, client-specific
├── AGENTS.md                      # must reference this policy
└── .github/workflows/
    └── partme-plugin-architecture.yml
```

## 4. Continuous integration: blocking versus review

The **shared reusable workflow** [Partme Plugin Architecture CI](https://github.com/full-aigc-plugins/.github/blob/main/.github/workflows/partme-plugin-architecture.yml) runs [`scripts/check_plugin_architecture.py`](https://github.com/full-aigc-plugins/.github/blob/main/scripts/check_plugin_architecture.py). Per-repository workflows call it; they must not duplicate its implementation.

**Automated blocking checks (static):**
- `AGENTS.md` points to this canonical policy.
- For initialized plugin repos: a parsable root `plugin.json` with the official v1 schema marker, valid `name` and no misleading portable top-level commands/hooks/skills/MCP declaration.
- If `mcp.json` exists, essential transport/configuration structure is correct.
- **Harness absence is a PASS.** If `*-harness` Skills exist, there is at most one and it contains a discoverable, frontmatter-identified `SKILL.md`.
- An explicitly named `harness.py` entry must not exist only as an orphan root script without a discoverable Harness Skill.

**Non-blocking architecture review flags:**
- Legacy `src/harness`, private task ledgers, or differing Harness names may require manual call-chain review; static checks cannot establish non-reachability or redundant functionality.
- Skeleton repositories without an initialized `plugin.json` are reported as `BOOTSTRAP / NOT A CONFORMING PLUGIN`; they are **not** treated as published plugins. On first manifest addition, initialized-plugin checks automatically become blocking.

**Not proven by static CI:** real model routing, Shell/MCP permission availability, native execution, artifacts, retries, authorization, multiple-client compatibility. These require real-host integration/acceptance tests.

## 5. Rollout and exceptions

Apply to active `*-plugin` repositories in **both** `full-aigc-plugins` and `full-stack-plugins`; do not mutate archived repos or upstream Fork/CLI and engine repositories with plugin-only rules. Reuse the public GitHub Actions workflow across organizations, without duplicating the checker or normative policy. The canonical policy is stored once, at `full-aigc-plugins/.github/docs/standards/partme-agent-plugin-architecture-rules-v1.md`; the location does not restrict its scope to AIGC. Each participating repository's `AGENTS.md` references that same canonical URL. Standalone `full-stack-plugins/guardengine`, `codeguard`, `specguard`, `archguard`, `testguard`, `gitguard` and `flowguard` are **engine/CLI** repos, not Agent Plugin packages, and are excluded from the mandatory plugin-shaped CI. Their `*-plugin` wrappers are in scope.

Existing domain-specific OpenSpec, CI and release scripts must be **preserved**. Fix static blocking problems rather than suppressing them. For a behavior-changing migration of execution logic, write an OpenSpec plan, prove host reachability and safety parity, and obtain the normal repository review before removal.
