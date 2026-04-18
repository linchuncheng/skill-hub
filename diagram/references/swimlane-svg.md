# 泳道图规范

> **公共规范**（配色、动画、SVG技术）详见：[svg-common.md](svg-common.md)  
> **连线规范**详见：[line_standard.md](line_standard.md)

## 图表结构

**结构**：泳道（角色/系统）→ 流程步骤 → 跨泳道交互

| 类型 | 说明 | 图形 |
|------|------|------|
| 泳道 | 角色/系统分区 | 水平或垂直分隔区域 |
| 流程步骤 | 操作节点 | 矩形 |
| 判断 | 条件分支 | 菱形 |
| 连线 | 流程走向 | 箭头线 |

## 布局原则

- 泳道**水平排列**（角色在左）或**垂直排列**（角色在上）
- 流程步骤在泳道内对齐
- 跨泳道交互清晰可见

## 泳道设计

- 每个泳道代表一个角色/系统
- 泳道宽度根据内容调整
- 使用不同背景色区分

## 水平 vs 垂直泳道

| 类型 | 适用场景 | 布局方向 |
|------|----------|----------|
| 水平泳道 | 角色较少、流程较长 | 从左到右 |
| 垂直泳道 | 角色较多、流程较短 | 从上到下 |

## SVG模板

```xml
<g>
  <rect x="x" y="y" width="W" height="H" fill="#e3f2fd" stroke="#1976d2"/>
  <text>角色A</text>
  <rect x="x" y="y+H" width="W" height="H" fill="#fff9c4" stroke="#f9a825"/>
  <text>角色B</text>
  <rect x="x" y="y+2H" width="W" height="H" fill="#f1f8e9" stroke="#689f38"/>
  <text>角色C</text>
  <rect x="x" y="y" width="w" height="h" rx="4" fill="#fff" stroke="#333"/>
  <text>步骤</text>
  <line x1="x1" y1="y1" x2="x2" y2="y2" stroke="#333" marker-end="url(#arrow)"/>
</g>
```
