#!/usr/bin/env python3
"""
领域模型图验证脚本（四色建模规范）
检查生成的模型图 SVG 是否符合 model-diagram.md 规范

用法:
    python3 model_diagram_validator.py <svg文件路径>

验证维度:
    1. 四色建模合规性（填充色/边框色）
    2. 模型结构规范（宽度/标题/分隔线/属性/行为）
    3. ER图特征检测（禁止出现数据库类型/英文字段名）
    4. 审计属性检测（禁止出现 created_at 等）
    5. 连线规范（虚线/无箭头/水平垂直/中点连接）
    6. 布局规范（间距/边距）
    7. 图例规范（必须包含四色图例）
    8. 动画规范（仅 fadeIn，禁止 scale/translateY）
"""

import sys
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

# ============================================================
# 四色建模规范常量
# ============================================================

FOUR_COLOR_FILLS = {'#fff9c4', '#f1f8e9', '#e3f2fd', '#fce4ec'}
FOUR_COLOR_STROKES = {'#f9a825', '#689f38', '#1976d2', '#e91e63'}
FILL_STROKE_PAIRS = {
    '#fff9c4': '#f9a825',  # 角色 - 黄
    '#f1f8e9': '#689f38',  # 事物 - 绿
    '#e3f2fd': '#1976d2',  # 配置 - 蓝
    '#fce4ec': '#e91e63',  # 单据 - 粉
}
FOUR_COLOR_NAMES = {
    '#fff9c4': '角色（黄色）',
    '#f1f8e9': '事物（绿色）',
    '#e3f2fd': '配置（蓝色）',
    '#fce4ec': '单据（粉色）',
}

# 审计属性关键词（出现则报错）
AUDIT_FIELDS = [
    'created_at', 'updated_at', 'created_by', 'updated_by',
    'deleted', 'create_time', 'update_time', 'is_deleted',
    'gmt_create', 'gmt_modified',
]

# 数据库类型关键词（ER图特征，出现则报错）
DB_TYPES = [
    'VARCHAR', 'BIGINT', 'INT', 'TINYINT', 'DATETIME', 'TIMESTAMP',
    'DECIMAL', 'FLOAT', 'DOUBLE', 'TEXT', 'BLOB', 'CHAR',
    'NOT NULL', 'DEFAULT', 'COMMENT', 'PRIMARY KEY',
]

# 英文字段名模式（snake_case，出现在属性行则报错）
SNAKE_CASE_FIELD_PATTERN = re.compile(r'\+\s+[a-z][a-z0-9]*(?:_[a-z0-9]+){1,}$')

# 有效背景色（非模型的填充色）
NON_MODEL_FILLS = {'#f8f9fa', '#fafafa', '#ffffff', '#fff', 'none', 'white'}

SVG_NS = 'http://www.w3.org/2000/svg'


@dataclass
class ModelInfo:
    """从 SVG 解析到的模型信息"""
    translate_x: float = 0
    translate_y: float = 0
    width: float = 0
    height: float = 0
    fill: str = ''
    stroke: str = ''
    texts: list = field(default_factory=list)   # 所有 text 内容
    title_y: Optional[float] = None              # 中文标题 y
    subtitle_y: Optional[float] = None           # 英文副标题 y
    separator_y: Optional[float] = None          # 分隔线 y


@dataclass
class LineInfo:
    """从 SVG 解析到的连线信息"""
    tag: str          # 'line' or 'polyline'
    x1: float = 0
    y1: float = 0
    x2: float = 0
    y2: float = 0
    points: list = field(default_factory=list)   # polyline 的点列表
    stroke_dasharray: str = ''
    marker_end: str = ''


class ModelDiagramValidator:
    """领域模型图验证器"""

    MODEL_WIDTH = 150
    MODEL_GAP = 45
    MODEL_MARGIN = 20
    TITLE_Y = 16
    SUBTITLE_Y = 28
    SEPARATOR_Y = 34
    ATTR_START_Y = 47

    def __init__(self, svg_path: str):
        self.svg_path = Path(svg_path)
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []
        self.content = ''
        self.models: list[ModelInfo] = []
        self.lines: list[LineInfo] = []

    # ============================================================
    # 主入口
    # ============================================================

    def validate(self) -> bool:
        if not self.svg_path.exists():
            self.errors.append(f"文件不存在: {self.svg_path}")
            return False

        try:
            self.content = self.svg_path.read_text(encoding='utf-8')
            root = ET.fromstring(self.content)
        except ET.ParseError as e:
            self.errors.append(f"XML 解析错误: {e}")
            return False
        except Exception as e:
            self.errors.append(f"读取文件错误: {e}")
            return False

        # 解析模型和连线
        self._parse_models(root)
        self._parse_lines(root)

        # 各项验证
        self._check_main_title()            # 大标题校验（必须在最前面，基础结构）
        self._check_er_features()           # ER 图特征检测（最高优先级）
        self._check_audit_fields()          # 审计属性检测
        self._check_four_color()            # 四色建模规范
        self._check_model_structure()       # 模型结构规范
        self._check_layout()                # 布局间距规范
        self._check_lines()                 # 连线规范
        self._check_legend()                # 图例规范
        self._check_context_frame()         # 上下文外框
        self._check_animation()             # 动画规范

        return len(self.errors) == 0

    # ============================================================
    # 解析阶段
    # ============================================================

    def _parse_models(self, root: ET.Element):
        """解析所有模型 <g transform="translate(x,y)"> 组"""
        for g in root.iter(f'{{{SVG_NS}}}g'):
            transform = g.get('transform', '')
            m = re.match(r'translate\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)', transform)
            if not m:
                continue

            tx, ty = float(m.group(1)), float(m.group(2))

            # 找主外框 rect（第一个 rect 子元素）
            rect = g.find(f'{{{SVG_NS}}}rect')
            if rect is None:
                continue

            width = float(rect.get('width', 0))
            height = float(rect.get('height', 0))
            fill = rect.get('fill', '').lower().strip()
            stroke = rect.get('stroke', '').lower().strip()

            # 仅处理四色模型（非背景、非图例）
            if fill not in FOUR_COLOR_FILLS:
                continue
            # 过滤图例小色块：图例 rect 宽度通常 ≤ 20px，模型宽度为 150px
            if width < 50:
                continue

            # 收集 text 内容
            texts = []
            title_y = subtitle_y = separator_y = None
            for child in g:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if tag == 'text':
                    y = float(child.get('y', 0))
                    text_content = (child.text or '').strip()
                    texts.append((y, text_content))
                    if abs(y - self.TITLE_Y) < 2 and title_y is None:
                        title_y = y
                    elif abs(y - self.SUBTITLE_Y) < 3 and subtitle_y is None:
                        subtitle_y = y
                elif tag == 'line':
                    y1 = float(child.get('y1', 0))
                    if abs(y1 - self.SEPARATOR_Y) < 2 and separator_y is None:
                        separator_y = y1

            model = ModelInfo(
                translate_x=tx, translate_y=ty,
                width=width, height=height,
                fill=fill, stroke=stroke,
                texts=texts,
                title_y=title_y,
                subtitle_y=subtitle_y,
                separator_y=separator_y,
            )
            self.models.append(model)

    def _parse_lines(self, root: ET.Element):
        """解析所有连线（line 和 polyline）"""
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag == 'line':
                info = LineInfo(
                    tag='line',
                    x1=float(elem.get('x1', 0)),
                    y1=float(elem.get('y1', 0)),
                    x2=float(elem.get('x2', 0)),
                    y2=float(elem.get('y2', 0)),
                    stroke_dasharray=elem.get('stroke-dasharray', ''),
                    marker_end=elem.get('marker-end', ''),
                )
                self.lines.append(info)
            elif tag == 'polyline':
                pts_str = elem.get('points', '')
                pts = []
                for pair in pts_str.split():
                    pair = pair.strip()
                    if ',' in pair:
                        x, y = pair.split(',')
                        pts.append((float(x), float(y)))
                info = LineInfo(
                    tag='polyline',
                    stroke_dasharray=elem.get('stroke-dasharray', ''),
                    marker_end=elem.get('marker-end', ''),
                    points=pts,
                )
                if pts:
                    info.x1, info.y1 = pts[0]
                    info.x2, info.y2 = pts[-1]
                self.lines.append(info)

    # ============================================================
    # 验证规则
    # ============================================================

    def _check_er_features(self):
        """检测 ER 图特征（数据库类型/英文字段名）"""
        # 检测数据库类型关键词
        # 先移除 CSS 和 defs 区域，避免 text {、<text> 等标签名被误判为数据库类型
        content_no_style = re.sub(r'<style[^>]*>.*?</style>', '', self.content, flags=re.DOTALL)
        content_no_defs = re.sub(r'<defs[^>]*>.*?</defs>', '', content_no_style, flags=re.DOTALL)
        # 移除 SVG 标签名（如 <text ...>、</text>）
        content_clean = re.sub(r'</?text\b[^>]*>', '', content_no_defs, flags=re.IGNORECASE)

        found_types = []
        for db_type in DB_TYPES:
            # 词边界：前后不能是字母或数字
            pattern = r'(?<![A-Za-z0-9])' + re.escape(db_type) + r'(?![A-Za-z0-9])'
            if re.search(pattern, content_clean, re.IGNORECASE):
                found_types.append(db_type)
        if found_types:
            self.errors.append(
                f"[ER图特征] 检测到数据库类型关键词，这是 ER 图写法，模型图禁止展示数据库类型: {found_types}"
            )

        # 检测属性行中的英文 snake_case 字段名
        text_pattern = re.compile(r'>\+\s+([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\s*<', re.IGNORECASE)
        found_snake = text_pattern.findall(self.content)
        # 过滤已知合法的英文标识（如类名/英文副标题）
        snake_in_attrs = [f for f in found_snake if '_' in f]
        if snake_in_attrs:
            self.errors.append(
                f"[ER图特征] 属性行中发现英文 snake_case 字段名（应改为中文描述）: {snake_in_attrs[:5]}"
            )

    def _check_audit_fields(self):
        """检测审计属性"""
        found = []
        content_lower = self.content.lower()
        for field_name in AUDIT_FIELDS:
            if field_name in content_lower:
                found.append(field_name)
        if found:
            self.errors.append(
                f"[审计属性] 检测到审计属性，必须从模型中移除: {found}"
            )

    def _check_four_color(self):
        """验证四色建模规范"""
        if not self.models:
            self.errors.append("[四色建模] 未检测到任何领域模型（含 fill 四色色值的 <g> 组）")
            return

        self.infos.append(f"[四色建模] 共检测到 {len(self.models)} 个模型")

        for i, model in enumerate(self.models):
            label = f"模型#{i+1}(translate={model.translate_x},{model.translate_y})"

            # 填充色必须是四色之一
            if model.fill not in FOUR_COLOR_FILLS:
                self.errors.append(
                    f"[四色建模] {label} 填充色 '{model.fill}' 不在四色规范内 "
                    f"（允许: {list(FOUR_COLOR_FILLS)}）"
                )

            # 边框色与填充色配对
            expected_stroke = FILL_STROKE_PAIRS.get(model.fill)
            if expected_stroke and model.stroke != expected_stroke:
                self.errors.append(
                    f"[四色建模] {label} 填充色 '{model.fill}'({FOUR_COLOR_NAMES.get(model.fill,'?')}) "
                    f"对应边框色应为 '{expected_stroke}'，实际为 '{model.stroke}'"
                )

    def _check_model_structure(self):
        """验证模型内部结构"""
        for i, model in enumerate(self.models):
            label = f"模型#{i+1}(translate={model.translate_x},{model.translate_y})"

            # 1. 宽度必须 150px
            if abs(model.width - self.MODEL_WIDTH) > 0.5:
                self.errors.append(
                    f"[模型结构] {label} 宽度为 {model.width}px，必须为 {self.MODEL_WIDTH}px"
                )

            # 2. 中文标题 y=16
            if model.title_y is None:
                self.warnings.append(f"[模型结构] {label} 未检测到 y={self.TITLE_Y} 的中文标题")
            elif abs(model.title_y - self.TITLE_Y) > 1:
                self.errors.append(
                    f"[模型结构] {label} 中文标题 y={model.title_y}，规范值为 y={self.TITLE_Y}"
                )

            # 3. 英文副标题 y=28
            if model.subtitle_y is None:
                self.warnings.append(f"[模型结构] {label} 未检测到 y={self.SUBTITLE_Y} 的英文副标题")
            elif abs(model.subtitle_y - self.SUBTITLE_Y) > 1:
                self.errors.append(
                    f"[模型结构] {label} 英文副标题 y={model.subtitle_y}，规范值为 y={self.SUBTITLE_Y}"
                )

            # 3.5 英文副标题命名规范：必须是 XxxXxx（PascalCase），不能是 snake_case 表名
            if model.subtitle_y is not None:
                # 从 texts 中找到 y≈28 的文本作为英文副标题内容
                subtitle_text = None
                for y, text in model.texts:
                    if abs(y - self.SUBTITLE_Y) < 2:
                        subtitle_text = text.strip()
                        break
                if subtitle_text:
                    # 检查是否包含下划线（snake_case 表名如 sys_user, order_item）
                    if '_' in subtitle_text:
                        self.errors.append(
                            f"[模型结构] {label} 英文副标题 '{subtitle_text}' 使用 snake_case，"
                            f"应改为 PascalCase（如：User, OrderItem, SysUser），禁止直接使用数据库表名"
                        )
                    # 检查是否全小写（也是表名风格）
                    elif subtitle_text.islower() and len(subtitle_text) > 2:
                        self.errors.append(
                            f"[模型结构] {label} 英文副标题 '{subtitle_text}' 全小写，"
                            f"应改为 PascalCase（首字母大写，如：User, OrderItem）"
                        )

            # 4. 分隔线 y=34
            if model.separator_y is None:
                self.warnings.append(f"[模型结构] {label} 未检测到 y={self.SEPARATOR_Y} 的分隔线")
            elif abs(model.separator_y - self.SEPARATOR_Y) > 1:
                self.errors.append(
                    f"[模型结构] {label} 分隔线 y={model.separator_y}，规范值为 y={self.SEPARATOR_Y}"
                )

            # 5. 属性格式检查（y >= 47 的 text）
            for y, text in model.texts:
                if y < self.ATTR_START_Y:
                    continue
                if not text:
                    continue
                # 必须以 "+ " 开头
                if not text.startswith('+ '):
                    self.errors.append(
                        f"[模型结构] {label} 属性/行为行格式错误（必须以'+ '开头）: '{text}'"
                    )
                    continue
                content_part = text[2:].strip()
                # 行为行：以 "行为名()" 结尾
                if content_part.endswith(')') or content_part.endswith('()'):
                    continue  # 行为行，格式正确
                # 属性行：检查是否包含 / （合并属性）
                if '/' in content_part:
                    self.errors.append(
                        f"[模型结构] {label} 属性合并（每属性必须单独一行，不允许用/分隔）: '{text}'"
                    )
                # 属性行：检查是否是英文字段名（snake_case）
                if re.match(r'^[a-z][a-z0-9]*(?:_[a-z0-9]+)+$', content_part):
                    self.errors.append(
                        f"[模型结构] {label} 属性名为英文字段名，应改为中文描述: '{text}'"
                    )

        # 6. 全局检查：所有模型中至少有一个模型含有行为（以 () 结尾的文本行）
        models_with_behavior = []
        for i, model in enumerate(self.models):
            for _, text in model.texts:
                content = text[2:].strip() if text.startswith('+ ') else text.strip()
                if content.endswith(')'):
                    models_with_behavior.append(i + 1)
                    break
        if self.models and not models_with_behavior:
            self.warnings.append(
                "[模型结构] 所有模型均未检测到行为（以 '()' 结尾的行），"
                "领域模型通常应包含核心业务行为（普通CRUD除外），请检查是否遗漏"
            )
        elif self.models:
            behavior_ratio = len(models_with_behavior) / len(self.models)
            if behavior_ratio < 0.3:
                self.warnings.append(
                    f"[模型结构] 仅 {len(models_with_behavior)}/{len(self.models)} 个模型有核心行为，"
                    f"比例偏低（{behavior_ratio:.0%}），建议核心实体模型补充核心业务行为"
                )

    def _check_layout(self):
        """验证模型布局间距"""
        if len(self.models) < 2:
            return

        xs = sorted(set(m.translate_x for m in self.models))
        ys = sorted(set(m.translate_y for m in self.models))

        # 检查水平间距（同行相邻列之间）
        if len(xs) >= 2:
            for i in range(len(xs) - 1):
                gap = xs[i + 1] - xs[i] - self.MODEL_WIDTH
                if abs(gap - self.MODEL_GAP) > 1:
                    self.errors.append(
                        f"[布局] 水平间距异常: x={xs[i]} 到 x={xs[i+1]} "
                        f"间距={gap}px，规范值={self.MODEL_GAP}px"
                    )

        # 检查每列垂直间距（需按列分组）
        col_map: dict[float, list[ModelInfo]] = {}
        for m in self.models:
            col_map.setdefault(m.translate_x, []).append(m)

        for x, col_models in col_map.items():
            if len(col_models) < 2:
                continue
            col_models_sorted = sorted(col_models, key=lambda m: m.translate_y)
            for i in range(len(col_models_sorted) - 1):
                upper = col_models_sorted[i]
                lower = col_models_sorted[i + 1]
                gap = lower.translate_y - upper.translate_y - upper.height
                if gap < 0:
                    self.errors.append(
                        f"[布局] 列x={x} 模型重叠: "
                        f"模型(y={upper.translate_y},H={upper.height}) 与 "
                        f"模型(y={lower.translate_y}) 重叠 {abs(gap):.1f}px，"
                        f"必须保证垂直间距≥25"
                    )
                elif abs(gap - self.MODEL_GAP) > 2:
                    self.errors.append(
                        f"[布局] 列x={x} 垂直间距异常: "
                        f"模型(y={upper.translate_y},H={upper.height}) → "
                        f"模型(y={lower.translate_y}) 间距={gap:.1f}px，"
                        f"规范值={self.MODEL_GAP}px"
                    )

    def _check_lines(self):
        """验证连线规范"""
        # 过滤掉模型内部的分隔线（y1=y2=34 且 x1=8, x2=142）
        connectors = []
        for ln in self.lines:
            # 跳过模型内部分隔线（短虚线：长度 ≤ 150px 且 y 很小）
            if ln.tag == 'line':
                length = abs(ln.x2 - ln.x1) + abs(ln.y2 - ln.y1)
                if length < 150 and ln.y1 < 50 and ln.y2 < 50:
                    continue
            connectors.append(ln)

        if not connectors:
            self.warnings.append("[连线] 未检测到连线（line/polyline）")
            return

        self.infos.append(f"[连线] 共检测到 {len(connectors)} 条连线")

        for i, ln in enumerate(connectors):
            label = f"连线#{i+1}"

            # 1. 必须是虚线
            if '4' not in ln.stroke_dasharray:
                self.errors.append(
                    f"[连线] {label} 未设置虚线 stroke-dasharray='4 2'，"
                    f"实际: '{ln.stroke_dasharray}'"
                )

            # 2. 禁止箭头
            if ln.marker_end:
                self.errors.append(
                    f"[连线] {label} 模型图连线禁止使用箭头（marker-end），"
                    f"实际: '{ln.marker_end}'"
                )

            # 3. 每段必须是水平或垂直线
            if ln.tag == 'line':
                if abs(ln.x1 - ln.x2) > 0.5 and abs(ln.y1 - ln.y2) > 0.5:
                    self.errors.append(
                        f"[连线] {label} 存在斜线！"
                        f"({ln.x1},{ln.y1}) → ({ln.x2},{ln.y2})，"
                        "连线只能是水平线或垂直线"
                    )
            elif ln.tag == 'polyline' and len(ln.points) >= 2:
                for j in range(len(ln.points) - 1):
                    px1, py1 = ln.points[j]
                    px2, py2 = ln.points[j + 1]
                    if abs(px1 - px2) > 0.5 and abs(py1 - py2) > 0.5:
                        self.errors.append(
                            f"[连线] {label} 第{j+1}段存在斜线！"
                            f"({px1},{py1}) → ({px2},{py2})，"
                            "折线每段必须是水平或垂直线"
                        )

            # 4. 检查连线起止点是否为模型边缘中点（非角点）
            self._check_line_endpoint(label, ln.x1, ln.y1, 'start')
            self._check_line_endpoint(label, ln.x2, ln.y2, 'end')

    def _check_line_endpoint(self, label: str, ex: float, ey: float, role: str):
        """检查连线端点是否在某模型的四边中点上（非角点）"""
        if not self.models:
            return

        for model in self.models:
            mx, my = model.translate_x, model.translate_y
            mw, mh = model.width, model.height

            # 四个角点
            corners = [(mx, my), (mx + mw, my), (mx, my + mh), (mx + mw, my + mh)]
            for cx, cy in corners:
                if abs(ex - cx) < 1 and abs(ey - cy) < 1:
                    self.errors.append(
                        f"[连线] {label} {role}点 ({ex},{ey}) 连接到了模型角点！"
                        f"模型(x={mx},y={my}) 角点({cx},{cy})，"
                        "必须连接到四边正中点（上/下/左/右）"
                    )
                    return  # 找到问题，不用继续检查该点

    def _check_legend(self):
        """验证四色图例"""
        legend_keywords = ['角色', '事物', '配置', '单据']
        missing = []
        for kw in legend_keywords:
            if kw not in self.content:
                missing.append(kw)
        if missing:
            self.errors.append(
                f"[图例] 缺少四色图例项: {missing}（图例必须包含角色/事物/配置/单据）"
            )
        else:
            self.infos.append("[图例] 四色图例完整 ✓")

    def _check_context_frame(self):
        """验证上下文外框"""
        # 检查是否有深色实线大矩形（上下文外框）
        has_context_rect = bool(re.search(
            r'<rect[^>]*stroke="#333"[^>]*stroke-width="2"', self.content
        ) or re.search(
            r'<rect[^>]*stroke-width="2"[^>]*stroke="#333"', self.content
        ))
        if not has_context_rect:
            self.warnings.append(
                "[上下文] 未检测到上下文外框（需要 stroke='#333' stroke-width='2' 的 rect）"
            )

        # 检查是否有上下文标签（带黑色填充的 path）
        label_paths = re.findall(r'<path[^>]*fill="#333"[^>]*/>', self.content)
        label_paths += re.findall(r'<path[^>]*fill="#333"[^>]*>', self.content)
        if not label_paths:
            self.warnings.append("[上下文] 未检测到上下文标签（需要 fill='#333' 的 path 角标）")
        else:
            # 检查标签右下角必须是圆角：path d 属性中必须含有 Q 命令（贝塞尔曲线）
            # 规范形状：M x0 y0 L x1 y0 L x1 y1 Q x1 y2 x2 y2 L x0 y2 L x0 y0 Z
            # 其中 Q 只出现一次（仅右下角圆角），左上/右上/左下三角均为直角
            found_corner = False
            for path_tag in label_paths:
                d_match = re.search(r'\bd="([^"]*)"', path_tag)
                if not d_match:
                    d_match = re.search(r"\bd='([^']*)'", path_tag)
                if not d_match:
                    continue
                d_val = d_match.group(1)
                q_count = d_val.upper().count('Q')
                if q_count == 1:
                    found_corner = True
                    break
                elif q_count == 0:
                    self.errors.append(
                        "[上下文] 角标 path 缺少贝塞尔圆角（Q 命令），"
                        "右下角必须是圆角，参考：'...L x1 y1 Q x1 y2 x2 y2 L...'"
                    )
                elif q_count > 1:
                    self.errors.append(
                        f"[上下文] 角标 path 含有 {q_count} 个 Q 命令，"
                        "只允许右下角一个圆角，其余三角必须是直角"
                    )
            if label_paths and not found_corner and not any(
                e.startswith('[上下文] 角标 path') for e in self.errors
            ):
                self.errors.append(
                    "[上下文] 未在角标 path 中找到有效的右下角圆角（Q 命令），"
                    "规范格式：M x0 y0 L x1 y0 L x1 y1 Q x1 y2 x2 y2 L x0 y2 L x0 y0 Z"
                )

    def _check_main_title(self):
        """验证大标题：居中、字号大、格式为 XXX领域模型"""
        # 提取所有 text 元素
        root = ET.fromstring(self.content)
        texts = []
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag == 'text':
                text_content = (elem.text or '').strip()
                if not text_content:
                    continue
                y = float(elem.get('y', 0))
                font_size_str = elem.get('font-size', '12')
                # 提取数字部分
                fs_match = re.search(r'[\d.]+', font_size_str)
                font_size = float(fs_match.group()) if fs_match else 12
                x = float(elem.get('x', 0))
                texts.append((y, font_size, x, text_content))

        if not texts:
            self.errors.append("[大标题] 未检测到任何文本元素")
            return

        # 筛选大字号文本（>=13px）且在上下文外框上方（y < 50）
        # 上下文外框通常从 y=60 开始，上下文标签在 y=80 左右
        # 大标题必须在上下文外框上方，独立居中
        large_top_texts = [
            t for t in texts
            if t[1] >= 13 and t[0] < 50
        ]

        if not large_top_texts:
            self.errors.append(
                "[大标题] 未检测到居中大标题，"
                "模型图顶部（上下文外框上方）应有字号≥13px的大标题，格式：XXX领域模型"
            )
            return

        # 按 y 坐标排序，取最上面的作为大标题候选
        large_top_texts.sort(key=lambda t: t[0])
        main_title = large_top_texts[0]
        title_text = main_title[3]

        # 检查格式：必须以"领域模型"结尾
        if not title_text.endswith('领域模型'):
            # 允许"XXX领域模型图"或"XXX领域模型"
            if '领域模型' not in title_text:
                self.errors.append(
                    f"[大标题] 标题格式错误：'{title_text}'，"
                    f"必须以'领域模型'结尾（如：订单领域模型、用户领域模型）"
                )

        # 检查是否居中：x 坐标应在 viewBox 宽度的中间区域
        vb_match = re.search(r'viewBox="[^"]*\s+[^"]*\s+(\d+)\s+(\d+)"', self.content)
        if vb_match:
            vb_width = float(vb_match.group(1))
            title_x = main_title[2]
            center_min = vb_width * 0.3
            center_max = vb_width * 0.7
            if not (center_min <= title_x <= center_max):
                self.warnings.append(
                    f"[大标题] 标题 '{title_text}' 位置可能未居中 "
                    f"(x={title_x}, 建议范围: {center_min:.0f}-{center_max:.0f})"
                )

        self.infos.append(f"[大标题] '{title_text}' ✓")

    def _check_animation(self):
        """验证动画规范"""
        has_anim = 'animation' in self.content or '@keyframes' in self.content
        if not has_anim:
            self.warnings.append("[动画] 未检测到入场动画，建议添加 fadeIn 动画")
            return

        # 禁止 scale transform 动画
        if 'transform: scale' in self.content or 'transform:scale' in self.content:
            self.errors.append(
                "[动画] 检测到 scale transform 动画（popIn），"
                "模型图禁止使用 scale/translateY 等 CSS transform 动画，"
                "必须只用 fadeIn（opacity 变化）"
            )

        # 禁止 translateY 动画
        if 'translateY' in self.content:
            self.errors.append(
                "[动画] 检测到 translateY 动画，"
                "模型图中 <g transform='translate()'> 与 CSS translateY 会冲突，"
                "必须只用 fadeIn（opacity 变化）"
            )

        # 检查 component-card 是否使用了正确的 fadeIn
        if 'component-card' in self.content:
            if 'fadeIn' not in self.content and 'fade-in' not in self.content:
                self.errors.append(
                    "[动画] component-card 类未使用 fadeIn 动画"
                )
            else:
                self.infos.append("[动画] component-card 使用 fadeIn ✓")

        # 检查带 translate 的 <g> 是否同时有 class（会触发动画冲突的条件）
        translate_with_class = re.findall(
            r'<g\s[^>]*transform="translate[^"]*"[^>]*class="([^"]*)"',
            self.content
        )
        for cls in translate_with_class:
            if 'component-card' in cls and (
                'translateY' in self.content or 'scale' in self.content
            ):
                self.errors.append(
                    f"[动画] <g transform='translate...'> 使用了 class='{cls}'，"
                    "且存在 transform CSS 动画，会导致模型位置错乱"
                )

    # ============================================================
    # 报告输出
    # ============================================================

    def report(self):
        print(f"\n{'='*60}")
        print(f"  领域模型图验证报告")
        print(f"  文件: {self.svg_path.name}")
        print(f"{'='*60}")

        if self.infos:
            print(f"\n📊 统计信息:")
            for info in self.infos:
                print(f"  {info}")

        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}) — 必须修复:")
            for i, err in enumerate(self.errors, 1):
                print(f"  {i}. {err}")

        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}) — 建议修复:")
            for i, warn in enumerate(self.warnings, 1):
                print(f"  {i}. {warn}")

        if not self.errors and not self.warnings:
            print("\n✅ 验证通过！符合四色建模领域模型图规范。")
        elif not self.errors:
            print(f"\n✅ 无错误（有 {len(self.warnings)} 个警告）")
        else:
            print(f"\n❌ 验证不通过（{len(self.errors)} 个错误，{len(self.warnings)} 个警告）")

        print(f"{'='*60}\n")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 model_diagram_validator.py <svg文件路径>")
        sys.exit(1)

    svg_path = sys.argv[1]
    validator = ModelDiagramValidator(svg_path)
    is_valid = validator.validate()
    validator.report()

    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
