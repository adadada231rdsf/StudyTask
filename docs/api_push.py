# -*- coding: utf-8 -*-
"""当 git push（github.com:443）被网络阻断时，用 api.github.com 直接写一个 commit。

用法：python docs/api_push.py [--push]

原理：Git Trees/Commits API 一次请求提交 "path" -> "blob sha" 的对照表，
用本地 git 算出每个文件的 blob sha 并先上传，再建 tree、建 commit、更新 ref。
网络抖动会重试；已存在的 blob / tree 会直接复用。
"""
import base64
import json
import subprocess
import sys
import time

GH = r"C:\Users\alice\AppData\Local\Temp\ghcli\bin\gh.exe"
REPO = "adadada231rdsf/StudyTask"
BRANCH = "main"
TRIES = 5


def git(*args, binary=False):
    out = subprocess.run(["git", *args], capture_output=True, check=True).stdout
    return out if binary else out.decode("utf-8", "replace").strip()


def gh_api(path, method="GET", payload=None):
    last = ""
    for attempt in range(1, TRIES + 1):
        proc = subprocess.run(
            [GH, "api", "-X", method, f"repos/{REPO}/{path}", "--input", "-"],
            input=json.dumps(payload).encode("utf-8") if payload is not None else b"",
            capture_output=True,
        )
        if proc.returncode == 0:
            out = proc.stdout.decode("utf-8", "replace").strip()
            return json.loads(out) if out else {}
        last = proc.stderr.decode("utf-8", "replace").strip()
        if "timeout" in last.lower() or "EOF" in last or "connection" in last.lower():
            wait = 2 * attempt
            print(f"  retry {attempt}/{TRIES} in {wait}s: {last.splitlines()[0][:90]}")
            time.sleep(wait)
            continue
        raise SystemExit(f"gh api {path} failed: {last}")
    raise SystemExit(f"gh api {path} failed after {TRIES} tries: {last}")


def main():
    head = git("rev-parse", "HEAD")
    message = git("log", "-1", "--pretty=%B")

    tree_map, blobs = {}, {}
    for line in git("ls-tree", "-r", "HEAD").splitlines():
        meta, path = line.split("\t", 1)
        mode, kind, sha = meta.split()
        if kind != "blob" or mode == "120000":
            continue
        tree_map[path] = {
            "path": path,
            "mode": "100755" if mode == "100755" else "100644",
            "type": "blob",
            "sha": sha,
        }
        blobs.setdefault(sha, path)

    print(f"commit {head}  files={len(tree_map)}  unique blobs={len(blobs)}")

    for i, (sha, path) in enumerate(sorted(blobs.items()), 1):
        content = base64.b64encode(git("cat-file", "blob", sha, binary=True)).decode("ascii")
        res = gh_api("git/blobs", "POST", {"content": content, "encoding": "base64"})
        if res["sha"] != sha:
            raise SystemExit(f"blob sha mismatch for {path}: {res['sha']} != {sha}")
        if i % 10 == 0 or i == len(blobs):
            print(f"  uploaded {i}/{len(blobs)}")

    # base_tree 用远端真实存在的那个 tree：本地父提交可能是 API 生成的，
    # 因此本地 git 里存着它的 sha，但 GitHub 上不存在（父提交不同）。
    remote = gh_api(f"git/ref/heads/{BRANCH}")
    base_tree = gh_api(f"git/commits/{remote['object']['sha']}")["tree"]["sha"]
    print("remote head:", remote["object"]["sha"], "base_tree:", base_tree)

    tree = gh_api("git/trees", "POST", {
        "base_tree": base_tree,
        "tree": list(tree_map.values()),
    })
    print("tree:", tree["sha"])

    commit = gh_api("git/commits", "POST", {
        "message": message,
        "tree": tree["sha"],
        "parents": [remote["object"]["sha"]],
    })
    print("commit:", commit["sha"])

    gh_api(f"git/refs/heads/{BRANCH}", "PATCH", {"sha": commit["sha"], "force": True})
    print("ref updated:", BRANCH, "->", commit["sha"])

    if "--push" in sys.argv:
        subprocess.run(["git", "update-ref", f"refs/remotes/origin/{BRANCH}", head], check=True)
        print(f"refs/remotes/origin/{BRANCH} ->", head)


if __name__ == "__main__":
    main()