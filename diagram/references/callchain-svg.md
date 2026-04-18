# 调用链路图规范

> **公共规范**（配色、动画、SVG技术）详见：[svg-common.md](svg-common.md)  
> **连线规范**详见：[line_standard.md](line_standard.md)

## 图表结构

**结构**：发起方 → 中间层 → 处理方 → 下游依赖

| 类型 | 说明 | 图形 |
|------|------|------|
| 发起方 | 请求的起始点 | 圆角矩形 |
| 中间层 | 转发/处理节点 | 矩形 |
| 处理方 | 核心业务处理 | 矩形 |
| 下游依赖 | 数据库/外部服务 | 圆柱/云形 |

## 连线规则

- 同步调用：实线箭头
- 异步调用：虚线箭头
- 回调：带标签的返回线
- 超时/重试：虚线 + 标注

## SVG模板

```xml
<g>
  <rect x="x" y="y" width="W" height="H" rx="8" fill="#fff9c4" stroke="#f9a825"/>
  <rect ... fill="#e3f2fd" stroke="#1976d2"/>
  <rect ... fill="#f1f8e9" stroke="#689f38"/>
  <ellipse ... fill="#fce4ec" stroke="#e91e63"/>
  <line x1="x1" y1="y1" x2="x2" y2="y2" stroke="#666" marker-end="url(#arrow)"/>
  <text>接口名</text>
</g>
```
