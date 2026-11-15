## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## Market numbers: one shared record (Jerry 2026-11-15)
- `data/market-numbers.json` is the ONE record of market numbers (Maryland REALTORS monthly county figures + the weekly Freddie Mac rate), live at https://jerrylyonsrealestate.com/data/market-numbers.json.
- Whenever you change ANY market number on the site (monthly Maryland REALTORS update, weekly Freddie Mac rate, county table), update this record IN THE SAME COMMIT and take the page numbers from it: a new month goes in as `months[0]` (older months stay below); a new rate updates `mortgage_rate` and is prepended to `rate_history`; set `updated` to today; check it parses (python json.load).
- The Facebook/Instagram, LinkedIn, Google Business and chat agents read ONLY this record, so the site and the posts always match. Never estimate; never put a number on a page that is not in the record.
- The town "This Month" boxes (Realtor.com data) are not in this record.
