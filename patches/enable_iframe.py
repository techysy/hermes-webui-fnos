#!/usr/bin/env python3
"""修补 HermesWebUI server 源码, 允许 iframe 嵌入 (窗口版).

用途: 打包 iframe 窗口变体前对 server 源码打补丁。
位置: 打包时对 build 目录的 app/server/api/helpers.py 执行此脚本。

修改:
1. helpers.py:77   frame-ancestors 'none'  → frame-ancestors *      (允许任意 iframe 嵌入)
2. helpers.py:184  X-Frame-Options: DENY   → X-Frame-Options: SAMEORIGIN

注意: 打完补丁打包 iframe 版后, 必须恢复原始 helpers.py (url 版保留安全头)。
"""
import sys


def patch_file(path: str) -> bool:
    with open(path) as f:
        content = f.read()
    orig = content
    content = content.replace("frame-ancestors 'none'; ", "frame-ancestors *; ")
    content = content.replace(
        "handler.send_header('X-Frame-Options', 'DENY')",
        "handler.send_header('X-Frame-Options', 'SAMEORIGIN')",
    )
    if content != orig:
        with open(path, 'w') as f:
            f.write(content)
        print(f"patched: {path}")
        return True
    print(f"no change: {path} (patterns not found, server version may differ)")
    return False


if __name__ == '__main__':
    helpers = sys.argv[1] if len(sys.argv) > 1 else 'api/helpers.py'
    sys.exit(0 if patch_file(helpers) else 1)
