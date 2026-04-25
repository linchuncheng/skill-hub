#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型图处理器 - 从JSON配置生成SVG

用法:
    python3 model_svg_generator.py --json config.json --svg output.svg

工作流:
    1. 用 model_json_generator.py 生成JSON配置
    2. 查看或修改JSON配置
    3. 用本脚本从JSON生成SVG

示例:
    python3 model_svg_generator.py --json rbac-config.json --svg RBAC领域模型图.svg
"""

import re
import json
import argparse
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass, field


# ==================== 常量配置 ====================

DOMAIN_GAP = 20  # 领域外框间隔
DEFAULT_DOMAIN_COLS = 4  # 默认领域列数

COLOR_MAP = {
    '时标': {'fill': '#fce4ec', 'stroke': '#e91e63'},
    '资源': {'fill': '#f1f8e9', 'stroke': '#689f38'},
    '角色': {'fill': '#fff9c4', 'stroke': '#f9a825'},
    '描述': {'fill': '#e3f2fd', 'stroke': '#1976d2'},
}

# 连线颜色调色板（用于区分不同连线）
CONNECTOR_COLORS = [
    '#e57373',  # 柔和红
    '#81c784',  # 柔和绿
    '#64b5f6',  # 柔和蓝
    '#ffb74d',  # 柔和橙
    '#ba68c8',  # 柔和紫
    '#4db6ac',  # 柔和青
    '#f06292',  # 柔和粉
    '#7986cb',  # 柔和靛
    '#aed581',  # 柔和黄绿
    '#ff8a65',  # 柔和深橙
    '#4dd0e1',  # 柔和青蓝
    '#9575cd',  # 柔和深紫
    '#fff176',  # 柔和黄
    '#90a4ae',  # 柔和灰蓝
]

MODEL_WIDTH = 150
MODEL_GAP_H = 45  # 水平间距
MODEL_GAP_V = 25  # 垂直间距
MARGIN = 20
CTX_X = 40
CTX_Y = 60  # 领域起始Y坐标
LABEL_H = 30


# ==================== 数据模型 ====================

@dataclass
class Model:
    """领域模型"""
    name: str
    english_name: str
    model_type: str
    attributes: List[str] = field(default_factory=list)
    behaviors: List[str] = field(default_factory=list)
    relation_attributes: List[str] = field(default_factory=list)
    height: int = 0
    position: Tuple[int, int] = (0, 0)
    width: int = MODEL_WIDTH
    domain_name: str = ""  # 所属领域名


@dataclass
class Domain:
    """领域"""
    name: str                          # 领域名，如"RBAC域"
    tables: List[str] = field(default_factory=list)  # 包含的表名
    models: Dict[str, Model] = field(default_factory=dict)
    width: int = 0
    height: int = 0
    position: Tuple[int, int] = (0, 0)  # 领域外框左上角坐标


@dataclass
class Connector:
    """模型连线"""
    from_model: str
    to_model: str
    line_type: str
    path: str
    path_dict: dict = field(default_factory=dict)  # 存储路径详情，用于圆角处理


class ModelConfig(NamedTuple):
    """模型配置（由LLM提供）"""
    layout: Dict[str, Tuple[int, int]]
    names: Dict[str, str]
    types: Dict[str, str]
    behaviors: Dict[str, List[str]]
    relation_attrs: Dict[str, List[str]]


# ==================== 布局计算器 ====================

class LayoutCalculator:
    """计算单个领域内布局和坐标"""
    
    def __init__(self, models: Dict[str, Model], layout_config: Dict[str, Tuple[int, int]], domain_name: str):
        self.models = models
        self.layout = layout_config
        self.domain_name = domain_name
    
    def calculate_domain_size(self) -> Tuple[int, int]:
        """计算领域内容尺寸（不含外框边距）
        
        Returns:
            (width, height) 领域内容区域尺寸
        """
        rows, cols = self._analyze_layout()
        if not rows or not cols:
            return (0, 0)
        
        row_heights = self._calculate_row_heights(rows)
        
        # 计算内容尺寸
        content_w = MODEL_WIDTH * len(cols) + MODEL_GAP_H * (len(cols) - 1)
        content_h = sum(row_heights.values()) + MODEL_GAP_V * (len(rows) - 1)
        
        return (content_w, content_h)
    
    def calculate_positions(self, offset_x: int, offset_y: int):
        """计算模型绝对位置
        
        Args:
            offset_x: 领域外框左上角X偏移
            offset_y: 领域外框左上角Y偏移
        """
        rows, cols = self._analyze_layout()
        if not rows or not cols:
            return
        
        row_heights = self._calculate_row_heights(rows)
        min_col = min(cols)
        
        # 计算每行起始Y（相对领域内）
        row_y = {}
        current_y = LABEL_H + 10  # 上边距改为10px
        for row in sorted(rows):
            row_y[row] = current_y
            current_y += row_heights[row] + MODEL_GAP_V
        
        # 计算每个模型的绝对坐标
        for model_name, (row, col) in self.layout.items():
            if model_name in self.models:
                x = offset_x + MARGIN + (col - min_col) * (MODEL_WIDTH + MODEL_GAP_H)
                y = offset_y + row_y[row]
                self.models[model_name].position = (x, y)
                self.models[model_name].domain_name = self.domain_name
    
    def _analyze_layout(self) -> Tuple[set, set]:
        """分析布局的行列范围"""
        rows = set()
        cols = set()
        for (row, col) in self.layout.values():
            rows.add(row)
            cols.add(col)
        return rows, cols
    
    def _calculate_row_heights(self, rows: set) -> Dict[int, int]:
        """计算每行最大高度"""
        heights = {row: 0 for row in rows}
        for model_name, (row, _) in self.layout.items():
            if model_name in self.models:
                h = self.models[model_name].height
                heights[row] = max(heights[row], h)
        return heights


class MultiDomainLayoutCalculator:
    """多领域布局计算器
    
    布局策略：固定列数 + 高度自适应
    - 所有领域宽度固定为 cols 列
    - 模型按固定列数自动换行排列
    - 领域高度根据模型数量自动计算
    - 领域从上到下垂直堆叠
    """
    
    def __init__(self, domains: Dict[str, Domain], all_models: Dict[str, Model], model_config: ModelConfig, cols: int = None):
        self.domains = domains
        self.all_models = all_models
        self.model_config = model_config
        self.cols = cols or DEFAULT_DOMAIN_COLS  # 使用传入的列数或默认值
        self.auto_layouts: Dict[str, Dict[str, Tuple[int, int]]] = {}  # 各领域的自动布局
    
    def calculate(self) -> Tuple[int, int, dict, List[dict]]:
        """计算多领域布局
        
        Returns:
            (svg_w, svg_h, legend_info, domain_infos)
        """
        # 1. 为每个领域计算自动布局和尺寸
        for domain_name, domain in self.domains.items():
            # 获取该领域的模型
            domain_models = {t: self.all_models[t] for t in domain.tables if t in self.all_models}
            
            # 从模型中读取JSON定义的坐标
            original_layout = {}
            for t in domain.tables:
                if t in self.all_models:
                    model = self.all_models[t]
                    # model.position 是 (row, col) 格式
                    original_layout[t] = model.position
            
            auto_layout = self._auto_relayout(original_layout, self.cols)
            self.auto_layouts[domain_name] = auto_layout
            
            # 计算领域尺寸
            calc = LayoutCalculator(domain_models, auto_layout, domain_name)
            w, h = calc.calculate_domain_size()
            
            # 固定宽度为 cols 列
            fixed_width = MODEL_WIDTH * self.cols + MODEL_GAP_H * (self.cols - 1)
            
            domain.width = fixed_width + MARGIN * 2
            domain.height = h + MARGIN * 2 + LABEL_H
            domain.models = domain_models
        
        # 2. 垂直堆叠排列
        self._calculate_vertical_positions()
        
        # 3. 计算模型绝对位置（使用自动布局）
        for domain_name, domain in self.domains.items():
            auto_layout = self.auto_layouts[domain_name]
            calc = LayoutCalculator(domain.models, auto_layout, domain_name)
            calc.calculate_positions(domain.position[0], domain.position[1])
        
        # 4. 计算SVG总尺寸
        max_width = max(d.width for d in self.domains.values())
        total_height = sum(d.height for d in self.domains.values()) + DOMAIN_GAP * (len(self.domains) - 1)
        svg_w = max_width + CTX_X * 2
        svg_h = total_height + CTX_Y + 20
        
        return (
            svg_w, svg_h,
            self._create_legend_info(),
            self._create_domain_infos()
        )
    
    def _auto_relayout(self, original_layout: Dict[str, Tuple[int, int]], max_cols: int) -> Dict[str, Tuple[int, int]]:
        """自动将模型按固定列数重新排列
        
        当指定了max_cols时，所有模型强制按max_cols列均匀分布，忽略原布局列数
        
        Args:
            original_layout: 原始布局 {表名: (行, 列)}
            max_cols: 最大列数
            
        Returns:
            新布局 {表名: (新行, 新列)}
        """
        if not original_layout:
            return {}
        
        # 检查原布局实际使用的列数
        cols_used = set()
        for row, col in original_layout.values():
            cols_used.add(col)
        
        # 如果原布局列数已经等于max_cols，保留原布局
        if len(cols_used) == max_cols:
            return original_layout.copy()
        
        # 否则，强制按max_cols列重新分布
        # 按原始坐标排序，保持相对顺序，然后均匀分布到max_cols列
        sorted_models = sorted(original_layout.items(), key=lambda x: (x[1][0], x[1][1]))
        new_layout = {}
        for i, (table_name, _) in enumerate(sorted_models):
            new_row = i // max_cols
            new_col = i % max_cols
            new_layout[table_name] = (new_row, new_col)
        return new_layout
    
    def _calculate_vertical_positions(self):
        """垂直堆叠排列领域"""
        y = CTX_Y
        for domain in self.domains.values():
            domain.position = (CTX_X, y)
            y += domain.height + DOMAIN_GAP
    
    def _create_legend_info(self) -> dict:
        """创建图例信息"""
        return {
            'x': CTX_X,
            'y': 30,
            'items': [
                {'name': '时标', 'fill': '#fce4ec', 'stroke': '#e91e63'},
                {'name': '资源', 'fill': '#f1f8e9', 'stroke': '#689f38'},
                {'name': '角色', 'fill': '#fff9c4', 'stroke': '#f9a825'},
                {'name': '描述', 'fill': '#e3f2fd', 'stroke': '#1976d2'},
            ]
        }
    
    def _create_domain_infos(self) -> List[dict]:
        """创建所有领域外框信息"""
        domain_infos = []
        for domain_name, domain in self.domains.items():
            domain_infos.append({
                'x': domain.position[0],
                'y': domain.position[1],
                'width': domain.width,
                'height': domain.height,
                'label': domain_name
            })
        return domain_infos


# ==================== 连线计算器 ====================

from model_line_generator import ComponentLineGenerator, NoValidPathError


class ConnectorCalculator:
    """计算模型连线（基于ComponentLineGenerator）"""
    
    def __init__(self, models: Dict[str, Model], generator: ComponentLineGenerator = None):
        self.models = models
        self._generator = generator or ComponentLineGenerator()
    
    def calculate(self, relations: List[Tuple[str, str]]) -> List[Connector]:
        """根据关系列表计算连线"""
        connectors = []
        for from_name, to_name in relations:
            conn = self._create_connector(from_name, to_name)
            if conn:
                connectors.append(conn)
        return connectors
    
    def _create_connector(self, from_name: str, to_name: str) -> Optional[Connector]:
        """创建单条连线
        
        使用ModelLineGenerator计算最优路径
        """
        model_from = self._find_model(from_name)
        model_to = self._find_model(to_name)
        
        if not model_from or not model_to:
            return None
        
        # 转换为ModelLineGenerator需要的格式
        all_models = self._convert_models()
        start_model = self._model_to_dict(model_from, from_name)
        end_model = self._model_to_dict(model_to, to_name)
        
        try:
            path_dict = self._generator.get_best_path(start_model, end_model, all_models)
            
            # 转换为Connector格式
            path_str = ' '.join(f"{x},{y}" for x, y in self._path_to_points(path_dict))
            line_type = 'polyline' if path_dict['turns'] > 0 else 'direct'
            
            return Connector(from_name, to_name, line_type, path_str, path_dict)
        except NoValidPathError:
            return None
    
    def _convert_models(self) -> List[dict]:
        """将所有模型转换为ModelLineGenerator格式"""
        result = []
        for name, model in self.models.items():
            # 使用模型名作为 model_id，与 --relations 参数一致
            result.append(self._model_to_dict(model, model.name))
        return result
    
    def _model_to_dict(self, model: Model, name: str) -> dict:
        """将Model对象转换为字典格式"""
        x, y = model.position
        return {
            "model_id": name,
            "x1": round(x, 2),
            "y1": round(y, 2),
            "x2": round(x + model.width, 2),
            "y2": round(y + model.height, 2)
        }
    
    def _path_to_points(self, path_dict: dict) -> List[Tuple[float, float]]:
        """将路径字典转换为点序列"""
        points = [path_dict['start_point']]
        points.extend(path_dict['inflections'])
        points.append(path_dict['end_point'])
        return points
    
    def _find_model(self, name: str) -> Optional[Model]:
        """通过表名、中文名或英文名查找模型"""
        for table_name, m in self.models.items():
            if table_name == name or m.name == name or m.english_name == name:
                return m
        
        # 尝试模糊匹配中文名（去掉"单"、"配置"等后缀）
        name_variants = [name]
        if name.endswith('单'):
            name_variants.append(name[:-1])
        if name.endswith('配置'):
            name_variants.append(name[:-2])
        
        for table_name, m in self.models.items():
            if m.name in name_variants:
                return m
            # 也检查中文名的变体
            for variant in name_variants:
                if m.name == variant or m.name.startswith(variant):
                    return m
        
        return None


# ==================== SVG生成器 ====================

class SVGGenerator:
    """生成SVG代码"""
    
    def generate(self) -> str:
        """生成完整SVG"""
        lines = [
            self._header(),
            self._background(),
            self._title(),  # 大标题
            self._legend(),
            self._domain_frames(),  # 多领域外框
            self._models(),
            self._connectors(),
            '</svg>'
        ]
        return '\n'.join(lines)

    def _title(self) -> str:
        """大标题"""
        if not self.title:
            return ''
        return f'  <text x="{self.svg_w // 2}" y="20" text-anchor="middle" font-size="18" font-weight="bold" fill="#333">{self.title}</text>'
    
    def __init__(self, models: Dict[str, Model], connectors: List[Connector],
                 legend: dict, domains: List[dict], svg_size: Tuple[int, int],
                 title: str = None, generator=None):
        self.models = models
        self.connectors = connectors
        self.legend = legend
        self.domains = domains  # 多领域列表
        self.svg_w, self.svg_h = svg_size
        self.title = title  # 大标题
        self._generator = generator  # 用于圆角路径生成

    def _header(self) -> str:
        """SVG头部"""
        # 生成每条连线对应的彩色箭头标记
        arrow_markers = []
        for i in range(len(self.connectors)):
            color = CONNECTOR_COLORS[i % len(CONNECTOR_COLORS)]
            arrow_markers.append(f'''    <marker id="arrow{i}" viewBox="0 0 8 8" refX="7.5" refY="4"
            markerWidth="5" markerHeight="5" orient="auto">
      <path d="M 0 0 L 8 4 L 0 8 L 1 4 Z" fill="{color}"/>
    </marker>''')
        
        markers_def = '\n'.join(arrow_markers)
        
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.svg_w} {self.svg_h}" font-family="'PingFang SC','Microsoft YaHei',sans-serif">
  <defs>
    <!-- 箭头标记：为每条连线定义对应颜色的箭头 -->
{markers_def}
  </defs>
  <style>
    .legend-text {{ font-size: 10px; fill: #555; }}
    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    .layer-frame {{ opacity: 0; animation: fadeIn 0.4s ease-out forwards; }}
    .component-card {{ opacity: 0; animation: fadeIn 0.5s ease-out forwards; }}
    
    /* 连线淡入 + 虚线流动动画 */
    .connector-line {{ 
      opacity: 0; 
      animation: fadeIn 0.4s ease-out forwards, dashFlow 2s linear infinite; 
    }}
    
    @keyframes dashFlow {{
      to {{ stroke-dashoffset: -12; }}
    }}
  </style>'''
    
    def _background(self) -> str:
        """背景"""
        return f'  <rect width="{self.svg_w}" height="{self.svg_h}" fill="#f8f9fa"/>'
    
    def _legend(self) -> str:
        """图例"""
        lines = [f'  <g transform="translate({self.legend["x"]}, {self.legend["y"]})" class="layer-frame">']
        x = 0
        for item in self.legend['items']:
            lines.append(f'    <rect x="{x}" y="0" width="12" height="12" fill="{item["fill"]}" stroke="{item["stroke"]}"/>')
            lines.append(f'    <text x="{x + 16}" y="10" class="legend-text">{item["name"]}</text>')
            x += 50
        lines.append('  </g>')
        return '\n'.join(lines)
    
    def _domain_frames(self) -> str:
        """所有领域外框"""
        lines = ['  <!-- 领域外框 -->']
        for i, ctx in enumerate(self.domains):
            # 根据文字长度计算标签宽度，保持左右边距与上下边距一致
            label_text = ctx['label']
            text_width = self._estimate_text_width(label_text, 13)
            padding_x = 12  # 左右边距
            padding_y = 6   # 上下边距
            label_w = text_width + padding_x * 2
            label_h = 13 + padding_y * 2  # 字号 + 上下边距
            text_y = ctx['y'] + padding_y + 11  # 基线位置
            corner_r = 8  # 右下角圆角半径
            
            path_d = f"M{ctx['x']} {ctx['y']} L{ctx['x'] + label_w} {ctx['y']} L{ctx['x'] + label_w} {ctx['y'] + label_h - corner_r} Q{ctx['x'] + label_w} {ctx['y'] + label_h} {ctx['x'] + label_w - corner_r} {ctx['y'] + label_h} L{ctx['x']} {ctx['y'] + label_h} Z"
            delay = 0.1 + i * 0.1
            
            lines.append(f'''  <rect x="{ctx['x']}" y="{ctx['y']}" width="{ctx['width']}" height="{ctx['height']}" rx="4" fill="#fff" stroke="#333" stroke-width="2" class="layer-frame" style="animation-delay: {delay}s"/>
  <path d="{path_d}" fill="#333" class="layer-frame" style="animation-delay: {delay + 0.05}s"/>
  <text x="{ctx['x'] + label_w/2}" y="{text_y}" text-anchor="middle" font-size="13" font-weight="bold" fill="#fff" class="layer-frame" style="animation-delay: {delay + 0.05}s">{label_text}</text>''')
        return '\n'.join(lines)
    
    def _estimate_text_width(self, text: str, font_size: int) -> int:
        """估算文字宽度
        
        中文字符约等于字号宽度，英文/数字约为字号的0.6倍
        """
        width = 0
        for char in text:
            if '\u4e00' <= char <= '\u9fff':  # 中文字符
                width += font_size
            else:  # 英文/数字/符号
                width += int(font_size * 0.6)
        return width
    
    def _models(self) -> str:
        """模型卡片"""
        lines = ['  <!-- 模型卡片 -->']
        for i, model in enumerate(self.models.values()):
            lines.append(self._model_card(model, i))
        return '\n'.join(lines)
    
    def _model_card(self, m: Model, index: int) -> str:
        """单个模型卡片"""
        x, y = m.position
        color = COLOR_MAP.get(m.model_type, COLOR_MAP['角色'])
        delay = 0.3 + index * 0.05
        
        lines = [
            f'  <g transform="translate({x}, {y})" class="component-card" style="animation-delay: {delay}s">',
            f'    <rect x="0" y="0" width="{m.width}" height="{m.height}" rx="6" fill="{color["fill"]}" stroke="{color["stroke"]}" stroke-width="1.5"/>',
            f'    <text x="{m.width/2}" y="16" text-anchor="middle" font-size="12" font-weight="bold">{m.name}</text>',
            f'    <text x="{m.width/2}" y="28" text-anchor="middle" font-size="10" fill="#666">{m.english_name}</text>',
            f'    <line x1="8" y1="35" x2="{m.width-8}" y2="35" stroke="{color["stroke"]}" stroke-width="0.5" stroke-dasharray="2,2"/>'
        ]
        
        # 属性（JSON字段用J前缀，关联属性用T前缀，普通属性用+前缀）
        y_pos = 50
        for attr in m.attributes:
            # 先去掉所有空格
            attr = attr.replace(' ', '')
            is_json = 'JSON' in attr or 'json' in attr
            prefix = 'J' if is_json else '+'
            # 如果是JSON字段，去掉 JSON 后缀
            display_attr = attr.replace('JSON', '').replace('json', '') if is_json else attr
            lines.append(f'    <text x="8" y="{y_pos}" font-size="10" fill="#555">{prefix} {display_attr}</text>')
            y_pos += 13
        
        # 关联属性（用T前缀，与其他属性放在一起，不加分隔线）
        for rel in m.relation_attributes:
            lines.append(f'    <text x="8" y="{y_pos}" font-size="10" fill="#555">T {rel}</text>')
            y_pos += 13

        # 行为
        if m.behaviors:
            lines.append(f'    <line x1="8" y1="{y_pos}" x2="{m.width-8}" y2="{y_pos}" stroke="{color["stroke"]}" stroke-width="0.5" stroke-dasharray="2,2"/>')
            y_pos += 12
            for behavior in m.behaviors:
                lines.append(f'    <text x="8" y="{y_pos}" font-size="10" fill="#555">+ {behavior}()</text>')
                y_pos += 13
        
        lines.append('  </g>')
        return '\n'.join(lines)
    
    def _connectors(self) -> str:
        """连线"""
        lines = ['  <!-- 连线 -->']
        for i, conn in enumerate(self.connectors):
            delay = 0.65 + i * 0.05
            # 为每条连线分配不同颜色
            color = CONNECTOR_COLORS[i % len(CONNECTOR_COLORS)]
            # 使用对应颜色的箭头标记
            arrow_id = f"arrow{i}"
            if conn.line_type == 'direct':
                # 直连：使用简单线段（加虚线流动）
                pts = conn.path.split()
                if len(pts) == 2:
                    x1, y1 = pts[0].split(',')
                    x2, y2 = pts[1].split(',')
                    lines.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" stroke-dasharray="4 2" marker-end="url(#{arrow_id})" class="connector-line" style="animation-delay: {delay}s, {delay}s"/>')
            else:
                # 折线：使用圆角路径（加虚线流动）
                if conn.path_dict:
                    d = self._generator.get_rounded_svg_path(conn.path_dict)
                    lines.append(f'  <path d="{d}" fill="none" stroke="{color}" stroke-width="1.5" stroke-dasharray="4 2" marker-end="url(#{arrow_id})" class="connector-line" style="animation-delay: {delay}s, {delay}s"/>')
                else:
                    # 降级到polyline
                    lines.append(f'  <polyline points="{conn.path}" fill="none" stroke="{color}" stroke-width="1.5" stroke-dasharray="4 2" marker-end="url(#{arrow_id})" class="connector-line" style="animation-delay: {delay}s, {delay}s"/>')
        return '\n'.join(lines)


# ==================== 配置解析器 ====================

class ConfigParser:
    """配置工具类"""
    
    @staticmethod
    def filter_cross_domain_relations(
        relations: List[Tuple[str, str]], 
        domains: Dict[str, Domain],
        name_to_table: Dict[str, str] = None
    ) -> List[Tuple[str, str]]:
        """过滤跨领域连线，只保留领域内连线
        
        Args:
            relations: 连线关系列表 [(from_model, to_model), ...]
            domains: 领域字典 {领域名: Domain}
            name_to_table: 中文名/英文名到表名的映射 {名称: 表名}
            
        Returns:
            过滤后的连线关系列表
        """
        # 构建表名到领域的映射
        table_to_domain = {}
        for domain_name, domain in domains.items():
            for table in domain.tables:
                table_to_domain[table] = domain_name
        
        # 过滤连线
        valid_relations = []
        for from_model, to_model in relations:
            from_table = from_model
            to_table = to_model
            
            if name_to_table:
                from_table = name_to_table.get(from_model, from_model)
                to_table = name_to_table.get(to_model, to_model)
            
            from_domain = table_to_domain.get(from_table)
            to_domain = table_to_domain.get(to_table)
            
            if from_domain and to_domain and from_domain == to_domain:
                valid_relations.append((from_model, to_model))
        return valid_relations


class JSONConfigParser:
    """解析JSON配置文件"""
    
    @staticmethod
    def parse(json_path: str) -> Tuple[Dict[str, Domain], Dict[str, Model], List[Tuple[str, str]], str, int]:
        """解析JSON配置文件
        
        Args:
            json_path: JSON配置文件路径
            
        Returns:
            (domains, models, relations, title, cols)
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        title = config.get('title', '')
        cols = config.get('cols', DEFAULT_DOMAIN_COLS)
        
        # 解析领域和模型
        domains = {}
        models = {}
        
        for domain_data in config.get('domains', []):
            domain_name = domain_data['name']
            domain = Domain(name=domain_name)
            
            for model_data in domain_data.get('models', []):
                model_key = model_data['model']
                domain.tables.append(model_key)
                
                model = Model(
                    name=model_data['name'],
                    english_name=model_key,
                    model_type=model_data['type'],
                    attributes=model_data.get('attributes', []),
                    behaviors=model_data.get('behaviors', []),
                    relation_attributes=model_data.get('associations', [])
                )
                model.height = _calculate_model_height(model)
                
                # 读取JSON中的坐标（如果存在）
                position = model_data.get('position')
                if position and len(position) >= 2:
                    model.position = (position[0], position[1])
                
                models[model_key] = model
            
            domains[domain_name] = domain
        
        
        # 解析连线关系 (格式: "源模型->目标模型")
        # ⚠️ 注意：relations 必须是字符串数组 ["租户->用户", "用户->角色"]
        # 禁止使用对象数组 [{"from": "租户", "to": "用户"}]，那是其他图类型的格式
        relations = []
        for rel in config.get('relations', []):
            if '->' in rel:
                source, target = rel.split('->')
                relations.append((source.strip(), target.strip()))
        
        
        return domains, models, relations, title, cols


def _to_pascal_case(table_name: str) -> str:
    """转换为PascalCase"""
    name = re.sub(r'^(sys_|t_|tb_)', '', table_name, flags=re.IGNORECASE)
    return ''.join(part.capitalize() for part in name.split('_'))


def _calculate_model_height(model: Model) -> int:
    """计算模型高度"""
    attr_count = len(model.attributes) + len(model.relation_attributes)
    behavior_count = len(model.behaviors)
    
    if behavior_count == 0:
        return 60 + attr_count * 13 - 13
    else:
        return 75 + (attr_count + behavior_count - 1) * 13


# ==================== 主流程 ====================

def main():
    parser = argparse.ArgumentParser(description='模型图处理器 - 从JSON配置生成SVG')
    parser.add_argument('--json', required=True, help='JSON配置文件路径')
    parser.add_argument('--svg', required=True, help='输出SVG文件路径')
    args = parser.parse_args()
    
    # 1. 解析JSON配置
    domains, models, relations, title, cols = JSONConfigParser.parse(args.json)
    print(f"已加载JSON配置: {len(domains)} 个领域, {len(models)} 个模型, {len(relations)} 条连线")
    
    # 2. 构建名称到表名的映射
    name_to_table = {}
    for table_name, model in models.items():
        name_to_table[model.name] = table_name
        name_to_table[model.english_name] = table_name
    
    # 3. 过滤跨领域连线
    valid_relations = ConfigParser.filter_cross_domain_relations(relations, domains, name_to_table)
    if len(valid_relations) < len(relations):
        print(f"已过滤 {len(relations) - len(valid_relations)} 条跨领域连线")
    
    # 4. 构建ModelConfig（用于布局计算）
    layout = {}
    for domain in domains.values():
        for table_name in domain.tables:
            if table_name in models:
                m = models[table_name]
                layout[table_name] = (0, 0)  # 临时坐标，会被自动重排
    config = ModelConfig(layout, {}, {}, {}, {})
    
    # 5. 计算多领域布局
    svg_w, svg_h, legend, domain_infos = MultiDomainLayoutCalculator(domains, models, config, cols=cols).calculate()
    print(f"布局计算完成: SVG尺寸 {svg_w}x{svg_h}")
    
    # 6. 计算连线
    generator = ComponentLineGenerator()
    connectors = ConnectorCalculator(models, generator).calculate(valid_relations)
    print(f"生成连线: {len(connectors)} 条")
    
    # 7. 生成SVG
    svg_content = SVGGenerator(models, connectors, legend, domain_infos, (svg_w, svg_h), title=title, generator=generator).generate()
    with open(args.svg, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"SVG已保存到: {args.svg}")


if __name__ == '__main__':
    main()
