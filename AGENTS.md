# Agent commit identity

Commits created by coding agents in this repository must use the repository
owner's GitHub identity for both author and committer:

- Name: `keepraw`
- Email: `49091395+keepraw@users.noreply.github.com`

Before committing, configure the current checkout explicitly:

```sh
git config --local user.name keepraw
git config --local user.email 49091395+keepraw@users.noreply.github.com
git config --local user.useConfigOnly true
```

Check `git var GIT_AUTHOR_IDENT` and `git var GIT_COMMITTER_IDENT` before
creating a commit. Both must match the identity above; environment variables can
override Git configuration. Check the resulting commit with
`git log -1 --format=fuller` before pushing. Do not inherit the execution
environment's global identity or add an unrelated co-author trailer.

Exception: normal GitHub Merge Pull Request merge commits may use GitHub/web-flow
as committer. This does not relax ordinary development commit identity, and does
not authorize automatic merges or rewriting earlier merge commits.

# Core mission and mandatory research rules

Every coding or research agent working in this repository must follow these
permanent operating rules without exception:

1. **Formal output first:** The primary goal of Airport History is to produce
   verified historical physical airport identities and formal historical
   IATA/ICAO code assignments in `data/`, together with the `resolved`
   `code + date -> physical airport` queries they enable for Keepraw-Fly — not
   to accumulate candidates.
2. **Research leads are not facts:** `candidate`, `research group`,
   `source revision`, and `geographic hypothesis` records are research inputs,
   never formal historical facts.
3. **Reuse before acquisition; no global rescans:** Before starting any research
   task, inspect `data/`, existing `research/` assets, `source-lock` records,
   and retained excerpts first. Repeating global upstream database scans is
   prohibited.
4. **Build the global passenger baseline:** Process the entire eligible
   population. Prioritize scheduled passenger sites, then regional airports
   and in-scope predecessors. Use batches for review and validation without
   imposing a project-wide airport cap.
5. **Mandatory per-batch reporting:** Every research or admission batch must
   explicitly report:
   - newly added formal airport identities;
   - newly added formal IATA assignments;
   - newly added formal ICAO assignments;
   - newly added `resolved` `code/date` queries (measured by the production
     resolver);
   - which candidates remain `pending`, and the exact evidence missing for each.
6. **No vanity metrics:** Candidate counts, source counts, and research file
   counts are never primary KPIs or success criteria.
7. **Owner-authorized continuity:** For a verified current airport-code
   association on a known physical site, presume continuous validity from
   the 2000 cutoff. Record this as `continuity_inference` and cite the current
   association and [owner policy](research/admission/default-continuity-v1/policy.json).
   The original allocation date is optional. Resolve a date only when the
   verified interval supports one physical airport.
8. **Evidence-driven exceptions:** Correct the baseline where affirmative
   evidence establishes a later opening, code transfer, withdrawal,
   metropolitan designation, wrong location or physical replacement. Record
   the scheme, affected site IDs, evidence and any uncertain transition.
   Prioritize cross-site reuse and preserve plausible ambiguity.
9. **Code boundaries are distinct from airport events:** Airport opening or
   closing dates, renames, regulatory certificates, and current directory rows
   cannot substitute for code effective or withdrawal dates.
10. **Independent scheme provenance:** IATA and ICAO assignments must be
    evidenced separately and must never be inferred from one another.
11. **Half-open intervals:** Every formal assignment must use the repository's
    left-closed, right-open local civil-date interval `[validFrom, validTo)`.
12. **Permanent physical IDs:** A permanent `airportId` (`apt_<UUIDv4>`)
    identifies a physical airfield and must never be regenerated when an IATA or
    ICAO code changes.
13. **Production resolver measurement:** Benefit to Keepraw-Fly must be measured
    with the production resolver (`resolveAirport()`), never estimated from
    unverified candidate counts.
14. **Repository hygiene:** Intermediate research outputs, global scan shards,
    duplicate/crosswalk indexes, full extractions, and large raw archives must
    stay in gitignored `work/` (or external archives) rather than accumulating
    in the main Git repository. Retain formal `data/`, source-lock provenance
    and SHA-256 hashes, minimal attributed citations/excerpts, reproducibility
    manifests, reviewed conclusions, and the four compact
    [targeted research indexes](docs/repository-slimming-and-history-plan.md#compact-index-retention)
    in Git.
15. **Historical scope:** Support local dates in `[2000-01-01, 2026-11-19)`.
    Prioritize approximately 3,800–4,000 scheduled commercial passenger sites
    and 6,000–6,500 broader passenger and regional sites. Include predecessors
    with passenger relevance inside the supported range. Store intervals and
    leave unestablished boundary dates open.

## Mandatory closed-loop workflow

All historical code work is evaluated against the full production loop:

```text
Research candidate
  -> Evidence
  -> Admission
  -> Formal assignment
  -> Production resolver
  -> Resolved code/date coverage
```

Any task that stops at the first three stages (`Research candidate` ->
`Evidence` -> `Admission`) is **incomplete** and must never be reported as
finished coverage.
