# Hermes WebUI for fnOS

[![Release](https://img.shields.io/github/v/release/techysy/hermes-webui-fnos?label=Release&color=blue)](https://github.com/techysy/hermes-webui-fnos/releases)
[![Downloads](https://img.shields.io/github/downloads/techysy/hermes-webui-fnos/total?label=Downloads&color=green)](https://github.com/techysy/hermes-webui-fnos/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![fnOS](https://img.shields.io/badge/fnOS-1.0+-green.svg)](https://www.fnnas.com)
[![Upstream v0.52.106](https://img.shields.io/badge/Upstream-v0.52.106-purple.svg)](https://github.com/nesquena/hermes-webui)
[![Build](https://img.shields.io/badge/build-fnpack-%23007bff.svg)](https://developer.fnnas.com/docs/cli/fnpack/)

[Hermes WebUI](https://github.com/nesquena/hermes-webui) 的飞牛 NAS（fnOS）应用打包，提供完整的 Hermes Agent 网页管理界面。

> 本项目基于 [Hermes WebUI](https://github.com/nesquena/hermes-webui) 开源项目，为飞牛 fnOS 提供一键部署方案。

## 功能特性

- 💬 **对话系统** - 支持多轮对话和流式输出
- 🛠️ **技能管理** - 内置和自定义技能管理
- 🧠 **记忆管理** - Agent 长期记忆查看和管理
- 🔌 **多模型支持** - 支持接入各种模型服务商
- 📱 **Web 访问** - 浏览器直接打开，无需安装客户端
- ⏰ **定时任务** - 查看和管理定时调度
- 🎯 **健康监控** - Gateway/Runtime 状态面板

## 安装方式

### 版本变体 / Variants

提供两个入口变体，按需选用：

| 变体 | 入口 | 说明 |
|------|------|------|
| `HermesWebUI-0.52.106-url.fpk` | url 新标签页 | 在浏览器新标签页打开 WebUI |
| `HermesWebUI-0.52.106-iframe.fpk` | iframe 窗口版 | 在 fnOS 桌面窗口内嵌打开 |

> 图标已对齐 Hermes Agent 设计语言（白色背景 + 黑色 logo）。若 iframe 窗口版遇到白屏/跨域，改用 url 版。

### 方式一：应用中心安装（推荐）

1. 从 [Releases](https://github.com/techysy/hermes-webui-fnos/releases) 下载 `HermesWebUI.fpk`（选 url 或 iframe 变体）
2. 打开飞牛 NAS → 应用中心 → 手动安装
3. 选择下载的 `HermesWebUI.fpk` 文件
4. 按照向导完成安装（配置 Agent 地址和 API Key）
5. **首次安装后手动启动**（fnOS 不会自动启动）：
```bash
# SSH 到飞牛执行
cd /var/apps/HermesWebUI && bash cmd/main start

# 验证
curl -sf http://127.0.0.1:8787/health
```

### 方式二：~~SSH 安装~~（已失效）

> ⚠️ `appcenter-cli install-fpk` 在 fnOS 1.1.31xx 系列后已被官方移除，不再支持命令行安装 fpk。请使用方式一通过应用中心手动安装。

```bash
# ⚠️ 以下命令已失效（保留仅供参考）
# scp HermesWebUI.fpk yangyu@192.168.31.101:/tmp/
# ssh yangyu@192.168.31.101
# sudo appcenter-cli install-fpk /tmp/HermesWebUI.fpk
```

## 快速开始

1. 在飞牛 NAS 桌面点击「Hermes WebUI」图标
2. 浏览器打开 Hermes WebUI 界面
3. 如果配置了远程 Gateway，可以直接对话

## 打包

```bash
# 在飞牛上
fnpack build
# 生成 HermesWebUI.fpk
```

## 项目结构

```
hermes-webui-fnos/
├── manifest          # 应用元数据
├── app/
│   ├── server/       # hermes-webui 源码（打包时拉取）
│   └── ui/
│       ├── config    # 入口配置（URL 类型，端口 8787）
│       └── images/   # 桌面图标
├── cmd/
│   ├── main          # 启动/停止/状态管理
│   ├── install_init  # no-op（源码已打包）
│   ├── install_callback  # no-op
│   ├── config_init   # no-op
│   ├── config_callback  # 保存 Gateway 配置
│   ├── upgrade_init  # no-op
│   ├── upgrade_callback  # no-op
│   ├── uninstall_init    # 卸载清理
│   └── uninstall_callback # 卸载清理
├── config/
│   ├── privilege     # 应用权限
│   └── resource      # 资源配置
├── ICON.PNG          # 64x64 包图标
└── ICON_256.PNG      # 256x256 包图标
```

## 架构说明

### 默认模式：连接本机 Hermes Core 内核（自闭环）✅ 已验证

WebUI 前端默认连接**本机**的 [Hermes Core](https://github.com/techysy/hermes-core-fnos) 内核（`http://127.0.0.1:8642`），
飞牛上同时运行 Hermes Core（本地内核/Gateway）和 Hermes WebUI（前端界面），完全自闭环，不依赖远程服务器。

```
fnOS (单机自闭环)
┌─────────────────────────────────────────┐
│ Hermes WebUI  :8787   ← 前端界面        │
│   └─ 连 127.0.0.1:8642                  │
│ Hermes Core   :8642   ← 本地内核/Gateway│
│   └─ 连本机 9Router :20128 / LLM        │
└─────────────────────────────────────────┘
```

### 模式 A：Remote Gateway（可选）

飞牛上不装内核，WebUI 前端连接远程 Gateway（在应用设置页修改 Gateway 地址即可）。

```
fnOS                    远程服务器
┌──────────────┐       ┌──────────────┐
│ Hermes WebUI │──────▶│ Hermes Agent │
│   :8787      │       │   Gateway    │
└──────────────┘       └──────────────┘
```

安装时向导可配置 Gateway 地址，默认 `http://127.0.0.1:8642`（本机内核）。

## 开发指南

### 开发流程

```bash
# 1. 基于 fnpack 模版创建
fnpack create HermesWebUI

# 2. 替换关键文件
# - manifest：应用元数据
# - cmd/main：生命周期脚本
# - app/ui/config：入口配置
# - wizard/：安装向导

# 3. 构建
fnpack build
```

## 手动重启

如果 WebUI 无法访问，手动重启：

```bash
# 停止
kill -9 $(pgrep -f 'server.py') 2>/dev/null

# 启动
cd /var/apps/HermesWebUI && bash cmd/main start

# 检查状态
ss -tlnp | grep 8787
curl -sf http://127.0.0.1:8787/health
```

## 系统自启（可选）

WebUI 默认通过 fnOS 应用生命周期管理。如需 systemd 自启：

```bash
# 创建 service 文件
cat > ~/.config/systemd/user/hermes-webui.service << 'EOF'
[Unit]
Description=HermesWebUI App
After=network.target

[Service]
Type=forking
ExecStart=/bin/bash /var/apps/HermesWebUI/cmd/main start
PIDFile=/var/apps/HermesWebUI/var/webui.pid
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

# 启用
systemctl --user daemon-reload
systemctl --user enable hermes-webui.service
systemctl --user start hermes-webui.service

# 检查
systemctl --user status hermes-webui.service
```

## 常见问题

### 无法连接到 Agent

1. 确认 Hermes Agent 实例正在运行
2. 检查 Agent 地址和端口是否正确
3. 如果用远程 Gateway，确认 API Key 配置正确

### 应用拒绝连接

1. 确认 WebUI 服务已启动：`ss -tlnp | grep 8787`
2. 检查启动日志：`cat /vol4/@appdata/HermesWebUI/webui.log`
3. 手动重启：`cd /var/apps/HermesWebUI && bash cmd/main start`

### 安装失败

1. 确认 fnOS 版本满足要求
2. 检查 `/var/log/apps/` 下的应用日志
3. 查看 `appcenter-cli list` 确认应用状态

## 相关项目

| 项目 | 说明 |
|------|------|
| [Hermes WebUI](https://github.com/nesquena/hermes-webui) | 上游 WebUI 项目 |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | Hermes Agent 官方项目 |
| [9Router](https://github.com/techysy/9router-fnos) | Hermes 相关 fnOS 应用 — FREE AI 路由器 / API 代理 |
| [MetaCubeXD](https://github.com/techysy/metacubexd-fnos) | Hermes 相关 fnOS 应用 — Mihomo 网络代理面板 |
| [Strava Panel](https://github.com/techysy/strava-panel-fnos) | Hermes 相关 fnOS 应用 — Strava 骑行数据面板 |
| [fnOS 开发文档](https://developer.fnnas.com) | 飞牛应用开发文档 |

## 🔮 Future / 迭代计划

等待上游 [nesquena/hermes-webui](https://github.com/nesquena/hermes-webui) 发布新版本后重新打包：

- 跟进上游版本更新（新功能、Bug 修复）
- WebUI 连接切换功能迭代（本地/远程 Gateway）
- 新增聊天后端适配

> 📖 上游项目：[nesquena/hermes-webui](https://github.com/nesquena/hermes-webui) · [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)

## License

MIT
