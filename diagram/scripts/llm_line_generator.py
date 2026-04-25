#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 连线生成器 - 从 JSON 配置生成 SVG 连线图

根据组件的 xywh 坐标和连线列表，自动生成带标签、动画的 SVG 连线图。
支持反向连线自动检测和偏移。

⚠️ JSON 配置中 connections 格式（字符串数组）：
{
  "connections": [
    "组件A->组件B",
    "组件B->组件C"
  ]
}

使用示例：
    python3 llm_line_generator.py config.json output.svg
"""

from typing import Dict, List, Tuple, Any, Optional
import json
import re
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model_line_generator import ComponentLineGenerator


# ==================== 核心函数 ====================

def generate_svg(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据配置生成 SVG
    
    Args:
        config: 配置字典，包含 components 和 connections
    
    Returns:
        包含 svg_content, stats, warnings 的字典
    
    ⚠️ connections 必须使用字符串数组格式：
    ["组件A->组件B", "组件B->组件C"]
    
    与领域模型图 (model_svg_generator.py) 使用相同的 relations 格式，避免混淆。
    脚本内部会将字符串转换为对象格式进行处理。
    """
    # 提取配置
    viewBox = config.get("viewBox", [0, 0, 900, 750])
    title = config.get("title", "")
    subtitle = config.get("subtitle", "")
    style = config.get("style", "rounded")
    components = config.get("components", [])
    connections_raw = config.get("connections", [])
    
    # 转换 connections 格式：["A->B", "B->C"] → [{"source": "A", "target": "B"}, {"source": "B", "target": "C"}]
    connections = []
    for conn in connections_raw:
        if isinstance(conn, str) and '->' in conn:
            # 字符串格式："组件A->组件B"
            parts = conn.split('->')
            connections.append({
                "source": parts[0].strip(),
                "target": parts[1].strip() if len(parts) > 1 else ""
            })
        else:
            raise ValueError(f"无效的连线格式: {conn}。必须使用字符串格式，例如：\"组件A->组件B\"")
    
    # 初始化
    generator = ComponentLineGenerator()
    lines = []
    warnings = []
    successful = 0
    failed = 0
    
    # 转换组件格式（xywh → x1,y1,x2,y2）
    component_map = {}
    models_for_generator = []
    
    for comp in components:
        x, y, w, h = comp["xywh"]
        comp_id = comp["id"]
        label = comp.get("label", "")
        subtitle_text = comp.get("subtitle", "")
        stroke = comp.get("stroke", "#3b82f6")
        
        component_map[comp_id] = {
            "id": comp_id,
            "x1": x,
            "y1": y,
            "x2": x + w,
            "y2": y + h,
            "label": label,
            "subtitle": subtitle_text,
            "stroke": stroke
        }
        
        models_for_generator.append({
            "model_id": comp_id,
            "x1": x,
            "y1": y,
            "x2": x + w,
            "y2": y + h
        })
    
    # 检测反向连线对（用于偏移处理）
    reverse_pairs = {}
    reverse_pair_indices = set()
    
    for idx, conn in enumerate(connections):
        pair_key = (conn["source"], conn["target"])
        reverse_key = (conn["target"], conn["source"])
        
        if reverse_key in reverse_pairs:
            first_idx = reverse_pairs[reverse_key]
            reverse_pair_indices.add(first_idx)
            reverse_pair_indices.add(idx)
        else:
            reverse_pairs[pair_key] = idx
    
    # 检测从同一点出发的多条连线（用于偏移处理）
    same_source_groups = {}  # source_id -> [indices]
    for idx, conn in enumerate(connections):
        from_id = conn["source"]
        if from_id not in same_source_groups:
            same_source_groups[from_id] = []
        same_source_groups[from_id].append(idx)
    
    # 找出有2条以上连线的起点
    same_source_indices = set()
    same_source_offset_map = {}  # index -> offset
    
    for from_id, indices in same_source_groups.items():
        if len(indices) >= 2:
            for i, idx in enumerate(indices):
                same_source_indices.add(idx)
                # 第一条偏移-10，第二条+10，第三条-20，以此类推
                if i % 2 == 0:
                    same_source_offset_map[idx] = -(i // 2 + 1) * 10
                else:
                    same_source_offset_map[idx] = (i // 2 + 1) * 10
    
    # 处理连线
    connection_elements = []
    
    for idx, conn in enumerate(connections):
        from_id = conn["source"]
        to_id = conn["target"]
        
        # 查找组件
        if from_id not in component_map or to_id not in component_map:
            warnings.append(f"连线 {from_id} → {to_id}: 组件不存在")
            failed += 1
            continue
        
        from_comp = component_map[from_id]
        to_comp = component_map[to_id]
        from_model = {"model_id": from_id, "x1": from_comp["x1"], "y1": from_comp["y1"], "x2": from_comp["x2"], "y2": from_comp["y2"]}
        to_model = {"model_id": to_id, "x1": to_comp["x1"], "y1": to_comp["y1"], "x2": to_comp["x2"], "y2": to_comp["y2"]}
        
        try:
            # 临时禁用双向缓存，确保每条线独立计算
            cached = generator._cache.copy()
            generator._cache.clear()
            
            # 计算最优路径
            path = generator.get_best_path(from_model, to_model, models_for_generator)
            
            # 恢复缓存
            generator._cache.update(cached)
            
            # 应用偏移（反向连线 或 同起点多条连线）
            needs_offset = False
            offset = 0
            
            if idx in reverse_pair_indices:
                # 反向连线偏移
                needs_offset = True
                pair_key = (from_id, to_id)
                reverse_key = (to_id, from_id)
                pair_indices = []
                for i, c in enumerate(connections):
                    if (c["from"], c["to"]) == pair_key or (c["from"], c["to"]) == reverse_key:
                        pair_indices.append(i)
                offset = -20 if pair_indices.index(idx) == 0 else 20
            elif idx in same_source_indices:
                # 同起点多条连线偏移
                needs_offset = True
                offset = same_source_offset_map[idx]
            
            if needs_offset:
                # 根据是否有折线采用不同的偏移策略
                if path['turns'] == 0:
                    # 直连线：沿着边框移动起点/终点
                    path = _offset_direct_line(path, offset, from_comp, to_comp, generator)
                else:
                    # 有折线：判断是同起点还是反向连线
                    # 同起点多条连线：只偏移起点附近
                    # 反向连线：偏移所有点
                    is_reverse_pair = idx in reverse_pair_indices
                    path = _offset_turned_line(path, offset, offset_end_point=is_reverse_pair)
            
            # 生成 SVG path
            if style == "rounded":
                path_d = generator.get_rounded_svg_path(path, radius=8)
            else:
                path_d = generator.get_svg_path(path)
            
            # 获取连线属性
            label = conn.get("label", "")
            color = conn.get("color", "#3b82f6")
            line_style = conn.get("style", "solid")
            animated = conn.get("animated", False)
            
            # 生成连线元素
            line_svg = _generate_connection_svg(
                path_d, color, line_style, animated, label, idx
            )
            connection_elements.append(line_svg)
            successful += 1
            
        except Exception as e:
            warnings.append(f"连线 {from_id} → {to_id}: {str(e)}")
            failed += 1
    
    # 生成组件 SVG
    component_elements = []
    for comp in components:
        comp_data = component_map[comp["id"]]
        comp_svg = _generate_component_svg(comp_data, len(components))
        component_elements.append(comp_svg)
    
    # 组装完整 SVG
    svg_content = _assemble_svg(
        viewBox, title, subtitle, connection_elements, component_elements
    )
    
    return {
        "svg_content": svg_content,
        "stats": {
            "total_components": len(components),
            "total_connections": len(connections),
            "successful": successful,
            "failed": failed
        },
        "warnings": warnings
    }


def _offset_direct_line(path: dict, offset: float, from_comp: dict, to_comp: dict, generator) -> dict:
    """
    偏移直连线（turns=0）
    
    策略：沿着组件边框移动起点和终点
    - 对于L/R边出发的线：沿着边框上下移动（调整y）
    - 对于T/B边出发的线：沿着边框左右移动（调整x）
    """
    # 获取所有点
    points = [path['start_point']]
    points.extend(path['inflections'])
    points.append(path['end_point'])
    
    if len(points) != 2:
        return path
    
    start_point = points[0]
    end_point = points[1]
    
    # 判断起点在哪个边
    from_centers = generator.get_side_centers(from_comp)
    to_centers = generator.get_side_centers(to_comp)
    
    # 找到起点所在的边
    start_side = None
    for side, center in from_centers.items():
        if abs(center[0] - start_point[0]) < 1.0 and abs(center[1] - start_point[1]) < 1.0:
            start_side = side
            break
    
    # 找到终点所在的边
    end_side = None
    for side, center in to_centers.items():
        if abs(center[0] - end_point[0]) < 1.0 and abs(center[1] - end_point[1]) < 1.0:
            end_side = side
            break
    
    # 根据边的方向应用偏移
    new_start = list(start_point)
    new_end = list(end_point)
    
    if start_side in ('L', 'R'):
        # 左右边：沿着边框上下移动（调整y）
        new_start[1] += offset
    elif start_side in ('T', 'B'):
        # 上下边：沿着边框左右移动（调整x）
        new_start[0] += offset
    
    if end_side in ('L', 'R'):
        new_end[1] += offset
    elif end_side in ('T', 'B'):
        new_end[0] += offset
    
    new_start = tuple(new_start)
    new_end = tuple(new_end)
    
    # 重新构建路径
    new_segments = [(new_start, new_end)]
    
    return {
        'start_model_id': path['start_model_id'],
        'start_point': new_start,
        'end_model_id': path['end_model_id'],
        'end_point': new_end,
        'turns': 0,
        'total_length': path['total_length'],
        'inflections': [],
        'segments': new_segments
    }


def _offset_turned_line(path: dict, offset: float, offset_end_point: bool = True) -> dict:
    """
    偏移有折线的连线（turns>0）
    
    Args:
        path: 路径字典
        offset: 偏移量
        offset_end_point: 是否偏移终点（反向连线=True，同起点=False）
    
    策略：
    - 反向连线：偏移所有点（包括起点、拐点、终点）
    - 同起点多条连线：偏移起点和第一个拐点，后面的拐点不偏移
    """
    # 获取所有点
    points = [path['start_point']]
    points.extend(path['inflections'])
    points.append(path['end_point'])
    
    if len(points) < 3:
        return path
    
    new_points = []
    
    for i, (x, y) in enumerate(points):
        if i == 0:
            # 起点：总是偏移
            # 根据第一段的方向决定偏移方向
            dx = abs(points[1][0] - x)
            dy = abs(points[1][1] - y)
            
            if dx > dy:
                new_points.append((x, y + offset))
            else:
                new_points.append((x + offset, y))
        elif i == len(points) - 1:
            # 终点：只有反向连线才偏移
            if offset_end_point:
                dx = abs(x - points[-2][0])
                dy = abs(y - points[-2][1])
                
                if dx > dy:
                    new_points.append((x, y + offset))
                else:
                    new_points.append((x + offset, y))
            else:
                # 同起点多条连线，终点不偏移
                new_points.append((x, y))
        else:
            # 拐点：反向连线全部偏移，同起点只偏移第一个拐点
            if offset_end_point:
                # 反向连线：所有拐点同时偏移 x 和 y
                new_points.append((x + offset, y + offset))
            else:
                # 同起点多条连线：只偏移第一个拐点
                if i == 1:
                    # 第一个拐点：同时偏移 x 和 y
                    new_points.append((x + offset, y + offset))
                else:
                    # 后面的拐点：不偏移
                    new_points.append((x, y))
    
    # 重新构建路径字典
    new_inflections = new_points[1:-1]
    new_segments = [(new_points[i], new_points[i+1]) for i in range(len(new_points)-1)]
    
    return {
        'start_model_id': path['start_model_id'],
        'start_point': new_points[0],
        'end_model_id': path['end_model_id'],
        'end_point': new_points[-1],
        'turns': path['turns'],
        'total_length': path['total_length'],
        'inflections': new_inflections,
        'segments': new_segments
    }


def _calculate_label_position(path_d: str) -> Tuple[float, float]:
    """
    计算标签位置（连线中心点，直接覆盖在连线上）
    
    Args:
        path_d: SVG path 字符串
    
    Returns:
        (x, y) 标签中心坐标
    """
    # 解析路径中的所有点
    pattern = r'[ML]\s+([\d.]+)\s+([\d.]+)'
    matches = re.findall(pattern, path_d)
    
    if not matches:
        return (0, 0)
    
    points = [(float(x), float(y)) for x, y in matches]
    
    if len(points) < 2:
        return points[0]
    
    # 计算路径总长度（曼哈顿距离）
    total_length = 0
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        length = abs(x2 - x1) + abs(y2 - y1)
        total_length += length
    
    # 找到中心点位置
    half_length = total_length / 2
    accumulated = 0
    
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        segment_length = abs(x2 - x1) + abs(y2 - y1)
        
        if accumulated + segment_length >= half_length:
            # 中心点在这个线段上
            remaining = half_length - accumulated
            ratio = remaining / segment_length if segment_length > 0 else 0
            
            center_x = x1 + (x2 - x1) * ratio
            center_y = y1 + (y2 - y1) * ratio
            return center_x, center_y
        
        accumulated += segment_length
    
    # 如果没有找到，返回最后一个点
    return points[-1]


def _generate_connection_svg(path_d: str, color: str, style: str, 
                             animated: bool, label: str, index: int) -> str:
    """
    生成单个连线的 SVG 元素
    
    Args:
        path_d: 路径字符串
        color: 连线颜色
        style: 连线样式（solid/dashed/dotted）
        animated: 是否动画
        label: 连线标签
        index: 连线索引（用于动画延迟）
    
    Returns:
        SVG 字符串
    """
    lines = []
    delay = 0.2 + index * 0.05
    
    # 根据样式设置 stroke-dasharray
    dasharray = ""
    if style == "dashed":
        dasharray = ' stroke-dasharray="6 3"'
    elif style == "dotted":
        dasharray = ' stroke-dasharray="4 2 1 2"'
    
    # 连线
    lines.append(f'  <path class="connector-line"')
    lines.append(f'        d="{path_d}"')
    lines.append(f'        stroke="{color}" stroke-width="2" fill="none"{dasharray}')
    lines.append(f'        marker-end="url(#arrow-{color[1:]})"')
    lines.append(f'        style="animation-delay: {delay}s;"/>')
    
    # 动画光点（仅 solid 样式）
    if animated and style == "solid":
        lines.append(f'  <circle class="flow-dot" r="4" fill="url(#glow-dot-{color[1:]})"')
        lines.append(f'          style="offset-path: path(\'{path_d}\'); animation-delay: {delay+0.3}s, {delay+0.3}s;"/>')
    
    # 标签
    if label:
        label_x, label_y = _calculate_label_position(path_d)
        
        # 添加白色背景矩形遮住连线
        text_width = len(label) * 8 + 12
        text_height = 16
        
        lines.append(f'  <rect x="{label_x - text_width/2}" y="{label_y - text_height/2}"')
        lines.append(f'        width="{text_width}" height="{text_height}" fill="#ffffff" rx="3"/>')
        
        # 文字（垂直居中）
        lines.append(f'  <text x="{label_x}" y="{label_y + 4}" text-anchor="middle" font-size="11" fill="#6b7280">{label}</text>')
    
    return "\n".join(lines)


def _generate_component_svg(comp: dict, total: int) -> str:
    """
    生成单个组件的 SVG 元素
    
    Args:
        comp: 组件数据
        total: 组件总数（用于计算动画延迟）
    
    Returns:
        SVG 字符串
    """
    lines = []
    
    x, y = comp["x1"], comp["y1"]
    w = comp["x2"] - comp["x1"]
    h = comp["y2"] - comp["y1"]
    label = comp.get("label", "")
    subtitle = comp.get("subtitle", "")
    stroke = comp.get("stroke", "#3b82f6")
    
    center_x = (comp["x1"] + comp["x2"]) / 2
    center_y = (comp["y1"] + comp["y2"]) / 2
    
    delay = (index % total) / total * 0.1 if 'index' in dir() else 0.1
    
    lines.append(f'  <g class="component-group" style="animation-delay: {delay}s; opacity: 0;">')
    lines.append(f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6"')
    lines.append(f'          fill="#ffffff" stroke="{stroke}" stroke-width="2"/>')
    
    # 计算文本位置
    text_y = center_y - 10 if subtitle else center_y
    
    lines.append(f'    <text x="{center_x}" y="{text_y}" text-anchor="middle" font-size="14" font-weight="bold" fill="#1f2937">{label}</text>')
    
    # 副标题
    if subtitle:
        lines.append(f'    <text x="{center_x}" y="{text_y + 20}" text-anchor="middle" font-size="11" fill="#6b7280">{subtitle}</text>')
    
    lines.append(f'  </g>')
    
    return "\n".join(lines)


def _assemble_svg(viewBox: list, title: str, subtitle: str,
                  connection_elements: list, component_elements: list) -> str:
    """
    组装完整 SVG
    
    Args:
        viewBox: 视图框
        title: 标题
        subtitle: 副标题
        connection_elements: 连线元素列表
        component_elements: 组件元素列表
    
    Returns:
        完整 SVG 字符串
    """
    lines = []
    
    # SVG 头部
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(map(str, viewBox))}" width="{viewBox[2]}" height="{viewBox[3]}">')
    lines.append(f'  <defs>')
    
    # 收集所有使用的颜色
    colors = set()
    for conn_elem in connection_elements:
        import re
        color_matches = re.findall(r'stroke="#([0-9a-fA-F]{6})"', conn_elem)
        colors.update(color_matches)
    
    # 生成箭头标记
    for color in sorted(colors):
        lines.append(f'    <marker id="arrow-{color}" viewBox="0 0 8 8" refX="7.5" refY="4"')
        lines.append(f'            markerWidth="5" markerHeight="5" orient="auto">')
        lines.append(f'      <path d="M 0 0 L 8 4 L 0 8 L 1 4 Z" fill="#{color}"/>')
        lines.append(f'    </marker>')
    
    # 生成光点渐变
    for color in sorted(colors):
        lines.append(f'    <radialGradient id="glow-dot-{color}" cx="50%" cy="50%" r="50%">')
        lines.append(f'      <stop offset="0%" style="stop-color:#{color};stop-opacity:1" />')
        lines.append(f'      <stop offset="100%" style="stop-color:#{color};stop-opacity:0" />')
        lines.append(f'    </radialGradient>')
    
    # CSS 样式
    lines.append(f'    <style>')
    lines.append(f'      @keyframes fadeIn {{')
    lines.append(f'        from {{ opacity: 0; }}')
    lines.append(f'        to {{ opacity: 1; }}')
    lines.append(f'      }}')
    lines.append(f'      @keyframes dotMove {{')
    lines.append(f'        0% {{ offset-distance: 0%; }}')
    lines.append(f'        100% {{ offset-distance: 100%; }}')
    lines.append(f'      }}')
    lines.append(f'      @keyframes dotFadeIn {{')
    lines.append(f'        0% {{ opacity: 0; }}')
    lines.append(f'        100% {{ opacity: 1; }}')
    lines.append(f'      }}')
    lines.append(f'      @keyframes dashMove {{')
    lines.append(f'        to {{ stroke-dashoffset: -9; }}')
    lines.append(f'      }}')
    lines.append(f'      .connector-line {{')
    lines.append(f'        opacity: 0;')
    lines.append(f'        animation: fadeIn 0.4s ease-out forwards;')
    lines.append(f'      }}')
    lines.append(f'      .flow-dot {{')
    lines.append(f'        opacity: 0;')
    lines.append(f'        animation: dotFadeIn 0.3s ease-out forwards, dotMove 2s ease-in-out infinite;')
    lines.append(f'      }}')
    lines.append(f'      .dash-flow {{')
    lines.append(f'        opacity: 0;')
    lines.append(f'        animation: fadeIn 0.4s ease-out forwards, dashMove 2s linear infinite;')
    lines.append(f'      }}')
    lines.append(f'      .component-group {{')
    lines.append(f'        opacity: 0;')
    lines.append(f'        animation: fadeIn 0.4s ease-out forwards;')
    lines.append(f'      }}')
    lines.append(f'    </style>')
    lines.append(f'  </defs>')
    
    # 背景
    lines.append(f'  <rect width="{viewBox[2]}" height="{viewBox[3]}" fill="#fafbfc"/>')
    
    # 标题
    if title:
        lines.append(f'  <text x="{viewBox[2]/2}" y="40" text-anchor="middle" font-size="24" font-weight="bold" fill="#1f2937">{title}</text>')
    if subtitle:
        lines.append(f'  <text x="{viewBox[2]/2}" y="65" text-anchor="middle" font-size="14" fill="#6b7280">{subtitle}</text>')
    
    # 连线和组件
    lines.append(f'  <!-- 连线 -->')
    lines.extend(connection_elements)
    lines.append(f'  <!-- 组件 -->')
    lines.extend(component_elements)
    
    lines.append(f'</svg>')
    
    return "\n".join(lines)


def generate_svg_from_file(json_file: str) -> Dict[str, Any]:
    """从 JSON 文件生成 SVG"""
    with open(json_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return generate_svg(config)


def save_svg(result: Dict[str, Any], output_file: str):
    """保存 SVG 到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result["svg_content"])
    print(f"✅ SVG 已保存到: {output_file}")
    print(f"📊 统计: {result['stats']}")
    if result['warnings']:
        print(f"⚠️  警告: {result['warnings']}")


# ==================== 主函数 ====================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 llm_line_generator.py <json配置文件>")
        print("示例: python3 llm_line_generator.py config.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else json_file.replace('.json', '.svg')
    
    result = generate_svg_from_file(json_file)
    save_svg(result, output_file)
