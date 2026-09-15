# pptx-compiler

**English** → [README.md](README.md)

一套编译为可编辑 PPTX 的 SVG 超集。

*本项目源自 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)
（MIT）。感谢上游项目，本编译器所依赖的 SVG→DrawingML 核心来自那里。*

## 项目是什么

pptx-compiler 把一个 SVG 页面目录编译为原生 PowerPoint 文稿。每页是
一份独立的合法 SVG 文件。动画、转场、演讲者备注、可编辑图表、表格、
公式等 PowerPoint 语义，通过一个 `pptx:` 命名空间内联声明，编译为
真实的 OOXML 对象。不经过栅格化：在 PowerPoint 里打开的是可编辑的
形状、文本和数据。

语言定义见 [SPEC.md](SPEC.md)，全特性示例见
[examples/showcase](examples/showcase/)。

## 为什么独立出来

ppt-master 是一个完整的 agent skill：在同一套编译核心之外，还包含
prompt 工作流、设计指导、源文档转换、媒体后端和预览界面。需要 agent
从素材自动设计整套演示时，那样的形态是合适的。

pptx-compiler 只保留编译这一步，把 SVG 本身当作编写语言。出发点是：
现在的模型已经能写出合格的 SVG，设计层可以交给模型，不必打包在
工具里。部件更少、安装更小，每个 PowerPoint 语义都内联声明在它
所属的页面上。

| | ppt-master（上游） | pptx-compiler |
|---|---|---|
| 形态 | agent skill + 生成工作流 | 编译器包（`pipx install`） |
| 页面语义 | sidecar 配置 + 设计规范文件 | 每个 SVG 内联 `pptx:` 命名空间 |
| 动画 | `animations.json` sidecar | `<pptx:anim>` 元素 |
| 转场 | 转场配置 | `<pptx:transition>` 元素 |
| 演讲者备注 | 备注 sidecar | `<pptx:notes>` 元素 |
| 图表 / 表格 / 公式 | 结构化 deck 契约 | `pptx:data` / `pptx:formula` 内联 |
| 占位符绑定 | 结构化 deck | `pptx:ph` 内联 |
| 校验 | 导出后报告 | `svg-lint` + 编译期报错（无静默回退） |
| 附带内容 | prompt、风格预设、转换器、图像/TTS、预览 UI | 不附带，如何编写 SVG 由使用方决定 |

如果你的需求是让 agent 决定演示文稿长什么样，用上游。如果你的需求是
把已经写好的 SVG 变成可编辑的 PPTX，要求结果确定、不挑调用方，
本项目只做这一件事。

## 一页长什么样

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:pptx="http://pptx-svg.dev/ns/1"
     viewBox="0 0 1280 720">
  <rect width="1280" height="720" fill="#0d1526"/>
  <text x="80" y="140" font-size="56" fill="#fff"
        pptx:effect="outer-shadow(blur=8,dist=4,color=#00000066)">
    <tspan>Quarterly Review</tspan>
  </text>
  <g id="hero">
    <circle cx="640" cy="400" r="90" fill="#e63946"/>
    <pptx:anim effect="fly" start="click" dur="0.5" dir="up"/>
    <pptx:anim effect="emphasis_grow_shrink" start="after"
               repeat="indefinite" autorev="true"/>
  </g>
  <pptx:transition effect="fade" dur="0.5"/>
  <pptx:notes>开场先讲核心数字。</pptx:notes>
</svg>
```

## 安装

```bash
pipx install pptx-compiler
# 或：pip install pptx-compiler

# 免安装直接运行
uvx --from pptx-compiler svg-to-pptx <project>
```

## 用法

```bash
# 工程目录结构：<project>/svg_output/*.svg（可选 deck.xml）
svg-lint <project> --quick-generate --canonical-authoring --stage final --json
svg-to-pptx <project> --quick-generate -o out.pptx
```

包内提供三个命令：

- `svg-to-pptx`——把 `svg_output/*.svg`（或 `deck.xml` 页面清单）
  编译为原生 PPTX（DrawingML 形状、图表、表格、OMML 公式、转场、
  对象动画、演讲者备注）
- `svg-lint`——语言的检查工具（导出时也会自动运行）
- `pptx-to-svg`——把现有 PPTX 导回 SVG 编写形态，用于往返编辑

源码 checkout 下有三个同名薄封装脚本：`python3 svg_to_pptx.py`、
`python3 svg_lint.py`、`python3 pptx_to_svg.py`。内部工具以模块形式
调用：`python3 -m svg_to_pptx.update_spec`、
`python3 -m svg_to_pptx.register_template` 等。

转场（`-t`）、对象动画（`-a`）、原生图表/表格、往返导入等选项见
`svg-to-pptx --help`。

## 许可

MIT——见 [LICENSE](LICENSE)。原作 © 2025-2026 Hugo He；
pptx-compiler 的改动 © 2026 gaoyu06。
