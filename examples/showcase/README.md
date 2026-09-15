# pptx-svg showcase — 全特性验收 deck

编译：

```bash
svg-to-pptx examples/showcase -o /tmp/showcase.pptx \
  --quick-generate --native-charts-and-tables
# 开发态等价命令：python3 svg_to_pptx.py examples/showcase ...
```

`--native-charts-and-tables` 决定 P5 的 `pptx:data` 是编译为原生
chart/table graphicFrame，还是回退为 SVG 预览形状。

## 每页检查点

| 页 | 语法 | 应该看到 |
|---|---|---|
| 01-cover | `pptx:transition`(fade) `pptx:notes` `pptx:anim`(entrance_fade / emphasis with) `pptx:effect`(outer-shadow/glow) `pptx:name` `pptx:autofit` | 淡入转场；标题点击淡入且有投影；红圆持续脉动+发光；演示者备注有文字 |
| 02-text | `push` 转场 `pptx:build="paragraph"` `pptx:vert` `pptx:anchor` `pptx:line-height`/`space-before`/`soft-break`/`line-break` | push 转场；bullet 按段落逐条 wipe；左侧竖排文字；第三条内联软换行 |
| 03-effects | 全部六种 `pptx:effect` | 六张卡片：外阴影/内阴影/发光/羽化/倒影/模糊；链式飞入+脉冲 |
| 04-media | `pptx:crop` `on="idref"` 触发器 `path` 自定义路径 `exit` 动画 | 图片只显示中心红块（裁剪工具可见全图）；点击绿按钮黄圆往返移动；点击蓝块淡出 |
| 05-data | `pptx:data`(chart+table) `pptx:formula` | 原生图表/表格可双击编辑；公式是 OMML 可编辑对象 |
| 06-end | `advance="5"` `repeat`/`autorev` `zoom` 转场 | 5 秒自动翻页；红方块点击后来回脉冲三次 |

`deck.xml` 本身也在验收范围内：页面在 `pages/`（非默认 `svg_output/`），
顺序由 manifest 决定；`dc:title`/`dc:language` 应写入 docProps/core.xml。

未覆盖：`pptx:ph` 占位符绑定需要结构化导出（master/layout 声明），
由测试套件覆盖。
