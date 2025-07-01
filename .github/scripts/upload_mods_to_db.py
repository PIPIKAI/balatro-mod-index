#!/usr/bin/env python3

import json
import os
import requests
from pathlib import Path

API_URL = os.environ.get("API_URL")  # 例如 api.example.com
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")
GAME_NAME = "balatro"

def main():
    all_json_path = Path("mods") / "all.json"
    if not all_json_path.exists():
        print("❌ all.json 文件不存在！请先运行生成 all.json 的脚本。")
        return

    with open(all_json_path, "r", encoding="utf-8") as f:
        mods = json.load(f)

    print(f"📦 准备上传 {len(mods)} 个 mod 到数据库")

    for mod in mods:
        if not API_URL or not ADMIN_TOKEN:
            print("❌ 缺少 API_URL 或 ADMIN_TOKEN 环境变量，跳过上传")
            return

        req_data = {
            "game_name": GAME_NAME,
            "repo_id": mod.get("repo_id"),
            "name": mod.get("name"),
            "github_repo_url": mod.get("github_repo_url"),
            "author": mod.get("author"),
            "author_avatar_url": mod.get("author_avatar_url"),
            "description": mod.get("description"),
            "version": mod.get("version"),
            "stars": mod.get("stars"),
        }

        try:
            resp = requests.post(
                f"https://{API_URL}/api/update_mod",
                headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
                json=req_data
            )
            if resp.status_code == 200:
                print(f"✅ 成功更新：{mod.get('name')}")
            else:
                print(f"⚠️ 更新失败：{mod.get('name')} - 状态码 {resp.status_code}")
                print(f"↪️ 返回内容: {resp.text}")
        except Exception as e:
            print(f"❌ 异常更新 mod：{mod.get('name')} - {e}")

if __name__ == "__main__":
    main()
