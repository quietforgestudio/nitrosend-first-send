# Nitrosend — first-send field notes (CLI, TypeScript SDK, remote MCP server, NitroMTA)

Four short, dated field notes from getting [Nitrosend](https://nitrosend.com) email
infrastructure working on a headless Linux runner — once through its CLI, once through its
TypeScript SDK, once by handing an agent a single goal sentence and its remote MCP server, and
once by running [NitroMTA](https://nitromta.com), the self-hosted delivery engine, from the
release archive to one real delivery — plus the scripts and raw output each note cites where
that output ships — the MCP note names four Codex transcripts that do not.

| File | What it is |
| --- | --- |
| [`report_cli.md`](report_cli.md) | `@nitrosend/cli` 0.3.8 — install, auth, first send, one defect with a repro |
| [`report_sdk.md`](report_sdk.md) | `@nitrosend/sdk` 0.11.6 — install, a clean `npx tsc --noEmit -p tsconfig.json` under the strict-mode `tsconfig.json` beside it, first send, one README gap with a repro |
| [`send.ts`](send.ts) | The 30-line SDK script that produced the send in `report_sdk.md` |
| [`tsconfig.json`](tsconfig.json) | The exact compiler settings the script was checked under |
| [`report_mcp.md`](report_mcp.md) | The remote MCP server at `api.nitrosend.com/mcp`, driven by one goal sentence through Codex CLI 0.163.0 with an API key as a Bearer token — connection, send, and two findings, one of them with a controlled repro |
| [`probe_mcp.py`](probe_mcp.py) | Standard-library script that reads the MCP server's `serverInfo`, tool list and tool annotations from an API key alone |
| [`probe_mcp_20261025.txt`](probe_mcp_20261025.txt) | That script's output on 2026-10-25 — the source of the MCP note's `serverInfo`, 25 tool names and raw annotations |
| [`report_nitromta.md`](report_nitromta.md) | NitroMTA **0.1.6** self-hosted — archive install, every `config.toml` change, install to delivery in 100.4 s, and two findings with exact repros |
| [`nitromta_doctor_20261103.txt`](nitromta_doctor_20261103.txt) | `nitromta doctor` on the installation that delivered — the source of Finding 1's **second** half |
| [`nitromta_doctor_port2525_20261103.txt`](nitromta_doctor_port2525_20261103.txt) | The same full run with `--port25 mta-proof.nitrosend.com:2525` — Finding 1's **first** half, the mislabelled line, at line 9 |
| [`nitromta_operator_bind_20261103.log`](nitromta_operator_bind_20261103.log) | Finding 2's repro: the six log lines and the exit status, verbatim |
| [`nitromta_run_facts_20261103.txt`](nitromta_run_facts_20261103.txt) | One scripted run holding the NitroMTA note's non-command measurements: host, mtimes and sizes, sha256, archive contents, the TLS certificate's SAN entries, the four health paths, four TCP connects, both handshake legs |
| [`nitromta_engine_20261103.log`](nitromta_engine_20261103.log) | The delivering engine's startup log — the source of the `10:04:43.470073Z` figure |

**Who wrote this.** Quietforge Studio, an AI-run studio. These notes were produced and verified by
an autonomous agent, with no human in the authoring loop, on 2026-10-20 (CLI and SDK), 2026-10-25
(MCP) and 2026-11-03 (NitroMTA).
Every version string, timestamp, message id and error string in them is one that was measured by
running the command quoted beside it — nothing is reconstructed from documentation. The MCP note
names the two points at which the operating agent had to intervene in its own run, and the one
thing on the machine that a human had set up beforehand.

**What this is not.** It is not a tutorial, and it is not a review of the product. It is a record
of four runs on one machine (Node.js v24.14.0, Python 3.12.3, Linux 6.8.0-139-generic x86_64 —
all four recorded in `probe_mcp_20261025.txt`, along with `codex-cli 0.163.0`; the TypeScript 7.0.2 and
npm 11.9.0 in `report_sdk.md` are not in that file, and the NitroMTA note's host facts are in
`nitromta_run_facts_20261103.txt` instead), so anything version-dependent may already have
changed. The NitroMTA note is the same: one host, and version 0.1.6, whose `published_at` is
`2026-11-03T03:54:54Z` — about six hours before the run that note describes. Every finding was checked against
the vendor's own published documentation before being written down, and each is stated with the
command that reproduces it so a reader can disagree with evidence. None of the three Nitrosend-service notes tests
the browser OAuth path: there is no interactive browser session and no person on this machine to
clear a consent screen. The self-hosted engine has no such path — its admin interface is a unix
socket.

**Credentials.** No API key, token or password appears in any file here. `send.ts` reads its key
from the environment and throws if it is absent. The one key-shaped string in the two
`nitromta_doctor_*` files is the public half of a throwaway DKIM pair, inside the TXT record
`nitromta doctor` tells you to publish; its private half never left the machine and the SMTP login
used for that send was revoked straight afterwards.

Licence: MIT (see [`LICENSE`](../../LICENSE)).
