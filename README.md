# Hermes WebUI for fnOS

Hermes Agent 网页管理界面的飞牛 NAS (fnOS) 应用包。

[![Release](https://img.shields.io/github/v/release/techysy/hermes-webui-fnos?label=Release&color=blue)](https://github.com/techysy/hermes-webui-fnos/releases)
[![Downloads](https://img.shields.io/github/downloads/techysy/hermes-webui-fnos/total?label=Downloads&color=green)](https://github.com/techysy/hermes-webui-fnos/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![fnOS](https://img.shields.io/badge/fnOS-1.0+-green.svg)](https://www.fnnas.com)
[![Hermes WebUI](https://img.shields.io/github/v/release/nesquena/hermes-webui?label=Hermes%20WebUI&color=purple)](https://github.com/nesquena/hermes-webui)

> 基于 [Hermes WebUI](https://github.com/nesquena/hermes-webui) 开源项目，为飞牛 fnOS 提供一键部署方案。

- [English README](./README.en.md)

---

## ✨ 功能亮点

- 💬 **对话系统** — 多轮对话 + 流式输出
- 🛠️ **技能管理** — 内置和自定义技能
- 🧠 **记忆管理** — Agent 长期记忆查看
- 🔌 **多模型支持** — 接入各种模型服务商
- 📱 **Web 访问** — 浏览器直接打开，无需客户端
- ⏰ **定时任务** — 查看和管理调度
- 🎯 **健康监控** — Gateway/Runtime 状态面板

## ⚠️ 移动端限制（fnOS iOS App）

**重要**：WebUI 完整功能（发消息、新建会话）仅在**桌面端**可用。**移动端（fnOS iOS App 的 WebView）只能查看历史会话**。

| 操作 | 桌面端 | 移动端 (fnOS iOS WebView) |
|------|--------|--------------------------|
| 查看历史会话 | ✅ | ✅ |
| 发消息 | ✅ | ❌ 501 (method 污染) |
| 新建会话 | ✅ | ❌ 501 (method 污染) |

> 原因：移动端 WebView 发送 POST 时把请求体拼进 HTTP method 字段（iOS WebView 硬限制）。历史会话存前端 localStorage，不依赖后端。

**建议**：完整对话用桌面端（fnOS 桌面窗口 / 浏览器访问 `http://<NAS>:8787`），移动端仅查看历史。

## 🚀 快速安装

### 选择版本

| 版本 | 入口 | 说明 |
|------|------|------|
| `HermesWebUI-1.0.0-url.fpk` | url 新标签页 | 浏览器新标签页打开（保留安全头）|
| `HermesWebUI-1.0.0-iframe.fpk` | iframe 窗口版 | fnOS 桌面窗口内嵌（打补丁移除安全头）|

### 安装步骤

1. 从 [Releases](https://github.com/techysy/hermes-webui-fnos/releases) 下载 `HermesWebUI.fpk`（推荐 url 版）
2. 飞牛 NAS → **应用中心 → 手动安装** → 选择 fpk
3. 按向导配置 Agent 地址和 API Key
4. **首次安装后手动启动**（fnOS 不会自动启动）：

```bash
# SSH 到飞牛执行
cd /var/apps/HermesWebUI && bash cmd/main start

# 验证
curl -sf http://127.0.0.1:8787/health
```

> ⚠️ **SSH 安装已失效**：`appcenter-cli install-fpk` 在 fnOS 1.1.31xx 后已被官方移除，请用应用中心手动安装。

## 📖 使用说明

1. 飞牛 NAS 桌面点击「Hermes WebUI」图标
2. 浏览器打开 WebUI 界面
3. 配置好 Gateway 后即可对话

## 🏗️ 架构

### 默认模式：连接本机 Hermes Core（自闭环）✅ 已验证

WebUI 默认连接**本机**的 [Hermes Core](https://github.com/techysy/hermes-core-fnos) 内核（`http://127.0.0.1:8642`），飞牛上同时运行内核 + 前端，完全自闭环。

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

飞牛上不装内核，WebUI 连接远程 Gateway（在应用设置页修改地址即可）。

```
fnOS                    远程服务器
┌──────────────┐       ┌──────────────┐
│ Hermes WebUI │──────▶│ Hermes Agent │
│   :8787      │       │   Gateway    │
└──────────────┘       └──────────────┘
```

## 🐛 问题排查

安装/运行/连接的问题与历史修复记录，见 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)。

## 🛠️ 从源码构建

```bash
# 在飞牛上
fnpack build   # 生成 HermesWebUI.fpk
```

## 📚 相关项目

| 项目 | 说明 |
|------|------|
| [Hermes WebUI](https://github.com/nesquena/hermes-webui) | 上游 WebUI 项目 |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | Hermes Agent 官方项目 |
| [Hermes Core](https://github.com/techysy/hermes-core-fnos) | 本地内核 fnOS 应用 |
| [9Router](https://github.com/techysy/9router-fnos) · [MetaCubeXD](https://github.com/techysy/metacubexd-fnos) · [Strava Panel](https://github.com/techysy/strava-panel-fnos) | 更多 fnOS 应用 |

## 🔮 迭代计划

等待上游 [nesquena/hermes-webui](https://github.com/nesquena/hermes-webui) 发布新版本后重新打包：

- 跟进上游版本更新
- WebUI 连接切换功能迭代
- 新增聊天后端适配

## License

MIT
