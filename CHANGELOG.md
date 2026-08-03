# CHANGELOG / 更新日志

---

## 0.52.106 (2026-08-03)

### 变更 / Changed
- **版本号同步上游** — 从自定义 0.54.0 改为同步上游 hermes-webui v0.52.106
- **双版本变体** — url 版（新标签页）+ iframe 窗口版（桌面窗口）
- 图标为白色背景 + 黑色 logo（Hermes Agent 设计语言）

### 版本变体
- `HermesWebUI-0.52.106-url.fpk` — 新标签页打开
- `HermesWebUI-0.52.106-iframe.fpk` — 桌面窗口内嵌

---

## 0.54.0 (2026-08-03)

### 变更 / Changed
- **图标改设计语言** — 从蓝色背景改为**白色背景 + 黑色 logo**（对齐 Hermes Agent 官方设计语言），带 fnOS 规范圆角
- **提供双版本变体** — url 版（新标签页）+ iframe 窗口版（桌面窗口），按需选用

### 版本变体
- `HermesWebUI-0.54.0-url.fpk` — 新标签页打开
- `HermesWebUI-0.54.0-iframe.fpk` — 桌面窗口内嵌

---

## 0.53.1 (2026-08-03)

### 修复 / Fixed
- **入口改为 url 新标签页** — v0.53.0 build 时 build 目录残留 iframe 版 `app/ui/config`，导致 fnOS 桌面窗口 iframe 嵌入 WebUI 跨域白屏
- 改用 `type: "url"` 新标签页打开（避免 iframe 跨域问题）

---

## 0.53.0 (2026-08-03)

### 变更 / Changed
- **默认连接本机 Hermes Core 内核** — Gateway 地址默认改为 `http://127.0.0.1:8642`，与 hermes-core-fnos 配套自闭环
- **移除对远程 31.31 的硬编码依赖** — cmd/main、config_callback、wizard 全部指向本机
- README 架构说明更新为"本地自闭环"默认模式

---

## 2026-07-31

### 修复 / Fixed
- **HERMES_API_URL** — 修正为指向 Gateway API (:8642) 而非 Dashboard (:9119)
- **install_init** — 改为 no-op（源码已打包在 app/ 目录）
- **systemd 服务** — 使用 Type=forking + PIDFile 跟踪后台进程
- **9个生命周期脚本** — 补齐所有必需脚本（fnOS 验证器要求）

### 变更 / Changed
- **移除 iframe 版本** — fnOS 桌面窗口与 WebUI API 存在 CORS 冲突
- **移除 wizard/ 目录** — 可能导致验证问题，用 config_callback 替代
- **移除 install_dep_apps** — fnOS 1.1.31xx+ 验证器不接受此字段
- **使用 Hermes 官方 favicon** — 替换占位符图标
- **源码打包方案** — 从 npm install 改为打包 hermes-webui 源码

### 文档 / Docs
- **TROUBLESHOOTING.md** — 新增问题排查与修复记录
- **README** — 更新项目结构、安装说明、系统自启配置
- **阶段性总结** — 记录 7/30-31 从零到可用的完整路径

---

## 2026-07-30

### 新增 / Added
- 初始版本 / Initial release
- manifest, cmd/, config/, wizard/ — fnOS 应用包结构 / fnOS app package structure
- install_init — npm install hermes-web-ui / 自动安装 WebUI
- cmd/main — 启动/停止/状态管理 / Start/stop/status management
- wizard/install + wizard/config — Gateway 连接配置 / Gateway connection config
- **uninstall_init + uninstall_callback** — 卸载清理脚本 / Uninstall cleanup scripts
- **应用设置页面** — 支持通过 fnOS 应用设置修改 Gateway 配置 / App settings page for Gateway config
- README.md — 项目说明 / Project documentation
