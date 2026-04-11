#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型JSON配置生成器 - 从SQL和参数生成JSON配置文件

用法:
    python3 model_json_generator.py <sql_file> [<sql_file2> ...] \
        --domains "领域名:表名,...;..." \
        --models "表名:中文名:类型:行,列:行为:关联属性" \
        [--relations "源模型->目标模型,..."] \
        --json output.json

功能:
    - 解析SQL文件提取表结构和属性
    - 接收LLM提供的布局配置
    - 生成标准JSON配置文件
    - 支持后续手动/LLM修改JSON后重新生成SVG

示例:
    python3 model_json_generator.py init.sql \
        --domains "RBAC域:sys_tenant,sys_user,sys_role,sys_permission,sys_menu,sys_login_log" \
        --models "sys_tenant:租户:角色:0,1;sys_user:用户:角色:1,0:登录、分配角色;sys_role:角色:角色:1,1:分配权限、分配菜单:权限集合、菜单集合" \
        --relations "租户->用户,租户->角色,用户->角色" \
        --title "RBAC领域模型" \
        --cols 4 \
        --json rbac-config.json
"""

import re
import json
import argparse
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict


class CompactJSONEncoder(json.JSONEncoder):
    """紧凑JSON编码器 - 短数组保持单行"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent_str = ' ' * self.indent
    
    def encode(self, obj):
        if isinstance(obj, dict):
            return self._encode_dict(obj, 0)
        elif isinstance(obj, list):
            return self._encode_list(obj, 0)
        return super().encode(obj)
    
    def _encode_dict(self, d, level):
        if not d:
            return '{}'
        items = []
        for k, v in d.items():
            key = json.dumps(k, ensure_ascii=self.ensure_ascii)
            val = self._encode_value(v, level + 1)
            items.append(f'{key}: {val}')
        indent = self.indent_str * level
        inner_indent = self.indent_str * (level + 1)
        return '{\n' + f',\n'.join(f'{inner_indent}{item}' for item in items) + f'\n{indent}}}'
    
    def _encode_list(self, lst, level):
        if not lst:
            return '[]'
        # 所有数组保持单行
        encoded_items = [self._encode_value(item, level) for item in lst]
        single_line = '[' + ', '.join(encoded_items) + ']'
        return single_line
    
    def _encode_value(self, v, level):
        if isinstance(v, dict):
            return self._encode_dict(v, level)
        elif isinstance(v, list):
            return self._encode_list(v, level)
        else:
            return json.dumps(v, ensure_ascii=self.ensure_ascii)


# ==================== 常量配置 ====================

AUDIT_FIELDS = {'created_at', 'updated_at', 'created_by', 'updated_by', 'deleted'}


# ==================== 数据模型 ====================

def to_pascal_case(snake_str: str) -> str:
    """将蛇形命名转换为 PascalCase"""
    return ''.join(word.capitalize() for word in snake_str.split('_'))


@dataclass
class ModelConfig:
    """模型配置"""
    model: str                    # 领域模型名（PascalCase）
    name: str                     # 中文模型名
    type: str                     # 四色类型：角色/资源/描述/时标
    position: List[int]           # 坐标 [行, 列]
    attributes: List[str] = field(default_factory=list)      # 业务属性
    behaviors: List[str] = field(default_factory=list)       # 核心行为
    associations: List[str] = field(default_factory=list)    # 关联属性


@dataclass
class DomainConfig:
    """领域配置"""
    name: str                                  # 领域名
    models: List[ModelConfig] = field(default_factory=list)  # 模型列表


@dataclass
class DiagramConfig:
    """图形配置（JSON输出格式）"""
    title: str                                         # 大标题
    cols: int                                          # 领域列数
    domains: List[DomainConfig] = field(default_factory=list)  # 领域列表
    relations: List[Dict[str, str]] = field(default_factory=list)  # 连线关系


# ==================== SQL解析器 ====================

class SQLParser:
    """解析SQL文件提取表结构"""
    
    @staticmethod
    def parse(sql_content: str) -> Dict[str, dict]:
        """解析SQL，返回 {表名: {columns, comment}}"""
        tables = {}
        pattern = re.compile(
            r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"]?(\w+)[`"]?\s*\((.*?)\)(?:\s*ENGINE|\s*COMMENT|\s*$)',
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
            
            col_match = re.match(r'[`"]?([\w_]+)[`"]?\s+(\w+)', line)
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


# ==================== 参数解析器 ====================

class ParamParser:
    """解析命令行参数"""
    
    @staticmethod
    def parse_models(models_str: str) -> Dict[str, dict]:
        """解析模型配置字符串
        
        格式: 表名:中文名:类型:行,列:行为:关联属性
        多模型用 ; 分隔
        行为用、或,分隔
        关联属性用、或,分隔
        """
        models = {}
        for item in models_str.split(';'):
            item = item.strip()
            if not item:
                continue
            parts = item.split(':')
            if len(parts) >= 4:
                table, chinese, mtype, pos = parts[0], parts[1], parts[2], parts[3]
                row, col = map(int, pos.split(','))
                
                model = {
                    'name': chinese,
                    'type': mtype,
                    'position': [row, col],
                    'behaviors': [],
                    'associations': []
                }
                
                # parts[4] 是行为（可选）
                # parts[5] 是关联属性（可选）
                if len(parts) >= 5 and parts[4]:
                    # 解析行为
                    behaviors = [b.strip() for b in re.split(r'[,，、；]', parts[4]) if b.strip()]
                    model['behaviors'] = behaviors
                
                if len(parts) >= 6 and parts[5]:
                    # 解析关联属性
                    associations = [a.strip() for a in re.split(r'[、,，]', parts[5]) if a.strip()]
                    model['associations'] = associations
                
                models[table] = model
        
        return models
    
    @staticmethod
    def parse_relations(rel_str: Optional[str]) -> List[Dict[str, str]]:
        """解析连线关系"""
        if not rel_str:
            return []
        relations = []
        for item in rel_str.split(','):
            item = item.strip()
            if not item:
                continue
            if '->' in item:
                relations.append(item)
        return relations
    
    @staticmethod
    def parse_domains(domains_str: str) -> Dict[str, List[str]]:
        """解析领域配置
        
        格式: 领域名:表名1,表名2,...;领域名:表名1,...
        """
        domains = {}
        for item in domains_str.split(';'):
            item = item.strip()
            if not item:
                continue
            if ':' not in item:
                continue
            parts = item.split(':', 1)
            domain_name = parts[0].strip()
            tables_str = parts[1].strip() if len(parts) > 1 else ''
            tables = [t.strip() for t in tables_str.split(',') if t.strip()]
            domains[domain_name] = tables
        return domains


# ==================== JSON生成器 ====================

class JSONGenerator:
    """生成JSON配置"""
    
    def __init__(self, tables: Dict[str, dict]):
        self.tables = tables
    
    def generate(
        self,
        title: str,
        cols: int,
        domains_config: Dict[str, List[str]],
        models_config: Dict[str, dict],
        relations: List[Dict[str, str]]
    ) -> DiagramConfig:
        """生成完整配置"""
        
        domains = []
        for domain_name, table_list in domains_config.items():
            domain = DomainConfig(name=domain_name)
            for table_name in table_list:
                if table_name in models_config:
                    model_cfg = models_config[table_name]
                    table_data = self.tables.get(table_name, {})
                    
                    model = ModelConfig(
                        model=to_pascal_case(table_name),
                        name=model_cfg['name'],
                        type=model_cfg['type'],
                        position=model_cfg['position'],
                        attributes=self._extract_attributes(table_data),
                        behaviors=model_cfg['behaviors'],
                        associations=model_cfg['associations']
                    )
                    domain.models.append(model)
            domains.append(domain)
        
        return DiagramConfig(
            title=title,
            cols=cols,
            domains=domains,
            relations=relations
        )
    
    def _extract_attributes(self, table_data: dict) -> List[str]:
        """提取业务属性（过滤id和外键）"""
        attrs = []
        columns = table_data.get('columns', [])
        for col in columns:
            name = col['name'].lower()
            if name == 'id':
                continue
            if name.endswith('_id') and name != 'tenant_id':
                continue
            attrs.append(self._simplify_name(col['comment']))
        return attrs
    
    @staticmethod
    def _simplify_name(comment: str) -> str:
        """简化属性名"""
        for sep in ['：', ':', '（', '(', '，', ',']:
            if sep in comment:
                comment = comment.split(sep)[0]
        return comment.strip()
    
    @staticmethod
    def to_dict(config: DiagramConfig) -> dict:
        """转换为可序列化的字典"""
        return {
            'title': config.title,
            'cols': config.cols,
            'domains': [
                {
                    'name': d.name,
                    'models': [
                        {
                            'model': m.model,
                            'name': m.name,
                            'type': m.type,
                            'position': m.position,
                            'attributes': m.attributes,
                            'behaviors': m.behaviors,
                            'associations': m.associations
                        }
                        for m in d.models
                    ]
                }
                for d in config.domains
            ],
            'relations': config.relations
        }


# ==================== 主流程 ====================

def main():
    parser = argparse.ArgumentParser(description='模型JSON配置生成器')
    parser.add_argument('sql_files', nargs='+', help='SQL文件路径（支持多个文件）')
    parser.add_argument('--domains', required=True, help='领域配置："领域名:表名1,表名2,...;..."')
    parser.add_argument('--models', required=True, help='模型配置："表名:中文名:类型:行,列:行为:关联属性;..."')
    parser.add_argument('--relations', default='', help='连线关系："源模型->目标模型,..."')
    parser.add_argument('--cols', type=int, default=4, help='领域列数（默认4）')
    parser.add_argument('--title', default='', help='SVG大标题')
    parser.add_argument('--json', required=True, help='输出JSON文件路径')
    args = parser.parse_args()
    
    # 1. 解析SQL文件
    tables = {}
    for sql_file in args.sql_files:
        with open(sql_file, 'r', encoding='utf-8') as f:
            file_tables = SQLParser.parse(f.read())
            tables.update(file_tables)
        print(f"已加载SQL文件: {sql_file} ({len(file_tables)} 个表)")
    print(f"共加载 {len(tables)} 个唯一表定义")
    
    # 2. 解析参数
    domains_config = ParamParser.parse_domains(args.domains)
    models_config = ParamParser.parse_models(args.models)
    relations = ParamParser.parse_relations(args.relations)
    
    print(f"解析配置: {len(domains_config)} 个领域, {len(models_config)} 个模型, {len(relations)} 条连线")
    
    # 3. 生成JSON配置
    generator = JSONGenerator(tables)
    config = generator.generate(
        title=args.title,
        cols=args.cols,
        domains_config=domains_config,
        models_config=models_config,
        relations=relations
    )
    
    # 4. 输出JSON（紧凑格式 - 短数组单行）
    config_dict = JSONGenerator.to_dict(config)
    with open(args.json, 'w', encoding='utf-8') as f:
        f.write(CompactJSONEncoder(indent=2, ensure_ascii=False).encode(config_dict))
    
    print(f"JSON配置已保存到: {args.json}")
    print(f"\n后续步骤:")
    print(f"  1. 查看或修改JSON配置文件")
    print(f"  2. 运行: python3 model_svg_generator.py --json {args.json} --svg XXX领域模型图.svg")


if __name__ == '__main__':
    main()
