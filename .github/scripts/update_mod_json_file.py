#!/usr/bin/env python3

import json
import os
import re
import sys
import time
from datetime import datetime
from enum import Enum
from pathlib import Path

import requests

API_URL = os.environ.get('API_URL')
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')
# GitHub API rate limits are higher with authentication
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}

def fetch_github_repo_info(repo_url):
    """从 GitHub API 获取仓库详细信息"""
    owner, repo = extract_repo_info(repo_url)
    if not owner or not repo:
        return {}

    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        response = requests.get(api_url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return {
                "author_avatar_url": data["owner"]["avatar_url"],
                "description": data.get("description", ""),
                "stars": data.get("stargazers_count", 0),
                "repo_id": data.get("id", 0),
                "github_repo_url": repo_url
            }
    except Exception as e:
        print(f"⚠️ Failed to fetch GitHub info for {repo_url}: {e}")
    return {}

def extract_repo_info(repo_url):
    """Extract owner and repo name from GitHub repo URL."""
    match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
    if match:
        owner = match.group(1)
        repo = match.group(2)
        # Remove .git suffix if present
        repo = repo.removesuffix('.git')
        return owner, repo
    return None, None



def generate_commit_message():
    """Generate a detailed commit message listing all updated mods."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"Auto-update all.json ({timestamp})\n"
        
    return message


if __name__ == "__main__":
    start_timestamp = int(time.time())
    start_datetime = datetime.fromtimestamp(start_timestamp).strftime('%H:%M:%S')
    print(f"🔄 Starting automatic gen mod json at {start_datetime}...")


    # ✅ 不管是否有更新都生成 all.json
    mods_dir = Path('mods')
    all_meta = []
    for mod_dir in (d for d in mods_dir.iterdir() if d.is_dir()):
        meta_file = mod_dir / 'meta.json'
        if meta_file.exists():
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)

                # 重组字段结构
                new_entry = {
                    "name": meta.get("title", mod_dir.name),
                    "requires-steamodded": meta.get("requires-steamodded", False),
                    "requires-talisman": meta.get("requires-talisman", False),
                    "categories": meta.get("categories", []),
                    "author": meta.get("author", ""),
                    "downloadURL": meta.get("downloadURL", ""),
                    "folderName": meta.get("folderName", mod_dir.name),
                    "version": meta.get("version", ""),
                    "automatic-version-check": meta.get("automatic-version-check", False),
                }

                # 额外请求 GitHub 信息，合并进 new_entry
                repo_url = meta.get("repo", "")
                if repo_url:
                    github_info = fetch_github_repo_info(repo_url)
                    new_entry.update(github_info)
                else:
                    # 没有 repo 时，github_repo_url 置空，其他置默认
                    new_entry.update({
                        "author_avatar_url": "",
                        "description": "",
                        "stars": 0,
                        "repo_id": 0,
                        "github_repo_url": ""
                    })

                all_meta.append(new_entry)

            except Exception as e:
                print(f"⚠️ Failed to load {meta_file}: {e}")

    # 写入 all.json
    all_json_path = mods_dir / 'all.json'
    with open(all_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_meta, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"📦 Generated all.json with {len(all_meta)} entries.")

    commit_message = generate_commit_message()
    with open('commit_message.txt', 'w', encoding='utf-8') as f:
        f.write(commit_message)

    sys.exit(0)

