#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件连线生成器 - ComponentLineGenerator

基于Python原生标准库实现轴对齐矩形组件间的90°折线连线生成。
适用于：领域模型图、系统架构图、部署架构图、流程图等任何需要
矩形组件连线的场景。

核心特性：
- 90°折线约束（水平/垂直线段交替）
- 组件避障（线段和拐点均不得进入组件区域）
- 四边中心起止点（L/R/T/B）
- 按「折线数最少→路径最短」优先级筛选最优路径

使用示例：
    # 模型图场景
    generator = ComponentLineGenerator()
    path = generator.get_best_path(start_model, end_model, all_models)
    
    # 架构图场景（组件即服务节点）
    path = generator.get_best_path(start_service, end_service, all_services)
"""

from typing import Dict, List, Tuple, Optional, Any
import math


# ==================== 自定义异常 ====================

class NoValidPathError(Exception):
    """当无法找到任何有效路径时抛出"""
    
    def __init__(self, start_id: Any, end_id: Any, max_turns: int):
        self.start_id = start_id
        self.end_id = end_id
        self.max_turns = max_turns
        super().__init__(
            f"无法在最大折线数 {max_turns} 内找到从 '{start_id}' 到 '{end_id}' 的有效路径"
        )


# ==================== 核心类 ====================

class ComponentLineGenerator:
    """
    组件连线生成器
    
    生成轴对齐矩形组件之间的90°折线路径，支持组件避障和最优路径筛选。
    
    适用场景：
    - 领域模型图（模型即组件）
    - 系统架构图（服务/模块即组件）
    - 部署架构图（服务器/容器即组件）
    - 流程图（流程节点即组件）
    
    Attributes:
        EPS: 浮点精度阈值，用于同行/同列/贴合判定（默认1.0）
        MAX_TURNS: 最大折线数阈值，防止无限循环（默认10）
    """
    
    # 类常量（可外部修改）
    EPS: float = 1.0  # 像素级精度，从0.01改为1.0
    MAX_TURNS: int = 10
    MIN_SEGMENT_LENGTH: float = 15.0  # 出发/进入线段最小长度（像素）
    CORNER_RADIUS: float = 8.0  # 拐角圆角半径（像素）
    
    def __init__(self):
        """初始化生成器，创建路径缓存"""
        # 路径缓存字典，键为(start_id, end_id)元组
        self._cache: Dict[Tuple[Any, Any], dict] = {}
    
    # ==================== 公共API方法 ====================
    
    def get_side_centers(self, component: dict) -> Dict[str, Tuple[float, float]]:
        """
        计算组件四边中心坐标
        
        Args:
            component: 组件字典，包含x1, y1, x2, y2键
            
        Returns:
            四边中心字典，键为L/R/T/B，值为(x, y)坐标元组
            
        Example:
            >>> comp = {"id": "A", "x1": 0, "y1": 0, "x2": 100, "y2": 50}
            >>> generator.get_side_centers(comp)
            {'L': (0, 25.0), 'R': (100, 25.0), 'T': (50.0, 0), 'B': (50.0, 50)}
        """
        x1, y1, x2, y2 = component["x1"], component["y1"], component["x2"], component["y2"]
        return {
            "L": (x1, round((y1 + y2) / 2, 2)),      # 左中心
            "R": (x2, round((y1 + y2) / 2, 2)),      # 右中心
            "T": (round((x1 + x2) / 2, 2), y1),      # 上中心
            "B": (round((x1 + x2) / 2, 2), y2),      # 下中心
        }
    
    def is_same_row(self, comp1: dict, comp2: dict) -> bool:
        """
        判定两个组件是否同行
        
        同行判定：两个组件中心y坐标差值的绝对值 < EPS
        
        Args:
            comp1: 第一个组件字典
            comp2: 第二个组件字典
            
        Returns:
            True表示同行，False表示不同行
        """
        cy1 = (comp1["y1"] + comp1["y2"]) / 2
        cy2 = (comp2["y1"] + comp2["y2"]) / 2
        return abs(cy1 - cy2) < self.EPS
    
    def is_same_col(self, comp1: dict, comp2: dict) -> bool:
        """
        判定两个组件是否同列
        
        同列判定：两个组件中心x坐标差值的绝对值 < EPS
        
        Args:
            comp1: 第一个组件字典
            comp2: 第二个组件字典
            
        Returns:
            True表示同列，False表示不同列
        """
        cx1 = (comp1["x1"] + comp1["x2"]) / 2
        cx2 = (comp2["x1"] + comp2["x2"]) / 2
        return abs(cx1 - cx2) < self.EPS
    
    def is_blocked(
        self,
        segment: Tuple[Tuple[float, float], Tuple[float, float]],
        all_components: List[dict],
        start_id: Any,
        end_id: Any
    ) -> bool:
        """
        检测线段是否被阻挡
        
        阻挡判定：线段与任何非起止组件的矩形区域相交/重叠
        起止组件本身不计入阻挡判定
        
        Args:
            segment: 线段，格式为((x1, y1), (x2, y2))
            all_components: 所有组件列表
            start_id: 源组件ID
            end_id: 目标组件ID
            
        Returns:
            True表示被阻挡，False表示未被阻挡
        """
        (x1, y1), (x2, y2) = segment
        
        # 确保是水平或垂直线段
        if x1 != x2 and y1 != y2:
            raise ValueError("只支持水平或垂直线段")
        
        for comp in all_components:
            comp_id = comp.get("id") or comp.get("component_id") or comp.get("model_id")
            
            # 跳过起止组件
            if comp_id == start_id or comp_id == end_id:
                continue
            
            # 检测线段是否与组件相交
            if self._segment_intersect_rect(segment, comp):
                return True
        
        return False
    
    def generate_direct_line(
        self,
        start_model: dict,
        end_model: dict,
        all_models: List[dict]
    ) -> Optional[dict]:
        """
        生成同行/同列的直连路径（折线数=0）
        
        仅当两个模型同行或同列时，才可能生成直连路径。
        同行：源在左用R→L，源在右用L→R
        同列：源在上用B→T，源在下用T→B
        
        Args:
            start_model: 源模型字典
            end_model: 目标模型字典
            all_models: 所有模型列表（用于检测中间阻挡）
            
        Returns:
            路径字典（有有效路径时）或None（无有效路径时）
        """
        start_id = start_model["model_id"]
        end_id = end_model["model_id"]
        
        # 获取四边中心
        start_centers = self.get_side_centers(start_model)
        end_centers = self.get_side_centers(end_model)
        
        # 同行情况
        if self.is_same_row(start_model, end_model):
            # 判断左右关系
            if start_model["x2"] <= end_model["x1"]:
                # 源在左，目标在右：R → L
                from_side, to_side = "R", "L"
            elif end_model["x2"] <= start_model["x1"]:
                # 源在右，目标在左：L → R
                from_side, to_side = "L", "R"
            else:
                # X轴有重叠，无法直连
                return None
            
            start_point = start_centers[from_side]
            end_point = end_centers[to_side]
            
            # 检测是否贴合（边对边无间隙）
            if from_side == "R" and to_side == "L":
                is_adjacent = abs(start_model["x2"] - end_model["x1"]) < self.EPS
            elif from_side == "L" and to_side == "R":
                is_adjacent = abs(start_model["x1"] - end_model["x2"]) < self.EPS
            else:
                is_adjacent = False
            
            # 贴合直接通过，否则检测阻挡（使用所有模型列表）
            if is_adjacent or not self.is_blocked(
                (start_point, end_point), all_models, start_id, end_id
            ):
                return self._create_path_dict(
                    start_id, start_point, end_id, end_point,
                    turns=0, inflections=[], segments=[(start_point, end_point)]
                )
        
        # 同列情况
        if self.is_same_col(start_model, end_model):
            # 判断上下关系
            if start_model["y2"] <= end_model["y1"]:
                # 源在上，目标在下：B → T
                from_side, to_side = "B", "T"
            elif end_model["y2"] <= start_model["y1"]:
                # 源在下，目标在上：T → B
                from_side, to_side = "T", "B"
            else:
                # Y轴有重叠，无法直连
                return None
            
            start_point = start_centers[from_side]
            end_point = end_centers[to_side]
            
            # 检测是否贴合
            if from_side == "B" and to_side == "T":
                is_adjacent = abs(start_model["y2"] - end_model["y1"]) < self.EPS
            elif from_side == "T" and to_side == "B":
                is_adjacent = abs(start_model["y1"] - end_model["y2"]) < self.EPS
            else:
                is_adjacent = False
            
            # 贴合直接通过，否则检测阻挡（使用所有模型列表）
            if is_adjacent or not self.is_blocked(
                (start_point, end_point), all_models, start_id, end_id
            ):
                return self._create_path_dict(
                    start_id, start_point, end_id, end_point,
                    turns=0, inflections=[], segments=[(start_point, end_point)]
                )
        
        return None
    
    def generate_turn_paths(
        self,
        start_model: dict,
        end_model: dict,
        all_models: List[dict],
        turns: int
    ) -> List[dict]:
        """
        生成指定折线数下的所有有效路径
        
        遍历源模型4边 × 目标模型4边 = 16组起止点组合，
        生成每组对应的折线路径，过滤掉被阻挡的路径。
        
        Args:
            start_model: 源模型字典
            end_model: 目标模型字典
            all_models: 所有模型列表（用于避障检测）
            turns: 折线数（拐点数 = 折线数 + 1）
            
        Returns:
            有效路径字典列表，可能为空列表
        """
        if turns < 1:
            raise ValueError("折线数必须>=1，使用generate_direct_line生成直连路径")
        
        start_id = start_model["model_id"]
        end_id = end_model["model_id"]
        
        # 获取四边中心
        start_centers = self.get_side_centers(start_model)
        end_centers = self.get_side_centers(end_model)
        
        valid_paths = []
        
        # 遍历16组起止点组合
        sides = ["L", "R", "T", "B"]
        for from_side in sides:
            for to_side in sides:
                start_point = start_centers[from_side]
                end_point = end_centers[to_side]
                
                # 生成该折线数下的所有可能路径
                paths = self._generate_paths_for_turns(
                    start_point, end_point, from_side, to_side, turns
                )
                
                for path_points in paths:
                    # 验证路径有效性（传入from_side和to_side以验证方向）
                    if self._validate_path(path_points, all_models, start_id, end_id, from_side, to_side):
                        # 构建路径字典
                        segments = []
                        for i in range(len(path_points) - 1):
                            segments.append((path_points[i], path_points[i + 1]))
                        
                        inflections = path_points[1:-1]  # 去掉起止点
                        
                        path_dict = self._create_path_dict(
                            start_id, start_point, end_id, end_point,
                            turns=turns, inflections=inflections, segments=segments
                        )
                        valid_paths.append(path_dict)
        
        return valid_paths
    
    def get_best_path(
        self,
        start_model: dict,
        end_model: dict,
        all_models: List[dict]
    ) -> dict:
        """
        获取两个模型间的最优路径（主方法）
        
        新算法思路：
        1. 用斜线距离找到最优起止边组合
        2. 基于起止点方向约束，计算可行拐点
        3. 验证拐点并生成90°折线路径
        
        路径筛选优先级：
        1. 折线数最少
        2. 曼哈顿距离最短
        
        Args:
            start_model: 源模型字典
            end_model: 目标模型字典
            all_models: 所有模型列表
            
        Returns:
            最优路径的结构化字典
        """
        start_id = start_model["model_id"]
        end_id = end_model["model_id"]
        
        # 参数校验
        self._validate_models(start_model, end_model, all_models)
        
        # 检查缓存
        cache_key = (start_id, end_id)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # 第一步：用斜线距离获取排序后的起止边组合
        side_combos = self._select_best_sides(start_model, end_model)
        
        # 第二步：按折线数递增尝试，找到第一个可行路径
        for turns in range(0, self.MAX_TURNS + 1):
            # 按斜线距离顺序尝试每个边组合
            for from_side, to_side, start_point, end_point, _ in side_combos:
                path = self._generate_path_with_turns(
                    start_model, end_model, all_models,
                    start_point, end_point, from_side, to_side, turns
                )
                if path:
                    # 缓存结果（双向缓存）
                    self._cache[(start_id, end_id)] = path
                    self._cache[(end_id, start_id)] = path
                    return path
        
        raise NoValidPathError(start_id, end_id, self.MAX_TURNS)
    
    def get_rounded_svg_path(self, path_dict: dict, radius: Optional[float] = None) -> str:
        """
        将路径字典转换为带圆角的SVG path字符串
        
        使用二次贝塞尔曲线(Q命令)在拐点处绘制圆角
        
        Args:
            path_dict: 路径字典，包含segments和inflections
            radius: 圆角半径，默认使用CORNER_RADIUS
            
        Returns:
            SVG path的d属性字符串
            
        Example:
            >>> path = generator.get_best_path(start, end, all_models)
            >>> d = generator.get_rounded_svg_path(path)
            >>> f'<path d="{d}" .../>'
        """
        if radius is None:
            radius = self.CORNER_RADIUS
        
        # 获取所有点（起点 -> 拐点 -> 终点）
        points = [path_dict['start_point']]
        points.extend(path_dict['inflections'])
        points.append(path_dict['end_point'])
        
        if len(points) < 2:
            return ""
        
        # 如果只有两个点（直连），返回简单的线段
        if len(points) == 2:
            x1, y1 = points[0]
            x2, y2 = points[1]
            return f"M {x1} {y1} L {x2} {y2}"
        
        # 构建带圆角的path
        path_parts = []
        
        # 起点
        sx, sy = points[0]
        path_parts.append(f"M {sx} {sy}")
        
        # 处理每个拐点
        for i in range(1, len(points) - 1):
            prev_x, prev_y = points[i - 1]
            curr_x, curr_y = points[i]
            next_x, next_y = points[i + 1]
            
            # 计算拐点前后方向的单位向量
            # 前一段方向（从prev到curr）
            dx1 = curr_x - prev_x
            dy1 = curr_y - prev_y
            len1 = math.sqrt(dx1 * dx1 + dy1 * dy1)
            if len1 > 0:
                dx1 /= len1
                dy1 /= len1
            
            # 后一段方向（从curr到next）
            dx2 = next_x - curr_x
            dy2 = next_y - curr_y
            len2 = math.sqrt(dx2 * dx2 + dy2 * dy2)
            if len2 > 0:
                dx2 /= len2
                dy2 /= len2
            
            # 计算实际圆角半径（确保不超过线段长度的一半）
            actual_radius = min(radius, len1 / 2, len2 / 2)
            actual_radius = max(actual_radius, 0)  # 确保非负
            
            # 圆角起点：从curr沿前一段反方向移动radius
            corner_start_x = curr_x - dx1 * actual_radius
            corner_start_y = curr_y - dy1 * actual_radius
            
            # 圆角终点：从curr沿后一段方向移动radius
            corner_end_x = curr_x + dx2 * actual_radius
            corner_end_y = curr_y + dy2 * actual_radius
            
            # 绘制到圆角起点
            path_parts.append(f"L {round(corner_start_x, 2)} {round(corner_start_y, 2)}")
            
            # 绘制圆角（使用二次贝塞尔曲线）
            # 控制点就是拐点本身
            path_parts.append(f"Q {round(curr_x, 2)} {round(curr_y, 2)} {round(corner_end_x, 2)} {round(corner_end_y, 2)}")
        
        # 绘制到最后一个拐点到终点的线段
        last_x, last_y = points[-1]
        path_parts.append(f"L {last_x} {last_y}")
        
        return " ".join(path_parts)
    
    def _calc_model_center(self, model: dict) -> Tuple[float, float]:
        """计算模型中心坐标"""
        cx = (model["x1"] + model["x2"]) / 2
        cy = (model["y1"] + model["y2"]) / 2
        return (round(cx, 2), round(cy, 2))
    
    def _calc_euclidean_distance(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float]
    ) -> float:
        """计算两点间欧几里得距离（斜线距离）"""
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
    
    def _select_best_sides(
        self,
        start_model: dict,
        end_model: dict
    ) -> List[Tuple[str, str, Tuple[float, float], Tuple[float, float], float]]:
        """
        基于斜线距离排序所有起止边组合
        
        遍历16种组合，按欧几里得距离排序返回。
        
        Returns:
            排序后的列表：[(from_side, to_side, start_point, end_point, distance), ...]
        """
        start_centers = self.get_side_centers(start_model)
        end_centers = self.get_side_centers(end_model)
        
        combos = []
        
        for from_side in ["L", "R", "T", "B"]:
            for to_side in ["L", "R", "T", "B"]:
                start_point = start_centers[from_side]
                end_point = end_centers[to_side]
                distance = self._calc_euclidean_distance(start_point, end_point)
                combos.append((from_side, to_side, start_point, end_point, distance))
        
        # 按距离排序
        combos.sort(key=lambda x: x[4])
        return combos
    
    def _generate_path_with_turns(
        self,
        start_model: dict,
        end_model: dict,
        all_models: List[dict],
        start_point: Tuple[float, float],
        end_point: Tuple[float, float],
        from_side: str,
        to_side: str,
        turns: int
    ) -> Optional[dict]:
        """
        基于指定折线数生成最优路径
        
        核心思路：根据起止边方向约束，计算可行拐点位置，
        选择最短且不被阻挡的路径。
        
        Args:
            start_model: 源模型
            end_model: 目标模型
            all_models: 所有模型列表
            start_point: 起点坐标
            end_point: 终点坐标
            from_side: 起始边（L/R/T/B）
            to_side: 目标边（L/R/T/B）
            turns: 折线数（拐点数）
            
        Returns:
            路径字典或None（无可行路径）
        """
        start_id = start_model["model_id"]
        end_id = end_model["model_id"]
        sx, sy = start_point
        ex, ey = end_point
        
        # 折线数=0：直连（必须同行或同列）
        if turns == 0:
            if self.is_same_row(start_model, end_model) or self.is_same_col(start_model, end_model):
                path_points = [start_point, end_point]
                if self._validate_path(path_points, all_models, start_id, end_id, from_side, to_side):
                    return self._create_path_dict(
                        start_id, start_point, end_id, end_point,
                        turns=0, inflections=[], segments=[(start_point, end_point)]
                    )
            return None
        
        # 折线数=1：1个拐点，2段线段（L形）
        if turns == 1:
            # 根据起止边方向确定拐点类型
            is_from_h = from_side in ("L", "R")  # 从水平边出发
            is_to_h = to_side in ("L", "R")     # 到水平边结束
            
            candidates = []
            
            if is_from_h and not is_to_h:
                # 水平边 -> 垂直边：先水平后垂直
                # 拐点：(ex, sy)
                candidates.append((ex, sy))
            elif not is_from_h and is_to_h:
                # 垂直边 -> 水平边：先垂直后水平
                # 拐点：(sx, ey)
                candidates.append((sx, ey))
            # 同类型边无法用1折线连接
            
            for inflection in candidates:
                # 检查最小线段长度约束
                seg1_len = self._calc_euclidean_distance(start_point, inflection)
                seg2_len = self._calc_euclidean_distance(inflection, end_point)
                
                if seg1_len < self.MIN_SEGMENT_LENGTH - self.EPS:
                    continue
                if seg2_len < self.MIN_SEGMENT_LENGTH - self.EPS:
                    continue
                
                path_points = [start_point, inflection, end_point]
                if self._validate_path(path_points, all_models, start_id, end_id, from_side, to_side):
                    segments = [(start_point, inflection), (inflection, end_point)]
                    return self._create_path_dict(
                        start_id, start_point, end_id, end_point,
                        turns=1, inflections=[inflection], segments=segments
                    )
            return None
        
        # 折线数=2：2个拐点，3段线段（Z形/U形）
        if turns == 2:
            candidates = []
            is_from_h = from_side in ("L", "R")
            is_to_h = to_side in ("L", "R")
            
            if is_from_h and is_to_h:
                # 水平边 -> 水平边：水平→垂直→水平
                # 拐点1：(mid_x, sy)，拐点2：(mid_x, ey)
                # 需要满足：|mid_x - sx| >= 20（第一段长度）
                #           |mid_x - ex| >= 20（最后一段长度）
                
                # 确定方向
                from_dir = -1 if from_side == "L" else 1  # L边往左(-1)，R边往右(+1)
                to_dir = 1 if to_side == "L" else -1      # L边往右(+1)，R边往左(-1)
                
                # 生成满足20px约束的mid_x候选
                from_candidates = self._generate_candidates_with_min_length(sx, ex, from_dir)
                to_candidates = self._generate_candidates_with_min_length(ex, sx, to_dir)
                
                # 取交集：同时满足从起点出发>=20px，到终点>=20px
                for mid_x in from_candidates:
                    if abs(mid_x - ex) >= self.MIN_SEGMENT_LENGTH - self.EPS:
                        candidates.append([(mid_x, sy), (mid_x, ey)])
                    
            elif not is_from_h and not is_to_h:
                # 垂直边 -> 垂直边：垂直→水平→垂直
                # 确定方向
                from_dir = -1 if from_side == "T" else 1  # T边往上(-1)，B边往下(+1)
                to_dir = 1 if to_side == "T" else -1      # T边往下(+1)，B边往上(-1)
                
                # 生成满足20px约束的mid_y候选
                from_candidates = self._generate_candidates_with_min_length(sy, ey, from_dir)
                to_candidates = self._generate_candidates_with_min_length(ey, sy, to_dir)
                
                # 取交集
                for mid_y in from_candidates:
                    if abs(mid_y - ey) >= self.MIN_SEGMENT_LENGTH - self.EPS:
                        # 路径：先垂直，再水平，再垂直
                        # 需要确定mid_x（水平段的位置）
                        mid_x_candidates = self._generate_mid_candidates(sx, ex, 50)
                        for mid_x in mid_x_candidates:
                            candidates.append([(sx, mid_y), (mid_x, mid_y), (mid_x, ey)])
            
            # 交叉类型（水平→垂直 或 垂直→水平）通常1折可以解决，
            # 如果1折被阻挡，则需要3折以上
            
            best_path = None
            best_length = float('inf')
            
            for inflections in candidates:
                path_points = [start_point] + inflections + [end_point]
                if self._validate_path(path_points, all_models, start_id, end_id, from_side, to_side):
                    segments = []
                    for i in range(len(path_points) - 1):
                        segments.append((path_points[i], path_points[i + 1]))
                    length = self._calc_manhattan_length(segments)
                    if length < best_length:
                        best_length = length
                        best_path = self._create_path_dict(
                            start_id, start_point, end_id, end_point,
                            turns=2, inflections=inflections, segments=segments
                        )
            
            return best_path
        
        # 折线数>2：暂不实现，返回None
        return None
    
    def _generate_mid_candidates(self, s: float, e: float, step: float) -> List[float]:
        """生成中间位置候选值"""
        candidates = [
            (s + e) / 2,  # 中点
        ]
        # 添加绕行候选点
        for offset in [step, step * 2, step * 3]:
            candidates.extend([min(s, e) - offset, max(s, e) + offset])
        
        # 去重并排序
        unique = []
        seen = set()
        for c in candidates:
            key = round(c, 2)
            if key not in seen:
                seen.add(key)
                unique.append(key)
        return unique
    
    def _generate_candidates_with_min_length(
        self,
        start: float,
        end: float,
        direction: int  # 1表示正向（+），-1表示负向（-）
    ) -> List[float]:
        """
        生成满足最小长度约束的候选点
        
        从start出发，沿direction方向至少MIN_SEGMENT_LENGTH距离
        """
        candidates = []
        
        # 计算最小距离点
        min_point = start + direction * self.MIN_SEGMENT_LENGTH
        
        # 基础候选：刚好20px的点
        candidates.append(round(min_point, 2))
        
        # 更远的位置
        for offset in [50, 100, 150]:
            point = start + direction * (self.MIN_SEGMENT_LENGTH + offset)
            candidates.append(round(point, 2))
        
        # 如果方向是朝向end的，也考虑end附近的位置
        if (direction > 0 and end > start) or (direction < 0 and end < start):
            # 在end之前20px的位置
            before_end = end - direction * self.MIN_SEGMENT_LENGTH
            if abs(before_end - start) >= self.MIN_SEGMENT_LENGTH:
                candidates.append(round(before_end, 2))
        
        # 去重并过滤掉不满足最小长度的
        valid = []
        seen = set()
        for c in candidates:
            if c in seen:
                continue
            seen.add(c)
            # 确保距离start至少MIN_SEGMENT_LENGTH
            if abs(c - start) >= self.MIN_SEGMENT_LENGTH - self.EPS:
                valid.append(c)
        
        return valid
    
    def _segment_intersect_rect(
        self,
        segment: Tuple[Tuple[float, float], Tuple[float, float]],
        model: dict
    ) -> bool:
        """
        检测线段与模型矩形是否相交
        
        相交判定：
        - 水平线段：y在模型y范围内，且x范围与模型x范围有交集
        - 垂直线段：x在模型x范围内，且y范围与模型y范围有交集
        - 贴边也算相交（线段在模型边界上）
        """
        (x1, y1), (x2, y2) = segment
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        
        model_left, model_right = model["x1"], model["x2"]
        model_top, model_bottom = model["y1"], model["y2"]
        
        # 水平线段
        if y1 == y2:
            # y在模型y范围内（含边界）
            if model_top - self.EPS <= y1 <= model_bottom + self.EPS:
                # x范围与模型x范围有交集
                if not (max_x < model_left or min_x > model_right):
                    return True
        
        # 垂直线段
        if x1 == x2:
            # x在模型x范围内（含边界）
            if model_left - self.EPS <= x1 <= model_right + self.EPS:
                # y范围与模型y范围有交集
                if not (max_y < model_top or min_y > model_bottom):
                    return True
        
        return False
    
    def _calc_manhattan_length(self, segments: List[Tuple[Tuple[float, float], Tuple[float, float]]]) -> float:
        """计算路径的曼哈顿距离"""
        total = 0.0
        for (x1, y1), (x2, y2) in segments:
            total += abs(x2 - x1) + abs(y2 - y1)
        return round(total, 2)
    
    def _is_point_in_model(self, point: Tuple[float, float], model: dict) -> bool:
        """检测点是否在模型矩形内（含边界）"""
        x, y = point
        return (
            model["x1"] - self.EPS <= x <= model["x2"] + self.EPS and
            model["y1"] - self.EPS <= y <= model["y2"] + self.EPS
        )
    
    def _generate_paths_for_turns(
        self,
        start_point: Tuple[float, float],
        end_point: Tuple[float, float],
        from_side: str,
        to_side: str,
        turns: int
    ) -> List[List[Tuple[float, float]]]:
        """
        生成指定折线数下的所有可能路径点序列
        
        核心约束：
        - 从某边出发的第一段必须垂直于该边
        - 到达某边的最后一段必须垂直于该边
        """
        sx, sy = start_point
        ex, ey = end_point
        paths = []
        
        # 定义边的方向：水平边(L/R)或垂直边(T/B)
        horizontal_sides = {"L", "R"}
        vertical_sides = {"T", "B"}
        
        is_from_horizontal = from_side in horizontal_sides
        is_to_horizontal = to_side in horizontal_sides
        
        if turns == 1:
            # 1转折（L形）：2段线段，1个拐点
            # 情况1：先水平后垂直
            if is_from_horizontal and not is_to_horizontal:
                # 从L/R出发，到T/B：先水平移动，再垂直移动
                paths.append([(sx, sy), (ex, sy), (ex, ey)])
            # 情况2：先垂直后水平
            elif not is_from_horizontal and is_to_horizontal:
                # 从T/B出发，到L/R：先垂直移动，再水平移动
                paths.append([(sx, sy), (sx, ey), (ex, ey)])
            # 情况3：同方向边，无法1转折（如L→R或T→B）
            # 这种情况需要2转折
        
        elif turns == 2:
            # 2转折（U形/Z形）：3段线段，2个拐点
            if is_from_horizontal and is_to_horizontal:
                # L/R → L/R：需要绕行
                # 路径：水平→垂直→水平
                # 注意：从L/R出发，第一段必须是水平的
                mid_y_candidates = [
                    sy, ey,  # 起点或终点的y
                    (sy + ey) / 2,  # 中点
                    min(sy, ey) - 50,  # 上方绕行
                    max(sy, ey) + 50,  # 下方绕行
                    min(sy, ey) - 100,  # 更上方绕行
                    max(sy, ey) + 100,  # 更下方绕行
                    min(sy, ey) - 150,
                    max(sy, ey) + 150,
                ]
                mid_x_candidates = [
                    (sx + ex) / 2,
                    min(sx, ex) - 50,
                    max(sx, ex) + 50,
                    min(sx, ex) - 100,
                    max(sx, ex) + 100,
                ]
                for mid_y in mid_y_candidates:
                    for mid_x in mid_x_candidates:
                        paths.append([
                            (sx, sy),
                            (round(mid_x, 2), sy),      # 第一段：水平
                            (round(mid_x, 2), round(mid_y, 2)),  # 第二段：垂直
                            (ex, round(mid_y, 2)),      # 第三段：水平
                            (ex, ey)
                        ])
            
            elif not is_from_horizontal and not is_to_horizontal:
                # T/B → T/B：需要绕行
                # 路径：垂直→水平→垂直
                # 注意：从T/B出发，第一段必须是垂直的
                mid_x_candidates = [
                    sx, ex,
                    (sx + ex) / 2,
                    min(sx, ex) - 50,
                    max(sx, ex) + 50,
                    min(sx, ex) - 100,
                    max(sx, ex) + 100,
                    min(sx, ex) - 150,
                    max(sx, ex) + 150,
                ]
                mid_y_candidates = [
                    (sy + ey) / 2,
                    min(sy, ey) - 50,
                    max(sy, ey) + 50,
                    min(sy, ey) - 100,
                    max(sy, ey) + 100,
                ]
                for mid_x in mid_x_candidates:
                    for mid_y in mid_y_candidates:
                        paths.append([
                            (sx, sy),
                            (sx, round(mid_y, 2)),      # 第一段：垂直
                            (round(mid_x, 2), round(mid_y, 2)),  # 第二段：水平
                            (round(mid_x, 2), ey),      # 第三段：垂直
                            (ex, ey)
                        ])
            
            else:
                # 交叉方向但1转折不可行，尝试2转折
                # 路径：垂直→水平→垂直 或 水平→垂直→水平
                if is_from_horizontal:  # L/R → T/B
                    # 从L/R出发，第一段必须是水平的
                    # 到T/B，最后一段必须是垂直的
                    # 路径：水平→垂直→水平→垂直
                    mid_x_candidates = [
                        (sx + ex) / 2,
                        min(sx, ex) - 50,
                        max(sx, ex) + 50,
                        min(sx, ex) - 100,
                        max(sx, ex) + 100,
                    ]
                    mid_y_candidates = [
                        (sy + ey) / 2,
                        min(sy, ey) - 50,
                        max(sy, ey) + 50,
                    ]
                    for mid_x in mid_x_candidates:
                        for mid_y in mid_y_candidates:
                            paths.append([
                                (sx, sy),
                                (round(mid_x, 2), sy),      # 第一段：水平
                                (round(mid_x, 2), round(mid_y, 2)),  # 第二段：垂直
                                (ex, round(mid_y, 2)),      # 第三段：水平
                                (ex, ey)                     # 第四段：垂直（到T/B）
                            ])
                else:  # T/B → L/R
                    # 从T/B出发，第一段必须是垂直的
                    # 到L/R，最后一段必须是水平的
                    # 路径：垂直→水平→垂直→水平
                    mid_x_candidates = [
                        (sx + ex) / 2,
                        min(sx, ex) - 50,
                        max(sx, ex) + 50,
                        min(sx, ex) - 100,
                        max(sx, ex) + 100,
                    ]
                    mid_y_candidates = [
                        (sy + ey) / 2,
                        min(sy, ey) - 50,
                        max(sy, ey) + 50,
                    ]
                    for mid_x in mid_x_candidates:
                        for mid_y in mid_y_candidates:
                            paths.append([
                                (sx, sy),
                                (sx, round(mid_y, 2)),      # 第一段：垂直
                                (round(mid_x, 2), round(mid_y, 2)),  # 第二段：水平
                                (round(mid_x, 2), ey),      # 第三段：垂直
                                (ex, ey)                     # 第四段：水平（到L/R）
                            ])
        
        elif turns >= 3:
            # 3+转折：使用通用路径生成
            paths.extend(self._generate_complex_paths(
                start_point, end_point, from_side, to_side, turns
            ))
        
        # 去除重复路径并坐标取整
        unique_paths = []
        seen = set()
        for path in paths:
            # 坐标取整
            rounded_path = [(round(x, 2), round(y, 2)) for x, y in path]
            # 去除连续重复点
            clean_path = [rounded_path[0]]
            for i in range(1, len(rounded_path)):
                if rounded_path[i] != rounded_path[i-1]:
                    clean_path.append(rounded_path[i])
            
            path_key = tuple(clean_path)
            if path_key not in seen and len(clean_path) >= 2:
                seen.add(path_key)
                unique_paths.append(clean_path)
        
        return unique_paths
    
    def _generate_complex_paths(
        self,
        start_point: Tuple[float, float],
        end_point: Tuple[float, float],
        from_side: str,
        to_side: str,
        turns: int
    ) -> List[List[Tuple[float, float]]]:
        """生成3+转折的复杂路径"""
        sx, sy = start_point
        ex, ey = end_point
        paths = []
        
        # 根据出发边确定初始方向
        horizontal_sides = {"L", "R"}
        is_from_horizontal = from_side in horizontal_sides
        
        # 生成一些通用的绕行路径模板
        # 3转折：4段线段
        if turns == 3:
            # 尝试在起点和终点周围生成绕行点
            offsets = [-100, -50, 50, 100, 150, 200]
            
            if is_from_horizontal:
                # 先水平移动
                for offset1 in offsets:
                    for offset2 in offsets:
                        mid_y1 = sy + offset1
                        mid_x = (sx + ex) / 2 + offset2
                        mid_y2 = ey + offset1
                        paths.append([
                            (sx, sy),
                            (sx, round(mid_y1, 2)),
                            (round(mid_x, 2), round(mid_y1, 2)),
                            (round(mid_x, 2), round(mid_y2, 2)),
                            (ex, round(mid_y2, 2)),
                            (ex, ey)
                        ])
            else:
                # 先垂直移动
                for offset1 in offsets:
                    for offset2 in offsets:
                        mid_x1 = sx + offset1
                        mid_y = (sy + ey) / 2 + offset2
                        mid_x2 = ex + offset1
                        paths.append([
                            (sx, sy),
                            (round(mid_x1, 2), sy),
                            (round(mid_x1, 2), round(mid_y, 2)),
                            (round(mid_x2, 2), round(mid_y, 2)),
                            (round(mid_x2, 2), ey),
                            (ex, ey)
                        ])
        
        # 4+转折：递归生成更复杂路径
        if turns >= 4:
            # 使用更激进的绕行策略
            margin = 50 * (turns - 2)
            
            if is_from_horizontal:
                # 大幅绕行
                mid_y = (sy + ey) / 2
                paths.append([
                    (sx, sy),
                    (sx, round(mid_y - margin, 2)),
                    (round((sx + ex) / 2, 2), round(mid_y - margin, 2)),
                    (round((sx + ex) / 2, 2), round(mid_y + margin, 2)),
                    (ex, round(mid_y + margin, 2)),
                    (ex, ey)
                ])
            else:
                mid_x = (sx + ex) / 2
                paths.append([
                    (sx, sy),
                    (round(mid_x - margin, 2), sy),
                    (round(mid_x - margin, 2), round((sy + ey) / 2, 2)),
                    (round(mid_x + margin, 2), round((sy + ey) / 2, 2)),
                    (round(mid_x + margin, 2), ey),
                    (ex, ey)
                ])
        
        return paths
    
    def _validate_path(
        self,
        path_points: List[Tuple[float, float]],
        all_models: List[dict],
        start_id: Any,
        end_id: Any,
        from_side: Optional[str] = None,
        to_side: Optional[str] = None
    ) -> bool:
        """
        验证路径是否有效
        
        验证项：
        1. 所有拐点不在任何模型内
        2. 所有线段不被阻挡
        3. 线段方向正确（水平或垂直）
        4. 从边出发/进入的方向正确（L/R边必须水平，T/B边必须垂直）
        """
        if len(path_points) < 2:
            return False
        
        start_model = None
        end_model = None
        for m in all_models:
            if m["model_id"] == start_id:
                start_model = m
            if m["model_id"] == end_id:
                end_model = m
        
        # 验证拐点不在任何模型内（起止点除外）
        for i, point in enumerate(path_points):
            if i == 0 or i == len(path_points) - 1:
                continue  # 跳过起止点
            for model in all_models:
                if self._is_point_in_model(point, model):
                    return False
        
        # 验证所有线段
        for i in range(len(path_points) - 1):
            p1, p2 = path_points[i], path_points[i + 1]
            x1, y1 = p1
            x2, y2 = p2
            
            # 计算线段长度
            length = abs(x2 - x1) + abs(y2 - y1)  # 曼哈顿长度
            
            # 必须是水平或垂直线段
            if x1 != x2 and y1 != y2:
                return False
            
            # 检测是否被阻挡
            if self.is_blocked((p1, p2), all_models, start_id, end_id):
                return False
            
            # 验证从边出发的方向（第一段）
            if i == 0 and from_side:
                is_horizontal = y1 == y2  # 水平线段
                is_vertical = x1 == x2   # 垂直线段
                
                # L/R边出发必须是水平
                if from_side in ("L", "R") and not is_horizontal:
                    return False
                # T/B边出发必须是垂直
                if from_side in ("T", "B") and not is_vertical:
                    return False
                
                # 验证方向：起点往外走
                if from_side == "L" and x2 > x1:  # L边出发应往左（x减小）
                    return False
                if from_side == "R" and x2 < x1:  # R边出发应往右（x增加）
                    return False
                if from_side == "T" and y2 > y1:  # T边出发应往上（y减小）
                    return False
                if from_side == "B" and y2 < y1:  # B边出发应往下（y增加）
                    return False
            
            # 验证进入边的方向（最后一段）
            if i == len(path_points) - 2 and to_side:
                is_horizontal = y1 == y2  # 水平线段
                is_vertical = x1 == x2   # 垂直线段
                
                # 进入L/R边必须是水平
                if to_side in ("L", "R") and not is_horizontal:
                    return False
                # 进入T/B边必须是垂直
                if to_side in ("T", "B") and not is_vertical:
                    return False
                
                # 验证方向：终点往里走
                if to_side == "L" and x2 < x1:  # 进入L边应往右（x增加）
                    return False
                if to_side == "R" and x2 > x1:  # 进入R边应往左（x减小）
                    return False
                if to_side == "T" and y2 < y1:  # 进入T边应往下（y增加）
                    return False
                if to_side == "B" and y2 > y1:  # 进入B边应往上（y减小）
                    return False
        
        return True
    
    def _select_best_path(self, paths: List[dict]) -> dict:
        """
        从所有有效路径中选择最优路径
        
        优先级：
        1. 折线数最少
        2. 曼哈顿距离最短
        3. 拐点坐标排序（x从小到大→y从小到大）
        """
        if not paths:
            raise ValueError("路径列表为空")
        
        # 按优先级排序
        def sort_key(path):
            turns = path["turns"]
            length = path["total_length"]
            # 拐点坐标排序键
            inflections_key = []
            for x, y in path["inflections"]:
                inflections_key.append((x, y))
            return (turns, length, inflections_key)
        
        sorted_paths = sorted(paths, key=sort_key)
        return sorted_paths[0]
    
    def _create_path_dict(
        self,
        start_model_id: Any,
        start_point: Tuple[float, float],
        end_model_id: Any,
        end_point: Tuple[float, float],
        turns: int,
        inflections: List[Tuple[float, float]],
        segments: List[Tuple[Tuple[float, float], Tuple[float, float]]]
    ) -> dict:
        """创建标准化的路径字典"""
        total_length = self._calc_manhattan_length(segments)
        
        return {
            "start_model_id": start_model_id,
            "start_point": start_point,
            "end_model_id": end_model_id,
            "end_point": end_point,
            "turns": turns,
            "total_length": total_length,
            "inflections": inflections,
            "segments": segments
        }
    
    def _validate_models(
        self,
        start_model: dict,
        end_model: dict,
        all_models: List[dict]
    ) -> None:
        """验证模型参数合法性"""
        # 检查空列表
        if not all_models:
            raise ValueError("模型列表不可为空")
        
        # 检查起止模型相同
        if start_model["model_id"] == end_model["model_id"]:
            raise ValueError("起止模型不可为同一模型")
        
        # 检查模型几何参数
        for model in all_models:
            if model["x1"] >= model["x2"] or model["y1"] >= model["y2"]:
                raise ValueError(
                    f"模型 '{model['model_id']}' 几何参数非法（要求x1<x2且y1<y2）"
                )


# ==================== 测试用例 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("ComponentLineGenerator 测试")
    print("=" * 60)
    
    generator = ComponentLineGenerator()
    
    # ========== 场景1：同行无阻挡（直连路径） ==========
    print("\n【场景1】同行无阻挡 - 验证直连路径（折线数=0）")
    print("-" * 50)
    
    models_1 = [
        {"model_id": "A", "x1": 0, "y1": 0, "x2": 100, "y2": 50},
        {"model_id": "B", "x1": 150, "y1": 0, "x2": 250, "y2": 50},  # 同行，无阻挡
    ]
    
    try:
        path = generator.get_best_path(models_1[0], models_1[1], models_1)
        print(f"✅ 找到路径！")
        print(f"   折线数: {path['turns']}")
        print(f"   总长度: {path['total_length']}")
        print(f"   起点: {path['start_point']} ({path['start_model_id']})")
        print(f"   终点: {path['end_point']} ({path['end_model_id']})")
        print(f"   拐点: {path['inflections'] if path['inflections'] else '无'}")
        print(f"   线段数: {len(path['segments'])}")
        for i, seg in enumerate(path['segments']):
            print(f"      线段{i+1}: {seg[0]} → {seg[1]}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # ========== 场景2：同列有阻挡（绕行路径） ==========
    print("\n【场景2】同列有阻挡 - 验证折线数≥2的绕行路径")
    print("-" * 50)
    
    models_2 = [
        {"model_id": "A2", "x1": 0, "y1": 0, "x2": 100, "y2": 50},
        {"model_id": "C2", "x1": 0, "y1": 80, "x2": 100, "y2": 130},  # 阻挡物
        {"model_id": "B2", "x1": 0, "y1": 160, "x2": 100, "y2": 210},  # 同列，被C阻挡
    ]
    
    try:
        path = generator.get_best_path(models_2[0], models_2[2], models_2)
        print(f"✅ 找到路径！")
        print(f"   折线数: {path['turns']}")
        print(f"   总长度: {path['total_length']}")
        print(f"   起点: {path['start_point']} ({path['start_model_id']})")
        print(f"   终点: {path['end_point']} ({path['end_model_id']})")
        print(f"   拐点: {path['inflections']}")
        print(f"   线段数: {len(path['segments'])}")
        for i, seg in enumerate(path['segments']):
            print(f"      线段{i+1}: {seg[0]} → {seg[1]}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # ========== 场景3：不同行不同列（16组基础路径筛选） ==========
    print("\n【场景3】不同行不同列 - 验证16组基础路径筛选最优")
    print("-" * 50)
    
    models_3 = [
        {"model_id": "A3", "x1": 0, "y1": 0, "x2": 100, "y2": 50},
        {"model_id": "B3", "x1": 200, "y1": 100, "x2": 300, "y2": 150},  # 右下方
    ]
    
    try:
        path = generator.get_best_path(models_3[0], models_3[1], models_3)
        print(f"✅ 找到路径！")
        print(f"   折线数: {path['turns']}")
        print(f"   总长度: {path['total_length']}")
        print(f"   起点: {path['start_point']} ({path['start_model_id']})")
        print(f"   终点: {path['end_point']} ({path['end_model_id']})")
        print(f"   拐点: {path['inflections']}")
        print(f"   线段数: {len(path['segments'])}")
        for i, seg in enumerate(path['segments']):
            print(f"      线段{i+1}: {seg[0]} → {seg[1]}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # ========== 场景4：复杂阻挡场景 ==========
    print("\n【场景4】复杂阻挡场景 - 验证多转折绕行")
    print("-" * 50)
    
    models_4 = [
        {"model_id": "A4", "x1": 0, "y1": 0, "x2": 100, "y2": 50},      # 左上
        {"model_id": "B4", "x1": 200, "y1": 0, "x2": 300, "y2": 50},   # 右上
        {"model_id": "C4", "x1": 100, "y1": 100, "x2": 200, "y2": 150}, # 中间阻挡
        {"model_id": "D4", "x1": 0, "y1": 200, "x2": 100, "y2": 250},   # 左下
        {"model_id": "E4", "x1": 200, "y1": 200, "x2": 300, "y2": 250}, # 右下
    ]
    
    # A4到E4，需要绕过中间的C4
    try:
        path = generator.get_best_path(models_4[0], models_4[4], models_4)
        print(f"✅ 找到路径！")
        print(f"   折线数: {path['turns']}")
        print(f"   总长度: {path['total_length']}")
        print(f"   起点: {path['start_point']} ({path['start_model_id']})")
        print(f"   终点: {path['end_point']} ({path['end_model_id']})")
        print(f"   拐点: {path['inflections']}")
        print(f"   线段数: {len(path['segments'])}")
        for i, seg in enumerate(path['segments']):
            print(f"      线段{i+1}: {seg[0]} → {seg[1]}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # ========== 场景5：异常处理测试 ==========
    print("\n【场景5】异常处理测试")
    print("-" * 50)
    
    # 测试起止模型相同
    try:
        generator.get_best_path(models_1[0], models_1[0], models_1)
        print("❌ 应抛出异常：起止模型相同")
    except ValueError as e:
        print(f"✅ 正确捕获异常: {e}")
    
    # 测试空模型列表
    try:
        generator.get_best_path(models_1[0], models_1[1], [])
        print("❌ 应抛出异常：空模型列表")
    except ValueError as e:
        print(f"✅ 正确捕获异常: {e}")
    
    # 测试缓存复用
    print("\n【缓存复用测试】")
    print("-" * 50)
    generator2 = ComponentLineGenerator()
    path1 = generator2.get_best_path(models_1[0], models_1[1], models_1)
    path2 = generator2.get_best_path(models_1[1], models_1[0], models_1)  # 反向
    print(f"A→B 路径: {path1['start_model_id']} → {path1['end_model_id']}")
    print(f"B→A 路径: {path2['start_model_id']} → {path2['end_model_id']}")
    print(f"缓存命中: {path1 is path2} (应为True)")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
