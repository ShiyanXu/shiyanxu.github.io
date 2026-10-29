#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库 → GitHub Pages 同步发布

扫描 Obsidian 知识库，只把**有变化**的笔记同步进站点仓库的 kb/ 目录，
同时生成分类数据、按天归档的更新日志，最后按「一天一提交」的规则 commit + push。

用法：
    python3 sync.py                # 同步 + 提交 + 推送
    python3 sync.py --dry-run      # 只看会改动什么，不落盘
    python3 sync.py --no-push      # 同步 + 提交，不推送
    python3 sync.py --force        # 忽略 manifest，全量重建
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

DEFAULT_VAULT = Path("/Users/xushiyan/Library/CloudStorage/OneDrive-个人/Obsidian/AI/知识库")
DEFAULT_REPO = Path("/Users/xushiyan/dev/kb-site")

SKIP_DIRS = {".obsidian", ".workbuddy", ".git", ".trash", "_site", "node_modules"}
# 「**01-Agent心法** —— 怎么跟 Agent 配合才出好活」
CAT_RE = re.compile(r"^\*\*(\d{2}-[^*]+)\*\*\s*——\s*(.+?)\s*$", re.M)
# 大写字母/数字与汉字之间补一个空格：MCP与工具接入 → MCP 与工具接入
CJK_GAP = re.compile(r"(?<=[A-Za-z0-9])(?=[\u4e00-\u9fff])")


# ---------------------------------------------------------------- 工具函数

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def read_title(path: Path, fallback: str) -> str:
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
                if line and not line.startswith(">"):
                    break
    except OSError:
        pass
    return fallback


def pretty_category(dirname: str) -> str:
    """01-Agent心法 → Agent 心法"""
    name = re.sub(r"^\d{2}-", "", dirname)
    return CJK_GAP.sub(" ", name)


def yaml_dump(obj) -> str:
    """JSON 是合法 YAML，用 JSON 输出避免手写转义出错。"""
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def run(cmd, cwd, check=True):
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if check and proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"命令失败：{' '.join(cmd)}")
    return proc


def git_has_changes(repo: Path) -> bool:
    out = run(["git", "status", "--porcelain"], repo).stdout.strip()
    return bool(out)


# ---------------------------------------------------------------- 扫描

def load_vault_readme(vault: Path):
    """从 README 抽分类的一句话描述。"""
    desc = {}
    readme = vault / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        for key, d in CAT_RE.findall(text):
            desc[key] = d.strip()
    return desc


def scan_vault(vault: Path):
    """返回 (files, categories)。files: relpath -> {sha,title,dir}"""
    desc = load_vault_readme(vault)
    files, categories = {}, []

    for d in sorted(vault.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name in SKIP_DIRS:
            continue
        mds = sorted(p for p in d.glob("*.md") if p.is_file())
        if not mds:
            continue
        categories.append({
            "key": d.name,
            "name": pretty_category(d.name),
            "desc": desc.get(d.name, ""),
        })
        for p in mds:
            rel = f"{d.name}/{p.name}"
            files[rel] = {
                "sha": sha256(p),
                "title": read_title(p, p.stem),
                "dir": d.name,
                "src": str(p),
            }
    return files, categories


# ---------------------------------------------------------------- manifest

def load_manifest(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("⚠️  manifest 损坏，按全量新增处理")
    return {"version": 1, "files": {}, "removed": []}


def diff_files(old: dict, new: dict):
    old_files = old.get("files", {})
    added = [k for k in new if k not in old_files]
    modified = [k for k in new if k in old_files and old_files[k]["sha"] != new[k]["sha"]]
    removed = [k for k in old_files if k not in new]
    return added, modified, removed


def update_manifest(manifest: dict, new: dict, added, modified, removed, today: str):
    files = manifest.setdefault("files", {})
    removed_log = manifest.setdefault("removed", [])

    for key, info in new.items():
        if key in files and key not in added and key not in modified:
            continue  # 没变，保留原有 first/events
        prev = files.get(key)
        events = prev.get("events", []) if prev else []
        if key in added:
            events.append({"date": today, "action": "added"})
        else:
            events.append({"date": today, "action": "modified"})
        # 同一天同类型事件只留一条
        dedup, seen = [], set()
        for e in events:
            sig = (e["date"], e["action"])
            if sig not in seen:
                seen.add(sig)
                dedup.append(e)
        files[key] = {
            "sha": info["sha"],
            "title": info["title"],
            "dir": info["dir"],
            "first": prev["first"] if prev else today,
            "last": today if (prev and (key in modified)) else (prev["last"] if prev else today),
            "events": dedup,
        }

    for key in removed:
        prev = files.pop(key, None)
        if prev:
            removed_log.append({
                "path": key,
                "title": prev.get("title", Path(key).stem),
                "dir": prev.get("dir", ""),
                "date": today,
            })

    manifest["version"] = 1
    manifest["generated"] = datetime.now().isoformat(timespec="seconds")
    return manifest


# ---------------------------------------------------------------- 写站点文件

def front_matter(meta: dict) -> str:
    lines = ["---"]
    for k, v in meta.items():
        lines.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def write_kb_pages(repo: Path, vault: Path, new: dict, changed: dict, today: str, dry: bool):
    kb = repo / "kb"
    if not dry:
        kb.mkdir(parents=True, exist_ok=True)

    for rel in changed:
        info = new[rel]
        dst = kb / rel
        title = info["title"]
        cat_name = pretty_category(info["dir"])
        fm = front_matter({
            "layout": "kb",
            "title": title,
            "kb_cat": cat_name,
            "kb_cat_key": info["dir"],
            "kb_src": rel,
            "kb_updated": today,
        })
        if dry:
            print(f"  [dry] 写入 kb/{rel}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        body = Path(info["src"]).read_text(encoding="utf-8")
        dst.write_text(fm + body, encoding="utf-8")


def prune_removed(repo: Path, removed, dry: bool):
    for rel in removed:
        dst = repo / "kb" / rel
        if dst.exists():
            if dry:
                print(f"  [dry] 删除 kb/{rel}")
            else:
                dst.unlink()
            # 顺手清理空目录
            if not dry and dst.parent.exists() and not any(dst.parent.iterdir()):
                dst.parent.rmdir()


# ---------------------------------------------------------------- 数据文件

def build_categories_data(new: dict, categories: list, manifest: dict) -> dict:
    files = manifest["files"]
    out = []
    for cat in categories:
        pages = []
        for rel, info in sorted(new.items()):
            if info["dir"] != cat["key"]:
                continue
            meta = files.get(rel, {})
            pages.append({
                "title": info["title"],
                "url": f"/kb/{cat['key']}/{Path(rel).stem}.html",
                "file": Path(rel).name,
                "first": meta.get("first", ""),
                "last": meta.get("last", ""),
            })
        cat = dict(cat)
        cat["count"] = len(pages)
        cat["pages"] = pages
        out.append(cat)
    return {
        "total": sum(c["count"] for c in out),
        "categories": out,
    }


def build_updates_data(manifest: dict, limit_days: int = 365) -> dict:
    files = manifest.get("files", {})
    by_date = {}

    def bucket(d):
        return by_date.setdefault(d, {"date": d, "added": [], "modified": [], "removed": []})

    for rel, info in files.items():
        for e in info.get("events", []):
            d = e["date"]
            item = {
                "title": info.get("title", Path(rel).stem),
                "url": f"/kb/{rel.rsplit('.md', 1)[0]}.html",
                "category": pretty_category(info.get("dir", "")),
            }
            key = "added" if e["action"] == "added" else "modified"
            bucket(d)[key].append(item)

    for r in manifest.get("removed", []):
        item = {
            "title": r.get("title", Path(r.get("path", "x")).stem),
            "url": "",
            "category": pretty_category(r.get("dir", "")),
        }
        bucket(r["date"])["removed"].append(item)

    days = []
    for d in sorted(by_date, reverse=True)[:limit_days]:
        entry = by_date[d]
        if entry["added"] or entry["modified"] or entry["removed"]:
            for k in ("added", "modified"):
                entry[k].sort(key=lambda x: x["title"])
            days.append(entry)

    return {
        "total": sum(len(v["added"]) for v in by_date.values()),
        "last_sync": manifest.get("generated", ""),
        "days": days,
    }


def write_data_files(repo: Path, cats: dict, updates: dict, dry: bool):
    if dry:
        print(f"  [dry] 写入 _data/kb.yml（{len(cats['categories'])} 分类，{cats['total']} 篇）")
        print(f"  [dry] 写入 _data/kb_updates.yml（{len(updates['days'])} 天）")
        return
    data = repo / "_data"
    data.mkdir(parents=True, exist_ok=True)
    (data / "kb.yml").write_text(yaml_dump(cats), encoding="utf-8")
    (data / "kb_updates.yml").write_text(yaml_dump(updates), encoding="utf-8")


INDEX_HEAD = """{fm}# 知识库

<div class="kb-stats">
  <div class="kb-stat"><b>{{{{ site.data.kb.total }}}}</b><span>篇笔记</span></div>
  <div class="kb-stat"><b>{{{{ site.data.kb.categories | size }}}}</b><span>个分类</span></div>
  <div class="kb-stat"><b>{{{{ site.data.kb_updates.days | size }}}}</b><span>天有更新</span></div>
</div>
"""


def write_kb_index(repo: Path, vault: Path, cats: dict, dry: bool):
    """kb/index.md = 统计条 + 知识库 README 原文（链接正好相对 kb/ 有效）"""
    readme = vault / "README.md"
    body = readme.read_text(encoding="utf-8") if readme.exists() else "# 知识库\n"
    # 去掉 README 自己的 H1，避免与模板标题重复
    body = re.sub(r"^#\s+.*\n+", "", body, count=1)

    fm = front_matter({
        "layout": "kb",
        "title": "知识库总览",
        "kb_home": True,
    })
    content = INDEX_HEAD.format(fm=fm) + "\n" + body

    if dry:
        print("  [dry] 写入 kb/index.md")
        return
    (repo / "kb").mkdir(parents=True, exist_ok=True)
    (repo / "kb" / "index.md").write_text(content, encoding="utf-8")


# ---------------------------------------------------------------- git

def push_with_retry(repo: Path) -> bool:
    p = run(["git", "push", "origin", "HEAD:main"], repo, check=False)
    if p.returncode != 0:
        print("  推送失败，尝试 rebase 后重试…")
        run(["git", "pull", "--rebase", "--autostash", "origin", "main"], repo, check=False)
        p = run(["git", "push", "origin", "HEAD:main"], repo, check=False)
        if p.returncode != 0:
            print(p.stderr, file=sys.stderr)
            return False
    return True


def pending_commits(repo: Path) -> int:
    out = run(["git", "rev-list", "--count", "@{u}..HEAD"], repo, check=False).stdout.strip()
    return int(out) if out.isdigit() else 0


def flush_pending(repo: Path):
    """补推上次没推成功的提交（推送失败时本地 commit 仍在）。"""
    n = pending_commits(repo)
    if n > 0:
        print(f"发现 {n} 个未推送的提交，先补推…")
        if push_with_retry(repo):
            print("✓ 补推成功")
        else:
            print("⚠️  补推仍然失败，本次不再继续")


def commit_and_push(repo: Path, today: str, counts: dict, push: bool, dry: bool):
    if dry or not git_has_changes(repo):
        return False

    run(["git", "add", "-A"], repo)

    parts = []
    if counts["added"]:
        parts.append(f"新增 {counts['added']} 篇")
    if counts["modified"]:
        parts.append(f"修改 {counts['modified']} 篇")
    if counts["removed"]:
        parts.append(f"移除 {counts['removed']} 篇")
    detail = "、".join(parts) if parts else "整理站点数据"
    msg = f"知识库更新 {today}：{detail}"

    # 一天一提交：若 HEAD 已是今天由本脚本产生的提交且尚未推送，则 amend
    head_msg = run(["git", "log", "-1", "--format=%s"], repo, check=False).stdout.strip()
    can_amend = head_msg.startswith(f"知识库更新 {today}") and pending_commits(repo) == 0

    if can_amend:
        run(["git", "commit", "--amend", "-m", msg], repo)
        print(f"✓ 已 amend 当天提交：{msg}")
    else:
        run(["git", "commit", "-m", msg], repo)
        print(f"✓ 已提交：{msg}")

    if push:
        if push_with_retry(repo):
            print("✓ 已推送，GitHub Pages 稍后自动构建")
        else:
            raise SystemExit("推送失败（提交已保存在本地，下次运行会自动补推）")
    return True


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="知识库同步发布")
    ap.add_argument("--vault", default=str(DEFAULT_VAULT))
    ap.add_argument("--repo", default=str(DEFAULT_REPO))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--today", default=None, help="覆盖提交日期（测试用）")
    args = ap.parse_args()

    vault, repo = Path(args.vault), Path(args.repo)
    if not vault.is_dir():
        raise SystemExit(f"知识库目录不存在：{vault}")
    if not (repo / ".git").exists():
        raise SystemExit(f"站点仓库未初始化：{repo}")

    today = args.today or date.today().isoformat()
    manifest_path = repo / ".kb-manifest.json"
    manifest = {"version": 1, "files": {}, "removed": []} if args.force else load_manifest(manifest_path)

    if not args.dry_run and not args.no_push:
        flush_pending(repo)

    new, categories = scan_vault(vault)
    added, modified, removed = diff_files(manifest, new)

    if not (added or modified or removed):
        print(f"无变化（{len(new)} 篇笔记，已是最新）")
        # 数据文件仍可能因模板调整需要刷新，这里保持幂等：不写、不提交
        return

    print(f"检测到变更：新增 {len(added)} / 修改 {len(modified)} / 移除 {len(removed)}")

    manifest = update_manifest(manifest, new, added, modified, removed, today)
    changed = added + modified
    write_kb_pages(repo, vault, new, changed, today, args.dry_run)
    prune_removed(repo, removed, args.dry_run)

    cats = build_categories_data(new, categories, manifest)
    updates = build_updates_data(manifest)

    write_data_files(repo, cats, updates, args.dry_run)
    write_kb_index(repo, vault, cats, args.dry_run)

    if not args.dry_run:
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    counts = {"added": len(added), "modified": len(modified), "removed": len(removed)}
    did = commit_and_push(repo, today, counts, push=not args.no_push, dry=args.dry_run)
    if not did and not args.dry_run:
        print("工作区无实际改动，未提交")


if __name__ == "__main__":
    main()
