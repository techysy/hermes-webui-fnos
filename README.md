# Hermes WebUI fnOS Package

fnOS (飞牛NAS) 应用包，用于安装 Hermes WebUI。

## 功能

- 浏览器访问 Hermes Agent Web 界面
- 支持 Chat、Sessions、Files、Models 等功能
- 通过 Gateway 连接远程 Hermes Agent

## 安装

1. 构建 fpk：`fnpack build`
2. 在 fnOS App Center 手动安装 `hermes-webui.fpk`
3. 安装时配置 Gateway 地址和 API Key

## 配置

安装后可通过 App Center → 应用设置 修改 Gateway 连接参数。

## 架构

```
fnOS App (port 8787) → npm hermes-web-ui → Gateway API (port 8642)
```

## 开发

```bash
fnpack build          # 构建 fpk
```

## License

MIT
