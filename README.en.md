# Hermes WebUI for fnOS

A fnOS package for the Hermes Agent web management interface.

[![Release](https://img.shields.io/github/v/release/techysy/hermes-webui-fnos?label=Release&color=blue)](https://github.com/techysy/hermes-webui-fnos/releases)
[![Downloads](https://img.shields.io/github/downloads/techysy/hermes-webui-fnos/total?label=Downloads&color=green)](https://github.com/techysy/hermes-webui-fnos/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![fnOS](https://img.shields.io/badge/fnOS-1.0+-green.svg)](https://www.fnnas.com)
[![Upstream v0.52.106](https://img.shields.io/badge/Upstream-v0.52.106-purple.svg)](https://github.com/nesquena/hermes-webui)

> One-click deployment of [Hermes WebUI](https://github.com/nesquena/hermes-webui) on fnOS.

- [中文 README](./README.md)

---

## ✨ Features

- 💬 **Chat** — multi-turn conversation + streaming
- 🛠️ **Skills** — built-in and custom skills
- 🧠 **Memory** — view agent long-term memory
- 🔌 **Multi-model** — connect various model providers
- 📱 **Web access** — open in browser, no client install
- ⏰ **Scheduled tasks** — view and manage schedules
- 🎯 **Health monitoring** — Gateway/Runtime status

## ⚠️ Mobile Limit (fnOS iOS App)

**Important**: Full WebUI functionality (sending messages, new sessions) works on **desktop only**. On **mobile (fnOS iOS App WebView) you can only view history**.

| Action | Desktop | Mobile (fnOS iOS WebView) |
|--------|---------|---------------------------|
| View history | ✅ | ✅ |
| Send message | ✅ | ❌ 501 (method corruption) |
| New session | ✅ | ❌ 501 (method corruption) |

> Cause: the mobile WebView mangles POST bodies into the HTTP method field (iOS WebView hard limit). History lives in frontend localStorage, so it works without the backend.

**Suggestion**: chat fully on desktop (fnOS window / browser at `http://<NAS>:8787`); mobile is for viewing history only.

## 🚀 Quick Install

### Choose a version

| Version | Entry | Description |
|---------|-------|-------------|
| `HermesWebUI-1.0.0-url.fpk` | url new tab | opens in browser tab (keeps security headers) |
| `HermesWebUI-1.0.0-iframe.fpk` | iframe window | embedded in fnOS desktop window (patch removes security headers) |

### Install steps

1. Download `HermesWebUI.fpk` from [Releases](https://github.com/techysy/hermes-webui-fnos/releases) (url version recommended)
2. fnOS → **App Center → Manual Install** → select the fpk
3. Configure Agent address and API key in the wizard
4. **Start manually after first install** (fnOS does not auto-start):

```bash
# SSH to fnOS
cd /var/apps/HermesWebUI && bash cmd/main start

# Verify
curl -sf http://127.0.0.1:8787/health
```

> ⚠️ **SSH install removed**: `appcenter-cli install-fpk` was removed in fnOS 1.1.31xx+. Use App Center manual install.

## 📖 Usage

1. Click the "Hermes WebUI" icon on the fnOS desktop
2. The WebUI opens in your browser
3. Chat once the Gateway is configured

## 🏗️ Architecture

### Default: connect to local Hermes Core (self-contained) ✅ verified

WebUI connects to the **local** [Hermes Core](https://github.com/techysy/hermes-core-fnos) kernel (`http://127.0.0.1:8642`). Both kernel and frontend run on the NAS — fully self-contained.

```
fnOS (single-machine self-contained)
┌─────────────────────────────────────────┐
│ Hermes WebUI  :8787   ← frontend        │
│   └─ connects to 127.0.0.1:8642         │
│ Hermes Core   :8642   ← local kernel    │
│   └─ connects to local 9Router / LLM    │
└─────────────────────────────────────────┘
```

### Mode A: Remote Gateway (optional)

No kernel on the NAS; WebUI connects to a remote Gateway (change the address in app settings).

```
fnOS                    remote server
┌──────────────┐       ┌──────────────┐
│ Hermes WebUI │──────▶│ Hermes Agent │
│   :8787      │       │   Gateway    │
└──────────────┘       └──────────────┘
```

## 🐛 Troubleshooting

Install/run/connect issues and historical fixes: see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).

## 🛠️ Build from Source

```bash
# On the fnOS NAS
fnpack build   # produces HermesWebUI.fpk
```

## 📚 Related

| Project | Description |
|---------|-------------|
| [Hermes WebUI](https://github.com/nesquena/hermes-webui) | upstream WebUI |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | official Hermes Agent |
| [Hermes Core](https://github.com/techysy/hermes-core-fnos) | local kernel fnOS app |
| [9Router](https://github.com/techysy/9router-fnos) · [MetaCubeXD](https://github.com/techysy/metacubexd-fnos) · [Strava Panel](https://github.com/techysy/strava-panel-fnos) | more fnOS apps |

## 🔮 Roadmap

Repack when upstream [nesquena/hermes-webui](https://github.com/nesquena/hermes-webui) releases a new version:

- Track upstream updates
- Connection-switching iteration (local/remote Gateway)
- New chat backend adapters

## License

MIT
