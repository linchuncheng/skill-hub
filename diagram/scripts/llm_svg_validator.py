#!/usr/bin/env python3
"""
SVG 架构图验证脚本
支持 8 种图类型的专项验证，每种图类型有独立的严格规则

用法:
    python3 llm_svg_validator.py <svg文件路径> [--type <图类型>]

图类型（--type 参数）:
    system       系统架构图
    deployment   部署架构图
    call-flow    调用链路图
    data-flow    数据流图
    sequence     时序图
    state        状态图
    flowchart    流程图
    swimlane     泳道图

若不传 --type，则自动从文件名推断，推断失败时运行通用验证。
"""

import sys
import re
import argparse
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Optional

SVG_NS = 'http://www.w3.org/2000/svg'

# ============================================================
# 预设配色（架构图使用的 c-* 色系）
# ============================================================
ARCH_COLORS = {
    '#F1EFE8', '#5F5E5A', '#444441',  # c-gray
    '#E6F1FB', '#185FA5', '#0C447C',  # c-blue
    '#E1F5EE', '#0F6E56', '#085041',  # c-teal
    '#EEEDFE', '#534AB7', '#3C3489',  # c-purple
    '#FAEEDA', '#854F0B', '#633806',  # c-amber
    '#FAECE7', '#993C1D', '#712B13',  # c-coral
    '#FCEBEB', '#A32D2D', '#791F1F',  # c-red
    '#888780',                         # 连接线
    '#333333', '#333', '#666', '#999', '#fff', '#ffffff',
    '#f8f8f8', '#f5f5f5', '#eeeeee',
}

# 领域模型图配色（四色建模法）
DOMAIN_COLORS = {
    '#fce4ec', '#e91e63',  # 时标
    '#f1f8e9', '#689f38',  # 资源
    '#fff9c4', '#f9a825',  # 角色
    '#e3f2fd', '#1976d2',  # 描述
    '#999', '#555', '#666', '#333', '#fff', '#ffffff', '#f8f9fa',
}

# 文件名 → 图类型映射
FILENAME_TYPE_MAP = {
    '系统架构图': 'system',
    '部署架构图': 'deployment',
    '调用链路图': 'call-flow',
    '数据流图':   'data-flow',
    '时序图':     'sequence',
    '状态图':     'state',
    '流程图':     'flowchart',
    '泳道图':     'swimlane',
    '业务架构图': 'system',
    '领域模型图': 'script-svg',
}


def strip_ns(tag: str) -> str:
    return tag.split('}')[-1] if '}' in tag else tag


def iter_tag(root, tagname: str):
    """遍历所有指定 tag 的元素（忽略命名空间）"""
    for elem in root.iter():
        if strip_ns(elem.tag) == tagname:
            yield elem


# ============================================================
# 通用验证基类
# ============================================================
class BaseValidator:
    def __init__(self, svg_path: str):
        self.svg_path = Path(svg_path)
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []
        self.content = ''
        self.root = None

    def load(self) -> bool:
        if not self.svg_path.exists():
            self.errors.append(f"文件不存在: {self.svg_path}")
            return False
        try:
            self.content = self.svg_path.read_text(encoding='utf-8')
            self.root = ET.fromstring(self.content)
            # 构建元素到父级的映射(用于获取 transform 偏移)
            self.parent_map = {c: p for p in self.root.iter() for c in p}
            return True
        except ET.ParseError as e:
            self.errors.append(f"XML 解析错误: {e}")
            return False
        except Exception as e:
            self.errors.append(f"读取文件错误: {e}")
            return False

    # ---------- 通用规则（所有图类型共享）----------

    def check_svg_root(self):
        """根元素必须是 <svg>"""
        if self.root is None:
            return
        if 'svg' not in self.root.tag:
            self.errors.append("[结构] 根元素必须是 <svg>")

    def check_viewbox(self):
        """必须有 viewBox"""
        vb = self.root.get('viewBox', '')
        if not vb:
            self.errors.append("[结构] 缺少 viewBox 属性")

    def check_defs(self):
        """必须有 <defs> 且包含 arrow marker"""
        defs = None
        for elem in self.root:
            if strip_ns(elem.tag) == 'defs':
                defs = elem
                break
        if defs is None:
            self.warnings.append("[结构] 缺少 <defs>（建议包含 arrow marker 和 CSS style）")
            return
        defs_str = ET.tostring(defs, encoding='unicode')
        # 检查是否有 arrow marker（支持 id="arrow" 或 id="arrow-*"）
        has_arrow = 'id="arrow"' in defs_str or "id='arrow'" in defs_str
        has_arrow_prefix = 'id="arrow-' in defs_str or "id='arrow-" in defs_str
        if not has_arrow and not has_arrow_prefix:
            self.warnings.append("[结构] <defs> 中缺少 arrow marker（id='arrow' 或 id='arrow-*'）")

    def check_animation(self):
        """有动画；检测 SVG transform 与 CSS 动画冲突"""
        if 'animation' not in self.content and '@keyframes' not in self.content:
            self.warnings.append("[动画] 未检测到动画效果（建议添加入场动画）")
            return
        # 检测 translateY / scale 动画（transform 类动画）
        bad_kf = re.findall(
            r'@keyframes\s+(\w+)\s*\{[^}]*transform\s*:', self.content
        )
        for kf in bad_kf:
            self.warnings.append(
                f"[动画] @keyframes {kf} 含有 transform 属性，"
                "若作用于有 SVG transform='translate()' 的 <g> 元素会导致位置错乱，"
                "应改为只变化 opacity（fadeIn）"
            )

    def check_title(self):
        """SVG 应有标题文本"""
        titles = list(iter_tag(self.root, 'title'))
        # 也可以是第一个 <text> 大字
        if not titles:
            first_texts = list(iter_tag(self.root, 'text'))
            large_font = [
                t for t in first_texts
                if float(re.sub(r'[^0-9.]', '', t.get('font-size', '0') or '0') or '0') >= 14
            ]
            if not large_font:
                self.warnings.append("[内容] 未检测到图表标题（建议添加大字号标题文本）")

    def check_has_connectors(self):
        """必须有连线（line 或 polyline 或 path）"""
        lines = list(iter_tag(self.root, 'line'))
        polylines = list(iter_tag(self.root, 'polyline'))
        # 检测有 stroke 属性的 path（连线）
        # 包括内联 stroke 属性和通过 CSS class 设置的 stroke
        paths_as_lines = []
        for p in iter_tag(self.root, 'path'):
            # 检查内联 stroke 属性
            if p.get('stroke'):
                paths_as_lines.append(p)
            # 检查 CSS class（如果 class 包含 line/connector/flow 等关键词）
            elif p.get('class'):
                css_class = p.get('class', '')
                if any(keyword in css_class for keyword in ['line', 'connector', 'flow', 'arrow', 'edge']):
                    paths_as_lines.append(p)
        
        if not lines and not polylines and not paths_as_lines:
            self.warnings.append("[连线] 未检测到任何连线（line/polyline/path），图表应有连接关系")

    def check_connectors_quality(self):
        """连线质量检测：不穿过组件、四边中点、线段长度、90°折线"""
        # 收集所有组件（rect）
        components = []
        for rect in iter_tag(self.root, 'rect'):
            x = float(rect.get('x', 0))
            y = float(rect.get('y', 0))
            w = float(rect.get('width', 0))
            h = float(rect.get('height', 0))
            # 过滤条件：
            # 1. 宽度 > 50 且高度 > 30（排除背景和大容器）
            # 2. 不是整个 SVG 尺寸（排除背景）
            vb = self.root.get('viewBox', '0 0 1000 1000').split()
            vb_w = float(vb[2]) if len(vb) >= 4 else 1000
            vb_h = float(vb[3]) if len(vb) >= 4 else 1000
            if w > 50 and h > 30 and w < vb_w * 0.95 and h < vb_h * 0.95:
                components.append({
                    'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h,
                    'text': self._get_rect_text(rect)
                })
        
        if not components:
            return
        
        # 收集所有连线路径
        paths = []
        for path in iter_tag(self.root, 'path'):
            if path.get('stroke'):
                d = path.get('d', '')
                if d.startswith('M'):
                    paths.append({
                        'd': d,
                        'element': path
                    })
        
        if not paths:
            return
        
        # 检测每条连线
        errors_count = 0
        for path_info in paths:
            path_errors = self._validate_path(path_info['d'], path_info['element'], components)
            errors_count += len(path_errors)
            self.errors.extend(path_errors)
        
        if errors_count > 0:
            self.infos.append(f"[连线质量] 检测到 {errors_count} 个连线问题")
        else:
            self.infos.append(f"[连线质量] 所有连线符合规范")
    
    def check_arrows(self):
        """箭头标记规范检查（line_standard.md 第12节）"""
        # 1. 检查 <defs> 中的 marker 定义
        defs = None
        for elem in self.root:
            if strip_ns(elem.tag) == 'defs':
                defs = elem
                break
        
        if defs is None:
            self.warnings.append("[箭头] 缺少 <defs>，无法定义 arrow marker")
            return
        
        # 检查所有 marker
        markers = list(iter_tag(defs, 'marker'))
        if not markers:
            self.warnings.append("[箭头] <defs> 中未定义任何 marker")
            return
        
        for marker in markers:
            marker_id = marker.get('id', '')
            if not marker_id.startswith('arrow'):
                continue
            
            # 检查 viewBox
            viewBox = marker.get('viewBox')
            if not viewBox or viewBox != '0 0 8 8':
                self.errors.append(
                    f"[箭头] marker#{marker_id} 的 viewBox 应为 '0 0 8 8'，"
                    f"当前为 '{viewBox}'"
                )
            
            # 检查 markerWidth/Height
            mw = marker.get('markerWidth')
            mh = marker.get('markerHeight')
            if mw != '5' or mh != '5':
                self.errors.append(
                    f"[箭头] marker#{marker_id} 的尺寸应为 markerWidth='5' markerHeight='5'，"
                    f"当前为 {mw}x{mh}"
                )
            
            # 检查 refX/refY
            refX = marker.get('refX')
            refY = marker.get('refY')
            if refX != '7.5' or refY != '4':
                self.warnings.append(
                    f"[箭头] marker#{marker_id} 的参考点建议为 refX='7.5' refY='4'，"
                    f"当前为 refX='{refX}' refY='{refY}'"
                )
            
            # 检查箭头路径
            arrow_paths = list(iter_tag(marker, 'path'))
            if not arrow_paths:
                self.errors.append(f"[箭头] marker#{marker_id} 缺少 <path> 定义")
                continue
            
            for arrow_path in arrow_paths:
                d = arrow_path.get('d', '')
                fill = arrow_path.get('fill')
                
                # 检查是否为标准带凹口V形箭头
                is_notched_v = 'M 0 0 L 8 4 L 0 8 L 1 4 Z' in d or 'M0 0L8 4L0 8L1 4Z' in d
                
                if not is_notched_v:
                    self.errors.append(
                        f"[箭头] marker#{marker_id} 的箭头路径不标准，"
                        f"应为 'M 0 0 L 8 4 L 0 8 L 1 4 Z'（带凹口V形）"
                    )
                
                # 检查必须是实心填充
                if not fill or fill == 'none':
                    self.errors.append(
                        f"[箭头] marker#{marker_id} 必须实心填充（fill='连线颜色'），"
                        f"当前为 fill='{fill}'"
                    )
    
    def _get_transform_offset(self, element):
        """获取元素及其所有父级 <g> 的 transform 偏移量"""
        total_x = 0.0
        total_y = 0.0
        
        current = element
        while current is not None:
            # 检查当前元素是否有 transform 属性
            transform = current.get('transform', '')
            if transform:
                # 解析 translate(x, y)
                match = re.search(r'translate\(([\d.]+),\s*([\d.]+)\)', transform)
                if match:
                    total_x += float(match.group(1))
                    total_y += float(match.group(2))
            
            # 移动到父元素
            current = self.parent_map.get(current)
        
        return total_x, total_y
        
    def _get_rect_text(self, rect):
        """获取矩形关联的文本(用于错误提示)"""
        # 获取矩形的绝对坐标(考虑父级 transform)
        offset_x, offset_y = self._get_transform_offset(rect)
        x = float(rect.get('x', 0)) + offset_x
        y = float(rect.get('y', 0)) + offset_y
        w = float(rect.get('width', 0))
        h = float(rect.get('height', 0))
        center_x = x + w / 2
        center_y = y + h / 2
            
        # 查找中心点附近的文本(考虑文本也可能在 transform 的 <g> 内)
        for text in iter_tag(self.root, 'text'):
            text_offset_x, text_offset_y = self._get_transform_offset(text)
            tx = float(text.get('x', 0)) + text_offset_x
            ty = float(text.get('y', 0)) + text_offset_y
            if abs(tx - center_x) < w / 2 and abs(ty - center_y) < h / 2:
                return text.text or ''
        return '未命名组件'
    
    def _parse_path_points(self, d):
        """解析 path 的 d 属性，提取所有坐标点和命令类型"""
        points = []
        commands = []
        
        # 匹配 M、L、Q 命令
        m_pattern = r'M\s+([\d.]+)\s+([\d.]+)'
        l_pattern = r'L\s+([\d.]+)\s+([\d.]+)'
        q_pattern = r'Q\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)'
        
        # 提取 M 命令（起点）
        for match in re.finditer(m_pattern, d):
            points.append((float(match.group(1)), float(match.group(2))))
            commands.append('M')
        
        # 提取 L 命令（直线）
        for match in re.finditer(l_pattern, d):
            points.append((float(match.group(1)), float(match.group(2))))
            commands.append('L')
        
        # 提取 Q 命令（二次贝塞尔曲线，圆角）
        # Q 命令格式：Q cx cy x y（控制点 + 终点）
        # 我们只关心终点，控制点用于后续验证
        for match in re.finditer(q_pattern, d):
            cx, cy = float(match.group(1)), float(match.group(2))
            ex, ey = float(match.group(3)), float(match.group(4))
            points.append((ex, ey))
            commands.append(('Q', cx, cy))  # 保存控制点信息
        
        return points, commands
    
    def _validate_path(self, d, element, components):
        """验证单条连线的质量"""
        errors = []
        
        # 解析所有命令和点
        segments = []  # 存储所有线段（包括 Q 命令的起始→终点）
        
        # 匹配所有命令
        cmd_pattern = r'([MLQ])\s+([\d.]+)\s+([\d.]+)(?:\s+([\d.]+)\s+([\d.]+))?'
        
        prev_point = None
        for match in re.finditer(cmd_pattern, d):
            cmd = match.group(1)
            x1, y1 = float(match.group(2)), float(match.group(3))
            
            if cmd == 'M':
                prev_point = (x1, y1)
            elif cmd == 'L':
                if prev_point:
                    segments.append({
                        'type': 'L',
                        'start': prev_point,
                        'end': (x1, y1)
                    })
                prev_point = (x1, y1)
            elif cmd == 'Q':
                # Q cx cy x y
                cx, cy = x1, y1
                ex, ey = float(match.group(4)), float(match.group(5))
                if prev_point:
                    segments.append({
                        'type': 'Q',
                        'start': prev_point,
                        'control': (cx, cy),
                        'end': (ex, ey)
                    })
                prev_point = (ex, ey)
        
        # 1. 检测 L 命令的线段是否为 90° 折线
        for seg in segments:
            if seg['type'] == 'L':
                x1, y1 = seg['start']
                x2, y2 = seg['end']
                if x1 != x2 and y1 != y2:
                    errors.append(
                        f"[连线质量] L 命令包含斜线段 ({x1},{y1})→({x2},{y2})，"
                        f"应改为 90° 折线（只能水平或垂直）"
                    )
                    break  # 只报告一次
        
        # 1.5 检测是否混合使用 L 和 Q 命令（不允许）
        has_l = any(seg['type'] == 'L' for seg in segments)
        has_q = any(seg['type'] == 'Q' for seg in segments)
        if has_l and has_q:
            errors.append(
                f"[连线质量] 连线混合使用直角(L)和圆角(Q)命令，"
                f"应统一使用一种风格（全直角或全圆角）"
            )
        
        # 2. 检测 L 命令的线段长度 ≥ 20px（排除 Q 命令前后的短线段）
        for i, seg in enumerate(segments):
            if seg['type'] == 'L':
                x1, y1 = seg['start']
                x2, y2 = seg['end']
                length = abs(x2 - x1) if y1 == y2 else abs(y2 - y1)
                
                # 检查是否是 Q 命令前后的线段
                is_near_q = False
                if i > 0 and segments[i-1]['type'] == 'Q':
                    is_near_q = True  # 前一个是 Q
                if i < len(segments) - 1 and segments[i+1]['type'] == 'Q':
                    is_near_q = True  # 后一个是 Q
                
                # 如果是 Q 命令附近的短线段，跳过检测
                if is_near_q and length < 20:
                    continue
                
                if length < 20 and length > 0:
                    errors.append(
                        f"[连线质量] L 线段长度 {length:.0f}px < 20px，"
                        f"({x1},{y1})→({x2},{y2}) 转折前长度不足"
                    )
        
        # 3. 检测所有线段是否穿过组件（排除起点和终点）
        all_points = []
        for seg in segments:
            all_points.append(seg['start'])
            all_points.append(seg['end'])
        
        if not all_points:
            return errors
        
        for seg in segments:
            segment = (seg['start'], seg['end'])
            
            for comp in components:
                # 跳过起点和终点所在的组件
                start_in_comp = self._point_in_rect(seg['start'], comp)
                end_in_comp = self._point_in_rect(seg['end'], comp)
                
                if start_in_comp or end_in_comp:
                    continue
                
                # 检测线段是否穿过组件
                if self._segment_intersects_rect(segment, comp):
                    comp_text = comp['text']
                    x1, y1 = seg['start']
                    x2, y2 = seg['end']
                    errors.append(
                        f"[连线质量] 连线穿过组件「{comp_text}」"
                        f"({comp['x1']:.0f}-{comp['x2']:.0f}, {comp['y1']:.0f}-{comp['y2']:.0f})，"
                        f"线段 ({x1:.0f},{y1:.0f})→({x2:.0f},{y2:.0f}) 需要绕行"
                    )
        
        return errors
    
    def _point_in_rect(self, point, rect):
        """检测点是否在矩形内"""
        x, y = point
        return (rect['x1'] <= x <= rect['x2'] and 
                rect['y1'] <= y <= rect['y2'])
    
    def _segment_intersects_rect(self, segment, rect):
        """检测线段是否与矩形相交（穿过组件）"""
        (x1, y1), (x2, y2) = segment
        rx1, ry1, rx2, ry2 = rect['x1'], rect['y1'], rect['x2'], rect['y2']
        
        # 水平线段
        if y1 == y2:
            y = y1
            x_start, x_end = min(x1, x2), max(x1, x2)
            # 线段的 y 在矩形 y 范围内
            if ry1 <= y <= ry2:
                # 线段的 x 与矩形 x 有交集
                if not (x_end < rx1 or x_start > rx2):
                    return True
        
        # 垂直线段
        if x1 == x2:
            x = x1
            y_start, y_end = min(y1, y2), max(y1, y2)
            # 线段的 x 在矩形 x 范围内
            if rx1 <= x <= rx2:
                # 线段的 y 与矩形 y 有交集
                if not (y_end < ry1 or y_start > ry2):
                    return True
        
        return False

    def _is_rect_inside_another(self, inner, outer_candidates):
        """检测一个矩形是否完全包含在另一个矩形内部（作为子元素）"""
        inner_x1, inner_y1 = inner['x1'], inner['y1']
        inner_x2, inner_y2 = inner['x2'], inner['y2']
        
        for outer in outer_candidates:
            # 跳过自己
            if inner is outer:
                continue
            # 检查 inner 是否完全在 outer 内部（留有一定边距）
            margin = 5  # 容差边距
            if (inner_x1 >= outer['x1'] + margin and 
                inner_y1 >= outer['y1'] + margin and
                inner_x2 <= outer['x2'] - margin and 
                inner_y2 <= outer['y2'] - margin):
                return True
        return False
    
    def check_component_overlap(self):
        """检测组件重叠:组件之间至少间隔 10px"""
        # 收集所有组件(rect)
        raw_components = []
        for rect in iter_tag(self.root, 'rect'):
            # 获取绝对坐标(考虑父级 <g> 的 transform)
            offset_x, offset_y = self._get_transform_offset(rect)
            x = float(rect.get('x', 0)) + offset_x
            y = float(rect.get('y', 0)) + offset_y
            w = float(rect.get('width', 0))
            h = float(rect.get('height', 0))
            # 过滤条件:
            # 1. 宽度 > 50 且高度 > 30(排除背景和大容器)
            # 2. 不是整个 SVG 尺寸(排除背景)
            # 3. 排除图例区域的小方块(宽度 <= 20)
            vb = self.root.get('viewBox', '0 0 1000 1000').split()
            vb_w = float(vb[2]) if len(vb) >= 4 else 1000
            vb_h = float(vb[3]) if len(vb) >= 4 else 1000
            if w > 50 and h > 30 and w < vb_w * 0.95 and h < vb_h * 0.95:
                raw_components.append({
                    'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h,
                    'text': self._get_rect_text(rect),
                    'element': rect
                })
        
        # 过滤掉完全包含在其他组件内部的子元素
        components = [
            comp for comp in raw_components 
            if not self._is_rect_inside_another(comp, raw_components)
        ]
        
        # 记录被过滤的子元素数量（用于调试信息）
        filtered_count = len(raw_components) - len(components)
        if filtered_count > 0:
            self.infos.append(f"[组件重叠] 检测到 {filtered_count} 个容器内部子元素，已排除")
        
        if len(components) < 2:
            return
        
        # 检测每对组件之间的重叠
        MIN_GAP = 20  # 最小间隔 20px
        overlap_count = 0
        
        for i in range(len(components)):
            for j in range(i + 1, len(components)):
                comp_a = components[i]
                comp_b = components[j]
                
                # 计算两个矩形之间的距离
                gap_x = max(0, max(comp_a['x1'], comp_b['x1']) - min(comp_a['x2'], comp_b['x2']))
                gap_y = max(0, max(comp_a['y1'], comp_b['y1']) - min(comp_a['y2'], comp_b['y2']))
                
                # 如果 gap_x 和 gap_y 都为 0，说明重叠
                # 如果只有一个为 0，另一个 < MIN_GAP，说明间距不足
                if gap_x == 0 and gap_y == 0:
                    # 完全重叠或部分重叠
                    overlap_count += 1
                    self.errors.append(
                        f"[组件重叠] 组件「{comp_a['text']}」与「{comp_b['text']}」重叠，"
                        f"需要调整位置确保至少间隔 {MIN_GAP}px"
                    )
                elif gap_x < MIN_GAP and gap_y == 0:
                    # 水平间距不足
                    overlap_count += 1
                    self.warnings.append(
                        f"[组件间距] 组件「{comp_a['text']}」与「{comp_b['text']}」"
                        f"水平间距 {gap_x:.0f}px < {MIN_GAP}px，建议增加间距"
                    )
                elif gap_y < MIN_GAP and gap_x == 0:
                    # 垂直间距不足
                    overlap_count += 1
                    self.warnings.append(
                        f"[组件间距] 组件「{comp_a['text']}」与「{comp_b['text']}」"
                        f"垂直间距 {gap_y:.0f}px < {MIN_GAP}px，建议增加间距"
                    )
        
        if overlap_count > 0:
            self.infos.append(f"[组件重叠] 检测到 {overlap_count} 个重叠/间距问题")
        else:
            self.infos.append(f"[组件重叠] 所有组件间距符合规范（≥{MIN_GAP}px）")
    
    def check_text_component_overlap(self):
        """检测文字是否与组件重叠(组件外的说明文字不能进入组件内部)"""
        # 收集所有组件
        components = []
        for rect in iter_tag(self.root, 'rect'):
            # 获取绝对坐标(考虑父级 <g> 的 transform)
            offset_x, offset_y = self._get_transform_offset(rect)
            x = float(rect.get('x', 0)) + offset_x
            y = float(rect.get('y', 0)) + offset_y
            w = float(rect.get('width', 0))
            h = float(rect.get('height', 0))
            vb = self.root.get('viewBox', '0 0 1000 1000').split()
            vb_w = float(vb[2]) if len(vb) >= 4 else 1000
            vb_h = float(vb[3]) if len(vb) >= 4 else 1000
            if w > 50 and h > 30 and w < vb_w * 0.95 and h < vb_h * 0.95:
                components.append({
                    'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h,
                    'text': self._get_rect_text(rect)
                })
        
        if not components:
            return
        
        # 收集所有文字元素（包括 tspan）
        texts = []
        for text_elem in iter_tag(self.root, 'text'):
            x = float(text_elem.get('x', 0))
            y = float(text_elem.get('y', 0))
            
            # 检查是否有 tspan
            tspans = list(iter_tag(text_elem, 'tspan'))
            if tspans:
                # 多行文字，计算总高度
                first_tspan = tspans[0]
                first_x = float(first_tspan.get('x', x))
                first_y = float(first_tspan.get('y', y))
                
                # 估算宽度（取最长的 tspan）
                max_width = 0
                longest_content = ''
                for tspan in tspans:
                    content = (tspan.text or '').strip()
                    if len(content) > len(longest_content):
                        longest_content = content
                    chinese_chars = len([c for c in content if '\u4e00' <= c <= '\u9fff'])
                    other_chars = len(content) - chinese_chars
                    estimated_width = chinese_chars * 12 + other_chars * 7
                    max_width = max(max_width, estimated_width)
                
                # 跳过空文字
                if not longest_content.strip():
                    continue
                
                # 估算总高度（每行约 18px）
                estimated_height = len(tspans) * 18
                
                texts.append({
                    'x1': first_x,
                    'y1': first_y,
                    'x2': first_x + max_width,
                    'y2': first_y + estimated_height,
                    'text': longest_content[:30],
                    'element': text_elem,
                    'is_multiline': True
                })
            else:
                # 单行文字
                text_content = (text_elem.text or '').strip()
                
                # 跳过空文字
                if not text_content:
                    continue
                
                chinese_chars = len([c for c in text_content if '\u4e00' <= c <= '\u9fff'])
                other_chars = len(text_content) - chinese_chars
                estimated_width = chinese_chars * 12 + other_chars * 7
                estimated_height = 16
                
                texts.append({
                    'x1': x,
                    'y1': y - estimated_height,  # 文字基线定位，需要向上偏移
                    'x2': x + estimated_width,
                    'y2': y,
                    'text': text_content[:30],
                    'element': text_elem,
                    'is_multiline': False
                })
        
        if not texts:
            return
        
        # 检测文字是否与组件重叠
        MIN_GAP = 10  # 文字与组件至少间隔 10px
        overlap_count = 0
        
        for text_info in texts:
            for comp in components:
                # 计算文字与组件的距离
                gap_x = max(0, max(text_info['x1'], comp['x1']) - min(text_info['x2'], comp['x2']))
                gap_y = max(0, max(text_info['y1'], comp['y1']) - min(text_info['y2'], comp['y2']))
                
                # 如果重叠（间距为 0）
                if gap_x == 0 and gap_y == 0:
                    # 检查文字中心点
                    text_center_x = (text_info['x1'] + text_info['x2']) / 2
                    text_center_y = (text_info['y1'] + text_info['y2']) / 2
                    
                    # 判断文字是否在组件内部
                    text_in_comp = (comp['x1'] <= text_center_x <= comp['x2'] and 
                                   comp['y1'] <= text_center_y <= comp['y2'])
                    
                    # 如果文字在组件内部，跳过（这是正常的组件标题/说明）
                    if text_in_comp:
                        continue
                    
                    # 外部文字与组件重叠，计算建议调整距离
                    overlap_count += 1
                    if overlap_count <= 3:
                        # 计算需要移动的距离
                        if text_info['x2'] > comp['x1'] and text_info['x1'] < comp['x1']:
                            move_x = int(text_info['x2'] - comp['x1'] + MIN_GAP)
                            suggestion = f"建议向左移动 {move_x}px"
                        elif text_info['x1'] < comp['x2'] and text_info['x2'] > comp['x2']:
                            move_x = int(text_info['x1'] - comp['x2'] + MIN_GAP)
                            suggestion = f"建议向右移动 {abs(move_x)}px"
                        elif text_info['y2'] > comp['y1'] and text_info['y1'] < comp['y1']:
                            move_y = int(text_info['y2'] - comp['y1'] + MIN_GAP)
                            suggestion = f"建议向上移动 {move_y}px"
                        elif text_info['y1'] < comp['y2'] and text_info['y2'] > comp['y2']:
                            move_y = int(text_info['y1'] - comp['y2'] + MIN_GAP)
                            suggestion = f"建议向下移动 {abs(move_y)}px"
                        else:
                            suggestion = "需要调整位置"
                        
                        self.warnings.append(
                            f"[文字重叠] 文字「{text_info['text']}」与组件「{comp['text']}」重叠，"
                            f"{suggestion} 避免遮挡"
                        )
        
        if overlap_count > 0:
            if overlap_count > 3:
                self.infos.append(f"[文字重叠] 检测到 {overlap_count} 个文字与组件重叠（仅显示前3个）")
            else:
                self.infos.append(f"[文字重叠] 检测到 {overlap_count} 个文字与组件重叠")
        else:
            self.infos.append("[文字重叠] 所有外部文字与组件间距符合规范")

    def check_connector_elements(self):
        """检查连线元素规范：必须使用 <path> 且 fill="none"（line_standard.md 第11.3节）"""
        # 检测是否使用了 <line> 元素（应该用 <path>）
        lines = list(iter_tag(self.root, 'line'))
        if lines:
            self.errors.append(
                f"[连线元素] 检测到 {len(lines)} 个 <line> 元素，"
                f"连线必须使用 <path> 而非 <line>（便于动画和 marker 支持）"
            )
        
        # 检测 <path> 是否缺少 fill="none"
        paths_without_fill_none = []
        for path in iter_tag(self.root, 'path'):
            if path.get('stroke'):  # 只检查有 stroke 的 path（连线）
                fill = path.get('fill', '')
                if fill != 'none':
                    paths_without_fill_none.append(path)
        
        if paths_without_fill_none:
            self.errors.append(
                f"[连线元素] 检测到 {len(paths_without_fill_none)} 个 <path> 缺少 fill='none'，"
                f"连线路径必须设置 fill='none' 防止填充形成黑色块"
            )
        
        if not lines and not paths_without_fill_none:
            self.infos.append("[连线元素] 所有连线符合规范（使用 <path> + fill='none'）")
    
    def check_connection_points(self):
        """检查连接点是否为四边中点（line_standard.md 第1.1节）"""
        # 收集所有组件
        components = []
        for rect in iter_tag(self.root, 'rect'):
            x = float(rect.get('x', 0))
            y = float(rect.get('y', 0))
            w = float(rect.get('width', 0))
            h = float(rect.get('height', 0))
            vb = self.root.get('viewBox', '0 0 1000 1000').split()
            vb_w = float(vb[2]) if len(vb) >= 4 else 1000
            vb_h = float(vb[3]) if len(vb) >= 4 else 1000
            if w > 50 and h > 30 and w < vb_w * 0.95 and h < vb_h * 0.95:
                # 计算四边中点
                center_x = x + w / 2
                center_y = y + h / 2
                components.append({
                    'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h,
                    'text': self._get_rect_text(rect),
                    'midpoints': {
                        'L': (x, center_y),
                        'R': (x + w, center_y),
                        'T': (center_x, y),
                        'B': (center_x, y + h)
                    }
                })
        
        if len(components) < 2:
            return
        
        # 检查所有连线的起点和终点
        TOLERANCE = 3  # 容忍度 3px
        violation_count = 0
        
        for path in iter_tag(self.root, 'path'):
            # 检查是否是连线（有 stroke 属性或 CSS class 包含 line/flow 等关键词）
            is_connector = False
            if path.get('stroke'):
                is_connector = True
            elif path.get('class'):
                css_class = path.get('class', '')
                if any(keyword in css_class for keyword in ['line', 'connector', 'flow', 'arrow', 'edge']):
                    is_connector = True
            
            if not is_connector:
                continue
            
            d = path.get('d', '')
            if not d.startswith('M'):
                continue
            
            # 正确解析路径点（区分 M/L 和 Q 命令）
            # Q 命令格式：Q cx cy x y（控制点 + 终点）
            # 我们只需要 M、L 的点和 Q 的终点
            path_points = []
            
            # 匹配 M 和 L 命令
            for match in re.finditer(r'[ML]\s+([\d.]+)\s+([\d.]+)', d):
                path_points.append((float(match.group(1)), float(match.group(2))))
            
            # 匹配 Q 命令的终点（第3、4个数字）
            for match in re.finditer(r'Q\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)', d):
                path_points.append((float(match.group(1)), float(match.group(2))))
            
            if len(path_points) < 2:
                continue
            
            start_point = path_points[0]
            end_point = path_points[-1]
            
            # 检查起点是否在某个组件的四边中点上
            start_valid = False
            for comp in components:
                for side, mid in comp['midpoints'].items():
                    if (abs(start_point[0] - mid[0]) <= TOLERANCE and 
                        abs(start_point[1] - mid[1]) <= TOLERANCE):
                        start_valid = True
                        break
                if start_valid:
                    break
            
            # 检查终点是否在某个组件的四边中点上
            end_valid = False
            for comp in components:
                for side, mid in comp['midpoints'].items():
                    if (abs(end_point[0] - mid[0]) <= TOLERANCE and 
                        abs(end_point[1] - mid[1]) <= TOLERANCE):
                        end_valid = True
                        break
                if end_valid:
                    break
            
            if not start_valid or not end_valid:
                violation_count += 1
                if violation_count <= 3:  # 只报告前3个错误
                    self.errors.append(
                        f"[连接点] 连线起点({start_point[0]:.0f},{start_point[1]:.0f}) "
                        f"或终点({end_point[0]:.0f},{end_point[1]:.0f}) "
                        f"不在组件四边中点上（L/R/T/B）"
                    )
        
        if violation_count > 0:
            if violation_count > 3:
                self.infos.append(f"[连接点] 检测到 {violation_count} 个连接点不规范（仅显示前3个）")
            else:
                self.infos.append(f"[连接点] 检测到 {violation_count} 个连接点不规范")
        else:
            self.infos.append("[连接点] 所有连线连接点符合规范（四边中点）")
    
    def check_connection_direction(self):
        """检查连线出发/进入方向是否垂直于边框（line_standard.md 第2节）"""
        # 收集所有组件
        components = []
        for rect in iter_tag(self.root, 'rect'):
            x = float(rect.get('x', 0))
            y = float(rect.get('y', 0))
            w = float(rect.get('width', 0))
            h = float(rect.get('height', 0))
            vb = self.root.get('viewBox', '0 0 1000 1000').split()
            vb_w = float(vb[2]) if len(vb) >= 4 else 1000
            vb_h = float(vb[3]) if len(vb) >= 4 else 1000
            if w > 50 and h > 30 and w < vb_w * 0.95 and h < vb_h * 0.95:
                center_x = x + w / 2
                center_y = y + h / 2
                components.append({
                    'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h,
                    'text': self._get_rect_text(rect),
                    'midpoints': {
                        'L': (x, center_y),
                        'R': (x + w, center_y),
                        'T': (center_x, y),
                        'B': (center_x, y + h)
                    }
                })
        
        if len(components) < 2:
            return
        
        TOLERANCE = 3
        violation_count = 0
        
        for path in iter_tag(self.root, 'path'):
            # 检查是否是连线（有 stroke 属性或 CSS class 包含 line/flow 等关键词）
            is_connector = False
            if path.get('stroke'):
                is_connector = True
            elif path.get('class'):
                css_class = path.get('class', '')
                if any(keyword in css_class for keyword in ['line', 'connector', 'flow', 'arrow', 'edge']):
                    is_connector = True
            
            if not is_connector:
                continue
            
            d = path.get('d', '')
            if not d.startswith('M'):
                continue
            
            # 解析所有命令
            commands = []
            for match in re.finditer(r'([MLQ])\s+([\d.]+)\s+([\d.]+)', d):
                cmd = match.group(1)
                x = float(match.group(2))
                y = float(match.group(3))
                commands.append((cmd, x, y))
            
            if len(commands) < 2:
                continue
            
            # 检查第一段线段的方向
            start_point = (commands[0][1], commands[0][2])
            second_point = (commands[1][1], commands[1][2])
            
            # 找到起点所在的组件和边
            for comp in components:
                for side, mid in comp['midpoints'].items():
                    if (abs(start_point[0] - mid[0]) <= TOLERANCE and 
                        abs(start_point[1] - mid[1]) <= TOLERANCE):
                        # 验证第一段是否垂直于该边
                        dx = second_point[0] - start_point[0]
                        dy = second_point[1] - start_point[1]
                        
                        valid = False
                        if side == 'L' and dx < 0 and abs(dy) < TOLERANCE:  # L边应该向左
                            valid = True
                        elif side == 'R' and dx > 0 and abs(dy) < TOLERANCE:  # R边应该向右
                            valid = True
                        elif side == 'T' and dy < 0 and abs(dx) < TOLERANCE:  # T边应该向上
                            valid = True
                        elif side == 'B' and dy > 0 and abs(dx) < TOLERANCE:  # B边应该向下
                            valid = True
                        
                        if not valid:
                            violation_count += 1
                            if violation_count <= 3:
                                self.errors.append(
                                    f"[方向约束] 从组件「{comp['text']}」{side}边出发的连线 "
                                    f"第一段方向不垂直于边框（应该{'向左' if side == 'L' else '向右' if side == 'R' else '向上' if side == 'T' else '向下'}）"
                                )
                        break
                
                # 检查最后一段线段的方向（进入方向）
                if len(commands) >= 2:
                    end_point = (commands[-1][1], commands[-1][2])
                    prev_point = (commands[-2][1], commands[-2][2])
                    
                    for side, mid in comp['midpoints'].items():
                        if (abs(end_point[0] - mid[0]) <= TOLERANCE and 
                            abs(end_point[1] - mid[1]) <= TOLERANCE):
                            # 验证最后一段是否垂直于该边
                            dx = end_point[0] - prev_point[0]
                            dy = end_point[1] - prev_point[1]
                            
                            valid = False
                            if side == 'L' and dx > 0 and abs(dy) < TOLERANCE:  # L边应该从左来
                                valid = True
                            elif side == 'R' and dx < 0 and abs(dy) < TOLERANCE:  # R边应该从右来
                                valid = True
                            elif side == 'T' and dy > 0 and abs(dx) < TOLERANCE:  # T边应该从下来
                                valid = True
                            elif side == 'B' and dy < 0 and abs(dx) < TOLERANCE:  # B边应该从上来
                                valid = True
                            
                            if not valid:
                                violation_count += 1
                                if violation_count <= 3:
                                    self.errors.append(
                                        f"[方向约束] 进入组件「{comp['text']}」{side}边的连线 "
                                        f"最后一段方向不垂直于边框（应该{'从右来' if side == 'L' else '从左来' if side == 'R' else '从下来' if side == 'T' else '从上来'}）"
                                    )
                            break
        
        if violation_count > 0:
            if violation_count > 3:
                self.infos.append(f"[方向约束] 检测到 {violation_count} 个方向问题（仅显示前3个）")
            else:
                self.infos.append(f"[方向约束] 检测到 {violation_count} 个方向问题")
        else:
            self.infos.append("[方向约束] 所有连线方向符合规范（垂直于边框）")

    def run_common(self):
        self.check_svg_root()
        self.check_viewbox()
        self.check_defs()
        self.check_animation()
        self.check_has_connectors()
        self.check_connectors_quality()
        self.check_arrows()  # 新增：箭头规范检查
        self.check_component_overlap()  # 新增：组件重叠检查
        self.check_text_component_overlap()  # 新增：文字与组件重叠检查
        self.check_connector_elements()  # 新增：连线元素规范检查
        self.check_connection_points()  # 新增：连接点四边中点检查
        self.check_connection_direction()  # 新增：方向垂直约束检查

    def validate(self) -> bool:
        raise NotImplementedError

    def report(self):
        diagram_type = self.__class__.__name__.replace('Validator', '')
        print()
        print("=" * 60)
        print(f"  SVG 验证报告 [{diagram_type}]")
        print(f"  文件: {self.svg_path.name}")
        print("=" * 60)

        if self.infos:
            print("\n📊 统计信息:")
            for info in self.infos:
                print(f"  {info}")

        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}) — 必须修复:")
            for i, err in enumerate(self.errors, 1):
                print(f"  {i}. {err}")

        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}) — 建议修复:")
            for i, w in enumerate(self.warnings, 1):
                print(f"  {i}. {w}")

        if not self.errors and not self.warnings:
            print("\n✅ 验证通过！")
        elif not self.errors:
            print(f"\n⚠️  验证通过（有 {len(self.warnings)} 个警告）")
        else:
            print(f"\n❌ 验证不通过（{len(self.errors)} 个错误，{len(self.warnings)} 个警告）")
        print("=" * 60)
        print()


# ============================================================
# 系统架构图 / 业务架构图
# ============================================================
class SystemValidator(BaseValidator):
    """系统架构图验证器"""

    MIN_LAYERS = 2  # 至少 2 个分层

    def validate(self) -> bool:
        if not self.load():
            return False
        self.run_common()
        self._check_layers()
        self._check_layer_labels()
        self._check_connector_arrows()
        return len(self.errors) == 0

    def _check_layers(self):
        """至少要有 2 个分层矩形（用不同 fill 区分层次）"""
        rects = list(iter_tag(self.root, 'rect'))
        # 统计不同 fill 的大矩形（宽度>100 视为层块）
        layer_fills = set()
        for r in rects:
            w = float(r.get('width', 0))
            fill = r.get('fill', '')
            if w > 100 and fill and fill not in ('none', '#fff', '#ffffff', 'white'):
                layer_fills.add(fill)
        self.infos.append(f"[分层] 检测到 {len(layer_fills)} 个不同颜色的分层")
        if len(layer_fills) < self.MIN_LAYERS:
            self.errors.append(
                f"[分层] 系统架构图至少需要 {self.MIN_LAYERS} 个层次（用不同填充色区分），"
                f"当前仅检测到 {len(layer_fills)} 个"
            )

    def _check_layer_labels(self):
        """每层应有文字标签"""
        texts = list(iter_tag(self.root, 'text'))
        if len(texts) < 3:
            self.warnings.append(
                f"[内容] 仅检测到 {len(texts)} 个文本元素，系统架构图各组件/层次应有标签"
            )

    def _check_connector_arrows(self):
        """连线应有箭头（marker-end）"""
        lines = list(iter_tag(self.root, 'line'))
        polylines = list(iter_tag(self.root, 'polyline'))
        all_lines = lines + polylines
        if not all_lines:
            return
        no_arrow = [
            l for l in all_lines
            if not l.get('marker-end') and not l.get('marker-start')
        ]
        if len(no_arrow) == len(all_lines):
            self.warnings.append(
                "[连线] 所有连线均无箭头（marker-end），系统架构图的调用关系应用箭头表示方向"
            )


# ============================================================
# 部署架构图
# ============================================================
class DeploymentValidator(BaseValidator):
    """部署架构图验证器"""

    def validate(self) -> bool:
        if not self.load():
            return False
        self.run_common()
        self._check_cluster_groups()
        self._check_has_infra_keywords()
        self._check_instance_labels()
        return len(self.errors) == 0

    def _check_cluster_groups(self):
        """应有虚线框表示集群/分组"""
        dashed_rects = [
            r for r in iter_tag(self.root, 'rect')
            if r.get('stroke-dasharray') or 'dasharray' in (r.get('style') or '')
        ]
        if not dashed_rects:
            self.warnings.append(
                "[集群] 未检测到虚线框（stroke-dasharray），"
                "部署架构图通常用虚线框包围同一集群/可用区的实例"
            )
        else:
            self.infos.append(f"[集群] 检测到 {len(dashed_rects)} 个虚线分组框")

    def _check_has_infra_keywords(self):
        """应包含基础设施相关关键词"""
        keywords = ['数据库', 'DB', 'MySQL', 'Redis', 'MQ', 'Kafka',
                    'Nginx', 'K8s', '负载', '集群', '实例', 'Node',
                    'Broker', '存储', 'Storage']
        found = [k for k in keywords if k in self.content]
        if not found:
            self.warnings.append(
                "[内容] 未检测到基础设施关键词（数据库/缓存/MQ/负载均衡等），"
                "部署架构图应展示实际部署的中间件和服务组件"
            )
        else:
            self.infos.append(f"[内容] 基础设施组件: {found[:5]}")

    def _check_instance_labels(self):
        """节点应有明确标签"""
        texts = list(iter_tag(self.root, 'text'))
        rects = list(iter_tag(self.root, 'rect'))
        if rects and len(texts) < len(rects) * 0.5:
            self.warnings.append(
                f"[内容] 文本数量（{len(texts)}）远少于图形数量（{len(rects)}），"
                "各部署节点应有清晰的标签"
            )


# ============================================================
# 调用链路图
# ============================================================
class CallFlowValidator(BaseValidator):
    """调用链路图验证器"""

    def validate(self) -> bool:
        if not self.load():
            return False
        self.run_common()
        self._check_horizontal_layout()
        self._check_connector_labels()
        self._check_arrows()
        return len(self.errors) == 0

    def _check_horizontal_layout(self):
        """调用链路图主要是水平布局（节点 y 坐标相近）"""
        rects = [
            r for r in iter_tag(self.root, 'rect')
            if float(r.get('width', 0)) > 40
        ]
        if len(rects) < 2:
            return
        ys = [float(r.get('y', 0)) for r in rects]
        y_spread = max(ys) - min(ys)
        xs = [float(r.get('x', 0)) for r in rects]
        x_spread = max(xs) - min(xs)
        if y_spread > x_spread and y_spread > 200:
            self.warnings.append(
                f"[布局] 节点 Y 轴跨度（{y_spread:.0f}px）大于 X 轴跨度（{x_spread:.0f}px），"
                "调用链路图推荐水平（从左到右）布局"
            )

    def _check_connector_labels(self):
        """连线上应有接口名称标注"""
        lines = list(iter_tag(self.root, 'line')) + list(iter_tag(self.root, 'polyline'))
        texts = list(iter_tag(self.root, 'text'))
        if lines and len(texts) < len(lines):
            self.warnings.append(
                f"[连线] 连线数量（{len(lines)}）多于文本标注（{len(texts)}），"
                "调用链路图的每条连线应标注接口名/方法名"
            )

    def _check_arrows(self):
        """所有连线必须有箭头"""
        lines = list(iter_tag(self.root, 'line')) + list(iter_tag(self.root, 'polyline'))
        if not lines:
            return
        no_arrow = [l for l in lines if not l.get('marker-end')]
        if no_arrow:
            self.errors.append(
                f"[连线] {len(no_arrow)} 条连线无箭头（marker-end），"
                "调用链路图必须用箭头表示调用方向"
            )


# ============================================================
# 数据流图
# ============================================================
class DataFlowValidator(BaseValidator):
    """数据流图验证器"""

    def validate(self) -> bool:
        if not self.load():
            return False
        self.run_common()
        self._check_data_nodes()
        self._check_flow_direction()
        self._check_connector_labels()
        return len(self.errors) == 0

    def _check_data_nodes(self):
        """应有数据源节点（平行四边形/polygon）或存储节点（椭圆/path）"""
        polygons = list(iter_tag(self.root, 'polygon'))
        ellipses = list(iter_tag(self.root, 'ellipse'))
        paths = list(iter_tag(self.root, 'path'))
        rects = list(iter_tag(self.root, 'rect'))
        special = len(polygons) + len(ellipses)
        self.infos.append(
            f"[节点] 矩形 {len(rects)} 个，多边形/椭圆 {special} 个（数据源/存储）"
        )
        if special == 0 and len(rects) > 0:
            self.warnings.append(
                "[节点] 未检测到多边形/椭圆节点，数据流图建议：\n"
                "  · 数据源使用平行四边形（polygon）\n"
                "  · 数据存储使用椭圆（ellipse）或圆柱形（path）"
            )

    def _check_flow_direction(self):
        """水平数据流方向（X 轴跨度应大于 Y 轴）"""
        rects = [r for r in iter_tag(self.root, 'rect') if float(r.get('width', 0)) > 40]
        if len(rects) < 2:
            return
        xs = [float(r.get('x', 0)) for r in rects]
        ys = [float(r.get('y', 0)) for r in rects]
        if (max(xs) - min(xs)) < (max(ys) - min(ys)) - 100:
            self.warnings.append(
                "[布局] 数据流图推荐水平（从左到右）流向布局，当前纵向跨度偏大"
            )

    def _check_connector_labels(self):
        """连线应标注数据格式"""
        lines = list(iter_tag(self.root, 'line')) + list(iter_tag(self.root, 'polyline'))
        texts = list(iter_tag(self.root, 'text'))
        if lines and len(texts) < len(lines):
            self.warnings.append(
                f"[连线] 连线（{len(lines)}）多于文本标注（{len(texts)}），"
                "数据流图建议在连线上标注数据格式/类型"
            )


# ============================================================
# 时序图
# ============================================================
class SequenceValidator(BaseValidator):
    """时序图验证器"""

    def validate(self) -> bool:
        if not self.load():
            return False
        self.run_common()
        self._check_lifelines()
        self._check_horizontal_messages()
        self._check_return_messages()
        self._check_participant_labels()
        return len(self.errors) == 0

    def _check_lifelines(self):
        """必须有垂直虚线（生命线）"""
        dashed_lines = [
            l for l in iter_tag(self.root, 'line')
            if l.get('stroke-dasharray') and
               abs(float(l.get('x1', 0)) - float(l.get('x2', 0))) < 2  # 垂直
        ]
        if not dashed_lines:
            self.errors.append(
                "[结构] 未检测到垂直虚线（生命线），时序图每个参与者下方必须有垂直虚线 "
                "（stroke-dasharray，x1=x2）"
            )
        else:
            self.infos.append(f"[参与者] 检测到 {len(dashed_lines)} 条生命线")

    def _check_horizontal_messages(self):
        """消息线应为水平线（y1=y2 的实线）"""
        h_lines = [
            l for l in iter_tag(self.root, 'line')
            if abs(float(l.get('y1', 0)) - float(l.get('y2', 0))) < 2  # 水平
               and not l.get('stroke-dasharray')
        ]
        if not h_lines:
            self.errors.append(
                "[消息] 未检测到水平消息线（y1=y2 的实线），"
                "时序图的消息调用必须是水平箭头"
            )
        else:
            no_arrow = [l for l in h_lines if not l.get('marker-end')]
            if no_arrow:
                self.errors.append(
                    f"[消息] {len(no_arrow)} 条消息线无箭头（marker-end），"
                    "时序图消息线必须带箭头表示调用方向"
                )
            self.infos.append(f"[消息] 检测到 {len(h_lines)} 条消息线")

    def _check_return_messages(self):
        """应有返回消息（水平虚线）"""
        return_lines = [
            l for l in iter_tag(self.root, 'line')
            if l.get('stroke-dasharray') and
               abs(float(l.get('y1', 0)) - float(l.get('y2', 0))) < 2  # 水平虚线
        ]
        if not return_lines:
            self.warnings.append(
                "[消息] 未检测到返回消息线（水平虚线 stroke-dasharray），"
                "时序图通常应包含 return/响应 虚线箭头"
            )

    def _check_participant_labels(self):
        """参与者矩形应有标签"""
        rects = [
            r for r in iter_tag(self.root, 'rect')
            if float(r.get('height', 0)) < 60  # 参与者头部矩形通常较矮
        ]
        texts = list(iter_tag(self.root, 'text'))
        if rects and len(texts) < len(rects):
            self.warnings.append(
                f"[参与者] 矩形数量（{len(rects)}）多于文本（{len(texts)}），"
                "每个参与者应有名称标签"
            )


# ============================================================
# 状态图
# ============================================================
class StateValidator(BaseValidator):
    """状态图验证器"""

    def validate(self) -> bool:
        if not self.load():
            return False
        self.run_common()
        self._check_initial_state()
        self._check_terminal_state()
        self._check_state_nodes()
        self._check_transition_labels()
        return len(self.errors) == 0

    def _check_initial_state(self):
        """必须有初始状态（实心圆 circle fill=#333）"""
        circles = list(iter_tag(self.root, 'circle'))
        initial = [
            c for c in circles
            if c.get('fill', '').lower() in ('#333', '#333333', 'black', '#000', '#000000')
               and float(c.get('r', 999)) <= 12
        ]
        if not initial:
            self.errors.append(
                "[结构] 未检测到初始状态节点（实心圆 <circle fill='#333' r≤12>），"
                "状态图必须有明确的起始点"
            )
        else:
            self.infos.append(f"[结构] 检测到 {len(initial)} 个初始/终止状态节点")

    def _check_terminal_state(self):
        """建议有终止状态（双圆）"""
        circles = list(iter_tag(self.root, 'circle'))
        # 终止状态通常有两个同心圆（一个空心一个实心）
        if len(circles) < 2:
            self.warnings.append(
                "[结构] 未检测到终止状态节点（双圆：空心圆+实心圆），"
                "建议状态图明确标注终止状态"
            )

    def _check_state_nodes(self):
        """状态节点必须是圆角矩形（rx>0）"""
        rects = [r for r in iter_tag(self.root, 'rect') if float(r.get('width', 0)) > 40]
        no_rx = [r for r in rects if float(r.get('rx', 0)) == 0]
        if no_rx:
            self.errors.append(
                f"[节点] {len(no_rx)} 个状态节点缺少圆角（rx 属性），"
                "状态图的状态节点必须使用圆角矩形（rx≥4）"
            )
        self.infos.append(f"[节点] 检测到 {len(rects)} 个状态节点")

    def _check_transition_labels(self):
        """状态转移线上应有事件/条件标注"""
        lines = list(iter_tag(self.root, 'line')) + list(iter_tag(self.root, 'polyline'))
        texts = list(iter_tag(self.root, 'text'))
        state_rects = [r for r in iter_tag(self.root, 'rect') if float(r.get('width', 0)) > 40]
        # 文本数 > 状态数 说明有转移标注
        if lines and len(texts) <= len(state_rects):
            self.warnings.append(
                f"[转移] 文本标注数（{len(texts)}）不多于状态节点数（{len(state_rects)}），"
                "状态转移线上应标注触发事件或条件"
            )


# ============================================================
# 流程图
# ============================================================
class FlowchartValidator(BaseValidator):
    """流程图验证器"""

    def validate(self) -> bool:
        if not self.load():
            return False
        self.run_common()
        self._check_start_end_nodes()
        self._check_decision_nodes()
        self._check_connector_arrows()
        self._check_branch_labels()
        return len(self.errors) == 0

    def _check_start_end_nodes(self):
        """必须有开始/结束节点（rx≥16 的圆角矩形或椭圆）"""
        rects = list(iter_tag(self.root, 'rect'))
        ellipses = list(iter_tag(self.root, 'ellipse'))
        # 圆角矩形 rx>=16 视为开始/结束
        rounded = [r for r in rects if float(r.get('rx', 0)) >= 16]
        start_end = rounded + ellipses
        if not start_end:
            self.errors.append(
                "[结构] 未检测到开始/结束节点，流程图必须有明确的边界节点，"
                "使用圆角矩形（rx≥16）或椭圆表示开始/结束"
            )
        else:
            self.infos.append(f"[结构] 检测到 {len(start_end)} 个开始/结束节点")

    def _check_decision_nodes(self):
        """应有判断节点（菱形 polygon）"""
        polygons = list(iter_tag(self.root, 'polygon'))
        if not polygons:
            self.warnings.append(
                "[节点] 未检测到判断节点（菱形 <polygon>），"
                "业务流程图通常有条件判断分支"
            )
        else:
            self.infos.append(f"[节点] 检测到 {len(polygons)} 个判断节点（菱形）")

    def _check_connector_arrows(self):
        """所有连线必须有箭头"""
        lines = list(iter_tag(self.root, 'line')) + list(iter_tag(self.root, 'polyline'))
        if not lines:
            return
        no_arrow = [l for l in lines if not l.get('marker-end')]
        if no_arrow:
            self.errors.append(
                f"[连线] {len(no_arrow)} 条连线无箭头（marker-end），"
                "流程图所有连线必须有箭头表示流向"
            )

    def _check_branch_labels(self):
        """判断节点的分支应有 Yes/No 或条件标注"""
        polygons = list(iter_tag(self.root, 'polygon'))
        if not polygons:
            return
        # 检测 Yes/No/是/否 等文字是否存在
        branch_keywords = ['Yes', 'No', '是', '否', 'Y', 'N', '成功', '失败', '通过', '拒绝']
        found = [k for k in branch_keywords if k in self.content]
        if not found:
            self.warnings.append(
                "[连线] 判断节点分支未检测到 Yes/No/是/否 等标注，"
                "判断分支应明确标注条件结果"
            )


# ============================================================
# 泳道图
# ============================================================
class SwimlaneValidator(BaseValidator):
    """泳道图验证器"""

    MIN_LANES = 2  # 至少 2 条泳道

    def validate(self) -> bool:
        if not self.load():
            return False
        self.run_common()
        self._check_lane_structure()
        self._check_lane_labels()
        self._check_steps_in_lanes()
        self._check_connector_arrows()
        return len(self.errors) == 0

    def _check_lane_structure(self):
        """泳道应由大矩形（宽>200 或高>200）组成且数量≥2"""
        rects = list(iter_tag(self.root, 'rect'))
        vb = self.root.get('viewBox', '0 0 800 600')
        vb_parts = vb.split()
        total_w = float(vb_parts[2]) if len(vb_parts) >= 4 else 800
        total_h = float(vb_parts[3]) if len(vb_parts) >= 4 else 600

        # 水平泳道：height > total_h * 0.15；垂直泳道：width > total_w * 0.15
        h_lanes = [
            r for r in rects
            if float(r.get('height', 0)) > total_h * 0.15
               and float(r.get('width', 0)) > total_w * 0.5
        ]
        v_lanes = [
            r for r in rects
            if float(r.get('width', 0)) > total_w * 0.15
               and float(r.get('height', 0)) > total_h * 0.5
        ]
        lane_count = max(len(h_lanes), len(v_lanes))
        self.infos.append(f"[泳道] 检测到约 {lane_count} 条泳道")
        if lane_count < self.MIN_LANES:
            self.errors.append(
                f"[泳道] 检测到 {lane_count} 条泳道，泳道图至少需要 {self.MIN_LANES} 条泳道"
            )

    def _check_lane_labels(self):
        """每条泳道应有角色/系统标签"""
        texts = list(iter_tag(self.root, 'text'))
        if len(texts) < self.MIN_LANES:
            self.warnings.append(
                f"[泳道] 文本数量（{len(texts)}）过少，每条泳道应有角色/系统名称标签"
            )

    def _check_steps_in_lanes(self):
        """泳道内应有流程步骤节点"""
        rects = list(iter_tag(self.root, 'rect'))
        vb = self.root.get('viewBox', '0 0 800 600')
        vb_parts = vb.split()
        total_w = float(vb_parts[2]) if len(vb_parts) >= 4 else 800
        # 小矩形（宽<泳道宽×0.5）视为步骤节点
        step_rects = [
            r for r in rects
            if float(r.get('width', 0)) < total_w * 0.3
               and float(r.get('width', 0)) > 30
        ]
        if not step_rects:
            self.errors.append(
                "[步骤] 未检测到流程步骤节点（泳道内的小矩形），泳道图必须有具体流程步骤"
            )
        else:
            self.infos.append(f"[步骤] 检测到 {len(step_rects)} 个流程步骤节点")

    def _check_connector_arrows(self):
        """连线必须有箭头"""
        lines = list(iter_tag(self.root, 'line')) + list(iter_tag(self.root, 'polyline'))
        if not lines:
            return
        no_arrow = [l for l in lines if not l.get('marker-end')]
        if no_arrow:
            self.errors.append(
                f"[连线] {len(no_arrow)} 条连线无箭头（marker-end），"
                "泳道图连线必须有箭头表示流向"
            )


# ============================================================
# 领域模型图验证器
# ============================================================
class DomainModelValidator(BaseValidator):
    """领域模型图验证器"""

    def validate(self) -> bool:
        if not self.load():
            return False
        # 领域模型图跳过部分通用检查
        self.check_svg_root()
        self.check_viewbox()
        self._check_domain_frames()
        self._check_model_cards()
        self._check_four_colors()
        self._check_model_width()
        self._check_connector_limit()
        return len(self.errors) == 0

    def _check_domain_frames(self):
        """应有领域外框（带 rx 属性的大矩形）"""
        rects = list(iter_tag(self.root, 'rect'))
        # 领域外框通常是较大的矩形（宽度 > 300）
        domain_frames = [
            r for r in rects
            if float(r.get('width', 0)) > 300
               and r.get('rx')  # 有圆角
               and r.get('stroke')  # 有边框
        ]
        if not domain_frames:
            self.warnings.append(
                "[领域外框] 未检测到领域外框（大矩形），"
                "领域模型图通常包含多个领域边界"
            )
        else:
            self.infos.append(f"[领域外框] 检测到 {len(domain_frames)} 个领域边界")

    def _check_model_cards(self):
        """检查模型卡片结构"""
        rects = list(iter_tag(self.root, 'rect'))
        # 模型卡片是宽度约150px的矩形
        model_cards = [
            r for r in rects
            if 140 <= float(r.get('width', 0)) <= 160
        ]
        if not model_cards:
            self.errors.append(
                "[模型卡片] 未检测到模型卡片（宽度约150px的矩形），"
                "领域模型图应包含领域模型"
            )
        else:
            self.infos.append(f"[模型卡片] 检测到 {len(model_cards)} 个模型")

    def _check_four_colors(self):
        """检查四色配色规范"""
        color_pattern = r'#[0-9A-Fa-f]{6}'
        found_colors = set(re.findall(color_pattern, self.content))
        found_lower = {c.lower() for c in found_colors}
        valid_lower = {c.lower() for c in DOMAIN_COLORS}
        
        # 检查是否使用了四色
        four_color_fills = {'#fce4ec', '#f1f8e9', '#fff9c4', '#e3f2fd'}
        found_four = found_lower & {c.lower() for c in four_color_fills}
        
        if len(found_four) < 2:
            self.warnings.append(
                f"[配色] 仅检测到 {len(found_four)} 种四色配色，"
                "领域模型图应使用时标/资源/角色/描述四种颜色区分模型类型"
            )
        else:
            self.infos.append(f"[配色] 检测到 {len(found_four)} 种四色配色")

    def _check_model_width(self):
        """检查模型宽度是否统一为150px"""
        rects = list(iter_tag(self.root, 'rect'))
        model_cards = [
            r for r in rects
            if float(r.get('width', 0)) > 100  # 过滤掉小图标
        ]
        widths = set(float(r.get('width', 0)) for r in model_cards)
        
        # 如果有宽度差异较大，发出警告
        if widths and (max(widths) - min(widths)) > 50:
            non_standard = [w for w in widths if abs(w - 150) > 20]
            if non_standard:
                self.warnings.append(
                    f"[尺寸] 检测到非标准模型宽度: {sorted(set(int(w) for w in non_standard))}，"
                    "领域模型图模型宽度应统一为150px"
                )

    def _check_connector_limit(self):
        """检查单个模型的连线数量"""
        # 统计连接到每个模型的连线数量（简化检测）
        lines = list(iter_tag(self.root, 'line'))
        paths = [
            p for p in iter_tag(self.root, 'path')
            if p.get('stroke') and not p.get('fill', 'none').startswith('#')
        ]
        connectors = lines + paths
        
        if len(connectors) > 20:
            self.warnings.append(
                f"[连线] 连线数量较多（{len(connectors)} 条），"
                "建议每个模型的连线不超过3条，避免图表过于复杂"
            )
        else:
            self.infos.append(f"[连线] 检测到 {len(connectors)} 条连线")


# ============================================================
# 通用兜底验证器
# ============================================================
class GenericValidator(BaseValidator):
    """通用 SVG 验证器（未知图类型）"""

    def validate(self) -> bool:
        if not self.load():
            return False
        self.run_common()
        # 移除硬性配色检查，配色规范通过 LLM 提示词引导，保留自由度
        return len(self.errors) == 0


# ============================================================
# 工厂函数：根据图类型创建验证器
# ============================================================
TYPE_MAP = {
    'system':        SystemValidator,
    'deployment':    DeploymentValidator,
    'call-flow':     CallFlowValidator,
    'data-flow':     DataFlowValidator,
    'sequence':      SequenceValidator,
    'state':         StateValidator,
    'flowchart':     FlowchartValidator,
    'swimlane':      SwimlaneValidator,
    'model': DomainModelValidator,
}


def detect_type_from_filename(path: Path) -> Optional[str]:
    stem = path.stem  # 去掉扩展名
    for keyword, t in FILENAME_TYPE_MAP.items():
        if keyword in stem:
            return t
    return None


def create_validator(svg_path: str, diagram_type: Optional[str]) -> BaseValidator:
    path = Path(svg_path)
    if not diagram_type:
        diagram_type = detect_type_from_filename(path)

    cls = TYPE_MAP.get(diagram_type, GenericValidator)
    return cls(svg_path)


# ============================================================
# 主入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description='SVG 架构图验证脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
图类型 (--type):
  system        系统架构图 / 业务架构图
  deployment    部署架构图
  call-flow     调用链路图
  data-flow     数据流图
  sequence      时序图
  state         状态图
  flowchart     流程图
  swimlane      泳道图
  model         领域模型图
        """,
    )
    parser.add_argument('svg_path', help='SVG 文件路径')
    parser.add_argument('--type', '-t', dest='diagram_type',
                        choices=list(TYPE_MAP.keys()),
                        help='图类型（不传则从文件名自动推断）')
    args = parser.parse_args()

    validator = create_validator(args.svg_path, args.diagram_type)
    is_valid = validator.validate()
    validator.report()
    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
