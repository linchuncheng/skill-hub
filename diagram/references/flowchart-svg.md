# 流程图规范

> **公共规范**（配色、动画、SVG技术）详见：[svg-common.md](svg-common.md)  
> **连线规范**详见：[line_standard.md](line_standard.md)

## 图表结构

**结构**：开始/结束 → 处理节点 → 判断分支

| 类型 | 说明 | 图形 |
|------|------|------|
| 开始/结束 | 流程边界 | 圆角矩形/椭圆 |
| 处理 | 操作步骤 | 矩形 |
| 判断 | 条件分支 | 菱形 |
| 输入/输出 | 数据交互 | 平行四边形 |
| 子流程 | 嵌套流程 | 双边框矩形 |

## 布局原则

- **从上到下**或**从左到右**流向
- 判断节点后分支水平排列
- 同层级节点对齐

## 布局策略

| 场景 | 布局方案 | 说明 |
|------|----------|------|
| 错误分支 | 左右分散布局 | 早期错误放左侧，后续错误放右侧，避免连线交叉 |
| 结束节点 | 统一放最下方 | 所有分支向下汇聚，避免先下后上的折线 |
| 主流程 | 垂直居中 | 保持主流程清晰，分支向两侧展开 |

## SVG模板

```xml
<g>
  <rect x="x" y="y" width="W" height="H" rx="20" fill="#f1f8e9" stroke="#689f38"/>
  <text>开始</text>
  <rect x="x" y="y" width="W" height="H" rx="4" fill="#e3f2fd" stroke="#1976d2"/>
  <text>处理步骤</text>
  <polygon points="x,y x+W/2,y-H/2 x+W,y x+W/2,y+H/2" fill="#fff9c4" stroke="#f9a825"/>
  <text>条件?</text>
  <polygon points="x+10,y x,y+H/2 x+10,y+H x+W-10,y+H x+W,y+H/2 x+W-10,y" fill="#fce4ec" stroke="#e91e63"/>
  <text>输入数据</text>
  <rect x="x" y="y" width="W" height="H" rx="20" fill="#fce4ec" stroke="#e91e63"/>
  <text>结束</text>
  <line x1="x1" y1="y1" x2="x2" y2="y2" stroke="#333" marker-end="url(#arrow)"/>
  <text>Yes/No</text>
</g>
```
