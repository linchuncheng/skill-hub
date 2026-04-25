# SVG 公共规范

适用于所有类型的 SVG 架构图，包含配色方案、动画规范、SVG 技术规范等公共内容。

> 📋 **工作流规范**：所有图类型的工作流定义统一在 [SKILL.md](../SKILL.md) 中，执行前请先阅读。
>
> - **标准工作流**（适用于除领域模型图外的所有图）：需求分析 → ASCII布局规划 → SVG布局规划 → 图形绘制 → 连线标注 → 动画配置 → 输出文件 → 验证文件 → 修复循环 → 结果展示
> - **领域模型图专属工作流**：分析SQL → 领域划分设计 → 确定四色类型 → 表格化布局 → 生成JSON配置 → 执行脚本生成SVG → 预览

## 连线规范

**连线规范详见**：[line_standard.md](line_standard.md)

> **注意**：line_standard.md 是连线规范的唯一权威来源，包含完整的连接点系统、方向约束、路径生成、避让规则等详细规范。

**核心要点速览**：
- ✅ 所有连线必须连接到组件四边中点（L/R/T/B）
- ✅ 禁止悬空连线（不得连接到空白区域）
- ✅ 出发/进入方向必须垂直于边框
- ✅ 只能水平或垂直90°折线
- ✅ 每段线段 ≥ 20px 才能转折
- ✅ 路径不能穿过任何组件
- ✅ 使用 `<path>` 而非 `<line>`

## 配色方案

### 💡 配色策略

**核心原则**：配色规范通过 LLM 提示词引导，代码不做硬性校验（除四色图外），保留创作自由度。

- ✅ **语义化优先** - 用颜色区分模块/阶段/层级，而非盲目遵循预设
- ✅ **一致性** - 同类组件使用相同色系
- ✅ **对比度** - 确保文字在背景色上清晰可读（WCAG AA 标准）
- ✅ **适度** - 单图建议不超过 6 种主色
- ⚠️ **四色图例外** - 领域模型图必须严格遵循四色规范（见 [model-svg.md](model-svg.md)）

### 推荐配色表（仅供参考，非强制）

> 以下是经典配色方案，可根据实际需求自由调整或使用现代色系（如 Tailwind CSS）。

| 类名 | 用途 | 填充色 | 边框色 | 文字色 |
|------|------|--------|--------|--------|
| c-gray | 用户层/通用 | #F1EFE8 | #5F5E5A | #444441 |
| c-blue | 前端/入口 | #E6F1FB | #185FA5 | #0C447C |
| c-teal | 业务服务 | #E1F5EE | #0F6E56 | #085041 |
| c-purple | 公共服务 | #EEEDFE | #534AB7 | #3C3489 |
| c-amber | 网关/代理 | #FAEEDA | #854F0B | #633806 |
| c-coral | 核心/重要 | #FAECE7 | #993C1D | #712B13 |
| c-red | 基础设施 | #FCEBEB | #A32D2D | #791F1F |

### 现代色系示例（Tailwind CSS）

| 场景 | 推荐色系 | 示例 |
|------|---------|------|
| 主流程 | 蓝色系 | #3b82f6, #6366f1, #8b5cf6 |
| 成功/正常 | 绿色系 | #10b981, #059669 |
| 警告/异步 | 黄色系 | #f59e0b, #d97706 |
| 错误/异常 | 红色系 | #ef4444, #dc2626 |
| 中性/辅助 | 灰色系 | #6b7280, #9ca3af |

### 连接线颜色

| 用途 | 颜色值 | 透明度 |
|------|--------|--------|
| 普通连线 | #888780 | 1.0 |
| 虚线标注 | #888780 | 0.35 |
| 分割线 | #888780 | 0.3 |

> 💡 连线颜色可根据语义调整（如蓝色=主流程、绿色=成功路径、红色=异常路径）

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

- **语义化配色** - 颜色应传达组件的语义（如网关用黄色、核心用红色）
- **一致性** - 同类组件使用相同色系
- **对比度** - 确保文字清晰可读（推荐对比度 ≥ 4.5:1）
- **适度** - 单图建议 4-6 种主色，避免颜色过多造成混乱
- **自由度** - 不强制使用预设配色，可根据主题灵活选择

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

> **连线规范必须参考**: [line_standard.md](line_standard.md)
>
> 核心要求（必须遵守）：
> - 连接点只能用四边中点（L/R/T/B）
> - **连线风格必须统一**：同一张图中，所有连线要么全用直角（L 命令），要么全用圆角（Q 命令），严禁混用
> - 使用 `<path>` 元素 + `fill="none"` + `marker-end`
> - 线段长度 ≥ 20px 才能转折
> - 路径不能穿过任何组件
>
> **连线风格选择**：
> - 架构图/流程图 → 推荐直角风格（L 命令）
> - 原理图/概念图/模型图 → 推荐圆角风格（Q 命令，控制点偏移 10px）

```xml
<!-- 带箭头的线（使用 path） -->
<path d="M 340 78 L 340 98" 
      stroke="#888780" stroke-width="1.5" fill="none"
      marker-end="url(#arrow)"/>

<!-- 虚线标注 -->
<path d="M 52 513 L 628 513" 
      stroke="#888780" stroke-width="0.5" fill="none"
      stroke-dasharray="4 3" stroke-opacity="0.35"/>
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

架构图支持入场动画,按三阶段依次渲染:

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

### 连线动画类型

> **完整动画规范必须参考**: [line_standard.md](line_standard.md) 第 14 章

#### 类型一:光点移动动画（推荐用于数据流/调用链）

在连线上添加一个移动的光点,强调数据流向。

**核心要求**：
- 必须使用 `<path>` 而非 `<line>`
- 必须添加 `fill="none"`
- `offset-path` 必须与 path 的 `d` 属性完全一致

```xml
<svg>
  <defs>
    <!-- 光点渐变 -->
    <radialGradient id="glow-dot" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:0" />
    </radialGradient>
    
    <style>
      /* 光点动画 */
      .flow-dot {
        opacity: 0;
        animation: dotFadeIn 0.3s ease-out forwards, dotMove 2s ease-in-out infinite;
      }
      
      @keyframes dotMove {
        0% { offset-distance: 0%; }
        100% { offset-distance: 100%; }
      }
    </style>
  </defs>
  
  <!-- 连线 -->
  <path class="connector-line" 
        d="M 130 95 L 180 95" 
        stroke="#185FA5" stroke-width="1.5" fill="none"
        marker-end="url(#arrow)"
        style="animation-delay: 0.5s"/>
  
  <!-- 移动光点 -->
  <circle class="flow-dot" r="4" fill="url(#glow-dot)"
          style="offset-path: path('M 130 95 L 180 95'); animation-delay: 0.8s, 0.8s;">
  </circle>
</svg>
```

**不同场景配色**：

| 连线类型 | 光点颜色 | 循环周期 |
|----------|----------|----------|
| 主流程(实线) | #3b82f6 (蓝) | 2s |
| 成功路径(绿线) | #10b981 (绿) | 2s |
| 异步调用(虚线) | #9ca3af (灰) | 3s |
| 失败路径(红线) | #ef4444 (红) | 1.5s |

#### 类型二:描边动画(连线绘制效果)

连线从起点到终点逐步"画"出来:

```xml
<style>
  .draw-line {
    stroke-dasharray: 200;
    stroke-dashoffset: 200;
    animation: drawStroke 1s ease-out forwards;
  }
  
  @keyframes drawStroke {
    to { stroke-dashoffset: 0; }
  }
</style>

<path class="draw-line" 
      d="M 130 95 L 180 95" 
      stroke="#185FA5" stroke-width="1.5" fill="none"
      marker-end="url(#arrow)"
      style="animation-delay: 0.5s"/>
```

#### 类型三:虚线流动动画

虚线持续沿路径方向流动,适合异步/消息场景。

**核心规则**（必须遵守）：
- `stroke-dashoffset` 必须是周期的**整数倍**
- 周期 = 实线长度 + 空白长度
- 推荐配置：`stroke-dasharray="6 3"` + `stroke-dashoffset: -9`

```xml
<style>
  .dash-flow {
    opacity: 0;
    animation: fadeIn 0.4s ease-out forwards, dashMove 2s linear infinite;
  }
  
  @keyframes dashMove {
    to { stroke-dashoffset: -9; } /* 必须是虚线周期的整数倍 */
  }
</style>

<path class="dash-flow" 
      d="M 130 95 L 180 95" 
      stroke="#9ca3af" stroke-width="1.5" fill="none"
      stroke-dasharray="6 3"
      marker-end="url(#arrow)"
      style="animation-delay: 0.6s, 0.6s"/>
```

### 注意事项

- **禁止在带 `transform="translate()"` 的元素上使用 CSS transform 动画**
- 使用绝对坐标定位,而非 `transform="translate()"`
- 每层动画间隔 0.2s,形成依次展示效果
- **光点动画**必须使用 `<path>` 元素,`<line>` 不支持 offset-path
- 光点动画在部分旧版浏览器可能不兼容,建议保留基础连线作为降级方案

## 标注规范

- **协议标注**: 连线上标注 HTTP/RPC/MQ 等
- **方向明确**: 使用箭头表示数据流向
- **文字简洁**: 组件描述控制在 10 字以内

#### 箭头修饰语（标签）规则

> **详细规范必须参考**: [line_standard.md](line_standard.md) 第 13 章

- **只能在线上**：标签必须落在连接线段中部，不允许压在箭头头部或落入节点框内
- **优先策略**（按顺序执行）：
  1. 优先拉长原有线段（移动节点位置），而非改为绕行大折线
  2. 必要时微调标签位置，不进框/不压箭头
  3. 最后才改走线
- **独立性**：多个箭头/标签不得相互覆盖
- **一致性**：同一张图中，同类标签风格保持一致
- **文字简洁**：标签 ≤ 10 字

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

## 脚本工具

### SVG 验证器

验证LLM生成 是否符合规范：

```bash
python3 scripts/llm_svg_validator.py {文件}.svg
```

## 布局原则

**适用范围**：系统架构图、调用链路图、部署架构图、数据流图、时序图、状态图、流程图、泳道图、领域模型图

**排除**：核心原理图（追求自由、有机的布局，详见 [principle-svg.md](principle-svg.md)）

| 原则 | 说明 |
|------|------|
| 层级清晰 | 从上到下或从左到右分层/流向 |
| 对齐整齐 | 同层组件水平对齐或垂直对齐 |
| 间距一致 | 组件间距保持统一 |
| 留白适当 | 避免过于拥挤，给眼睛留停顿空间 |
| 防重叠 | 同级别组件禁止重叠，间距 ≥ 20px |
| 连线优化 | 尽可能不重叠，优先使用直线 |
| **减少转折** | 垂直关系用垂直连线，水平关系用水平连线 |
| **箭头唯一** | 转折线只在终点设置一个箭头，禁止在转折点出现箭头 |
| **避让组件** | 连线路径禁止穿过任何组件 |

## 关键约束与反模式

**适用范围：所有图表类型**（系统架构图、调用链路图、部署架构图、数据流图、时序图、状态图、流程图、泳道图、核心原理图、领域模型图等）

### 外框包裹

| 约束 | 说明 | 反模式 | 正确做法 |
|------|------|--------|----------|
| **外框完全包裹** | 所有外框必须完全包裹内部所有元素(含文字、图标、子组件) | ❌ 外框未包裹内部元素 | 计算 max(Y+height)+padding(16-24px) |
| **外框高度计算** | height = max(内部元素Y + 元素height) + 底部padding(16-24px) | ❌ 文字贴近边框 | 底部至少甼16px padding |
| **外框宽度计算** | width = max(内部元素X + 元素width) + 右侧padding(16-24px) | ❌ 文字溢出右侧 | 右侧至少甼16px padding |
| **多行文字预留** | 每行20px行高,至少甼16px上下padding | ❌ 多行文字溢出 | 行数×20px行高 + 上下各16px padding |

### 文字规范

| 约束 | 说明 | 反模式 | 正确做法 |
|------|------|--------|----------|
| **文字精简** | 节点标题 ≤ 10字,标签 ≤ 10字 | ❌ 文字过长/溢出 | 精简文字,用副标题或浮动标签补充 |
| **禁止文字溢出** | 文字绝不允许超出组件边界 | ❌ 文字撑破组件 | 拆分到副标题、提取为浮动标签、移到 Footer |

### 连线规范

| 约束 | 说明 | 反模式 | 正确做法 |
|------|------|--------|----------|
| **连线规范** | 详见 line_standard.md,禁止悬空连线,必须连接组件四边中点 | ❌ 悬空连线 | 连接到组件四边中点（L/R/T/B） |
| **连线优化** | 尽可能不重叠，优先使用直线 | ❌ 连线交叉混乱 | 调整节点位置,优化路径 |
| **减少转折** | 垂直关系用垂直连线，水平关系用水平连线 | ❌ 频繁转折 | 优先直连，减少拐点 |
| **箭头唯一** | 转折线只在终点设置一个箭头 | ❌ 转折点出现箭头 | 只在路径末尾加 marker-end |
| **避让组件** | 连线路径禁止穿过任何组件 | ❌ 连线穿过组件 | 绕行组件上方/下方/侧方 |

### 视觉规范

| 约束 | 说明 | 反模式 | 正确做法 |
|------|------|--------|----------|
| **尺寸梯度** | 按重要度/复杂度设置尺寸 | ❌ 所有节点统一尺寸 | 英雄组件大，简单组件小 |
| **布局展开** | 分层/分支展开，避免单列 | ❌ 所有节点排成一列 | 横向/纵向分层排列 |
| **配色适度** | 按语义归类,避免颜色过多 | ❌ 颜色过多(>8种) | 建议 4-6 种主色，同类组件同色 |
| **风格一致** | 同类元素形状/颜色/字体一致 | ❌ 风格混乱 | 统一使用预设配色和图形 |