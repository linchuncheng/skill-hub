# 状态图规范

> **公共规范**（配色、动画、SVG技术）详见：[svg-common.md](svg-common.md)  
> **连线规范**详见：[line_standard.md](line_standard.md)

## 图表结构

**结构**：状态节点 → 转移条件 → 事件触发

| 类型 | 说明 | 图形 |
|------|------|------|
| 初始状态 | 起始点 | 实心圆 |
| 状态 | 系统状态 | 圆角矩形 |
| 转移 | 状态变化 | 箭头线 |
| 终止状态 | 结束点 | 圆环（空心圆+实心圆）|
| 复合状态 | 包含子状态 | 嵌套矩形 |

## 布局原则

- 初始状态在左上或上方
- 终止状态在右下或下方
- 主要状态横向或纵向排列

## 标注规范

- 状态名称
- 转移条件：`事件[条件]/动作`
- 状态内部：`entry/动作 exit/动作`

## SVG模板

```xml
<g>
  <circle cx="x" cy="y" r="8" fill="#333"/>
  <rect x="x" y="y" width="W" height="H" rx="8" fill="#e3f2fd" stroke="#1976d2"/>
  <text>状态名</text>
  <rect x="x" y="y" width="W" height="H" rx="8" fill="#fff" stroke="#1976d2"/>
  <text>复合状态</text>
  <rect ... fill="#f1f8e9" stroke="#689f38"/>
  <line x1="x1" y1="y1" x2="x2" y2="y2" stroke="#333" marker-end="url(#arrow)"/>
  <text>事件[条件]/动作</text>
  <circle cx="x" cy="y" r="8" fill="#fff" stroke="#333" stroke-width="2"/>
  <circle cx="x" cy="y" r="4" fill="#333"/>
</g>
```
