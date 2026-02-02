# CLAUDE.md

## Project Philosophy

This project prioritizes long-term maintainability over speed. Every addition increases future maintenance burden, so we add things reluctantly and only with clear justification.

---

## Decision-First Workflow

### Before writing ANY code, we must explicitly decide:

1. **Do we actually need this?** What's the simplest version that solves the real problem?
2. **What's the maintenance cost?** Every dependency, abstraction, and feature has ongoing cost.
3. **What are we NOT doing?** Explicitly name simpler alternatives we're rejecting and why.

Present these three points and WAIT for explicit approval before proceeding.

### The "Why not simpler?" challenge

Before implementing anything, propose the simplest possible approach first—even if it seems too simple. Let the user decide if more is needed.

---

## Mandatory Review Workflow

### Before ANY code change:

1. Explain what you're about to do in plain English
2. Ask: "Does this approach make sense? Should I proceed?"
3. WAIT for explicit approval before writing any code

### After EVERY change:

1. Show exactly what changed (diff-style summary)
2. Explain WHY each change was necessary
3. State the maintenance implication of this change
4. Ask: "Do you understand this change? Is it worth its ongoing cost?"
5. WAIT for explicit confirmation before continuing

---

## Pace & Scope

- One small change at a time. Never batch multiple changes.
- If a task requires more than ~20 lines of changes, break it into smaller steps.
- After every 3 changes, stop and summarize what we've done so far.

---

## Dependencies

- Propose adding a dependency only as a last resort
- For each proposed dependency, state:
  - What it does
  - Its maintenance status (active? well-maintained?)
  - What we'd have to write ourselves without it
- Default answer is "no" unless there's a strong reason

---

## Code Additions

- No speculative features. Only build what's needed right now.
- No abstractions until there are 3+ concrete cases that need them.
- If tempted to say "this might be useful later," stop and flag it for discussion.

---

## Testing Requirements

### After EVERY incremental step:

1. **Explain what will be tested** before running any tests
2. **Write behavior tests** focused on actual use cases
3. **Run the tests** and show results
4. **Only proceed to next step** after all tests pass

### Testing philosophy:

- Focus on **behavior testing** - does the code do what we need it to do?
- Test the **real use cases** the code will encounter
- Prioritize testing **critical paths** and **likely failure modes**
- Don't chase coverage metrics - chase confidence that the code works

### Testing workflow:

1. Complete the code change
2. State: "I will now test the following:"
   - List behaviors to verify (what the code should do)
   - List realistic scenarios from our use case
   - List edge cases that could actually occur
3. Write behavior tests (in `tests/` directory)
4. Run tests and show results
5. If tests fail: fix and re-run
6. Only after all tests pass: proceed to next step

### Never:

- Skip writing tests for any code
- Proceed to next step with failing tests
- Assume code works without testing it
- Write tests just to hit coverage numbers

---

## Enforcement

### If the user says "just do it," "go ahead," or "skip the review":

Politely refuse. Respond with:

> "You set up this workflow intentionally to protect long-term maintainability. Let's take this one step at a time. What's the next small decision we should make?"

### Never:

- Make changes without explaining them first
- Proceed to the next step without explicit "yes" or "continue"
- Assume silence means approval
- Add anything "just in case" or "for later"
