#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出可用的项目模板
"""

import os
import sys
from pathlib import Path


def list_templates():
    """列出 templates 目录下的所有模板"""
    # 获取 templates 目录路径
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(skill_dir, 'templates')
    
    if not os.path.exists(templates_dir):
        print(f"❌ 模板目录不存在: {templates_dir}")
        sys.exit(1)
    
    # 获取所有子目录（即模板）
    templates = []
    for item in os.listdir(templates_dir):
        item_path = os.path.join(templates_dir, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            # 读取 _project.json 文件
            project_file = os.path.join(item_path, '_project.json')
            project_info = {
                'name': item,
                'path': item_path,
                'description': '',
                'author': '',
                'version': '',
                'tech_stack': {},
                'modules': {},
                'features': []
            }
            
            if os.path.exists(project_file):
                try:
                    import json
                    with open(project_file, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                        project_info['name'] = json_data.get('name', item)
                        project_info['description'] = json_data.get('description', '')
                        project_info['author'] = json_data.get('author', '')
                        project_info['version'] = json_data.get('version', '')
                        project_info['tech_stack'] = json_data.get('tech_stack', {})
                        project_info['modules'] = json_data.get('modules', {})
                        project_info['features'] = json_data.get('features', [])
                except Exception as e:
                    print(f"  ⚠️  读取 {item}/_project.json 失败: {e}")
            
            templates.append(project_info)
    
    # 排序
    templates.sort(key=lambda x: x['name'])
    
    return templates


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='列出可用的项目模板')
    parser.add_argument('--detail', action='store_true', help='显示详细信息')
    args = parser.parse_args()
    
    templates = list_templates()
    
    if not templates:
        print("⚠️  没有找到可用的模板")
        sys.exit(0)
    
    print("=" * 60)
    print("📦 可用的项目模板")
    print("=" * 60)
    
    for i, template in enumerate(templates, 1):
        print(f"\n{i}. {template['name']} (v{template['version']})")
        if template['description']:
            print(f"   描述: {template['description']}")
        if template['author']:
            print(f"   作者: {template['author']}")
        print(f"   路径: {template['path']}")
        
        # 如果开启了详细模式，显示更多信息
        if args.detail:
            if template['tech_stack']:
                print(f"   技术栈:")
                if template['tech_stack'].get('backend'):
                    print(f"     后端: {template['tech_stack']['backend']}")
                if template['tech_stack'].get('frontend'):
                    print(f"     前端: {template['tech_stack']['frontend']}")
                if template['tech_stack'].get('devops'):
                    print(f"     DevOps: {template['tech_stack']['devops']}")
            
            if template['features']:
                print(f"   特性:")
                for feature in template['features']:
                    print(f"     • {feature}")
            
            if template['modules']:
                if template['modules'].get('backend'):
                    print(f"   后端模块:")
                    for module in template['modules']['backend']:
                        print(f"     • {module}")
                if template['modules'].get('frontend'):
                    print(f"   前端模块:")
                    for module in template['modules']['frontend']:
                        print(f"     • {module}")
            
            # 输出替换变量列表（带顺序编号）
            project_file = os.path.join(template['path'], '_project.json')
            if os.path.exists(project_file):
                try:
                    import json
                    with open(project_file, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                        replacements = json_data.get('replacements', {})
                        if replacements:
                            print(f"   需要提供的变量（按顺序）:")
                            for idx, (placeholder, description) in enumerate(replacements.items(), 1):
                                print(f"     {idx}. {placeholder}: {description}")
                            print(f"   ⚠️  注意：请按上述顺序传递变量，第一个通常是项目名，第二个通常是组织名")
                except Exception as e:
                    pass  # 静默失败，不影响主流程
    
    print("\n" + "=" * 60)
    print(f"共 {len(templates)} 个模板")
    print("=" * 60)
    
    # 输出模板名称列表（供脚本调用）
    template_names = [t['name'] for t in templates]
    print(f"\n模板列表: {','.join(template_names)}")


if __name__ == '__main__':
    main()
