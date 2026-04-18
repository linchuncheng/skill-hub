# 系统架构图规范

> **公共规范**（配色、动画、SVG技术）详见：[svg-common.md](svg-common.md)  
> **连线规范**详见：[line_standard.md](line_standard.md)

## 图表结构

**结构**：用户层 → 前端应用 → 网关/代理 → 后端服务 → 基础设施

| 层次 | 说明 | 示例组件 |
|------|------|----------|
| 用户层 | 终端用户访问入口 | 浏览器、App、小程序 |
| 前端应用 | 用户界面层 | React/Vue SPA、SSR应用 |
| 网关/代理 | 流量入口、路由分发 | Nginx、API Gateway、Kong |
| 后端服务 | 业务逻辑层 | 微服务、单体应用 |
| 基础设施 | 底层支撑服务 | 数据库、缓存、消息队列 |

## 布局原则

- 采用**自上而下**或**自左向右**的层次布局
- 同层组件水平对齐
- 层与层之间保持统一间距

## SVG模板

```xml
<g transform="translate(0, 0)">
  <rect x="x" y="y" width="W" height="H" rx="4" fill="#e3f2fd" stroke="#1976d2"/>
  <text>用户层</text>
  <rect ... fill="#fff3e0" stroke="#ff9800"/>
  <rect ... fill="#f3e5f5" stroke="#9c27b0"/>
  <rect ... fill="#e8f5e9" stroke="#4caf50"/>
  <rect ... fill="#fce4ec" stroke="#e91e63"/>
</g>
```
