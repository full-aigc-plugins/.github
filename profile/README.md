<div align="center">

# Full-AIGC-Plugins

</div>


<div align="center">

# 🎨 面向 AI Agent 的多平台 AIGC 内容生成插件生态

[![Repos](https://img.shields.io/badge/Repos-13-blue?style=flat-square)](#)
[![Plugins](https://img.shields.io/badge/Plugins-10-green?style=flat-square)](https://github.com/full-aigc-plugins/full-aigc-plugins)
[![Hosts](https://img.shields.io/badge/Hosts-Codex%20·%20ZCode%20·%20Kimi-blue?style=flat-square)](https://github.com/full-aigc-plugins/full-aigc-plugins)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange?style=flat-square)](LICENSE)

</div>

---

## 🧭 关于本组织

**Full-AIGC-Plugins** 是一个面向 AI Agent 的多平台 AIGC（AI Generated Content）内容生成**插件**生态，涵盖**图像生成、视频创作、音频/音乐、3D 制作、多模态工作流**等 AIGC 核心领域，面向 **Codex、ZCode、Kimi Code** 三个宿主平台。

每个插件以独立仓库交付，内置三平台适配层（`.codex-plugin` / `.zcode-plugin` / `kimi.plugin.json`）与渐进式披露的 Agent Skills，提供从**生成流水线**到**审批门禁**到**结果校验**的可执行能力。

与姊妹组织 [Full-AIGC-Skills](https://github.com/full-aigc-skills) 对位：技能侧沉淀「怎么想」的领域知识，本组织提供「能做到」的插件能力，按同一套领域划分共建同一个生态。

### 核心理念

> **插件标准化封装（三平台 Manifest） · MCP 工具 · 渐进式披露技能**

---

## 📦 插件仓库

| 插件 | 仓库 | 版本 | 说明 |
|------|------|:----:|------|
| 🎬 **Maya 制作** | [maya-design-plugin](https://github.com/full-aigc-plugins/maya-design-plugin) | 0.1.2 | Maya 场景检查与可逆 Playblast，产出经核验的即梦链接 |
| 🧱 **Blender 制作** | [blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) | 0.3.2 | Blender 场景的受控设计、审阅与导出（视觉里程碑 + 恢复检查点） |
| 🎞️ **Comfy 生成** | [comfy-design-plugin](https://github.com/full-aigc-plugins/comfy-design-plugin) | 0.1.1 | Comfy Cloud 生成工作流（图像 / 视频 / 音频 / 3D） |
| 🎨 **即梦画布** | [dreamina-canvas-plugin](https://github.com/full-aigc-plugins/dreamina-canvas-plugin) | 0.1.3 | 结构化 Dreamina 画布与时间线的构建和运行（带审批与恢复） |
| 🖼️ **即梦设计** | [dreamina-design-plugin](https://github.com/full-aigc-plugins/dreamina-design-plugin) | 0.4.1 | 即梦图像与视频创作 |
| 🏭 **图片工厂** | [image-factory-plugin](https://github.com/full-aigc-plugins/image-factory-plugin) | 0.1.3 | 图像的发现、批量生产与评估闭环 |
| ✂️ **剪映剪辑** | [jianying-edit-plugin](https://github.com/full-aigc-plugins/jianying-edit-plugin) | 0.12.0 | pyJianYingDraft 驱动的剪映草稿原生引擎 |
| 🎵 **MiniMax 设计** | [minimax-design-plugin](https://github.com/full-aigc-plugins/minimax-design-plugin) | 0.4.2 | MiniMax H3 视频生成（白模首尾帧锚定） |
| 🎥 **视频工厂** | [video-factory-plugin](https://github.com/full-aigc-plugins/video-factory-plugin) | 0.1.2 | 视频的剪辑、合成、审校与校验 |
| 🌋 **火山引擎设计** | [volcengine-design-plugin](https://github.com/full-aigc-plugins/volcengine-design-plugin) | 0.1.0 | 豆包 ASR/TTS 与图像、视频生成工作流 |
| 📋 **影视制片规划** | [cine-planning](https://github.com/full-aigc-plugins/cine-planning) | 规划 | 故事 → 镜头表 → 分镜（纯规格，未发布） |
| ⚙️ **剪映引擎** | [jianying-cli](https://github.com/full-aigc-plugins/jianying-cli) | 1.2.0 | 全能力 Rust 剪映草稿引擎（jianying-edit 底座） |

---

## 🚀 快速开始

插件市场清单由 [full-aigc-plugins/full-aigc-plugins](https://github.com/full-aigc-plugins/full-aigc-plugins) 统一发布：

```bash
# Codex
codex plugin marketplace add full-aigc-plugins/full-aigc-plugins
codex plugin add blender-design@full-aigc-plugins   # 其余插件同理
```

```text
# Kimi Code CLI
/plugins marketplace https://raw.githubusercontent.com/full-aigc-plugins/full-aigc-plugins/main/kimi-marketplace.json
```

> ZCode：设置 → 插件 → 添加插件市场，输入 `full-aigc-plugins/full-aigc-plugins`。

---

## 📁 插件结构规范

```
<plugin-repo>/
├── .codex-plugin/plugin.json     # Codex 适配
├── .zcode-plugin/plugin.json     # ZCode 适配
├── kimi.plugin.json              # Kimi 适配
├── skills/<skill>/SKILL.md       # 渐进式披露技能
└── assets/                       # Logo 与资源
```

---

## 🤝 贡献指南

1. **Fork** 对应插件仓库
2. 任何代码改动都要 bump + 发版（市场端靠版本号感知更新）
3. 提交 **Pull Request**，由市场仓统一重生成三平台清单

> 新插件提案请在 [Discussions](https://github.com/orgs/full-aigc-plugins/discussions) 中发起。

---

## 📄 许可协议

本组织下所有项目均采用 [Apache 2.0](LICENSE) 开源许可协议。

---

<div align="center">

**Made with ❤️ by PartMe AI Team**

</div>
