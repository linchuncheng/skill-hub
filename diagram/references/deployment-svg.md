# 部署架构图规范

> **公共规范**（配色、动画、SVG技术）详见：[svg-common.md](svg-common.md)  
> **连线规范**详见：[line_standard.md](line_standard.md)

## 图表结构

**结构**：负载均衡 → 应用集群 → 数据存储 → 中间件

| 类型 | 说明 | 图形 |
|------|------|------|
| 负载均衡 | 流量分发 | 菱形/六边形 |
| 应用集群 | 服务实例组 | 矩形组（含多个实例）|
| 数据存储 | 数据库/存储 | 圆柱形 |
| 中间件 | 缓存/消息队列 | 矩形 |

## 布局原则

- 采用**分层布局**：接入层 → 应用层 → 数据层
- 同一集群的实例用虚线框包围
- 跨可用区用不同背景色区分

## SVG模板

```xml
<g>
  <polygon points="..." fill="#e3f2fd" stroke="#1976d2"/>
  <rect x="x" y="y" width="W" height="H" rx="4" fill="none" stroke="#999" stroke-dasharray="5 3"/>
  <text>应用集群 (N实例)</text>
  <ellipse ... fill="#fce4ec" stroke="#e91e63"/>
  <text>MySQL</text>
  <rect ... fill="#fff3e0" stroke="#ff9800"/>
  <text>Redis</text>
</g>
```
