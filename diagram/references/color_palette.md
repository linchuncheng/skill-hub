# 配色方案参考

## 预设配色表

| 类名 | 用途 | 填充色 | 边框色 | 文字色 |
|------|------|--------|--------|--------|
| c-gray | 用户层/通用 | #F1EFE8 | #5F5E5A | #444441 |
| c-blue | 前端/入口 | #E6F1FB | #185FA5 | #0C447C |
| c-teal | 业务服务 | #E1F5EE | #0F6E56 | #085041 |
| c-purple | 公共服务 | #EEEDFE | #534AB7 | #3C3489 |
| c-amber | 网关/代理 | #FAEEDA | #854F0B | #633806 |
| c-coral | 核心/重要 | #FAECE7 | #993C1D | #712B13 |
| c-red | 基础设施 | #FCEBEB | #A32D2D | #791F1F |

## 连接线颜色

| 用途 | 颜色值 | 透明度 |
|------|--------|--------|
| 普通连线 | #888780 | 1.0 |
| 虚线标注 | #888780 | 0.35 |
| 分割线 | #888780 | 0.3 |

## CSS 类定义

```css
/* 基础样式 */
text { font-family: system-ui, -apple-system, sans-serif; fill: #1a1a1a; }
.th { font-size: 14px; font-weight: 500; }
.ts { font-size: 12px; font-weight: 400; }

/* 配色类 */
.c-gray { fill: #F1EFE8; stroke: #5F5E5A; }
.c-gray text { fill: #444441; }

.c-blue { fill: #E6F1FB; stroke: #185FA5; }
.c-blue text { fill: #0C447C; }

.c-teal { fill: #E1F5EE; stroke: #0F6E56; }
.c-teal text { fill: #085041; }

.c-purple { fill: #EEEDFE; stroke: #534AB7; }
.c-purple text { fill: #3C3489; }

.c-amber { fill: #FAEEDA; stroke: #854F0B; }
.c-amber text { fill: #633806; }

.c-coral { fill: #FAECE7; stroke: #993C1D; }
.c-coral text { fill: #712B13; }

.c-red { fill: #FCEBEB; stroke: #A32D2D; }
.c-red text { fill: #791F1F; }
```

## 配色原则

- 同层同色，区分职责
- 单图不超过 5 种颜色
- 重要组件可用暖色（c-coral/c-red）突出
