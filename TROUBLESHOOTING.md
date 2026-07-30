# HermesWebUI fnOS — 问题排查与修复记录

> 记录开发过程中遇到的问题和解决方案，方便后续迭代参考。

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

**结论**：fnOS 的 iframe 嵌入与 WebUI 的 API 请求存在 CORS 冲突，**无法修复**（需要改上游 server.py 添加 CORS 头）。

**解决方案**：使用 `type: "url"` 在新标签页打开，不存在跨域问题。

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
