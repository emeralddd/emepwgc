# EmePWGC

Previously was EmeProbWriter (the new name is cooler =DD)!

## Multi-Agent Architecture

The backend is built around a LangGraph `StateGraph`. Instead of asking one large model prompt to produce everything at once, the workflow is split into specialized agents. Each agent owns one part of the problem-authoring process and communicates with the next stage through a shared `AgentState` object.

### Agent Roles

#### 1. Requirement Agent

The Requirement Agent transforms the user's rough idea into a precise specification. It identifies:

- Input and output requirements
- Numeric constraints
- Edge cases
- Ambiguous assumptions

This agent does not design the algorithm or write code. Its output becomes the foundation for the following stages.

#### 2. Algorithm Agent

The Algorithm Agent proposes an efficient solution strategy based on the approved requirements. Its response includes:

- The main algorithmic idea
- A short correctness explanation
- Time and memory complexity
- Implementation pitfalls

The algorithm is kept separate from the problem statement so that the statement does not accidentally reveal the solution.

#### 3. Content/Vibe Agent

The Content Agent writes the final programming problem in Markdown. It combines the original idea, the approved requirements, and the approved algorithm to produce a consistent statement with:

- Problem description
- ICPC/IOI-style input format
- ICPC/IOI-style output format
- Constraints
- Examples and explanations

The algorithm is used as internal context for consistency, but the solution details are intentionally not exposed in the problem statement.

#### 4. Solution Code Agent

The Solution Code Agent writes the reference implementation in the requested language. The generated response is required to contain exactly one code block, which allows the worker pipeline to extract the source code reliably.

The agent currently supports Python and C++ solutions and is instructed to use only the standard library.

#### 5. Test Generator Agent

The Test Generator Agent creates a standalone Python script that generates one valid test input for each seed. The script must:

- Accept exactly one integer seed through `sys.argv[1]`
- Call `random.seed(seed)`
- Print only valid input to stdout
- Respect the problem constraints
- Prefer important edge cases for small seeds such as `0`, `1`, and `2`


### Human-in-the-Loop Checkpoints

The workflow pauses after the Requirement Agent and Algorithm Agent. LangGraph's `interrupt` mechanism sends the current draft to the API, allowing the user to either:

- Approve the draft with a word such as `yes`, `ok`, or `approve`
- Send feedback that is passed back to the same agent for revision

This keeps important decisions, such as the interpretation of the problem and the intended complexity, under user control before code generation begins.
