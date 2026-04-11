#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型图处理器 - LLM决策 + 脚本执行

用法:
    python3 model_diagram_preprocessor.py <sql_file> [<sql_file2> ...] --models "表名:中文名:类型:行,列:行为:关联属性" [--relations "源模型->目标模型,..."] [--svg output.svg]

功能:
    - 支持多个SQL文件，表定义会合并（后加载的覆盖同名表）
    - --models 参数指定参与该领域的表，从合并后的表定义中选择

示例:
    # 单个SQL文件
    python3 model_diagram_preprocessor.py init.sql \
        --models "sys_tenant:租户:角色:0,1;sys_user:用户:角色:1,0:登录,分配角色:用户角色" \
        --relations "租户->用户,用户->角色" \
        --svg RBAC领域模型图.svg
    
    # 多个SQL文件（从合并后的表定义中选择WMS相关表）
    python3 model_diagram_preprocessor.py 01-base.sql 02-wms.sql 03-phase2.sql \
        --models "wms_warehouse:仓库:角色:0,0;wms_inbound_order:入库单:单据:1,1" \
        --relations "仓库->入库单" \
        --context WMS \
        --svg WMS领域模型图.svg
"""

import re
import json
import argparse
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass, field


# ==================== 常量配置 ====================

COLOR_MAP = {
    '角色': {'fill': '#fff9c4', 'stroke': '#f9a825'},
    '事物': {'fill': '#f1f8e9', 'stroke': '#689f38'},
    '配置': {'fill': '#e3f2fd', 'stroke': '#1976d2'},
    '单据': {'fill': '#fce4ec', 'stroke': '#e91e63'},
}

AUDIT_FIELDS = {'created_at', 'updated_at', 'created_by', 'updated_by', 'deleted'}

MODEL_WIDTH = 150
MODEL_GAP = 45
MARGIN = 20
CTX_X = 40
CTX_Y = 60
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


@dataclass
class Connector:
    """模型连线"""
    from_model: str
    to_model: str
    line_type: str
    path: str


class ModelConfig(NamedTuple):
    """模型配置（由LLM提供）"""
    layout: Dict[str, Tuple[int, int]]
    names: Dict[str, str]
    types: Dict[str, str]
    behaviors: Dict[str, List[str]]
    relation_attrs: Dict[str, List[str]]


# ==================== SQL解析器 ====================

class SQLParser:
    """解析SQL文件提取表结构"""
    
    @staticmethod
    def parse(sql_content: str) -> Dict[str, dict]:
        """解析SQL，返回 {表名: {columns, comment}}"""
        tables = {}
        pattern = re.compile(
            r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\((.*?)\)(?:\s*ENGINE|\s*$)',
            re.IGNORECASE | re.DOTALL
        )
        
        for match in pattern.finditer(sql_content):
            table_name = match.group(1)
            columns_str = match.group(2)
            tables[table_name] = {
                'columns': SQLParser._parse_columns(columns_str),
                'comment': SQLParser._extract_table_comment(columns_str)
            }
        return tables
    
    @staticmethod
    def _parse_columns(columns_str: str) -> List[dict]:
        """解析列定义"""
        columns = []
        for line in columns_str.split('\n'):
            line = line.strip()
            if not line or line.startswith(('PRIMARY', 'UNIQUE', 'INDEX', 'KEY')):
                continue
            
            col_match = re.match(r'(\w+)\s+(\w+)', line)
            if col_match:
                col_name = col_match.group(1)
                if col_name.lower() in AUDIT_FIELDS:
                    continue
                
                comment_match = re.search(r"COMMENT\s+'([^']+)'", line, re.IGNORECASE)
                columns.append({
                    'name': col_name,
                    'type': col_match.group(2),
                    'comment': comment_match.group(1) if comment_match else col_name
                })
        return columns
    
    @staticmethod
    def _extract_table_comment(columns_str: str) -> str:
        """提取表注释"""
        match = re.search(r"COMMENT='([^']+)'", columns_str, re.IGNORECASE)
        return match.group(1) if match else ''


# ==================== 模型处理器 ====================

class ModelProcessor:
    """处理模型数据"""
    
    def __init__(self, tables: Dict[str, dict], config: ModelConfig):
        self.tables = tables
        self.config = config
        self.models: Dict[str, Model] = {}
    
    def process(self) -> Dict[str, Model]:
        """处理所有模型"""
        association_tables = self._find_association_tables()
        
        # 只为配置中指定的表创建模型
        for table_name in self.config.layout.keys():
            if table_name in self.tables:
                self._create_model(table_name, self.tables[table_name])
        
        # 处理关联表
        self._process_association_tables(association_tables)
        
        # 计算高度和位置
        for model in self.models.values():
            model.height = self._calculate_height(model)
        
        return self.models
    
    def _find_association_tables(self) -> set:
        """识别纯关联表（只有id+外键）"""
        association_tables = set()
        for table_name, table_data in self.tables.items():
            non_fk = [c for c in table_data['columns'] 
                     if c['name'].lower() not in ['id'] 
                     and not c['name'].lower().endswith('_id')]
            if len(non_fk) == 0:
                association_tables.add(table_name)
        return association_tables
    
    def _create_model(self, table_name: str, table_data: dict):
        """创建单个模型"""
        # 使用LLM配置或默认值
        chinese_name = self.config.names.get(table_name) or self._extract_chinese_name(table_data)
        model_type = self.config.types.get(table_name) or self._infer_type(table_name, table_data)
        
        model = Model(
            name=chinese_name,
            english_name=self._to_pascal_case(table_name),
            model_type=model_type,
            attributes=self._extract_attributes(table_data),
            behaviors=self.config.behaviors.get(table_name, []),
            relation_attributes=self.config.relation_attrs.get(table_name, [])
        )
        self.models[table_name] = model
    
    def _process_association_tables(self, association_tables: set):
        """处理关联表，添加关联属性到主模型
        
        如果LLM已经通过参数传入了关联属性，则不再自动添加
        """
        for table_name in association_tables:
            table_data = self.tables[table_name]
            fk_cols = [c for c in table_data['columns'] 
                      if c['name'].lower().endswith('_id') and c['name'].lower() != 'id']
            
            if len(fk_cols) >= 2:
                self._add_relation_attribute(fk_cols[0], fk_cols[1])
    
    def _add_relation_attribute(self, fk1: dict, fk2: dict):
        """添加关联属性到主模型
        
        如果该模型已有LLM传入的关联属性，则跳过自动添加
        """
        related_table = fk2['name'][:-3]  # 移除 _id
        for table_name in self.tables:
            if table_name.lower() == related_table or table_name.lower() == f'sys_{related_table}':
                if table_name in self.models:
                    # 如果LLM已传入关联属性，不再自动添加
                    if not self.models[table_name].relation_attributes:
                        self.models[table_name].relation_attributes.append(f"T {related_table}关联")
                break
    
    def _extract_attributes(self, table_data: dict) -> List[str]:
        """提取业务属性（过滤id和外键）"""
        attrs = []
        for col in table_data['columns']:
            name = col['name'].lower()
            if name == 'id':
                continue
            if name.endswith('_id') and name != 'tenant_id':
                continue
            attrs.append(self._simplify_name(col['comment']))
        return attrs
    
    def _calculate_height(self, model: Model) -> int:
        """计算模型高度（精确匹配渲染逻辑）
        
        渲染结构：
        - 标题 y=16，英文名 y=28
        - 分隔线 y=35
        - 属性起始 y=50，行距13px
        - 行为分隔线：y = 50 + attr_count * 13
        - 行为起始：y = 分隔线 + 15，行距13px
        - 底部边距：约8px（与左边距x=8视觉一致）
        
        注意：text的y是基线位置，字体底部约在基线下方2px
        """
        attr_count = len(model.attributes) + len(model.relation_attributes)
        behavior_count = len(model.behaviors)
        
        if behavior_count == 0:
            # 最后一个属性 y = 50 + (attr_count-1) * 13
            # 高度 = last_y + 10 (字体高度约10px，底部留8px)
            return 60 + attr_count * 13 - 13  # = 47 + attr_count * 13
        else:
            # 最后一个行为 y = 50 + attr_count*13 + 15 + (behavior_count-1)*13
            # 高度 = last_y + 10
            return 75 + (attr_count + behavior_count - 1) * 13
    
    @staticmethod
    def _extract_chinese_name(table_data: dict) -> str:
        """从SQL注释提取中文名"""
        name = table_data['comment']
        if name.endswith('表'):
            name = name[:-1]
        return name
    
    @staticmethod
    def _infer_type(table_name: str, table_data: dict) -> str:
        """推断模型类型"""
        name_lower = table_name.lower()
        if 'log' in name_lower:
            return '单据'
        if any(c['name'].lower() == 'parent_id' for c in table_data['columns']):
            return '配置'
        return '角色'
    
    @staticmethod
    def _to_pascal_case(table_name: str) -> str:
        """转换为PascalCase"""
        name = re.sub(r'^(sys_|t_|tb_)', '', table_name, flags=re.IGNORECASE)
        return ''.join(part.capitalize() for part in name.split('_'))
    
    @staticmethod
    def _simplify_name(comment: str) -> str:
        """简化属性名"""
        for sep in ['：', ':', '（', '(', '，', ',']:
            if sep in comment:
                comment = comment.split(sep)[0]
        return comment.strip()


# ==================== 布局计算器 ====================

class LayoutCalculator:
    """计算SVG布局和坐标"""
    
    def __init__(self, models: Dict[str, Model], layout_config: Dict[str, Tuple[int, int]], context_name: str):
        self.models = models
        self.layout = layout_config
        self.context_name = context_name
    
    def calculate(self) -> Tuple[int, int, dict, dict, dict]:
        """计算布局，返回 (svg_w, svg_h, title_info, legend_info, context_info)"""
        rows, cols = self._analyze_layout()
        row_heights = self._calculate_row_heights(rows)
        
        # 计算尺寸
        content_w = MODEL_WIDTH * len(cols) + MODEL_GAP * (len(cols) - 1)
        content_h = sum(row_heights.values()) + MODEL_GAP * (len(rows) - 1)
        ctx_w = content_w + MARGIN * 2
        ctx_h = content_h + MARGIN * 2 + LABEL_H
        svg_w = ctx_w + CTX_X * 2
        svg_h = ctx_h + CTX_Y + 20
        
        # 计算模型位置
        self._calculate_positions(rows, row_heights, min(cols))
        
        return (
            svg_w, svg_h,
            self._create_title_info(svg_w),
            self._create_legend_info(),
            self._create_context_info(ctx_w, ctx_h)
        )
    
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
    
    def _calculate_positions(self, rows: set, row_heights: Dict[int, int], min_col: int):
        """计算每个模型的坐标"""
        # 计算每行起始Y
        row_y = {}
        current_y = CTX_Y + LABEL_H + MARGIN
        for row in sorted(rows):
            row_y[row] = current_y
            current_y += row_heights[row] + MODEL_GAP
        
        # 计算每个模型的X,Y
        for model_name, (row, col) in self.layout.items():
            if model_name in self.models:
                x = CTX_X + MARGIN + (col - min_col) * (MODEL_WIDTH + MODEL_GAP)
                self.models[model_name].position = (x, row_y[row])
    
    def _create_title_info(self, svg_w: int) -> dict:
        """创建大标题信息"""
        text = f"{self.context_name}领域模型图"
        return {
            'text': text,
            'x': svg_w // 2,
            'y': 20,
            'fontSize': 16,
            'width': len(text) * 16
        }
    
    def _create_legend_info(self) -> dict:
        """创建图例信息"""
        return {
            'x': CTX_X,
            'y': 30,
            'items': [
                {'name': '角色', 'fill': '#fff9c4', 'stroke': '#f9a825'},
                {'name': '事物', 'fill': '#f1f8e9', 'stroke': '#689f38'},
                {'name': '配置', 'fill': '#e3f2fd', 'stroke': '#1976d2'},
                {'name': '单据', 'fill': '#fce4ec', 'stroke': '#e91e63'},
            ]
        }
    
    def _create_context_info(self, ctx_w: int, ctx_h: int) -> dict:
        """创建上下文外框信息"""
        return {
            'x': CTX_X,
            'y': CTX_Y,
            'width': ctx_w,
            'height': ctx_h,
            'label': self.context_name
        }


# ==================== 连线计算器 ====================

from component_line_generator import ComponentLineGenerator, NoValidPathError


class ConnectorCalculator:
    """计算模型连线（基于ComponentLineGenerator）"""
    
    def __init__(self, models: Dict[str, Model]):
        self.models = models
        self._generator = ComponentLineGenerator()
    
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
            
            return Connector(from_name, to_name, line_type, path_str)
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
    
    def __init__(self, models: Dict[str, Model], connectors: List[Connector], 
                 title: dict, legend: dict, context: dict, svg_size: Tuple[int, int]):
        self.models = models
        self.connectors = connectors
        self.title = title
        self.legend = legend
        self.context = context
        self.svg_w, self.svg_h = svg_size
    
    def generate(self) -> str:
        """生成完整SVG"""
        lines = [
            self._header(),
            self._background(),
            self._title(),
            self._legend(),
            self._context_frame(),
            self._models(),
            self._connectors(),
            '</svg>'
        ]
        return '\n'.join(lines)
    
    def _header(self) -> str:
        """SVG头部"""
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.svg_w} {self.svg_h}" font-family="'PingFang SC','Microsoft YaHei',sans-serif">
  <defs>
    <!-- 箭头标记：小巧三角形，refX控制箭头离终点距离 -->
    <marker id="arrow" viewBox="0 0 8 8" refX="7.5" refY="4"
            markerWidth="5" markerHeight="5" orient="auto">
      <path d="M 0 0 L 8 4 L 0 8 L 1 4 Z" fill="#999"/>
    </marker>
  </defs>
  <style>
    .legend-text {{ font-size: 10px; fill: #555; }}
    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    .layer-frame {{ opacity: 0; animation: fadeIn 0.4s ease-out forwards; }}
    .component-card {{ opacity: 0; animation: fadeIn 0.5s ease-out forwards; }}
    .connector-line {{ opacity: 0; animation: fadeIn 0.4s ease-out forwards; }}
  </style>'''
    
    def _background(self) -> str:
        """背景"""
        return f'  <rect width="{self.svg_w}" height="{self.svg_h}" fill="#f8f9fa"/>'
    
    def _title(self) -> str:
        """大标题"""
        t = self.title
        return f'  <text x="{t["x"]}" y="{t["y"]}" text-anchor="middle" font-size="{t["fontSize"]}" font-weight="bold" fill="#333">{t["text"]}</text>'
    
    def _legend(self) -> str:
        """图例"""
        lines = [f'  <g transform="translate({self.legend["x"]}, {self.legend["y"]})" class="layer-frame">']
        x = 0
        for item in self.legend['items']:
            lines.append(f'    <rect x="{x}" y="0" width="12" height="12" fill="{item["fill"]}" stroke="{item["stroke"]}"/>')
            lines.append(f'    <text x="{x + 16}" y="10" class="legend-text">{item["name"]}</text>')
            x += 60
        lines.append('  </g>')
        return '\n'.join(lines)
    
    def _context_frame(self) -> str:
        """上下文外框"""
        ctx = self.context
        label_w, label_h = 60, 29
        path_d = f"M{ctx['x']} {ctx['y']} L{ctx['x'] + label_w} {ctx['y']} L{ctx['x'] + label_w} {ctx['y'] + 21} Q{ctx['x'] + label_w} {ctx['y'] + label_h} {ctx['x'] + label_w - 8} {ctx['y'] + label_h} L{ctx['x']} {ctx['y'] + label_h} Z"
        
        return f'''  <rect x="{ctx['x']}" y="{ctx['y']}" width="{ctx['width']}" height="{ctx['height']}" rx="4" fill="#fff" stroke="#333" stroke-width="2" class="layer-frame" style="animation-delay: 0.1s"/>
  <path d="{path_d}" fill="#333" class="layer-frame" style="animation-delay: 0.15s"/>
  <text x="{ctx['x'] + label_w/2}" y="{ctx['y'] + 20}" text-anchor="middle" font-size="13" font-weight="bold" fill="#fff" class="layer-frame" style="animation-delay: 0.15s">{ctx['label']}</text>'''
    
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
            if conn.line_type in ('vertical', 'horizontal'):
                pts = conn.path.split()
                if len(pts) == 2:
                    x1, y1 = pts[0].split(',')
                    x2, y2 = pts[1].split(',')
                    lines.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#999" stroke-width="1.5" stroke-dasharray="4 2" marker-end="url(#arrow)" class="connector-line" style="animation-delay: {delay}s"/>')
            else:
                lines.append(f'  <polyline points="{conn.path}" fill="none" stroke="#999" stroke-width="1.5" stroke-dasharray="4 2" marker-end="url(#arrow)" class="connector-line" style="animation-delay: {delay}s"/>')
        return '\n'.join(lines)


# ==================== 配置解析器 ====================

class ConfigParser:
    """解析命令行配置"""
    
    @staticmethod
    def parse_models(models_str: str) -> ModelConfig:
        """解析模型配置字符串，使用分号分隔多个模型
        
        格式: 表名:中文名:类型:行,列:行为:关联属性
        
        行为和关联属性用 : 分隔
        关联属性以 T 开头，如: T用户角色集合
        无行为时 : 保留，如: 表名:中文名:类型:行,列::关联属性
        """
        layout, names, types, behaviors, relation_attrs = {}, {}, {}, {}, {}

        for item in models_str.split(';'):
            item = item.strip()
            if not item:
                continue
            parts = item.split(':')
            if len(parts) >= 4:
                table, chinese, mtype, pos = parts[0], parts[1], parts[2], parts[3]
                names[table] = chinese
                types[table] = mtype
                row, col = map(int, pos.split(','))
                layout[table] = (row, col)
                
                # 解析行为（parts[4]）和关联属性（parts[5]）
                # 行为和关联属性用 : 分隔
                # 支持多种分隔符：逗号、中文顿号、分号
                if len(parts) >= 5 and parts[4]:
                    behavior_list = [b.strip() for b in re.split(r'[,，、；]', parts[4]) if b.strip()]
                    if behavior_list:
                        behaviors[table] = behavior_list
                
                if len(parts) >= 6 and parts[5]:
                    # 关联属性以 T 开头，去掉 T 前缀
                    relation_list = []
                    for attr in parts[5].split(','):
                        attr = attr.strip()
                        if attr.startswith('T'):
                            relation_list.append(attr[1:])  # 去掉T前缀
                        elif attr:
                            relation_list.append(attr)
                    if relation_list:
                        relation_attrs[table] = relation_list

        return ModelConfig(layout, names, types, behaviors, relation_attrs)

    @staticmethod
    def parse_relations(rel_str: Optional[str]) -> List[Tuple[str, str]]:
        """解析连线关系，使用逗号分隔多个关系"""
        if not rel_str:
            return []
        relations = []
        for item in rel_str.split(','):
            item = item.strip()
            if not item:
                continue
            if '->' in item:
                from_model, to_model = item.split('->')
                relations.append((from_model.strip(), to_model.strip()))
        return relations


# ==================== 主流程 ====================

def main():
    parser = argparse.ArgumentParser(description='模型图预处理器 - LLM决策 + 脚本执行')
    parser.add_argument('sql_files', nargs='+', help='SQL文件路径（支持多个文件，用空格分隔）')
    parser.add_argument('--models', required=True, help='模型配置："表名:中文名:类型:行,列:行为..."')
    parser.add_argument('--relations', help='连线关系："源模型1->目标模型1,源模型2->目标模型2..."')
    parser.add_argument('--context', '-c', default='RBAC', help='上下文名称，默认RBAC')
    parser.add_argument('--svg', help='输出SVG文件路径')
    parser.add_argument('--output', '-o', help='输出JSON文件路径')
    args = parser.parse_args()
    
    # 1. 解析配置
    config = ConfigParser.parse_models(args.models)
    relations = ConfigParser.parse_relations(args.relations)
    
    # 2. 解析SQL（支持多个文件合并）
    tables = {}
    for sql_file in args.sql_files:
        with open(sql_file, 'r', encoding='utf-8') as f:
            file_tables = SQLParser.parse(f.read())
            # 合并表定义，后加载的文件覆盖先加载的同名表
            tables.update(file_tables)
        print(f"已加载SQL文件: {sql_file} ({len(file_tables)} 个表)")
    print(f"共加载 {len(tables)} 个唯一表定义")
    
    # 3. 处理模型
    models = ModelProcessor(tables, config).process()
    
    # 4. 计算布局
    svg_w, svg_h, title, legend, context = LayoutCalculator(models, config.layout, args.context).calculate()
    
    # 5. 计算连线
    connectors = ConnectorCalculator(models).calculate(relations)
    
    # 6. 生成SVG或JSON
    if args.svg:
        svg_content = SVGGenerator(models, connectors, title, legend, context, (svg_w, svg_h)).generate()
        with open(args.svg, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"SVG已保存到: {args.svg}")
    else:
        result = {
            'title': title,
            'legend': legend,
            'context': context,
            'models': [{**{'name': m.name, 'englishName': m.english_name, 'type': m.model_type}, 
                       'position': {'x': m.position[0], 'y': m.position[1]},
                       'color': COLOR_MAP.get(m.model_type, COLOR_MAP['角色'])} for m in models.values()],
            'connectors': [{'from': c.from_model, 'to': c.to_model, 'path': c.path} for c in connectors],
            'svg': {'width': svg_w, 'height': svg_h}
        }
        json_str = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_str)
            print(f"输出已保存到: {args.output}")
        else:
            print(json_str)


if __name__ == '__main__':
    main()
