# 时序图规范

> **公共规范**（配色、动画、SVG技术）详见：[svg-common.md](svg-common.md)  
> **连线规范**详见：[line_standard.md](line_standard.md)

## 图表结构

**结构**：参与者 → 生命线 → 消息交互

| 类型 | 说明 | 图形 |
|------|------|------|
| 参与者 | 交互实体 | 矩形/小人图标 |
| 生命线 | 存活时间 | 垂直虚线 |
| 消息 | 方法调用 | 水平箭头 |
| 激活框 | 执行期间 | 细长矩形 |
| 返回 | 响应数据 | 虚线箭头 |

## 连线规则

- 同步消息：实线箭头
- 异步消息：实线开放箭头
- 返回消息：虚线箭头
- 自调用：箭头指向自身

## SVG模板

```xml
<g>
  <rect x="x" y="y" width="W" height="H" rx="4" fill="#e3f2fd" stroke="#1976d2"/>
  <text>服务A</text>
  <line x1="x" y1="y1" x2="x" y2="y2" stroke="#999" stroke-dasharray="5 3"/>
  <rect x="x" y="y" width="10" height="H" fill="#fff" stroke="#1976d2"/>
  <line x1="x1" y1="y" x2="x2" y2="y" stroke="#333" marker-end="url(#arrow)"/>
  <text>methodName()</text>
  <line x1="x1" y1="y" x2="x2" y2="y" stroke="#999" stroke-dasharray="4 2" marker-end="url(#arrow)"/>
  <text>return data</text>
</g>
```
