# SVG 规范参考

## viewBox 计算指南

### 标准尺寸

| 类型 | viewBox | 适用场景 |
|------|---------|----------|
| 标准 | `0 0 680 790` | 通用系统架构图 |
| 宽型 | `0 0 960 540` | 调用链路图、泳道图 |
| 高型 | `0 0 680 960` | 多层系统架构、流程图 |
| 方型 | `0 0 800 800` | 状态图、数据流图 |

### 自定义计算

根据组件数量计算 viewBox：

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

## SVG 头部模板

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 680 790"
     preserveAspectRatio="xMidYMid meet"
     style="width: 100%; height: auto; max-width: 800px; min-width: 320px;">
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
</svg>
```

## 坐标定位规则

| 元素 | 坐标原点 | 说明 |
|------|----------|------|
| rect | 左上角 (x, y) | width/height 向右下延伸 |
| text | 基线定位点 | 配合 text-anchor/dominant-baseline |
| line | (x1, y1) 到 (x2, y2) | 起点到终点 |
| circle | 圆心 (cx, cy) | r 为半径 |

## 文字对齐

```xml
<!-- 水平居中 + 垂直居中 -->
<text x="142" y="138" text-anchor="middle" dominant-baseline="central">文本</text>

<!-- 左对齐 + 垂直居中 -->
<text x="60" y="138" text-anchor="start" dominant-baseline="central">文本</text>
```
