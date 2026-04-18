# 数据流图规范

> **公共规范**（配色、动画、SVG技术）详见：[svg-common.md](svg-common.md)  
> **连线规范**详见：[line_standard.md](line_standard.md)

## 图表结构

**结构**：数据源 → 处理节点 → 存储 → 消费端

| 类型 | 说明 | 图形 |
|------|------|------|
| 数据源 | 数据产生方 | 平行四边形 |
| 处理节点 | 数据转换/计算 | 矩形 |
| 存储 | 数据持久化 | 圆柱形/开口矩形 |
| 消费端 | 数据使用方 | 矩形 |

## 绘制要点

- 采用**从左到右**的水平布局
- 数据流向清晰可见
- 分支和合并使用菱形决策节点

## SVG模板

```xml
<g>
  <polygon points="..." fill="#fff9c4" stroke="#f9a825"/>
  <text>数据源</text>
  <rect x="x" y="y" width="W" height="H" rx="4" fill="#e3f2fd" stroke="#1976d2"/>
  <text>数据处理</text>
  <path d="..." fill="#f1f8e9" stroke="#689f38"/>
  <text>数据存储</text>
  <rect ... fill="#fce4ec" stroke="#e91e63"/>
  <text>消费端</text>
  <line x1="x1" y1="y1" x2="x2" y2="y2" stroke="#666" marker-end="url(#arrow)"/>
  <text>数据格式</text>
</g>
```
