## General Principles
- Do not use comments, except for TODO comments. Instead, use clear and concise naming.
- Adhere to Clean Code principles.
- with naming do never use abbreviations.
- No one-line functions (single expression functions) are allowed. Always use curly braces and explicit returns.

## Testing Requirements
- Every line of UseCases and Services must be unit tested.
- Every Controller endpoint must be integration tested.
- Use the `given_when_then` naming convention for tests.
- Negative test cases must be at the top, positive cases must be last (TDD Style).
- Comments can be placed directly before a test name if the requirement is too complex to fit into the test name.
- Tests must follow the **Arrange-Act-Assert (AAA)** pattern.
- Every test must have exactly **one Act**.
- Formatting: Include exactly one empty line between the Arrange, Act, and Assert blocks.
- No other empty lines are allowed within the test body.
- No logic in tests; keep them strictly imperative.
- use statism over mockism, only mock when necessary (mostly real boundaries, like db-repositories).
- In integration tests, avoid mocking when possible. Only mock real external boundaries (e.g., external APIs, LLM calls).
- TDD Red Phase: Always verify a failing test fails for the correct reason before writing production code. If it fails for an unexpected reason, fix the test or surrounding code first.
`

## TDD Cycle Rules
Follow strict outside-in TDD. Each cycle is: **Red → Green → Refactor**, one test at a time.

**Test ordering — most degenerate first:**
Start with the case that requires the least production code to satisfy, then progressively add complexity. The canonical order is:
1. **Null / missing input** — e.g. required data is absent → throw exception, return empty
2. **Empty collection / zero value** — e.g. no items, zero count
3. **Single element / minimal valid input** — the smallest possible happy-path input
4. **Multiple elements / full happy path** — realistic, complete scenario
5. **Edge cases and boundaries** — e.g. exactly at a limit, duplicate entries

Each test should only force you to write the **minimum production code** needed to make it pass. If you find yourself writing logic that no current failing test demands, stop — you are ahead of the tests.

**Mandatory cycle — never skip or batch steps:**
1. **Write one test.** Stop. Do not write any production code yet.
2. **Run that single test.** It must fail. If it does not compile due to missing production types, create the minimal stub (empty class, method that throws `NotImplementedError`) to make it compile — then run again and confirm a red failure for the expected reason.
3. **Write the minimum production code** to make only that test pass. Nothing more.
4. **Run all tests.** They must all be green before continuing.
5. **Refactor** if needed, keeping all tests green.
6. Go to step 1 for the next test.

Writing multiple tests before running, or writing production code before seeing a red test, is a violation of this process.

