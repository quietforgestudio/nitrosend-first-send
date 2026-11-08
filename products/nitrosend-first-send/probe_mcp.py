#!/usr/bin/env python3
"""Read the Nitrosend remote MCP server's identity, tool list and tool annotations.

Self-contained: standard library only, no package install, no account beyond an API key.
It reads the key from the environment (`NITROSEND_API_KEY`) and never prints it.

    NITROSEND_API_KEY=... python3 probe_mcp.py > probe_mcp_<date>.txt

This is the exact script that produced `probe_mcp_20261025.txt` in this directory, so every
version string, tool count and annotation quoted in `report_mcp.md` is reproducible by anyone
with a free Nitrosend API key.
"""
import json, os, subprocess, sys, urllib.error, urllib.request

URL = os.environ.get("NITROSEND_API_URL", "https://api.nitrosend.com/mcp")
KEY = os.environ.get("NITROSEND_API_KEY")
if not KEY:
    sys.exit("NITROSEND_API_KEY is not set")


def rpc(method, params, sid=None, mid=1):
    req = urllib.request.Request(
        URL,
        data=json.dumps({"jsonrpc": "2.0", "id": mid, "method": method, "params": params}).encode(),
        method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json, text/event-stream")
    req.add_header("Authorization", "Bearer " + KEY)
    if sid:
        req.add_header("Mcp-Session-Id", sid)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, r.read().decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace"), dict(e.headers or {})


def ver(*argv):
    try:
        return subprocess.run(argv, capture_output=True, text=True).stdout.strip()
    except Exception as e:
        return "(%s)" % type(e).__name__


print("== runtime ==")
print("python3 -V:", ver("python3", "-V"))
print("node -v  :", ver("node", "-v"))
print("uname -r :", ver("uname", "-r"))
print("uname -m :", ver("uname", "-m"))
print("codex --version:", ver("codex", "--version"))
print()

st, txt, hd = rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                 "clientInfo": {"name": "moneymaker-probe", "version": "1"}})
print("== initialize http=%s ==" % st)
d = json.loads(txt[txt.find("{"):])
print("serverInfo:", json.dumps(d["result"]["serverInfo"]))
print("protocolVersion:", d["result"]["protocolVersion"])

sid = hd.get("Mcp-Session-Id") or hd.get("mcp-session-id")
st2, t2, _ = rpc("tools/list", {}, sid=sid, mid=2)
tools = json.loads(t2[t2.find("{"):])["result"]["tools"]
print("\n== tools/list http=%s : %d tools ==" % (st2, len(tools)))
print(", ".join(sorted(t["name"] for t in tools)))

print("\n== the two tools the MCP field note's run used, raw annotations ==")
for t in sorted(tools, key=lambda x: x["name"]):
    if t["name"] in ("nitro_get_status", "nitro_send_message"):
        print(t["name"], json.dumps(t.get("annotations"), sort_keys=True))
