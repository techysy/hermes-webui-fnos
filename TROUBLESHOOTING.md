# HermesWebUI fnOS — 问题排查与修复记录

> 记录开发过程中遇到的问题和解决方案，方便后续迭代参考。

---

## 2026-08-03：白屏 — build 目录残留 iframe 版入口配置

**现象**：应用中心装完 HermesWebUI 后，点图标白屏（fnOS 桌面窗口 iframe 嵌入，跨域加载失败）。

**根因**：重新打包时只 `scp` 同步了 `cmd/`、`wizard/`、`manifest` 等文件，**漏了 `app/ui/config`**。build 目录里的 `app/ui/config` 还是旧的 `"type": "iframe"` 版本，被打包进 fpk。fnOS 桌面窗口（5666）iframe 嵌入 WebUI（8787）→ 跨域 → 白屏。

**修复**：把 `app/ui/config` 同步为 `"type": "url"`，重新打包。

**教训**：
1. **改入口配置时务必确认 build 目录同步了 `app/ui/config`**（`scp` 清单不能漏）
2. build 前检查 build 目录的 `app/ui/config` 的 `type` 是 `url` 还是 `iframe`
3. 打包后用 `tar xzf HermesWebUI.fpk` + `tar xzf app.tgz` 验证入口类型

**入口配置对照**：
- `type: "url"` — 新标签页打开（推荐，无 iframe 跨域问题）
- `type: "iframe"` — fnOS 桌面窗口内嵌（有跨域问题，WebUI 不适用）

---

## 阶段性总结（2026-07-30 ~ 07-31）

### 从零到可用的完整路径

**Day 1（7/30）：环境搭建**
- 飞牛上安装 Hermes Agent（pip + venv）
- 配置 Gateway API server（.env + config.yaml）
- 启动 Dashboard（:8787）和 Gateway（:18642）
- 遇到：API server 绑定 127.0.0.1 导致局域网不可达
- 遇到：Gateway 进程树保护阻止重启
- 清理旧 fnOS 应用残留
- 创建独立仓库 hermes-webui-fnos（非 fork）

**Day 2（7/31）：fnOS 打包**
- 理解 fnpack 打包流程：manifest + app/ + cmd/ + config/
- 发现关键坑：9个生命周期脚本必须全部存在
- 发现关键坑：install_dep_apps 字段导致验证失败
- 发现关键坑：config/privilege JSON 格式必须匹配模板
- 发现关键坑：config/resource shares 不能为空
- 从 npm install 方案改为打包源码方案（更稳定）
- 修正 HERMES_API_URL 指向 Gateway API 而非 Dashboard
- 配置 systemd user service 实现开机自启
- iframe 版本因 CORS 问题放弃，只保留新标签页版

### 关键决策

| 决策 | 原因 |
|------|------|
| 独立仓库非 Fork | fnOS 包只需打包文件，源码打包在 app/ 里 |
| 打包源码非 npm install | install_init 阶段 TRIM_PKGVAR 不存在，npm 失败 |
| 去掉 install_dep_apps | fnOS 1.1.31xx+ 验证器不接受此字段 |
| 去掉 wizard/ | 可能导致验证问题，用 config_callback 替代 |
| 新标签页非 iframe | fnOS 桌面窗口与 WebUI API 存在 CORS 冲突 |
| HERMES_API_URL 指向 Gateway | Dashboard 未运行时健康检查失败导致聊天报错 |

### 最终架构

```
飞牛 fnOS
├── HermesWebUI fnOS App (:8787)  ← 新标签页打开
│   └── server.py (hermes-webui)
│       └── HERMES_WEBUI_CHAT_BACKEND=gateway
│           └── 远程 Gateway API (:8642)
│
Arch VM (192.168.31.31)
├── Hermes Gateway (:18642)  ← API server
│   └── Xiaomi mimo-v2.5
└── Hermes Dashboard (:8787)  ← 停用
```

### 已验证可用

- ✅ 安装 fpk → 应用中心手动安装
- ✅ 启动服务 → `bash cmd/main start`
- ✅ 聊天功能 → 连接远程 Gateway
- ✅ 应用设置 → 保存 Gateway 配置
- ✅ systemd 自启 → 重启飞牛后自动拉起
- ✅ 卸载清理 → uninstall_init + uninstall_callback

---

## 2026-07-30

### Dashboard "Chat unavailable: 1"

**现象**：飞牛上访问 Dashboard (:8787) 能打开界面，但聊天报 "Chat unavailable: 1"

**根因**：API server 绑定在 `127.0.0.1:18642`，浏览器从局域网访问不到

**修复**：修改 `config.yaml` 中 `api_server.host` 为 `0.0.0.0`，然后重启 gateway

**陷阱**：gateway 配置修改后必须重启才生效，但 gateway 进程树保护会阻止从内部重启。必须从**另一台机器** SSH 执行 `hermes gateway restart`。

---

### Gateway 进程树保护阻止重启

**现象**：任何从 gateway 进程树内执行的 `systemctl --user restart`、`kill`、`pkill` 都被拦截

**根因**：Hermes Gateway 拦截 SIGTERM 信号传播，防止自身被意外重启

**解决方案**（按优先级）：
1. 从**另一台 LAN 机器** SSH 执行重启命令
2. 在飞牛桌面终端手动执行
3. 重启 VM

**确认**：`delegate_task` 和 `cronjob` 也无法绕过此限制 (#30719)

---

### 原生 Dashboard 占用端口导致 WebUI 无法启动

**现象**：WebUI app 安装后显示 "Chat unavailable: 1"，实际打开的是原生 Dashboard 而非 WebUI

**根因**：历史 Hermes 实例的 `hermes-dashboard.service` 已占用 :8787 端口。WebUI app 安装后因端口冲突无法启动，用户访问 :8787 看到的是原生 Dashboard 界面。

**修复**：停止并禁用原生 Dashboard service：
```bash
systemctl --user stop hermes-dashboard.service
systemctl --user disable hermes-dashboard.service
```

**说明**：v0.19.0 的 `hermes dashboard` 是内置管理界面，功能完整。如果只需要基本功能，直接用内置 dashboard 即可，不需要 hermes-webui-fnos 包。但如果需要自定义 UI 或远程 Gateway 模式，WebUI 包更合适。

---

### 旧 fnOS 应用残留清理

**现象**：卸载旧应用后，数据目录、配置目录、日志仍有残留

**清理位置**：
```
/vol4/@appdata/    — HermesAgentCN, HermesWebUI, HermesWebUICN
/vol4/@appconf/    — HermesAgentCN, HermesStudio, HermesWebUI, HermesWebUICN, trim.hermes
/var/log/apps/     — 各应用 .log 文件（需要 sudo）
/tmp/              — hermes-pty-active-*.json, hermes-webui-fnos
```

**注意**：`/var/log/apps/` 下的文件需要 sudo 删除

---

### 新建独立仓库（非 Fork）

**决策**：hermes-webui-fnos 从 nesquena/hermes-webui 的 fork 改为独立仓库

**原因**：
- Fork 会混入上游提交，维护成本高
- fnOS 包只需要打包文件（manifest、cmd/、config/、wizard/）
- 源码通过 npm install 或打包在 app/ 目录获取
- 独立仓库更清晰，易维护

---

### appcenter-cli install-fpk 已移除

**现象**：fnOS 1.1.31xx+ 不再支持 `appcenter-cli install-fpk` 命令

**替代方案**：使用 Web UI 手动安装（应用中心 → 手动安装）

---

## 2026-07-31

### 安装失败："应用包不符合系统版本要求"

**现象**：fnOS 应用中心安装 fpk 时报错"应用包不符合系统版本要求"

**排查过程**：
1. 对比 `fnpack create` 模板和工作版本 v1.3.0 的 fpk 结构
2. 发现缺少生命周期脚本是根本原因

**根因**：fnOS 验证器要求**完整的 9 个生命周期脚本**，缺任何一个都会拒绝安装。

**必需脚本清单**：
```
cmd/main              # start/stop/status
cmd/install_init      # 安装前（源码已打包则为 no-op）
cmd/install_callback  # 安装后（venv 创建等）
cmd/config_init       # 配置修改前（no-op）
cmd/config_callback   # 配置修改后（保存 gateway.env）
cmd/upgrade_init      # 升级前（no-op）
cmd/upgrade_callback  # 升级后（no-op）
cmd/uninstall_init    # 卸载前（停止进程、清理）
cmd/uninstall_callback # 卸载后（清理目录）
```

**修复**：补齐所有缺失脚本，不需要的功能用 `#!/bin/bash\nexit 0` 占位。

---

### 安装失败："执行脚本出错且原因未知"

**现象**：fpk 能通过验证，但安装过程中报错

**排查**：
```bash
cat /var/log/apps/HermesWebUI.log
# 输出: /var/apps/HermesWebUI/cmd/main: line 25: /vol4/@appdata/HermesWebUI/webui.log: Permission denied
```

**根因**：`install_init` 试图执行 `npm install`，但：
1. 源码已打包在 `app/` 目录，不需要 npm install
2. `TRIM_PKGVAR` 目录在 install_init 阶段还不存在

**修复**：`install_init` 改为 no-op（`exit 0`），源码打包时已包含所有文件。

---

### 聊天报错："Error: Internal server error"

**现象**：WebUI 能打开，但发消息返回 Internal server error

**排查**：
```bash
curl -sf http://127.0.0.1:8787/api/health/agent
# 输出: "alive": false, "reason": "remote_gateway_unreachable", "endpoint": "http://192.168.31.31:9119"
```

**根因**：`HERMES_API_URL` 指向 Dashboard (:9119)，但 Dashboard 没运行。WebUI 健康检查失败后拒绝处理聊天请求，即使 `HERMES_WEBUI_GATEWAY_BASE_URL` 指向正确的 Gateway API (:8642)。

**修复**：将 `HERMES_API_URL` 也指向 Gateway API URL，统一为一个端点。

```bash
# cmd/main 中
export HERMES_API_URL="${REMOTE_GATEWAY}"   # 而不是 REMOTE_DASHBOARD
```

**教训**：Dashboard (:9119) 和 Gateway API (:8642) 是两个独立服务。WebUI 只需要 Gateway API，不需要 Dashboard。

---

### 端口冲突：原生 Dashboard 占用 :8787

**现象**：WebUI app 安装后无法启动，端口被占

**排查**：
```bash
ss -tlnp | grep 8787
# 输出: hermes dashboard --port 8787
```

**根因**：之前配置的原生 Hermes Dashboard (systemd user service) 占着 :8787

**修复**：
```bash
systemctl --user stop hermes-dashboard.service
systemctl --user disable hermes-dashboard.service
```

**教训**：安装 WebUI 前确保端口未被占用。

---

### config/privilege JSON 格式问题

**现象**：fpk 被拒绝

**排查**：对比 fnpack 模板和自定义的 privilege 文件

**根因**：fnOS 验证器要求 JSON 使用 **4 空格缩进**，压缩格式 `{"defaults": {"run-as": "package"}}` 不通过

**正确格式**：
```json
{
    "defaults":
    {
        "run-as": "package"
    }
}
```

---

### config/resource shares 为空

**现象**：fpk 被拒绝

**根因**：`{"data-share": {"shares": []}}` 空数组不通过

**修复**：至少需要 2 个 share 条目：
```json
{
    "data-share": {
        "shares": [
            {"name": "HermesWebUI", "permission": {"rw": ["HermesWebUI"]}},
            {"name": "HermesWebUI/data", "permission": {"rw": ["HermesWebUI"]}}
        ]
    }
}
```

---

### install_dep_apps 导致拒绝

**现象**：manifest 中 `install_dep_apps = nodejs_v24` 导致验证失败

**根因**：fnOS 1.1.31xx+ 的验证器不接受此字段

**修复**：从 manifest 中移除，在 `cmd/install_init` 或 `cmd/main` 中处理依赖。

---

### fnpack build 失败："bin: no such file or directory"

**现象**：`fnpack build` 报错

**根因**：直接复制 `app.tgz` 文件到构建目录，fnpack 期望 `app/` 目录

**修复**：
```bash
# 错误
cp app.tgz app_backup.tgz

# 正确
mkdir app
tar xzf app_backup.tgz -C app
fnpack build
```

---

### iframe 嵌入 CORS 跨域错误

**现象**：使用 `type: "iframe"` 打开 WebUI 时，第一次能用，后续发消息报错：
```
Error: Cross-origin mismatch - check reverse proxy headers
```

**根因**：fnOS 桌面窗口（端口 5666）通过 iframe 嵌入 WebUI（端口 8787），浏览器检测到 origin 不同，拦截跨域请求。

**与 Gateway 位置无关**：无论是 Bundled Agent（本机 :8642）还是 Remote Gateway（远程 :8642），iframe CORS 问题都存在。问题根源是 fnOS iframe 嵌入方式（5666 vs 8787），不是 Gateway 在哪里。

| 模式 | Gateway 位置 | iframe CORS 问题 |
|---|---|---|
| Bundled Agent | 本机 :8642 | ✅ 有（5666 vs 8787） |
| Remote Gateway | 远程 :8642 | ✅ 有（5666 vs 8787） |

**解决方案**：
1. **`type: "url"` 新标签页**（推荐）— 完整浏览器环境，无 iframe 限制
2. **fnOS 统一网关** — 通过 fnOS 域名访问 WebUI，origin 相同，无跨域（需 fnOS ≥1.2.0401）
3. **上游修复** — 改 server.py 添加 CORS 头（需上游 [nesquena/hermes-webui](https://github.com/nesquena/hermes-webui) 接受 PR）

---

### 重装后进程未重启

**现象**：重装 fpk 后，旧 server.py 进程仍在运行（用老配置），或进程已死但新进程未启动

**根因**：fnOS 重装不会自动杀掉旧进程。旧进程可能：
1. 还在运行但用老环境变量（HERMES_API_URL 指向 :9119）
2. 已被杀掉但新进程未启动

**修复**：手动重启
```bash
kill -9 $(pgrep -f 'server.py')
cd /var/apps/HermesWebUI && bash cmd/main start
```

---

### 图标不更新

**现象**：重装后桌面图标仍是旧的紫色纯色图标

**根因**：fnOS 缓存了旧图标数据，简单重装不会刷新

**修复**：
1. 完全卸载应用
2. 清除图标缓存（如有）
3. 重新安装

---

### app.tgz 内容不完整

**现象**：安装成功但 server.py 不存在，启动失败

**根因**：打包时 `app/server/` 目录为空（git clone 失败或被中断），fnpack 仍然能打包空目录

**修复**：重新打包前验证 `app/server/` 有完整文件
```bash
ls app/server/server.py  # 必须存在
du -sh app/server/        # 应该 > 10MB
```

---

## 通用排查流程

1. **检查端口**：`ss -tlnp | grep <port>`
2. **检查进程**：`ps aux | grep <app>`
3. **检查日志**：`cat /var/log/apps/<AppName>.log`
4. **检查应用日志**：`cat /vol4/@appdata/<AppName>/webui.log`
5. **检查健康状态**：`curl -sf http://127.0.0.1:<port>/api/health/agent`
6. **检查环境变量**：`cat /proc/<pid>/environ | tr '\0' '\n' | grep HERMES`
7. **对比工作版本**：解压旧 fpk 对比 manifest、config、cmd/ 文件

---

## fnOS 应用目录结构

```
/var/apps/HermesWebUI/           # TRIM_APPDEST
├── target -> /vol4/@appcenter/  # 实际文件（symlink）
├── var -> /vol4/@appdata/       # 运行时数据
├── etc -> /vol4/@appconf/       # 配置
├── shares/                      # 数据共享目录
├── cmd/                         # 生命周期脚本
├── config/                      # privilege/resource
├── wizard/                      # 安装/设置向导
├── ICON.PNG
└── manifest
```

**注意**：`target/` 是 symlink，源码在 `${TRIM_APPDEST}/target/server/`。
