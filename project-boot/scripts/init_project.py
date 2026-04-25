#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目脚手架生成器
基于模板快速生成新的微服务项目
"""

import os
import sys
import shutil
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

# 模板路径（SKILL 目录内）
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(SKILL_DIR, 'templates')

# 需要跳过的目录和文件
SKIP_DIRS = {'.git', 'node_modules', 'target', 'dist', '.idea', '.vscode', '__pycache__', '.planning'}
SKIP_FILES = {'.DS_Store', 'init_project.py'}


def load_template_config(template_path: str) -> Dict:
    """读取模板的 _project.json 配置文件"""
    project_json = os.path.join(template_path, '_project.json')
    if not os.path.exists(project_json):
        print(f"❌ 模板配置文件不存在: {project_json}")
        sys.exit(1)
    
    try:
        with open(project_json, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"❌ 读取模板配置文件失败: {e}")
        sys.exit(1)


def build_replacements_from_config(config: Dict, user_inputs: Dict[str, str]) -> Dict[str, str]:
    """
    根据模板配置和用户输入构建替换映射表
    
    Args:
        config: _project.json 的配置内容
        user_inputs: 用户提供的变量值 {placeholder: value}
    
    Returns:
        完整的替换映射表
    """
    replacements_config = config.get('replacements', {})
    if not replacements_config:
        print("⚠️  模板配置中未定义 replacements 字段")
        return {}
    
    replacements = {}
    
    # 按顺序处理每个占位符
    for placeholder, description in replacements_config.items():
        if placeholder not in user_inputs:
            print(f"❌ 缺少必填变量: {placeholder} ({description})")
            sys.exit(1)
        
        user_value = user_inputs[placeholder]
        
        # 基础替换
        replacements[placeholder] = user_value
        
        # 自动生成大写版本（如果占位符是全小写且不是单个词）
        if placeholder.islower() and len(placeholder) > 0:
            replacements[placeholder.upper()] = user_value.upper()
    
    return replacements


def get_replacements_questions(template_path: str) -> List[Dict[str, str]]:
    """
    获取模板需要用户提供的变量列表（供大模型组织问题使用）
    
    Returns:
        [{
            'placeholder': 'your_project_name',
            'description': '项目英文名',
            'question': '请提供您的项目英文名'
        }, ...]
    """
    config = load_template_config(template_path)
    replacements_config = config.get('replacements', {})
    
    questions = []
    for placeholder, description in replacements_config.items():
        questions.append({
            'placeholder': placeholder,
            'description': description,
            'question': f'请提供您的{description}'
        })
    
    return questions


def should_skip_file(file_path: str) -> bool:
    """判断是否应该跳过文件"""
    # 跳过二进制文件
    binary_extensions = {'.jar', '.war', '.class', '.png', '.jpg', '.gif', '.ico', '.lock'}
    ext = os.path.splitext(file_path)[1].lower()
    if ext in binary_extensions:
        return True
    
    # 跳过特定文件
    if os.path.basename(file_path) in SKIP_FILES:
        return True
    
    return False


def should_skip_dir(dir_name: str) -> bool:
    """判断是否应该跳过目录"""
    return dir_name in SKIP_DIRS


def replace_content_in_file(file_path: str, replacements: Dict[str, str]) -> int:
    """替换文件内容，返回替换次数"""
    changed_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return 0
    
    original_content = content
    
    # 按照键的长度降序排序，避免短键先替换导致长键无法匹配
    for old_val in sorted(replacements.keys(), key=len, reverse=True):
        new_val = replacements[old_val]
        if old_val in content:
            content = content.replace(old_val, new_val)
            changed_count += 1
    
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except PermissionError:
            print(f"  ⚠️  无法写入文件: {file_path}")
    
    return changed_count




def rename_directory_structure(dest_dir: str, replacements: Dict[str, str]) -> int:
    """重命名目录结构：根据 replacements 中的占位符进行重命名"""
    renamed_count = 0
    dest_path = Path(dest_dir)
    
    # 从 replacements 中提取原始占位符（小写的，不要求必须有下划线）
    placeholders = [k for k in replacements.keys() if k.islower() and not k.isupper()]
    
    # 按占位符顺序依次重命名
    for placeholder in placeholders:
        new_value = replacements[placeholder]
        placeholder_upper = placeholder.upper()
        
        # 收集所有需要重命名的目录
        dirs_to_rename = []
        for root, dirs, files in os.walk(dest_dir):
            for dir_name in dirs:
                # 跳过 target、node_modules 等目录
                if dir_name in ('target', 'node_modules', 'dist'):
                    continue
                # 检查是否包含占位符（不区分大小写）
                if placeholder in dir_name.lower():
                    old_path = Path(root) / dir_name
                    # 保持原有大小写模式进行替换
                    new_name = dir_name.replace(placeholder, new_value).replace(placeholder_upper, new_value.upper())
                    new_path = Path(root) / new_name
                    dirs_to_rename.append((old_path, new_path))
        
        # 从深到浅排序，避免父目录先重命名导致子目录路径错误
        dirs_to_rename.sort(key=lambda x: len(str(x[0])), reverse=True)
        
        for old_path, new_path in dirs_to_rename:
            if old_path.exists() and old_path != new_path:
                try:
                    old_path.rename(new_path)
                    renamed_count += 1
                    print(f"  📁 重命名目录: {old_path.name} → {new_path.name}")
                except Exception as e:
                    print(f"  ❌ 重命名失败 {old_path.name}: {e}")
    
    return renamed_count


def copy_and_transform(
    src_dir: str,
    dest_dir: str,
    replacements: Dict[str, str]
) -> Dict:
    """复制并转换项目"""
    stats = {
        'files_copied': 0,
        'files_modified': 0,
        'dirs_renamed': 0,
        'errors': []
    }
    
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)
    
    # 创建目标目录
    dest_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📦 正在复制文件...")
    
    # 收集所有需要复制的文件和目录
    for root, dirs, files in os.walk(src_dir):
        # 过滤需要跳过的目录
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        
        # 计算相对路径
        rel_root = Path(root).relative_to(src_path)
        
        # 创建目标目录（先不重命名，后续统一处理）
        dest_root = dest_path / rel_root
        dest_root.mkdir(parents=True, exist_ok=True)
        
        # 处理文件
        for file in files:
            if should_skip_file(file):
                continue
            
            src_file = src_path / rel_root / file
            
            # 检查文件名是否需要重命名
            dest_filename = file
            
            # 从 replacements 中提取原始占位符（小写的，不要求必须有下划线）
            placeholders = [k for k in replacements.keys() if k.islower() and not k.isupper()]
            
            # 替换文件名中的占位符
            for placeholder in placeholders:
                if placeholder in dest_filename:
                    new_value = replacements[placeholder]
                    dest_filename = dest_filename.replace(placeholder, new_value)
                    # 也处理大写版本
                    dest_filename = dest_filename.replace(placeholder.upper(), new_value.upper())
            
            dest_file = dest_root / dest_filename
            
            try:
                # 复制文件
                shutil.copy2(src_file, dest_file)
                stats['files_copied'] += 1
                
                # 替换文件内容
                changed = replace_content_in_file(str(dest_file), replacements)
                if changed > 0:
                    stats['files_modified'] += 1
                    if stats['files_modified'] <= 20:  # 只显示前20个
                        print(f"  ✏️  {dest_file.relative_to(dest_path)} ({changed} 处替换)")
            
            except Exception as e:
                stats['errors'].append(f"{src_file}: {str(e)}")
    
    # 重命名目录（包括 Java 包目录）
    print(f"\n📁 正在重命名目录...")
    stats['dirs_renamed'] = rename_directory_structure(dest_dir, replacements)
    
    # 删除 _project.json 文件（模板元数据，不需要复制到目标项目）
    project_json = dest_path / '_project.json'
    if project_json.exists():
        try:
            project_json.unlink()
            print(f"\n🗑️  已删除: _project.json")
        except Exception as e:
            print(f"\n⚠️  删除 _project.json 失败: {e}")
    
    return stats


def validate_project(project_path: str, replacements: Dict[str, str]) -> List[str]:
    """验证生成的项目是否正确"""
    issues = []
    project_path = Path(project_path)
    
    # 从 replacements 中提取原始占位符（小写的，不要求必须有下划线）
    placeholders = [k for k in replacements.keys() if k.islower() and not k.isupper()]
    
    # 检查是否还有未替换的占位符
    all_files = list(project_path.glob('**/*'))
    for file_path in all_files:
        if file_path.is_file():
            # 只检查文本文件
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for placeholder in placeholders:
                        if placeholder in content:
                            issues.append(f"文件 {file_path.relative_to(project_path)} 中仍包含未替换的占位符: {placeholder}")
                            break  # 每个文件只报告一次
            except (UnicodeDecodeError, PermissionError):
                continue
    
    return issues


def main():
    parser = argparse.ArgumentParser(description='项目脚手架生成器')
    parser.add_argument('--template', required=True, help='模板名称（如：saas）')
    parser.add_argument('--target-path', required=True, help='目标代码工作区路径（项目将创建在该目录下）')
    parser.add_argument('--vars', required=False, help='用户提供的变量值，JSON 格式：{"your_project_name": "fms", "your_group_name": "fengqun"}')
    parser.add_argument('--list-questions', action='store_true', help='列出需要用户提供的变量列表（供大模型使用）')
    
    args = parser.parse_args()
    
    # 验证模板名称
    template_path = os.path.join(TEMPLATES_DIR, args.template)
    if not os.path.exists(template_path):
        print(f"❌ 模板不存在: {args.template}")
        print(f"可用模板: ", end='')
        if os.path.exists(TEMPLATES_DIR):
            templates = [d for d in os.listdir(TEMPLATES_DIR) if os.path.isdir(os.path.join(TEMPLATES_DIR, d))]
            print(', '.join(templates) if templates else '无')
        else:
            print('无')
        sys.exit(1)
    
    # 如果只是列出问题，直接输出后退出
    if args.list_questions:
        questions = get_replacements_questions(template_path)
        print(json.dumps(questions, ensure_ascii=False, indent=2))
        sys.exit(0)
    
    # 加载模板配置
    config = load_template_config(template_path)
    
    # 解析用户输入的变量
    if not args.vars:
        print("❌ 请提供 --vars 参数，格式为 JSON")
        sys.exit(1)
    
    try:
        user_inputs = json.loads(args.vars)
    except json.JSONDecodeError as e:
        print(f"❌ --vars 参数格式错误: {e}")
        sys.exit(1)
    
    # 构建替换规则
    replacements = build_replacements_from_config(config, user_inputs)
    
    # 构建实际目标路径:工作区 + 项目目录名
    # 优先使用"组织名-项目名"格式(如 fengqun-fms)
    # 提取所有小写占位符(不要求必须有下划线)
    placeholders = [k for k in replacements.keys() if k.islower() and not k.isupper()]
    
    # 严格按照 replacements 配置的顺序来识别
    # 第一个占位符通常是项目名，第二个通常是组织名
    config_replacements = config.get('replacements', {})
    
    if len(placeholders) >= 2:
        # 有两个或更多占位符时，按顺序识别
        project_placeholder = placeholders[0]
        group_placeholder = placeholders[1]
    elif len(placeholders) == 1:
        # 只有一个占位符时，作为项目名
        project_placeholder = placeholders[0]
        group_placeholder = None
    else:
        # 没有小写占位符，使用模板名
        project_placeholder = None
        group_placeholder = None
        
    # 构建目录名
    if project_placeholder and group_placeholder:
        project_dir_name = f"{replacements[group_placeholder]}-{replacements[project_placeholder]}"
    elif project_placeholder:
        project_dir_name = replacements[project_placeholder]
    elif placeholders:
        project_dir_name = replacements[placeholders[0]]
    else:
        project_dir_name = args.template
    
    target_path = os.path.join(args.target_path, project_dir_name)
    
    print("=" * 60)
    print("🚀 项目脚手架生成器")
    print("=" * 60)
    print(f"📦 模板名称: {args.template}")
    print(f"📂 模板路径: {template_path}")
    print(f"📂 工作区路径: {args.target_path}")
    print(f"📂 项目路径: {target_path}")
    print(f"📋 用户变量:")
    for placeholder, value in user_inputs.items():
        description = config.get('replacements', {}).get(placeholder, '')
        print(f"   {placeholder} ({description}): {value}")
    print("=" * 60)
    
    print(f"\n📋 替换规则（共 {len(replacements)} 条）:")
    for old, new in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)[:10]:
        print(f"  {old} → {new}")
    if len(replacements) > 10:
        print(f"  ... 还有 {len(replacements) - 10} 条规则")
    
    # 检查目标路径是否存在
    if os.path.exists(target_path):
        response = input(f"\n⚠️  项目目录已存在: {target_path}\n是否覆盖？(y/N): ")
        if response.lower() != 'y':
            print("❌ 操作已取消")
            sys.exit(0)
        shutil.rmtree(target_path)
    
    # 执行复制和转换
    stats = copy_and_transform(
        template_path,
        target_path,
        replacements
    )
    
    # 输出统计信息
    print("\n" + "=" * 60)
    print("✅ 项目生成完成!")
    print("=" * 60)
    print(f"📄 复制文件: {stats['files_copied']}")
    print(f"✏️  修改文件: {stats['files_modified']}")
    print(f"📁 重命名目录: {stats['dirs_renamed']}")
    
    if stats['errors']:
        print(f"\n⚠️  错误 ({len(stats['errors'])}):")
        for error in stats['errors'][:5]:
            print(f"  - {error}")
        if len(stats['errors']) > 5:
            print(f"  ... 还有 {len(stats['errors']) - 5} 个错误")
    
    # 验证项目
    print("\n🔍 验证项目...")
    issues = validate_project(target_path, replacements)
    if issues:
        print(f"⚠️  发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ 验证通过，未发现明显问题")
    
    # 输出后续步骤
    print("\n" + "=" * 60)
    print("📌 后续步骤:")
    print("=" * 60)
    print(f"1. 进入项目目录:")
    print(f"   cd {target_path}")
    print(f"\n2. 初始化 Git 仓库:")
    print(f"   git init && git add . && git commit -m 'Initial commit'")
    print(f"\n3. 启动基础设施:")
    print(f"   docker-compose up -d")
    print(f"\n4. 初始化数据库:")
    print(f"   使用 /dbmate 技能进行数据库迁移")
    print(f"\n5. 编译后端:")
    print(f"   mvn clean install")
    print("=" * 60)


if __name__ == '__main__':
    main()
