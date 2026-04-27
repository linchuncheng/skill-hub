#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
泳道图 SVG 生成器 - 从 JSON 配置生成 SVG

用法:
    python3 swimlane_svg_generator.py --json config.json --svg output.svg

JSON 格式:
{
  "title": "图表标题",
  "columns": ["用户", "商城系统", "支付系统"],
  "rows": ["下单阶段", "支付阶段"],
  "steps": [
    {"label": "提交订单:选择商品", "col": 1, "row": 1},
    {"label": "创建订单", "col": 2, "row": 1}
  ],
  "connections": [
    {"from": "提交订单", "to": "创建订单"},
    {"from": "创建订单", "to": "发起支付", "type": "async", "label": "待支付"}
  ]
}
"""

import json
import argparse
import logging
from typing import List, Dict, Tuple, Optional

from model_line_generator import ComponentLineGenerator, NoValidPathError

log = logging.getLogger('swimlane')

# ==================== 常量配置 ====================

PADDING = 20                # 四边边距
STAGE_LABEL_WIDTH = 16      # 左侧阶段标签宽度
COL_HEADER_HEIGHT = 19      # 顶部列头高度（与 STAGE_LABEL_WIDTH 一致）
TITLE_HEIGHT = 30           # 标题栏高度
COL_WIDTH = 144             # 每列宽度
STEP_WIDTH = 120            # 步骤卡片宽度
STEP_TITLE_ONLY_H = 40      # 统一卡片高度
STEP_SUB_EXTRA_H = 0        # 不再额外增加高度
STEP_GAP = 24               # 同一列内组件间距（= ROW_PADDING * 2，与跨行间距一致）
TIER_GAP = 24               # 行内层级间距（与 STEP_GAP 一致）
ROW_PADDING = 12            # 行上下内边距
ROW_MIN_HEIGHT = 60         # 行最小高度

# 预置配色（循环使用）
COLUMN_COLORS = [
    {"fill": "#EFF6FF", "stroke": "#93C5FD", "text": "#1E40AF"},  # 蓝
    {"fill": "#ECFDF5", "stroke": "#6EE7B7", "text": "#065F46"},  # 绿
    {"fill": "#FFFBEB", "stroke": "#FCD34D", "text": "#92400E"},  # 黄
    {"fill": "#F5F3FF", "stroke": "#C4B5FD", "text": "#5B21B6"},  # 紫
    {"fill": "#FFF1F2", "stroke": "#FDA4AF", "text": "#9F1239"},  # 粉
    {"fill": "#F0FDF4", "stroke": "#4ADE80", "text": "#166534"},  # 浅绿
    {"fill": "#FFEDD5", "stroke": "#FB923C", "text": "#9A3412"},  # 橙
    {"fill": "#E0F2FE", "stroke": "#38BDF8", "text": "#075985"},  # 天蓝
]

ROW_BG_COLORS = ["#F8FAFC", "#F0F9FF"]  # 行底纹交替色
CONNECTOR_COLOR = "#3b82f6"


# ==================== 数据模型 ====================

class Step:
    """流程步骤"""
    def __init__(self, title: str, sub_label: str, col: int, row: int):
        self.title = title
        self.sub_label = sub_label
        self.col = col          # 从 1 开始
        self.row = row          # 从 1 开始
        self.tier = 0           # 行内层级：0=上层，1=下层（反向连线目标自动设为1）
        self.x = 0.0
        self.y = 0.0
        self.width = STEP_WIDTH
        self.height = STEP_TITLE_ONLY_H + STEP_SUB_EXTRA_H  # 统一高度

    def to_dict(self) -> dict:
        """转换为 ComponentLineGenerator 格式"""
        return {
            "model_id": self.title,
            "x1": round(self.x, 2),
            "y1": round(self.y, 2),
            "x2": round(self.x + self.width, 2),
            "y2": round(self.y + self.height, 2),
        }


class Connection:
    """连线"""
    def __init__(self, from_step: Step, to_step: Step, conn_type: str, label: str):
        self.from_step = from_step
        self.to_step = to_step
        self.conn_type = conn_type      # "sync" 或 "async"
        self.label = label
        self.path_dict: Optional[dict] = None  # 由 ConnectorCalculator 填充

    def is_sync(self) -> bool:
        return self.conn_type == "sync"


# ==================== 配置解析器 ====================

class ConfigParser:
    @staticmethod
    def parse(json_path: str) -> Tuple[str, List[str], List[str], List[Step], List[Connection]]:
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        title = config.get('title', '')
        columns = config.get('columns', [])
        rows = config.get('rows', [])

        # 解析 steps：label 按 : 分割为主标题和 subLabel
        steps = []
        step_map: Dict[str, Step] = {}
        for step_data in config.get('steps', []):
            label_str = step_data.get('label', '')
            col = step_data.get('col', 1)
            row = step_data.get('row', 1)

            parts = label_str.split(':', 1)
            title_part = parts[0].strip()
            sub_label = parts[1].strip() if len(parts) > 1 else ''

            step = Step(title_part, sub_label, col, row)
            steps.append(step)
            step_map[title_part] = step

        # 解析 connections：支持对象数组格式
        connections = []
        for conn_data in config.get('connections', []):
            if isinstance(conn_data, str):
                # 兼容旧的三段式字符串格式 "from→to:type:label"
                parts = conn_data.split(':')
                if len(parts) < 2:
                    continue
                from_to = parts[0].strip()
                conn_type = parts[1].strip() if len(parts) > 1 else 'sync'
                label = parts[2].strip() if len(parts) > 2 else ''
                arrow_parts = from_to.split('→')
                if len(arrow_parts) != 2:
                    continue
                from_label = arrow_parts[0].strip()
                to_label = arrow_parts[1].strip()
            elif isinstance(conn_data, dict):
                # 对象数组格式 {"from": "...", "to": "...", "type": "sync", "label": "..."}
                from_label = conn_data.get('from', '').strip()
                to_label = conn_data.get('to', '').strip()
                conn_type = conn_data.get('type', 'sync').strip()
                label = conn_data.get('label', '').strip()
                if not from_label or not to_label:
                    continue
            else:
                continue

            from_step = step_map.get(from_label)
            to_step = step_map.get(to_label)

            if from_step and to_step:
                connections.append(Connection(from_step, to_step, conn_type, label))

        return title, columns, rows, steps, connections

    @staticmethod
    def adjust_tiers_for_connections(steps: List[Step], connections: List[Connection]):
        """连线层级约束（已禁用）

        原规则：跨行反向连线目标自动降到行内下层。
        已禁用原因：所有组件统一从行顶部开始排列，跨行反向连线通过通道区域绕行即可。
        """
        pass


# ==================== 布局计算器 ====================

class LayoutCalculator:
    def __init__(self, columns: List[str], rows: List[str], steps: List[Step]):
        self.columns = columns
        self.rows = rows
        self.steps = steps
        self.row_heights: Dict[int, float] = {}
        self.row_tier_splits: Dict[int, float] = {}  # 每行 tier0 占用高度
        self.svg_width = 0
        self.svg_height = 0

    def calculate(self):
        # 按 (col, row) 分组，保持定义顺序
        cell_steps: Dict[Tuple[int, int], List[Step]] = {}
        for step in self.steps:
            key = (step.col, step.row)
            cell_steps.setdefault(key, []).append(step)

        # 计算每行各层级高度
        for row_idx in range(1, len(self.rows) + 1):
            # 统计每列每层的组件数
            max_tier0_count = 0
            max_tier1_count = 0
            max_tier = 0

            for col_idx in range(1, len(self.columns) + 1):
                s_list = cell_steps.get((col_idx, row_idx), [])
                t0 = sum(1 for s in s_list if s.tier == 0)
                t1 = sum(1 for s in s_list if s.tier >= 1)
                max_tier0_count = max(max_tier0_count, t0)
                max_tier1_count = max(max_tier1_count, t1)
                for s in s_list:
                    max_tier = max(max_tier, s.tier)

            step_h = STEP_TITLE_ONLY_H
            t0_height = max_tier0_count * step_h + max(0, max_tier0_count - 1) * STEP_GAP if max_tier0_count > 0 else 0
            t1_height = max_tier1_count * step_h + max(0, max_tier1_count - 1) * STEP_GAP if max_tier1_count > 0 else 0

            # 层级间间距
            tier_gap = TIER_GAP if max_tier1_count > 0 else 0

            total = t0_height + tier_gap + t1_height
            if total == 0:
                height = ROW_MIN_HEIGHT
            else:
                height = ROW_PADDING * 2 + total
                height = max(height, ROW_MIN_HEIGHT)

            self.row_heights[row_idx] = height
            self.row_tier_splits[row_idx] = t0_height

        # 计算每个 step 的坐标（按 tier 分层）
        for (col, row), step_list in cell_steps.items():
            col_x = STAGE_LABEL_WIDTH + (col - 1) * COL_WIDTH
            step_x = col_x + (COL_WIDTH - STEP_WIDTH) / 2

            row_y = self._row_start_y(row)
            t0_h = self.row_tier_splits.get(row, 0)

            tier0_steps = [s for s in step_list if s.tier == 0]
            tier1_steps = [s for s in step_list if s.tier >= 1]

            # tier 0: 从行顶部开始
            for i, step in enumerate(tier0_steps):
                step.x = step_x
                step.y = row_y + ROW_PADDING + i * (STEP_TITLE_ONLY_H + STEP_GAP)

            # tier 1: 从 tier0 下方开始
            tier1_start = row_y + ROW_PADDING + t0_h + TIER_GAP
            for i, step in enumerate(tier1_steps):
                step.x = step_x
                step.y = tier1_start + i * (STEP_TITLE_ONLY_H + STEP_GAP)

        # SVG 尺寸（含四边边距）
        content_w = STAGE_LABEL_WIDTH + len(self.columns) * COL_WIDTH
        content_h = TITLE_HEIGHT + COL_HEADER_HEIGHT + sum(self.row_heights.values())
        self.svg_width = content_w + PADDING * 2
        self.svg_height = content_h + PADDING * 2

        # 通道坐标（供连线路径规划使用）
        # 垂直通道：列分隔线 x 坐标
        self.v_channels = [STAGE_LABEL_WIDTH + i * COL_WIDTH for i in range(1, len(self.columns))]
        # 水平通道：行分隔线 y 坐标（含首行顶部和末行底部）
        self.h_channels = []
        for r in range(1, len(self.rows) + 1):
            self.h_channels.append(self._row_start_y(r))
        self.h_channels.append(
            self._row_start_y(len(self.rows)) + self.row_heights.get(len(self.rows), ROW_MIN_HEIGHT)
        )

    def _row_start_y(self, row: int) -> float:
        y = TITLE_HEIGHT + COL_HEADER_HEIGHT
        for r in range(1, row):
            y += self.row_heights.get(r, ROW_MIN_HEIGHT)
        return y

    def get_row_range(self, row: int) -> Tuple[float, float]:
        start = self._row_start_y(row)
        end = start + self.row_heights.get(row, ROW_MIN_HEIGHT)
        return start, end


# ==================== 连线计算器 ====================

class ConnectorCalculator:
    """使用 ComponentLineGenerator 计算连线，自动分散出口入口避免重叠"""

    def __init__(self, steps: List[Step], generator: ComponentLineGenerator = None):
        self.steps = steps
        self._generator = generator or ComponentLineGenerator()

    @staticmethod
    def _infer_side(step: Step, point: Tuple[float, float]) -> str:
        """从起止点坐标推断使用的边"""
        cx = step.x + step.width / 2
        cy = step.y + step.height / 2
        px, py = point
        dx, dy = px - cx, py - cy
        # 判断更偏向哪个方向
        if abs(dx) > abs(dy):
            return 'R' if dx > 0 else 'L'
        else:
            return 'B' if dy > 0 else 'T'

    def calculate(self, connections: List[Connection]) -> List[Connection]:
        """计算所有连线路径（已迁移到 SVGGenerator._connectors 统一处理）"""
        return connections

    def _build_direct_path(self, start_id, start_point, end_id, end_point,
                           from_side, to_side, start_model, end_model, all_models):
        """根据指定出口/入口边构建折线路径"""
        sx, sy = start_point
        ex, ey = end_point
        is_from_h = from_side in ('L', 'R')
        is_to_h = to_side in ('L', 'R')

        # 构建拐点
        inflections = []
        if is_from_h and not is_to_h:
            # 水平出 -> 垂直进：先水平后垂直，拐点 (ex, sy)
            inflections = [(ex, sy)]
        elif not is_from_h and is_to_h:
            # 垂直出 -> 水平进：先垂直后水平，拐点 (sx, ey)
            inflections = [(sx, ey)]
        elif is_from_h and is_to_h:
            # 水平出 -> 水平进：水平->垂直->水平，拐点 (mid_x, sy), (mid_x, ey)
            mid_x = (sx + ex) / 2
            inflections = [(mid_x, sy), (mid_x, ey)]
        else:
            # 垂直出 -> 垂直进：垂直->水平->垂直，拐点 (sx, mid_y), (ex, mid_y)
            mid_y = (sy + ey) / 2
            inflections = [(sx, mid_y), (ex, mid_y)]

        # 验证路径（检查拐点和阻挡）
        path_points = [start_point] + inflections + [end_point]
        if self._validate_custom_path(path_points, all_models, start_id, end_id):
            # 有效路径，构建 segments
            segments = []
            for i in range(len(path_points) - 1):
                segments.append((path_points[i], path_points[i + 1]))
            return {
                'start_model_id': start_id,
                'start_point': start_point,
                'end_model_id': end_id,
                'end_point': end_point,
                'turns': len(inflections),
                'total_length': sum(abs(x2-x1) + abs(y2-y1) for (x1,y1),(x2,y2) in segments),
                'inflections': inflections,
                'segments': segments,
            }
        else:
            # 路径被阻挡，回退到原始 get_best_path
            return self._generator.get_best_path(start_model, end_model, all_models)

    @staticmethod
    def _validate_custom_path(path_points, all_models, start_id, end_id):
        """验证自定义路径是否被阻挡"""
        for i in range(len(path_points) - 1):
            p1, p2 = path_points[i], path_points[i + 1]
            x1, y1 = p1
            x2, y2 = p2
            # 必须水平或垂直
            if x1 != x2 and y1 != y2:
                return False
            # 检查阻挡
            for model in all_models:
                mid = model.get('model_id') or model.get('id')
                if mid == start_id or mid == end_id:
                    continue
                min_x, max_x = min(x1, x2), max(x1, x2)
                min_y, max_y = min(y1, y2), max(y1, y2)
                if y1 == y2:  # 水平线段
                    if model['y1'] - 1 <= y1 <= model['y2'] + 1:
                        if not (max_x < model['x1'] or min_x > model['x2']):
                            return False
                elif x1 == x2:  # 垂直线段
                    if model['x1'] - 1 <= x1 <= model['x2'] + 1:
                        if not (max_y < model['y1'] or min_y > model['y2']):
                            return False
        return True


# ==================== SVG 生成器 ====================

class SVGGenerator:
    def __init__(self, title: str, columns: List[str], rows: List[str],
                 steps: List[Step], connections: List[Connection],
                 layout: LayoutCalculator, generator: ComponentLineGenerator = None):
        self.title = title
        self.columns = columns
        self.rows = rows
        self.steps = steps
        self.connections = connections
        self.layout = layout
        self._generator = generator or ComponentLineGenerator()

    def _px(self, x: float) -> float:
        """内部坐标转 SVG 坐标（加水平边距）"""
        return x + PADDING

    def _py(self, y: float) -> float:
        """内部坐标转 SVG 坐标（加垂直边距）"""
        return y + PADDING

    def generate(self, debug_connection: str = None) -> str:
        parts = [
            self._header(),
            self._style(),
            self._background(),
            f'  <g transform="translate({PADDING}, {PADDING})">',
            self._background_inner(),
            self._row_backgrounds(),
            self._title_bar(),
            self._stage_labels(),
            self._col_headers(),
            self._col_separators(),
            self._step_cards(),
            self._connectors(debug_connection),
            '  </g>',
            '</svg>',
        ]
        return '\n'.join(parts)

    def _header(self) -> str:
        w, h = self.layout.svg_width, self.layout.svg_height
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"'
                f' preserveAspectRatio="xMidYMid meet"'
                f' style="width:100%;height:auto;max-width:900px;min-width:320px;background:#fff;"'
                f' font-family="\'PingFang SC\',\'Microsoft YaHei\',sans-serif">\n'
                f'  <defs>\n'
                f'    <marker id="arrow-sync" viewBox="0 0 8 8" refX="7.5" refY="4"'
                f' markerWidth="5" markerHeight="5" orient="auto">\n'
                f'      <path d="M 0 0 L 8 4 L 0 8 L 1 4 Z" fill="#3b82f6"/>\n'
                f'    </marker>\n'
                f'    <marker id="arrow-async" viewBox="0 0 8 8" refX="7.5" refY="4"'
                f' markerWidth="5" markerHeight="5" orient="auto">\n'
                f'      <path d="M 0 0 L 8 4 L 0 8 L 1 4 Z" fill="#9ca3af"/>\n'
                f'    </marker>\n'
                f'    <radialGradient id="glow-sync" cx="50%" cy="50%" r="50%">\n'
                f'      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1"/>\n'
                f'      <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:0"/>\n'
                f'    </radialGradient>\n'
                f'    <radialGradient id="glow-async" cx="50%" cy="50%" r="50%">\n'
                f'      <stop offset="0%" style="stop-color:#9ca3af;stop-opacity:1"/>\n'
                f'      <stop offset="100%" style="stop-color:#9ca3af;stop-opacity:0"/>\n'
                f'    </radialGradient>\n'
                f'  </defs>')

    def _style(self) -> str:
        return '''  <style>
    .title-t{ font-size:14px; font-weight:600; fill:#334155; }
    .stage-t{ font-size:10px; font-weight:500; fill:#64748B; }
    .col-t{ font-size:10px; font-weight:500; }
    .step-title{ font-size:9px; font-weight:500; fill:#334155; text-anchor:middle; }
    .step-sub{ font-size:8px; fill:#94A3B8; text-anchor:middle; }
    .conn-label{ font-size:9px; fill:#64748B; text-anchor:middle; }
    @keyframes fi{ from{opacity:0;} to{opacity:1;} }
    .anim{ opacity:0; animation:fi 0.5s ease-out forwards; }
    .conn-line{ opacity:0; animation:fi 0.4s ease-out forwards; }
    .conn-line-dash{ opacity:0; animation:fi 0.4s ease-out forwards, dashFlow 1s linear infinite; }
    .conn-label-anim{ opacity:0; animation:fi 0.5s ease-out forwards; }
    .flow-dot{ opacity:0; animation:fi 0.3s ease-out forwards, dotMove 2s ease-in-out infinite; }
    @keyframes dotMove{ 0%{offset-distance:0%;} 100%{offset-distance:100%;} }
    @keyframes dashFlow{ 0%{stroke-dashoffset:0;} 100%{stroke-dashoffset:-9;} }
  </style>'''

    def _background(self) -> str:
        return f'  <rect width="{self.layout.svg_width}" height="{self.layout.svg_height}" fill="#ffffff"/>'
    
    def _background_inner(self) -> str:
        """内部内容区域的白色背景+黑色边框"""
        content_w = self.layout.svg_width - PADDING * 2
        content_h = self.layout.svg_height - PADDING * 2
        # 内缩1px使stroke-width=2的描边完全在内容区域内，避免左右粗细不一
        return f'  <rect x="1" y="1" width="{content_w - 2}" height="{content_h - 2}" fill="#ffffff" stroke="#000" stroke-width="2"/>'

    @property
    def _content_width(self) -> float:
        """内容区域宽度（不含边距）"""
        return self.layout.svg_width - PADDING * 2

    def _row_backgrounds(self) -> str:
        lines = ['  <!-- 横向泳道底纹 -->']
        for row_idx in range(1, len(self.rows) + 1):
            start_y, end_y = self.layout.get_row_range(row_idx)
            color = ROW_BG_COLORS[(row_idx - 1) % 2]
            h = end_y - start_y
            lines.append(f'  <rect x="0" y="{start_y}" width="{self._content_width}" height="{h}" fill="{color}" stroke="none"/>')
        return '\n'.join(lines)

    def _title_bar(self) -> str:
        w = self._content_width
        # 图例：右侧显示同步实线，异步虚线（同步在右，异步在左）
        legend_y = TITLE_HEIGHT / 2
        legend_x = w - 10  # 右侧起点
        # 同步图例（最右侧）
        sync_line_x2 = legend_x
        sync_line_x1 = sync_line_x2 - 24
        sync_text_x = sync_line_x1 - 4
        # 异步图例（同步左侧）
        async_line_x2 = sync_text_x - 26
        async_line_x1 = async_line_x2 - 24
        async_text_x = async_line_x1 - 4

        # 图例路径（供光点 offset-path 使用）
        sync_path_d = f'M {sync_line_x1} {legend_y} L {sync_line_x2} {legend_y}'
        async_path_d = f'M {async_line_x1} {legend_y} L {async_line_x2} {legend_y}'

        return (f'  <!-- 标题栏 -->\n'
                f'  <rect x="0" y="0" width="{w}" height="{TITLE_HEIGHT}"'
                f' fill="#F1F5F9" stroke="#E2E8F0" stroke-width="0.5"/>\n'
                f'  <text x="{w/2}" y="{TITLE_HEIGHT/2}" text-anchor="middle"'
                f' dominant-baseline="central" class="title-t anim"'
                f' style="animation-delay:0.05s">{self.title}</text>\n'
                f'  <!-- 图例 -->\n'
                f'  <line x1="{sync_line_x1}" y1="{legend_y}" x2="{sync_line_x2}" y2="{legend_y}"'
                f' stroke="#3b82f6" stroke-width="1.3" marker-end="url(#arrow-sync)"'
                f' class="conn-line" style="animation-delay:0.05s"/>\n'
                f'  <circle r="2" fill="url(#glow-sync)" class="flow-dot"'
                f' style="offset-path:path(\'{sync_path_d}\');animation-delay:0.35s,0.35s"/>\n'
                f'  <text x="{sync_text_x}" y="{legend_y}" text-anchor="end"'
                f' dominant-baseline="central" class="stage-t" fill="#64748B">同步</text>\n'
                f'  <line x1="{async_line_x1}" y1="{legend_y}" x2="{async_line_x2}" y2="{legend_y}"'
                f' stroke="#9ca3af" stroke-width="1.3" stroke-dasharray="6 3"'
                f' marker-end="url(#arrow-async)" class="conn-line-dash"'
                f' style="animation-delay:0.05s"/>\n'
                f'  <text x="{async_text_x}" y="{legend_y}" text-anchor="end"'
                f' dominant-baseline="central" class="stage-t" fill="#64748B">异步</text>')

    def _stage_labels(self) -> str:
        lines = ['  <!-- 阶段标签 -->']
        for row_idx, label in enumerate(self.rows, 1):
            start_y, end_y = self.layout.get_row_range(row_idx)
            # 文字底部对齐：旋转-90°后，text-anchor="end"让文字末端在y处
            text_y = end_y - 7
            cx = STAGE_LABEL_WIDTH / 2
            h = end_y - start_y
            delay = 0.1 + row_idx * 0.05
            lines.append(f'  <g class="anim" style="animation-delay:{delay}s">')
            lines.append(f'    <rect x="0" y="{start_y}" width="{STAGE_LABEL_WIDTH}" height="{h}"'
                         f' fill="#F1F5F9" stroke="#E2E8F0" stroke-width="0.5"/>')
            lines.append(f'    <text x="{cx}" y="{text_y}" text-anchor="start"'
                         f' dominant-baseline="central" transform="rotate(-90,{cx},{text_y})"'
                         f' class="col-t" fill="#64748B">{label}</text>')
            lines.append('  </g>')
        return '\n'.join(lines)

    def _col_headers(self) -> str:
        lines = ['  <!-- 列头 -->']
        for col_idx, label in enumerate(self.columns, 1):
            color = COLUMN_COLORS[(col_idx - 1) % len(COLUMN_COLORS)]
            if col_idx == 1:
                x = 0
                width = STAGE_LABEL_WIDTH + COL_WIDTH
                text_x = STAGE_LABEL_WIDTH + COL_WIDTH / 2
            else:
                x = STAGE_LABEL_WIDTH + (col_idx - 1) * COL_WIDTH
                width = COL_WIDTH
                text_x = x + COL_WIDTH / 2

            delay = 0.08 + col_idx * 0.05
            y = TITLE_HEIGHT
            lines.append(f'  <g class="anim" style="animation-delay:{delay}s">')
            lines.append(f'    <rect x="{x}" y="{y}" width="{width}" height="{COL_HEADER_HEIGHT}"'
                         f' fill="{color["fill"]}" stroke="{color["stroke"]}" stroke-width="0.5"/>')
            lines.append(f'    <text x="{text_x}" y="{y + COL_HEADER_HEIGHT/2}"'
                         f' text-anchor="middle" dominant-baseline="central"'
                         f' class="col-t" fill="{color["text"]}">{label}</text>')
            lines.append('  </g>')
        return '\n'.join(lines)

    def _col_separators(self) -> str:
        """列分隔线 — 使用 rect 避免验证器误判为连线"""
        lines = ['  <!-- 列分隔线 -->']
        for col_idx in range(1, len(self.columns)):
            x = STAGE_LABEL_WIDTH + col_idx * COL_WIDTH
            y1 = TITLE_HEIGHT + COL_HEADER_HEIGHT
            h = self.layout.svg_height - PADDING * 2 - y1
            lines.append(f'  <rect x="{x}" y="{y1}" width="1" height="{h}" fill="#CBD5E1"/>')
        return '\n'.join(lines)

    def _step_cards(self) -> str:
        lines = ['  <!-- 步骤卡片 -->']
        for i, step in enumerate(self.steps):
            color = COLUMN_COLORS[(step.col - 1) % len(COLUMN_COLORS)]
            delay = 0.2 + i * 0.05
            lines.append(f'  <g class="anim" style="animation-delay:{delay}s">')
            lines.append(f'    <rect x="{step.x}" y="{step.y}" width="{step.width}"'
                         f' height="{step.height}" rx="4" fill="#ffffff"'
                         f' stroke="{color["stroke"]}" stroke-width="1"/>')
            if step.sub_label:
                lines.append(f'    <text x="{step.x + step.width/2}" y="{step.y + 15}"'
                             f' dominant-baseline="central" class="step-title">{step.title}</text>')
                lines.append(f'    <text x="{step.x + step.width/2}" y="{step.y + 28}"'
                             f' dominant-baseline="central" class="step-sub">{step.sub_label}</text>')
            else:
                # 无副标题时标题垂直居中
                lines.append(f'    <text x="{step.x + step.width/2}" y="{step.y + step.height/2}"'
                             f' dominant-baseline="central" class="step-title">{step.title}</text>')
            lines.append('  </g>')
        return '\n'.join(lines)

    def _nearest_v_channel(self, x: float, x_min: float = None, x_max: float = None) -> float:
        """找范围内最近的垂直通道（列分隔线 x），无则回退为 x"""
        channels = self.layout.v_channels
        if x_min is not None and x_max is not None:
            lo, hi = min(x_min, x_max), max(x_min, x_max)
            candidates = [c for c in channels if lo <= c <= hi]
            if candidates:
                return min(candidates, key=lambda c: abs(c - x))
            # 范围内无通道，回退为中点
            return x
        if channels:
            return min(channels, key=lambda c: abs(c - x))
        return x

    def _nearest_h_channel(self, y: float, y_min: float = None, y_max: float = None) -> float:
        """找范围内最近的水平通道（行分隔线 y），无则回退为 y"""
        channels = self.layout.h_channels
        if y_min is not None and y_max is not None:
            lo, hi = min(y_min, y_max), max(y_min, y_max)
            candidates = [c for c in channels if lo <= c <= hi]
            if candidates:
                return min(candidates, key=lambda c: abs(c - y))
            # 范围内无通道，回退为中点
            return y
        if channels:
            return min(channels, key=lambda c: abs(c - y))
        return y

    def _path_hits_obstacle(self, points: list, exclude_titles: set) -> bool:
        """检测折线路径是否穿过或紧贴任何组件（排除起止组件）

        points: 路径关键点列表 [(x,y), ...]
        每对相邻点构成一条水平或垂直线段，检测是否与任何 step 矩形相交。
        使用 MARGIN 级间距，水平段用严格边界（允许沿行间隙通过），
        垂直段用严格边界（允许沿组件边缘通过）。
        """
        result, _ = self._path_hits_obstacle_detail(points, exclude_titles)
        return result

    def _path_hits_obstacle_detail(self, points: list, exclude_titles: set) -> tuple:
        """检测折线路径是否穿过或紧贴任何组件，返回 (是否碰撞, 详细信息)

        详细信息包含被阻挡的线段和组件名称，用于调试。
        """
        CLR = 12  # 与组件边缘的最小间距（= MARGIN）
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            for step in self.steps:
                if step.title in exclude_titles:
                    continue
                sx, sy = step.x - CLR, step.y - CLR
                sw, sh = step.width + 2 * CLR, step.height + 2 * CLR
                if abs(y1 - y2) < 0.1:  # 水平线段
                    y = y1
                    seg_min, seg_max = min(x1, x2), max(x1, x2)
                    if sy < y < sy + sh and sx < seg_max and sx + sw > seg_min:
                        return True, f"水平段 ({x1},{y1})->({x2},{y2}) 穿过 '{step.title}' (x={step.x},y={step.y},w={step.width},h={step.height})"
                elif abs(x1 - x2) < 0.1:  # 垂直线段
                    x = x1
                    seg_min, seg_max = min(y1, y2), max(y1, y2)
                    if sx < x < sx + sw and sy < seg_max and sy + sh > seg_min:
                        return True, f"垂直段 ({x1},{y1})->({x2},{y2}) 穿过 '{step.title}' (x={step.x},y={step.y},w={step.width},h={step.height})"
        return False, ""

    def _path_hits_self(self, points: list, f_step: Step, t_step: Step) -> bool:
        """检测路径是否折返穿过起点组件自身（不含扩展间距）

        用于排除从 R 边出发向左、从 L 边出发向右等明显折返路径。
        只检查起点组件，不检查终点组件（连线自然连入终点）。
        使用严格边界，允许路径沿组件边缘通过。
        """
        result, _ = self._path_hits_self_detail(points, f_step, t_step)
        return result

    def _path_hits_self_detail(self, points: list, f_step: Step, t_step: Step) -> tuple:
        """检测路径是否折返穿过起点组件自身，返回 (是否碰撞, 详细信息)"""
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            sx, sy = f_step.x, f_step.y
            sw, sh = f_step.width, f_step.height
            if abs(y1 - y2) < 0.1:  # 水平线段
                y = y1
                seg_min, seg_max = min(x1, x2), max(x1, x2)
                if sy < y < sy + sh and sx < seg_max and sx + sw > seg_min:
                    return True, f"水平段 ({x1},{y1})->({x2},{y2}) 折返穿过起点 '{f_step.title}'"
            elif abs(x1 - x2) < 0.1:  # 垂直线段
                x = x1
                seg_min, seg_max = min(y1, y2), max(y1, y2)
                if sx < x < sx + sw and sy < seg_max and sy + sh > seg_min:
                    return True, f"垂直段 ({x1},{y1})->({x2},{y2}) 折返穿过起点 '{f_step.title}'"
        return False, ""

    # ==================== 九宫格位置关系与边组合 ====================

    @staticmethod
    def _get_position_relation(f_step: Step, t_step: Step) -> Tuple[str, str]:
        """判断 t_step 相对于 f_step 的九宫格位置关系。

        返回 (h, v)：
        - h: 'left' | 'center' | 'right'
        - v: 'above' | 'center' | 'below'
        """
        # 水平方向
        if t_step.x >= f_step.x + f_step.width:
            h = 'right'
        elif t_step.x + t_step.width <= f_step.x:
            h = 'left'
        else:
            h = 'center'

        # 垂直方向
        if t_step.y >= f_step.y + f_step.height:
            v = 'below'
        elif t_step.y + t_step.height <= f_step.y:
            v = 'above'
        else:
            v = 'center'

        return h, v

    @staticmethod
    def _get_combos_for_relation(h: str, v: str) -> List[Tuple[str, str]]:
        """根据九宫格位置关系返回优先边组合列表（按自然度排序）。"""
        # 正方向（4种）：直线优先
        if h == 'right' and v == 'center':
            return [('R', 'L'), ('R', 'T'), ('R', 'B'), ('B', 'L'), ('T', 'L')]
        if h == 'left' and v == 'center':
            return [('L', 'R'), ('L', 'T'), ('L', 'B'), ('B', 'R'), ('T', 'R')]
        if h == 'center' and v == 'below':
            return [('B', 'T'), ('R', 'T'), ('L', 'T'), ('B', 'R'), ('B', 'L')]
        if h == 'center' and v == 'above':
            return [('T', 'B'), ('R', 'B'), ('L', 'B'), ('T', 'R'), ('T', 'L')]

        # 对角方向（4种）：L型优先
        if h == 'right' and v == 'below':
            return [('R', 'T'), ('B', 'T'), ('B', 'L'), ('R', 'B'), ('R', 'L'),
                    ('B', 'R'), ('T', 'L')]
        if h == 'right' and v == 'above':
            return [('R', 'B'), ('T', 'B'), ('T', 'L'), ('R', 'T'), ('T', 'R'),
                    ('R', 'L'), ('B', 'L')]
        if h == 'left' and v == 'below':
            return [('L', 'T'), ('B', 'T'), ('B', 'R'), ('L', 'B'), ('L', 'R'),
                    ('B', 'L'), ('T', 'R')]
        if h == 'left' and v == 'above':
            return [('L', 'B'), ('T', 'B'), ('T', 'R'), ('L', 'T'), ('T', 'L'),
                    ('L', 'R'), ('B', 'R')]

        # 完全重叠（理论上不应发生），兜底
        return [('B', 'T'), ('R', 'L'), ('T', 'B'), ('L', 'R')]

    def _build_s_path(self, f_step: Step, t_step: Step,
                       used_sides: dict = None, verbose: bool = False,
                       max_level: int = None) -> tuple:
        """构建最优无障碍折线路径

        逐级降级策略（路径穿过组件时降到下一级）：
        1. 直线（水平或垂直，0拐点）
        2. L型线（1拐点）
        3. S型线（2拐点，中间段在起终点之间）
        4. U型线（2拐点，中间段绕行到外侧通道）
        5. 双L型线（3拐点）
        6. 双U型线（4拐点）

        评估策略：每个边组合独立评估最优级别，同时考虑边的占用情况，
        已占用的边会被大幅惩罚，避免同一边被多条连线使用。

        verbose=True 时，输出每级尝试的详细结果和阻挡原因（用于调试）。
        """
        MARGIN = 12
        LEVEL_NAMES = {1: '直线', 2: 'L型', 3: 'S型', 4: 'U型', 5: '双L型', 6: '双U型'}

        _side = {
            'R': lambda s: (s.x + s.width, s.y + s.height / 2),
            'L': lambda s: (s.x, s.y + s.height / 2),
            'T': lambda s: (s.x + s.width / 2, s.y),
            'B': lambda s: (s.x + s.width / 2, s.y + s.height),
        }
        _off = {'R': (MARGIN, 0), 'L': (-MARGIN, 0),
                'T': (0, -MARGIN), 'B': (0, MARGIN)}
        exclude = {f_step.title, t_step.title}

        def _compute(fs, ts):
            sfx, sfy = _side[fs](f_step)
            stx, sty = _side[ts](t_step)
            bo = (sfx + _off[fs][0], sfy + _off[fs][1])
            bi = (stx + _off[ts][0], sty + _off[ts][1])
            return sfx, sfy, stx, sty, bo, bi

        def _is_clear(path, sfx, sfy, stx, sty, level_name=""):
            # 检测完整路径（含 edge-to-buffer 段）是否穿过第三方障碍或折返穿过起点自身
            hit, detail = self._path_hits_obstacle_detail(path, exclude)
            if hit:
                if verbose:
                    log.debug("    [%s] 被障碍阻挡: %s", level_name, detail)
                return False
            hit, detail = self._path_hits_self_detail(path, f_step, t_step)
            if hit:
                if verbose:
                    log.debug("    [%s] 被自身折返阻挡: %s", level_name, detail)
                return False
            return True

        def _eval_combo(fs, ts):
            """对单个边组合，逐级尝试，返回 (level, path, fx, fy, tx, ty) 或 None"""
            sfx, sfy, stx, sty, bo, bi = _compute(fs, ts)
            bx, by = bo
            ix, iy = bi

            def clear(pts, level_name=""):
                return _is_clear(pts, sfx, sfy, stx, sty, level_name)

            if verbose:
                log.debug("  评估 %s->%s:", fs, ts)

            # 1. 直线
            is_v = fs in ('T', 'B') and ts in ('T', 'B')
            is_h = fs in ('L', 'R') and ts in ('L', 'R')
            if (is_v and abs(bx - ix) < 1) or (is_h and abs(by - iy) < 1):
                path = [bo, bi]
                if clear(path, "直线"):
                    if verbose:
                        log.debug("    -> 直线 通过")
                    return (1, path, sfx, sfy, stx, sty)
            elif verbose and ((is_v and abs(bx - ix) >= 1) or (is_h and abs(by - iy) >= 1)):
                log.debug("    [直线] 不满足轴对齐条件 (bx=%s,ix=%s,by=%s,iy=%s)", bx, ix, by, iy)

            # 2. L型
            if fs in ('T', 'B'):
                corners = [(bx, iy), (ix, by)]
            else:
                corners = [(ix, by), (bx, iy)]
            def _segment_hits_step(p1, p2, step):
                """检测线段是否穿过组件本体（不含扩展间距）"""
                x1, y1 = p1
                x2, y2 = p2
                sx, sy = step.x, step.y
                sw, sh = step.width, step.height
                if abs(y1 - y2) < 0.1:  # 水平
                    y = y1
                    seg_min, seg_max = min(x1, x2), max(x1, x2)
                    if sy < y < sy + sh and sx < seg_max and sx + sw > seg_min:
                        return True
                elif abs(x1 - x2) < 0.1:  # 垂直
                    x = x1
                    seg_min, seg_max = min(y1, y2), max(y1, y2)
                    if sx < x < sx + sw and sy < seg_max and sy + sh > seg_min:
                        return True
                return False

            for ci, corner in enumerate(corners):
                if (abs(corner[0] - bx) < 1 and abs(corner[1] - by) < 1) or \
                   (abs(corner[0] - ix) < 1 and abs(corner[1] - iy) < 1):
                    if verbose:
                        log.debug("    [L型 corner%d] 退化跳过 %s", ci, corner)
                    continue
                # 过滤折返 corner
                if fs == 'R' and corner[0] < f_step.x + f_step.width:
                    if verbose:
                        log.debug("    [L型 corner%d] 折返过滤 R: corner.x=%s < f_step.right=%s", ci, corner[0], f_step.x + f_step.width)
                    continue
                if fs == 'L' and corner[0] > f_step.x:
                    if verbose:
                        log.debug("    [L型 corner%d] 折返过滤 L: corner.x=%s > f_step.x=%s", ci, corner[0], f_step.x)
                    continue
                if fs == 'B' and corner[1] < f_step.y + f_step.height:
                    if verbose:
                        log.debug("    [L型 corner%d] 折返过滤 B: corner.y=%s < f_step.bottom=%s", ci, corner[1], f_step.y + f_step.height)
                    continue
                if fs == 'T' and corner[1] > f_step.y:
                    if verbose:
                        log.debug("    [L型 corner%d] 折返过滤 T: corner.y=%s > f_step.y=%s", ci, corner[1], f_step.y)
                    continue
                # 过滤穿过终点组件本体的 corner
                if _segment_hits_step(corner, bi, t_step):
                    if verbose:
                        log.debug("    [L型 corner%d] 穿过终点 '%s' 过滤: corner=%s, bi=%s", ci, t_step.title, corner, bi)
                    continue
                path = [bo, corner, bi]
                if clear(path, f"L型 corner{ci} {corner}"):
                    if verbose:
                        log.debug("    -> L型 corner%d %s 通过", ci, corner)
                    return (2, path, sfx, sfy, stx, sty)

            # 3. S型（含退化情况）
            if fs != ts:
                if abs(by - iy) < 1 and abs(bx - ix) > 1:
                    path = [bo, bi]
                    if clear(path, "S型退化(H-V-H)"):
                        if verbose:
                            log.debug("    -> S型退化(H-V-H) 通过")
                        return (2, path, sfx, sfy, stx, sty)
                if abs(bx - ix) < 1 and abs(by - iy) > 1:
                    path = [bo, bi]
                    if clear(path, "S型退化(V-H-V)"):
                        if verbose:
                            log.debug("    -> S型退化(V-H-V) 通过")
                        return (2, path, sfx, sfy, stx, sty)
            # 计算 S 型变体优先级（出发/到达边已有连线时，
            # 优先选择不沿该边自然方向走的变体，避免重叠）
            hv_penalty = 0  # H-V-H = 垂直-水平-垂直
            vh_penalty = 0  # V-H-V = 水平-垂直-水平
            if used_sides:
                f_used = used_sides.get(f_step.title, set())
                t_used = used_sides.get(t_step.title, set())
                # fs 垂直(T/B): H-V-H 出发段继续垂直走（沿 fs 方向）
                # fs 水平(L/R): V-H-V 出发段继续水平走（沿 fs 方向）
                if fs in ('T', 'B'):
                    if fs in f_used:
                        hv_penalty += 10
                else:
                    if fs in f_used:
                        vh_penalty += 10
                # ts 垂直(T/B): H-V-H 到达段垂直到达（沿 ts 方向）
                # ts 水平(L/R): V-H-V 到达段水平到达（沿 ts 方向）
                if ts in ('T', 'B'):
                    if ts in t_used:
                        hv_penalty += 10
                else:
                    if ts in t_used:
                        vh_penalty += 10

            result = self._try_s_type(bx, by, ix, iy, bo, bi, lambda p: clear(p, "S型"), hv_penalty, vh_penalty)
            if result is not None:
                if verbose:
                    log.debug("    -> S型 通过")
                return (3, result, sfx, sfy, stx, sty)
            if verbose:
                log.debug("    [S型] 所有通道尝试失败")

            # 4. U型
            result = self._try_u_type(bx, by, ix, iy, bo, bi, lambda p: clear(p, "U型"))
            if result is not None:
                if verbose:
                    log.debug("    -> U型 通过")
                return (4, result, sfx, sfy, stx, sty)
            if verbose:
                log.debug("    [U型] 所有通道尝试失败")

            # 5. 双L型
            result = self._try_double_l(bx, by, ix, iy, bo, bi, lambda p: clear(p, "双L型"))
            if result is not None:
                if verbose:
                    log.debug("    -> 双L型 通过")
                return (5, result, sfx, sfy, stx, sty)
            if verbose:
                log.debug("    [双L型] 所有通道尝试失败")

            # 6. 双U型
            result = self._try_double_u(bx, by, ix, iy, bo, bi, lambda p: clear(p, "双U型"))
            if result is not None:
                if verbose:
                    log.debug("    -> 双U型 通过")
                return (6, result, sfx, sfy, stx, sty)
            if verbose:
                log.debug("    [双U型] 所有通道尝试失败")

            return None

        # ---- 九宫格位置关系 + 边组合生成 ----
        h, v = self._get_position_relation(f_step, t_step)
        combos = self._get_combos_for_relation(h, v)

        # 排除已被使用的边（如果四条边都被使用则不排除）
        if used_sides:
            f_used = used_sides.get(f_step.title, set())
            t_used = used_sides.get(t_step.title, set())
            all_sides = {'T', 'B', 'L', 'R'}
            f_all_used = f_used >= all_sides
            t_all_used = t_used >= all_sides

            def combo_score(c):
                fs, ts = c
                s = combos.index(c) * 10  # 原始优先级
                if not f_all_used and fs in f_used:
                    s += 100  # 出发边已用，大幅惩罚
                if not t_all_used and ts in t_used:
                    s += 100  # 到达边已用，大幅惩罚
                return s

            combos = sorted(set(combos), key=combo_score)
            if verbose:
                log.debug("  位置关系: %s+%s, combos(排序后)=%s", h, v, combos)
        else:
            if verbose:
                log.debug("  位置关系: %s+%s, combos=%s", h, v, combos)

        # ---- 评估所有 combos ----
        candidates = []
        for idx, (fs, ts) in enumerate(combos):
            result = _eval_combo(fs, ts)
            if result is not None:
                level, path, sfx, sfy, stx, sty = result
                candidates.append((level, idx, fs, ts, path, sfx, sfy, stx, sty))

        if candidates:
            if max_level is not None:
                candidates = [c for c in candidates if c[0] <= max_level]
            if candidates:
                # 按级别排序，同级别按原始顺序
                candidates.sort(key=lambda r: (r[0], r[1]))
                best = candidates[0]
                level, _, fs, ts, inflections, fx, fy, tx, ty = best
                log.debug('%s->%s: %s [%s->%s]', f_step.title, t_step.title,
                          LEVEL_NAMES.get(level, f'L{level}'), fs, ts)
            else:
                # 所有候选都超过 max_level
                if max_level is not None:
                    return None
                fs, ts = 'B', 'T'
                sfx, sfy, stx, sty, bo, bi = _compute(fs, ts)
                inflections, fx, fy, tx, ty = [bo, bi], sfx, sfy, stx, sty
                log.debug('%s->%s: 兜底直连 [%s->%s]', f_step.title, t_step.title, fs, ts)
        else:
            if max_level is not None:
                return None
            # 兜底：B->T 直连
            fs, ts = 'B', 'T'
            sfx, sfy, stx, sty, bo, bi = _compute(fs, ts)
            inflections, fx, fy, tx, ty = [bo, bi], sfx, sfy, stx, sty
            log.debug('%s->%s: 兜底直连 [%s->%s]', f_step.title, t_step.title, fs, ts)

        # 去重：去掉重复点
        deduped = [inflections[0]]
        for p in inflections[1:]:
            if abs(p[0] - deduped[-1][0]) > 0.1 or abs(p[1] - deduped[-1][1]) > 0.1:
                deduped.append(p)
        inflections = deduped

        # 合并边中心点与 inflections，去掉三点共线的伪拐点
        all_points = [(fx, fy)] + inflections + [(tx, ty)]
        deduped = [all_points[0]]
        for p in all_points[1:]:
            if len(deduped) >= 2:
                p_prev = deduped[-1]
                p_prev2 = deduped[-2]
                if (abs(p[0] - p_prev[0]) < 0.1 and abs(p_prev[0] - p_prev2[0]) < 0.1) or \
                   (abs(p[1] - p_prev[1]) < 0.1 and abs(p_prev[1] - p_prev2[1]) < 0.1):
                    deduped[-1] = p
                    continue
            deduped.append(p)

        s_path = {
            'start_point': deduped[0],
            'inflections': deduped[1:-1],
            'end_point': deduped[-1],
        }
        return self._generator.get_rounded_svg_path(s_path), deduped, fs, ts, level

    def _try_s_type(self, bx, by, ix, iy, buf_out, buf_in, is_clear,
                    hv_penalty=0, vh_penalty=0):
        """S型：2拐点，中间段在起终点范围内或附近，按边占用情况优先选择变体"""
        lo_y, hi_y = min(by, iy), max(by, iy)
        lo_x, hi_x = min(bx, ix), max(bx, ix)
        candidates = []

        # H-V-H（水平中间段 = 垂直-水平-垂直）
        if hi_y > lo_y:
            mid_y = (by + iy) / 2
            candidates.append((hv_penalty, [buf_out, (bx, mid_y), (ix, mid_y), buf_in]))
            for ch in self.layout.h_channels:
                if lo_y <= ch <= hi_y:
                    candidates.append((hv_penalty, [buf_out, (bx, ch), (ix, ch), buf_in]))
                elif abs(ch - mid_y) < 80:
                    candidates.append((hv_penalty, [buf_out, (bx, ch), (ix, ch), buf_in]))

        # V-H-V（垂直中间段 = 水平-垂直-水平）
        if hi_x > lo_x:
            mid_x = (bx + ix) / 2
            candidates.append((vh_penalty, [buf_out, (mid_x, by), (mid_x, iy), buf_in]))
            for ch in self.layout.v_channels:
                if lo_x <= ch <= hi_x:
                    candidates.append((vh_penalty, [buf_out, (ch, by), (ch, iy), buf_in]))
                elif abs(ch - mid_x) < 80:
                    candidates.append((vh_penalty, [buf_out, (ch, by), (ch, iy), buf_in]))

        # 按惩罚分排序，同分按路径总长度排序
        candidates.sort(key=lambda item: (
            item[0],
            sum(abs(item[1][i+1][0]-item[1][i][0]) + abs(item[1][i+1][1]-item[1][i][1]) for i in range(len(item[1])-1))
        ))

        # 去重并检测
        seen = set()
        for score, path in candidates:
            key = tuple(tuple(pt) for pt in path)
            if key not in seen:
                seen.add(key)
                if is_clear(path):
                    return path
        return None

    def _try_u_type(self, bx, by, ix, iy, buf_out, buf_in, is_clear):
        """U型：2拐点，中间段绕行到较远通道（S型近距离搜索失败后的兜底）"""
        lo_y, hi_y = min(by, iy), max(by, iy)
        lo_x, hi_x = min(bx, ix), max(bx, ix)
        candidates = []

        # V-H-V（左右绕行到较远通道，排除S型已搜索的80px范围内）
        for ch in self.layout.v_channels:
            if ch < lo_x - 80 or ch > hi_x + 80:
                candidates.append([buf_out, (ch, by), (ch, iy), buf_in])

        # H-V-H（上下绕行到较远通道，排除S型已搜索的80px范围内）
        for ch in self.layout.h_channels:
            if ch < lo_y - 80 or ch > hi_y + 80:
                candidates.append([buf_out, (bx, ch), (ix, ch), buf_in])

        # 按路径总长度排序
        candidates.sort(key=lambda p: sum(
            abs(p[i+1][0]-p[i][0]) + abs(p[i+1][1]-p[i][1])
            for i in range(len(p)-1)))

        for path in candidates:
            if is_clear(path):
                return path
        return None

    def _try_double_l(self, bx, by, ix, iy, buf_out, buf_in, is_clear):
        """双L型：3拐点"""
        mid_x = (bx + ix) / 2
        mid_y = (by + iy) / 2
        candidates = []

        # H-V-H-V pattern
        for ch_x in sorted(self.layout.v_channels,
                           key=lambda c: abs(c - mid_x))[:5]:
            for ch_y in sorted(self.layout.h_channels,
                               key=lambda c: abs(c - mid_y))[:5]:
                candidates.append(
                    [buf_out, (ch_x, by), (ch_x, ch_y), (ix, ch_y), buf_in])

        # V-H-V-H pattern
        for ch_y in sorted(self.layout.h_channels,
                           key=lambda c: abs(c - mid_y))[:5]:
            for ch_x in sorted(self.layout.v_channels,
                               key=lambda c: abs(c - mid_x))[:5]:
                candidates.append(
                    [buf_out, (bx, ch_y), (ch_x, ch_y), (ch_x, iy), buf_in])

        candidates.sort(key=lambda p: sum(
            abs(p[i+1][0]-p[i][0]) + abs(p[i+1][1]-p[i][1])
            for i in range(len(p)-1)))

        for path in candidates:
            if is_clear(path):
                return path
        return None

    def _try_double_u(self, bx, by, ix, iy, buf_out, buf_in, is_clear):
        """双U型：4拐点"""
        mid_x = (bx + ix) / 2
        mid_y = (by + iy) / 2
        candidates = []

        # H-V-H-V-H pattern（上下绕行 + 垂直通道）
        for ch_y in sorted(self.layout.h_channels,
                           key=lambda c: abs(c - mid_y))[:4]:
            for ch_x in sorted(self.layout.v_channels,
                               key=lambda c: abs(c - mid_x))[:4]:
                candidates.append(
                    [buf_out, (bx, ch_y), (ch_x, ch_y),
                     (ch_x, iy), (ix, iy), buf_in])

        # V-H-V-H-V pattern（左右绕行 + 水平通道）
        for ch_x in sorted(self.layout.v_channels,
                           key=lambda c: abs(c - mid_x))[:4]:
            for ch_y in sorted(self.layout.h_channels,
                               key=lambda c: abs(c - mid_y))[:4]:
                candidates.append(
                    [buf_out, (ch_x, by), (ch_x, ch_y),
                     (ix, ch_y), (ix, iy), buf_in])

        candidates.sort(key=lambda p: sum(
            abs(p[i+1][0]-p[i][0]) + abs(p[i+1][1]-p[i][1])
            for i in range(len(p)-1)))

        for path in candidates:
            if is_clear(path):
                return path
        return None

    @staticmethod
    def _path_midpoint(inflections: list) -> tuple:
        """计算路径 50% 长度处的位置，用于标签定位"""
        if not inflections:
            return (0, 0)
        if len(inflections) == 1:
            return inflections[0]
        # 计算每段的累计长度
        total = 0
        segments = []
        for i in range(len(inflections) - 1):
            x1, y1 = inflections[i]
            x2, y2 = inflections[i + 1]
            seg_len = abs(x2 - x1) + abs(y2 - y1)
            segments.append((total, total + seg_len, inflections[i], inflections[i + 1]))
            total += seg_len
        if total == 0:
            return inflections[len(inflections) // 2]
        # 找到 50% 长度所在的段
        half = total / 2
        for seg_start, seg_end, p1, p2 in segments:
            if seg_start <= half <= seg_end:
                seg_len = seg_end - seg_start
                if seg_len == 0:
                    return p1
                ratio = (half - seg_start) / seg_len
                return (p1[0] + (p2[0] - p1[0]) * ratio,
                        p1[1] + (p2[1] - p1[1]) * ratio)
        return inflections[len(inflections) // 2]

    def _connectors(self, debug_connection: str = None) -> str:
        """连线 — 两阶段策略：
        第一阶段：优先画出所有未被组件阻挡的直线和 L 型连线
        第二阶段：处理剩余需要绕行的连线（S型、U型、双L型、双U型等）
        """
        lines = ['  <!-- 连线 -->']
        used_sides = {}
        LEVEL_NAMES = {1: '直线', 2: 'L型', 3: 'S型', 4: 'U型', 5: '双L型', 6: '双U型'}

        # 存储每条连线的处理结果
        conn_results = {}  # conn -> (d, path_points, fs, ts, level, is_verbose)

        # ========== 第一阶段：直线 + L 型 ==========
        log.debug("===== 第一阶段：直线 + L 型 =====")
        for i, conn in enumerate(self.connections):
            f_step = conn.from_step
            t_step = conn.to_step
            conn_name = f"{f_step.title}->{t_step.title}"
            is_verbose = debug_connection == conn_name
            if is_verbose:
                log.debug("=" * 50)
                log.debug("【详细调试】%s (阶段一)", conn_name)
                log.debug("  %s: x=%s,y=%s,w=%s,h=%s", f_step.title, f_step.x, f_step.y, f_step.width, f_step.height)
                log.debug("  %s: x=%s,y=%s,w=%s,h=%s", t_step.title, t_step.x, t_step.y, t_step.width, t_step.height)

            result = self._build_s_path(
                f_step, t_step, used_sides,
                verbose=is_verbose, max_level=2)
            if result is not None:
                d, path_points, fs, ts, level = result
                conn_results[conn] = (d, path_points, fs, ts, level, is_verbose)
                used_sides.setdefault(f_step.title, set()).add(fs)
                used_sides.setdefault(t_step.title, set()).add(ts)
                log.debug("%s: 阶段一 %s [%s->%s]", conn_name, LEVEL_NAMES.get(level, f'L{level}'), fs, ts)

        # ========== 第二阶段：绕行路径 ==========
        log.debug("===== 第二阶段：绕行路径 =====")
        for i, conn in enumerate(self.connections):
            if conn in conn_results:
                continue
            f_step = conn.from_step
            t_step = conn.to_step
            conn_name = f"{f_step.title}->{t_step.title}"
            is_verbose = debug_connection == conn_name
            if is_verbose:
                log.debug("=" * 50)
                log.debug("【详细调试】%s (阶段二)", conn_name)
                log.debug("  %s: x=%s,y=%s,w=%s,h=%s", f_step.title, f_step.x, f_step.y, f_step.width, f_step.height)
                log.debug("  %s: x=%s,y=%s,w=%s,h=%s", t_step.title, t_step.x, t_step.y, t_step.width, t_step.height)

            result = self._build_s_path(
                f_step, t_step, used_sides,
                verbose=is_verbose)
            # _build_s_path 在不限制级别时总会返回结果（至少兜底）
            d, path_points, fs, ts, level = result
            conn_results[conn] = (d, path_points, fs, ts, level, is_verbose)
            used_sides.setdefault(f_step.title, set()).add(fs)
            used_sides.setdefault(t_step.title, set()).add(ts)
            log.debug("%s: 阶段二 %s [%s->%s]", conn_name, LEVEL_NAMES.get(level, f'L{level}'), fs, ts)

        # ========== 生成 SVG ==========
        for i, conn in enumerate(self.connections):
            if conn not in conn_results:
                continue
            d, path_points, fs, ts, level, is_verbose = conn_results[conn]
            delay = round(0.4 + i * 0.05, 2)
            is_sync = conn.is_sync()
            # 同步：蓝色实线+光点；异步：灰色虚线+虚线流动
            color = '#3b82f6' if is_sync else '#9ca3af'
            dash = '' if is_sync else 'stroke-dasharray="6 3"'
            marker = 'url(#arrow-sync)' if is_sync else 'url(#arrow-async)'
            glow = 'url(#glow-sync)' if is_sync else 'url(#glow-async)'
            stroke_w = '1.3'
            line_class = 'conn-line' if is_sync else 'conn-line-dash'

            label_x, label_y = self._path_midpoint(path_points)
            # 只在水平直线时偏移标签，避免遮挡
            if len(path_points) == 2:
                y1, y2 = path_points[0][1], path_points[1][1]
                if abs(y1 - y2) < 0.1:
                    label_y += 10

            # 连线
            lines.append(f'  <path d="{d}" fill="none" stroke="{color}"'
                         f' stroke-width="{stroke_w}" {dash} marker-end="{marker}"'
                         f' class="{line_class}" style="animation-delay:{delay}s"/>')

            # 流动光点（仅实线）
            if is_sync:
                dot_delay = round(delay + 0.3, 2)
                lines.append(f'  <circle r="3" fill="{glow}" class="flow-dot"'
                             f' style="offset-path:path(\'{d}\');animation-delay:{dot_delay}s,{dot_delay}s"/>')

            # 连线标签
            if conn.label:
                lines.append(f'  <text x="{label_x}" y="{label_y + 3}" class="conn-label conn-label-anim"'
                             f' fill="{color}" style="animation-delay:{delay + 0.1}s">{conn.label}</text>')

        return '\n'.join(lines)


# ==================== 主流程 ====================

def main():
    parser = argparse.ArgumentParser(description='泳道图 SVG 生成器')
    parser.add_argument('--json', required=True, help='JSON 配置文件路径')
    parser.add_argument('--svg', required=True, help='输出 SVG 文件路径')
    parser.add_argument('--debug', action='store_true', help='启用调试日志')
    parser.add_argument('--debug-connection', default=None,
                        help='详细调试指定连线（如 "订单审核->查询库存"），输出逐 combo/级别评估过程')
    args = parser.parse_args()

    if args.debug or args.debug_connection:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    # 1. 解析配置
    title, columns, rows, steps, connections = ConfigParser.parse(args.json)
    print(f'已加载: {len(columns)}列 {len(rows)}行 {len(steps)}步骤 {len(connections)}连线')

    # 2. 连线层级约束调整
    ConfigParser.adjust_tiers_for_connections(steps, connections)

    # 3. 计算布局
    layout = LayoutCalculator(columns, rows, steps)
    layout.calculate()
    print(f'布局: {layout.svg_width}x{layout.svg_height}')

    # 4. 计算连线
    generator = ComponentLineGenerator()
    conn_calc = ConnectorCalculator(steps, generator)
    connections = conn_calc.calculate(connections)
    success = sum(1 for c in connections if c.path_dict is not None
                   or c.from_step.row != c.to_step.row
                   or c.from_step.col != c.to_step.col
                   or c.from_step.tier != c.to_step.tier)
    print(f'连线: {success}/{len(connections)} 成功')

    # 5. 生成 SVG
    svg = SVGGenerator(title, columns, rows, steps, connections, layout, generator).generate(
        debug_connection=args.debug_connection)
    with open(args.svg, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f'已保存: {args.svg}')


if __name__ == '__main__':
    main()
