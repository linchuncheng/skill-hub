# LLM生成SVG规范

适用于系统架构图、调用链路图、部署架构图、数据流图、时序图、状态图、流程图、泳道图等需要手工绘制的架构图。

## 标准工作流

使用 `todo_write` 工具创建任务清单：

```
需求分析 → 布局规划 → 图形绘制 → 连线标注 → 动画配置 → 输出文件 → 验证文件 → 结果展示
```

| 步骤 | 操作 | 输出 |
|------|------|------|
| 需求分析 | 确定架构图类型、层级数量、组件清单 | 架构草图 |
| 布局规划 | 计算 viewBox、确定每层 Y 坐标 | 布局参数 |
| 图形绘制 | 按层级绘制组件矩形、标签 | SVG 图形组 |
| 连线标注 | 添加连接线、协议标注 | 完整 SVG |
| 动画配置 | 添加 CSS 动画、设置延迟 | 动态 SVG |
| 输出文件 | 保存为 `{名称}.svg` | 文件路径 |
| 验证文件 | 执行 `python3 scripts/llm_svg_validator.py {文件}.svg` | 验证报告 |
| 修复循环 | 验证不通过则修复，最多3次循环 | 通过为止 |
| 结果展示 | 对话返回SVG结果 | 包含SVG图的对话信息 |

## 图表类型规范

### 系统架构图

**结构**：用户层 → 前端应用 → 网关/代理 → 后端服务 → 基础设施

| 层次 | 说明 | 示例组件 |
|------|------|----------|
| 用户层 | 终端用户访问入口 | 浏览器、App、小程序 |
| 前端应用 | 用户界面层 | React/Vue SPA、SSR应用 |
| 网关/代理 | 流量入口、路由分发 | Nginx、API Gateway、Kong |
| 后端服务 | 业务逻辑层 | 微服务、单体应用 |
| 基础设施 | 底层支撑服务 | 数据库、缓存、消息队列 |

**布局原则**
- 采用**自上而下**或**自左向右**的层次布局
- 同层组件水平对齐
- 层与层之间保持统一间距

**SVG模板**

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

### 调用链路图

**结构**：发起方 → 中间层 → 处理方 → 下游依赖

| 类型 | 说明 | 图形 |
|------|------|------|
| 发起方 | 请求的起始点 | 圆角矩形 |
| 中间层 | 转发/处理节点 | 矩形 |
| 处理方 | 核心业务处理 | 矩形 |
| 下游依赖 | 数据库/外部服务 | 圆柱/云形 |

**连线规则**
- 同步调用：实线箭头
- 异步调用：虚线箭头
- 回调：带标签的返回线
- 超时/重试：虚线 + 标注

**SVG模板**

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

### 部署架构图

**结构**：负载均衡 → 应用集群 → 数据存储 → 中间件

| 类型 | 说明 | 图形 |
|------|------|------|
| 负载均衡 | 流量分发 | 菱形/六边形 |
| 应用集群 | 服务实例组 | 矩形组（含多个实例）|
| 数据存储 | 数据库/存储 | 圆柱形 |
| 中间件 | 缓存/消息队列 | 矩形 |

**布局原则**
- 采用**分层布局**：接入层 → 应用层 → 数据层
- 同一集群的实例用虚线框包围
- 跨可用区用不同背景色区分

**SVG模板**

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

### 数据流图

**结构**：数据源 → 处理节点 → 存储 → 消费端

| 类型 | 说明 | 图形 |
|------|------|------|
| 数据源 | 数据产生方 | 平行四边形 |
| 处理节点 | 数据转换/计算 | 矩形 |
| 存储 | 数据持久化 | 圆柱形/开口矩形 |
| 消费端 | 数据使用方 | 矩形 |

**绘制要点**
- 采用**从左到右**的水平布局
- 数据流向清晰可见
- 分支和合并使用菱形决策节点

**SVG模板**

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

### 时序图

**结构**：参与者 → 生命线 → 消息交互

| 类型 | 说明 | 图形 |
|------|------|------|
| 参与者 | 交互实体 | 矩形/小人图标 |
| 生命线 | 存活时间 | 垂直虚线 |
| 消息 | 方法调用 | 水平箭头 |
| 激活框 | 执行期间 | 细长矩形 |
| 返回 | 响应数据 | 虚线箭头 |

**连线规则**
- 同步消息：实线箭头
- 异步消息：实线开放箭头
- 返回消息：虚线箭头
- 自调用：箭头指向自身

**SVG模板**

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

### 状态图

**结构**：状态节点 → 转移条件 → 事件触发

| 类型 | 说明 | 图形 |
|------|------|------|
| 初始状态 | 起始点 | 实心圆 |
| 状态 | 系统状态 | 圆角矩形 |
| 转移 | 状态变化 | 箭头线 |
| 终止状态 | 结束点 | 圆环（空心圆+实心圆）|
| 复合状态 | 包含子状态 | 嵌套矩形 |

**布局原则**
- 初始状态在左上或上方
- 终止状态在右下或下方
- 主要状态横向或纵向排列

**标注规范**
- 状态名称
- 转移条件：`事件[条件]/动作`
- 状态内部：`entry/动作 exit/动作`

**SVG模板**

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

### 流程图

**结构**：开始/结束 → 处理节点 → 判断分支

| 类型 | 说明 | 图形 |
|------|------|------|
| 开始/结束 | 流程边界 | 圆角矩形/椭圆 |
| 处理 | 操作步骤 | 矩形 |
| 判断 | 条件分支 | 菱形 |
| 输入/输出 | 数据交互 | 平行四边形 |
| 子流程 | 嵌套流程 | 双边框矩形 |

**布局原则**
- **从上到下**或**从左到右**流向
- 判断节点后分支水平排列
- 同层级节点对齐

**布局策略**

| 场景 | 布局方案 | 说明 |
|------|----------|------|
| 错误分支 | 左右分散布局 | 早期错误放左侧，后续错误放右侧，避免连线交叉 |
| 结束节点 | 统一放最下方 | 所有分支向下汇聚，避免先下后上的折线 |
| 主流程 | 垂直居中 | 保持主流程清晰，分支向两侧展开 |

**SVG模板**

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

### 泳道图

**结构**：泳道（角色/系统）→ 流程步骤 → 跨泳道交互

| 类型 | 说明 | 图形 |
|------|------|------|
| 泳道 | 角色/系统分区 | 水平或垂直分隔区域 |
| 流程步骤 | 操作节点 | 矩形 |
| 判断 | 条件分支 | 菱形 |
| 连线 | 流程走向 | 箭头线 |

**布局原则**
- 泳道**水平排列**（角色在左）或**垂直排列**（角色在上）
- 流程步骤在泳道内对齐
- 跨泳道交互清晰可见

**泳道设计**
- 每个泳道代表一个角色/系统
- 泳道宽度根据内容调整
- 使用不同背景色区分

**水平 vs 垂直泳道**

| 类型 | 适用场景 | 布局方向 |
|------|----------|----------|
| 水平泳道 | 角色较少、流程较长 | 从左到右 |
| 垂直泳道 | 角色较多、流程较短 | 从上到下 |

**SVG模板**

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

## 配色方案

### 预设配色表

| 类名 | 用途 | 填充色 | 边框色 | 文字色 |
|------|------|--------|--------|--------|
| c-gray | 用户层/通用 | #F1EFE8 | #5F5E5A | #444441 |
| c-blue | 前端/入口 | #E6F1FB | #185FA5 | #0C447C |
| c-teal | 业务服务 | #E1F5EE | #0F6E56 | #085041 |
| c-purple | 公共服务 | #EEEDFE | #534AB7 | #3C3489 |
| c-amber | 网关/代理 | #FAEEDA | #854F0B | #633806 |
| c-coral | 核心/重要 | #FAECE7 | #993C1D | #712B13 |
| c-red | 基础设施 | #FCEBEB | #A32D2D | #791F1F |

### 连接线颜色

| 用途 | 颜色值 | 透明度 |
|------|--------|--------|
| 普通连线 | #888780 | 1.0 |
| 虚线标注 | #888780 | 0.35 |
| 分割线 | #888780 | 0.3 |

### CSS类定义

```css
text { font-family: system-ui, -apple-system, sans-serif; fill: #1a1a1a; }
.th { font-size: 14px; font-weight: 500; }
.ts { font-size: 12px; font-weight: 400; }

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

### 配色原则

- **同层同色**：同一层使用相同配色
- **区分职责**：不同职责使用不同配色
- **避免过多**：单图配色不超过 5 种

## SVG技术规范

### viewBox计算

| 类型 | viewBox | 适用场景 |
|------|---------|----------|
| 标准 | `0 0 680 790` | 通用系统架构图 |
| 宽型 | `0 0 960 540` | 调用链路图、泳道图 |
| 高型 | `0 0 680 960` | 多层系统架构、流程图 |
| 方型 | `0 0 800 800` | 状态图、数据流图 |

**自定义计算**

```
宽度 = 边距*2 + (组件宽 + 间距) * 列数 - 间距
高度 = 边距*2 + (层标题高) + (层高 + 层间距) * 层数
```

示例：3层架构，每层4个组件
```
宽度 = 40*2 + (140 + 20) * 4 - 20 = 700
高度 = 40*2 + 30 + (100 + 40) * 3 = 550
viewBox = "0 0 700 550"
```

### SVG头部模板

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 680 790"
     preserveAspectRatio="xMidYMid meet"
     style="width: 100%; height: auto; max-width: 800px; min-width: 320px;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" 
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" 
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
    <style>
      text { font-family: system-ui, -apple-system, sans-serif; fill: #1a1a1a; }
      .th { font-size: 14px; font-weight: 500; }
      .ts { font-size: 12px; font-weight: 400; }
    </style>
  </defs>
</svg>
```

### 坐标定位规则

| 元素 | 坐标原点 | 说明 |
|------|----------|------|
| rect | 左上角 (x, y) | width/height 向右下延伸 |
| text | 基线定位点 | 配合 text-anchor/dominant-baseline |
| line | (x1, y1) 到 (x2, y2) | 起点到终点 |
| circle | 圆心 (cx, cy) | r 为半径 |

### 文字对齐

```xml
<!-- 水平居中 + 垂直居中 -->
<text x="142" y="138" text-anchor="middle" dominant-baseline="central">文本</text>

<!-- 左对齐 + 垂直居中 -->
<text x="60" y="138" text-anchor="start" dominant-baseline="central">文本</text>
```

## 图形元素规范

### 矩形框（组件）

```xml
<g class="c-blue">
  <rect x="52" y="122" width="180" height="46" rx="8" stroke-width="0.5"/>
  <text class="th" x="142" y="138" text-anchor="middle" dominant-baseline="central">标题</text>
  <text class="ts" x="142" y="156" text-anchor="middle" dominant-baseline="central">💻 描述</text>
</g>
```

### 圆角标签

```xml
<g class="c-gray">
  <rect x="85" y="44" width="108" height="34" rx="17" stroke-width="0.5"/>
  <text class="ts" x="139" y="61" text-anchor="middle" dominant-baseline="central">👤 标签</text>
</g>
```

### 连接线

```xml
<!-- 带箭头的线 -->
<line x1="340" y1="78" x2="340" y2="98" 
      stroke="#888780" stroke-width="1.5" marker-end="url(#arrow)"/>

<!-- 虚线标注 -->
<line x1="52" y1="513" x2="628" y2="513" 
      stroke="#888780" stroke-width="0.5" stroke-dasharray="4 3" stroke-opacity="0.35"/>
```

### 分割线

```xml
<line x1="30" y1="110" x2="263" y2="110" 
      stroke="#888780" stroke-width="0.8" stroke-opacity="0.3"/>
<text class="ts" x="340" y="110" text-anchor="middle" dominant-baseline="central" font-weight="500">分层名称</text>
<line x1="417" y1="110" x2="650" y2="110" 
      stroke="#888780" stroke-width="0.8" stroke-opacity="0.3"/>
```

## 动画渲染规范

### 渲染顺序

架构图支持入场动画，按三阶段依次渲染：

| 阶段 | 内容 | 动画效果 | 延迟 |
|------|------|----------|------|
| 框架+说明 | 层标签、分隔线、文字说明 | 淡入 | 0s |
| 组件 | 服务卡片、节点 | 缩放弹出 | +0.2s |
| 连线 | 连接线、箭头、连线说明 | 绘制动画 | +0.2s |

### 实现方式

```xml
<svg>
  <style>
    .layer-frame {
      opacity: 0;
      animation: fadeIn 0.2s ease-out forwards;
    }
    
    .component-card {
      opacity: 0;
      transform-origin: center;
      animation: popIn 0.4s ease-out forwards;
    }
    
    @keyframes popIn {
      0% { opacity: 0; transform: scale(0.8); }
      100% { opacity: 1; transform: scale(1); }
    }
    
    .connector-line {
      opacity: 0;
      animation: fadeIn 0.4s ease-out forwards;
    }
  </style>
  
  <g class="layer-frame" style="animation-delay: 0s">...</g>
  <g class="component-card" style="animation-delay: 0.2s">...</g>
  <line class="connector-line" style="animation-delay: 0.6s"/>
</svg>
```

### 注意事项

- **禁止在带 `transform="translate()"` 的元素上使用 CSS transform 动画**
- 使用绝对坐标定位，而非 `transform="translate()"`
- 每层动画间隔 0.2s，形成依次展示效果

## 验证清单

### 通用验证

| 检查项 | 规范值 | 检查方法 |
|--------|--------|----------|
| viewBox | 有定义 | 搜索 `viewBox=` |
| 箭头标记 | 有 arrow marker | 搜索 `id="arrow"` |
| 动画 | fadeIn | 只使用 `opacity` 变化 |
| 连线 | 水平/垂直 | 检查 `x1=x2` 或 `y1=y2` |

### 架构图验证

| 检查项 | 规范值 | 检查方法 |
|--------|--------|----------|
| 模型宽度 | 150px | 搜索 `width="150"` |
| 水平间距 | 45px | 相邻模型 x 坐标差 = 195px |
| 垂直间距 | 45px | 相邻模型 y 坐标差 = 上一模型高度 + 45px |
| 边距 | 20px | 模型与外框四边距离一致 |
| 配色 | 规范色值 | 填充/边框色匹配配色规范 |

**强制规则**：
- 所有模型宽度统一为 150px
- 连线只能是水平或垂直线，禁止斜线

## 最佳实践

### 布局原则

| 原则 | 说明 |
|------|------|
| 层级清晰 | 从上到下或从左到右分层 |
| 对齐整齐 | 同一层组件水平对齐 |
| 间距一致 | 组件间距保持统一 |
| 留白适当 | 避免过于拥挤 |
| 防重叠 | 同级别组件禁止重叠，间距 ≥ 20px |
| 连线优化 | 尽可能不重叠，优先使用直线 |

### 换行策略

- 每行建议 3-4 个组件
- 使用折线连接跨行组件，保持流程连贯
- 文字标注禁止与组件框重叠

### 减少转折线

| 关系类型 | 对齐方式 | 连线方式 |
|----------|----------|----------|
| 垂直关系 | 上下对齐 | 垂直连线 |
| 水平关系 | 左右对齐 | 水平连线 |

- 避免不必要的转折线
- 转折线只在终点设置一个箭头
- 转折线禁止在转折点出现箭头
- 多条连线交叉时，调整组件位置或使用不同路径

### 连接点规范

组件的连接点**只能使用四边正中点**（上边中点/下边中点/左边中点/右边中点），**禁止连接到角点或边上任意非中点位置**

### 标注规范

- **协议标注**: 连线上标注 HTTP/RPC/MQ 等
- **方向明确**: 使用箭头表示数据流向
- **文字简洁**: 组件描述控制在 10 字以内

#### 箭头修饰语（标签）规则

- **只能在线上**：标签必须落在连接线段中部，不允许压在箭头头部或落入节点框内
- **优先策略**（按顺序执行）：
  1. 优先拉长原有线段（移动节点位置），而非改为绕行大折线
  2. 必要时微调标签位置，不进框/不压箭头
  3. 最后才改走线
- **独立性**：多个箭头/标签不得相互覆盖
- **一致性**：同一张图中，同类标签风格保持一致

# 配色方案参考

## 架构图配色（七色）

| 类名 | 语义 | 填充/边框/文字 |
|------|------|----------------|
| c-gray | 通用/辅助/次要 | #F1EFE8 / #5F5E5A / #444441 |
| c-blue | 起点/输入/外部 | #E6F1FB / #185FA5 / #0C447C |
| c-teal | 主流程/核心处理 | #E1F5EE / #0F6E56 / #085041 |
| c-purple | 支撑/配置/工具 | #EEEDFE / #534AB7 / #3C3489 |
| c-amber | 中间层/转换/协调 | #FAEEDA / #854F0B / #633806 |
| c-coral | 重点/关键/突出 | #FAECE7 / #993C1D / #712B13 |
| c-red | 基础/底层/存储 | #FCEBEB / #A32D2D / #791F1F |

## 领域模型图配色（四色）

| 类型 | 填充色 | 边框色 | 用途 |
|------|--------|--------|------|
| 时标 | #fce4ec | #e91e63 | 事件/记录 |
| 资源 | #f1f8e9 | #689f38 | 实体/物品 |
| 角色 | #fff9c4 | #f9a825 | 参与者 |
| 描述 | #e3f2fd | #1976d2 | 分类/配置 |

## 使用原则

- 同层同色，区分职责
- 单图不超过 5 种颜色
- 重要组件可用暖色突出

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

## 模板参考

模板文件位于 `assets/` 目录：

| 模板 | 文件 | 适用场景 |
|------|------|----------|
| 系统架构图 | `系统架构图.svg` | 微服务整体架构、中台系统 |
| 业务架构图 | `业务架构图.svg` | 电商/直播等业务系统分层 |
| 调用链路图 | `调用链路图.svg` | 业务流程链路、服务调用链 |
| 部署架构图 | `部署架构图.svg` | K8s 部署、云架构拓扑 |
| 数据流图 | `数据流图.svg` | 数据流转、ETL流程 |
| 时序图 | `时序图.svg` | 接口调用顺序、交互流程 |
| 状态图 | `状态图.svg` | 订单状态、审批状态机 |
| 流程图 | `流程图.svg` | 业务流程、算法步骤 |
| 泳道图 | `泳道图.svg` | 跨部门协作、责任分工 |
| 领域模型图 | `领域模型图.svg` | 领域模型、四色建模 |

### 使用方式

```
1. 根据架构图类型选择对应模板
2. 复制模板文件到目标路径
3. 修改标题、组件、连线
4. 调整配色（可选）
```

## 脚本工具

### SVG 验证器

验证LLM生成 是否符合规范：

```bash
python3 scripts/llm_svg_validator.py {文件}.svg
```

## 输出规范

### viewBox 调整原则

| 形态 | 推荐 viewBox | 特征 |
|------|--------------|------|
| 宽型 | `0 0 960 540` | 横向展开、多列并排 |
| 高型 | `0 0 680 960` | 纵向展开、多层堆叠 |
| 方型 | `0 0 800 800` | 中心辐射、网状关系 |
| 自由 | `0 0 W H` | 根据布局动态确定 |

### SVG 基础规范

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 700 800"
     preserveAspectRatio="xMidYMid meet"
     style="width: 100%; height: auto; max-width: 800px; min-width: 320px; background-color: #ffffff;">
  <defs>
    <!-- 箭头标记 -->
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" 
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" 
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
    <!-- 样式定义 -->
    <style>
      text { font-family: system-ui, -apple-system, sans-serif; fill: #1a1a1a; }
      .th { font-size: 14px; font-weight: 500; }
      .ts { font-size: 12px; font-weight: 400; }
    </style>
  </defs>
  <!-- 图形内容 -->
</svg>
```
