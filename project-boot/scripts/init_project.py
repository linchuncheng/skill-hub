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
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

# 模板路径（SKILL 目录内）
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(SKILL_DIR, 'templates')

# 需要跳过的目录和文件
SKIP_DIRS = {'.git', 'node_modules', 'target', 'dist', '.idea', '.vscode', '__pycache__', '.planning'}
SKIP_FILES = {'.DS_Store', 'init_project.py', 'README.md'}

# 目录重命名映射（支持占位符）
DIR_RENAMES = {
    'your_project_name-server': '{project_name}-server',
    'your_project_name-api': '{project_name}-api',
    'your_project_name-auth': '{project_name}-auth',
    'your_project_name-common': '{project_name}-common',
    'your_project_name-gateway': '{project_name}-gateway',
    'your_project_name-platform': '{project_name}-platform',
    'your_project_name-admin': '{project_name}-admin',
}


def build_replacements(group_name: str, project_name: str, project_desc: str) -> Dict[str, str]:
    """构建完整的替换映射表"""
    project_desc_short = project_desc.replace('管理系统', '').replace('系统', '')
    
    # 模板中的占位符（小写和大写版本）
    old_group = 'your_group_name'
    old_project = 'your_project_name'
    old_group_upper = old_group.upper()
    old_project_upper = old_project.upper()
    
    replacements = {
        # 全局替换占位符（核心规则 - 小写）
        # 注意：your_project_name 只替换为 project_name，不包含 group_name
        old_project: project_name,
        old_group: group_name,
        
        # 全局替换占位符（大写版本）
        old_project_upper: project_name.upper(),
        old_group_upper: group_name.upper(),
        
        # 项目描述
        '模板示例平台': project_desc,
        '模板': project_desc_short,
        'XXX平台': project_desc,
    }
    
    return replacements


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




def rename_directory_structure(dest_dir: str, group_name: str, project_name: str) -> int:
    """重命名目录结构：先替换 your_project_name，再替换 your_group_name（包含大小写）"""
    renamed_count = 0
    dest_path = Path(dest_dir)
    
    old_group = 'your_group_name'
    old_project = 'your_project_name'
    old_group_upper = old_group.upper()
    old_project_upper = old_project.upper()
    
    # 第一步：重命名包含 your_project_name 的目录（小写和大写）
    # 收集所有需要重命名的目录
    dirs_to_rename = []
    for root, dirs, files in os.walk(dest_dir):
        for dir_name in dirs:
            # 跳过 target、node_modules 等目录
            if dir_name in ('target', 'node_modules', 'dist'):
                continue
            # 替换 your_project_name（不区分大小写）
            if old_project in dir_name.lower():
                old_path = Path(root) / dir_name
                # 保持原有大小写模式进行替换
                new_name = dir_name.replace(old_project, project_name).replace(old_project_upper, project_name.upper())
                new_path = Path(root) / new_name
                dirs_to_rename.append((old_path, new_path))
    
    # 从重到深排序，避免父目录先重命名导致子目录路径错误
    dirs_to_rename.sort(key=lambda x: len(str(x[0])), reverse=True)
    
    for old_path, new_path in dirs_to_rename:
        if old_path.exists() and old_path != new_path:
            try:
                old_path.rename(new_path)
                renamed_count += 1
                print(f"  📁 重命名目录: {old_path.name} → {new_path.name}")
            except Exception as e:
                print(f"  ❌ 重命名失败 {old_path.name}: {e}")
    
    # 第二步：重命名包含 your_group_name 的目录（小写和大写）
    dirs_to_rename = []
    for root, dirs, files in os.walk(dest_dir):
        for dir_name in dirs:
            # 跳过 target、node_modules 等目录
            if dir_name in ('target', 'node_modules', 'dist'):
                continue
            # 替换 your_group_name（不区分大小写）
            if old_group in dir_name.lower():
                old_path = Path(root) / dir_name
                # 保持原有大小写模式进行替换
                new_name = dir_name.replace(old_group, group_name).replace(old_group_upper, group_name.upper())
                new_path = Path(root) / new_name
                dirs_to_rename.append((old_path, new_path))
    
    # 从重到深排序
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
    replacements: Dict[str, str],
    group_name: str,
    project_name: str
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
            old_group = 'your_group_name'
            old_project = 'your_project_name'
            
            # 替换文件名中的占位符
            if old_project in dest_filename or old_group in dest_filename:
                dest_filename = dest_filename.replace(old_project, project_name).replace(old_group, group_name)
                # 也处理大写版本
                dest_filename = dest_filename.replace(old_project.upper(), project_name.upper()).replace(old_group.upper(), group_name.upper())
            
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
    stats['dirs_renamed'] = rename_directory_structure(dest_dir, group_name, project_name)
    
    # 删除 _project.json 文件（模板元数据，不需要复制到目标项目）
    project_json = dest_path / '_project.json'
    if project_json.exists():
        try:
            project_json.unlink()
            print(f"\n🗑️  已删除: _project.json")
        except Exception as e:
            print(f"\n⚠️  删除 _project.json 失败: {e}")
    
    return stats


def validate_project(project_path: str, group_name: str, project_name: str) -> List[str]:
    """验证生成的项目是否正确"""
    issues = []
    project_path = Path(project_path)
    
    # 检查关键目录是否存在
    required_dirs = [
        f'{project_name}-server',
        f'{project_name}-api',
        f'{project_name}-auth',
        f'{project_name}-common',
        f'{project_name}-gateway',
        f'{project_name}-platform',
        f'{project_name}-admin',
    ]
    
    for dir_name in required_dirs:
        if not (project_path / dir_name).exists():
            issues.append(f"缺少目录: {dir_name}")
    
    # 检查父 POM 文件
    pom_file = project_path / 'pom.xml'
    if pom_file.exists():
        with open(pom_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if f'<artifactId>{group_name}-{project_name}</artifactId>' not in content:
                issues.append(f"POM 文件中缺少项目 artifactId: {group_name}-{project_name}")
    
    # 检查是否有未替换的包名
    java_files = list(project_path.glob('**/src/**/*.java'))
    if java_files:
        sample_file = java_files[0]
        with open(sample_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 检查是否还有旧的占位符包名
            old_pattern = f'com.your_group_name.your_project_name'
            if old_pattern in content:
                issues.append(f"Java 文件中仍包含占位符包名 '{old_pattern}': {sample_file}")
            
            # 检查是否包含新的包名
            if f'com.{group_name}.{project_name}' not in content:
                issues.append(f"Java 文件中缺少新包名 'com.{group_name}.{project_name}': {sample_file}")
    
    # 检查数据库名称
    docker_compose = project_path / 'docker-compose.yml'
    if docker_compose.exists():
        with open(docker_compose, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'your_group_name_your_project_name' in content:
                issues.append("docker-compose.yml 中数据库名称仍包含占位符")
    
    return issues


def main():
    parser = argparse.ArgumentParser(description='项目脚手架生成器')
    parser.add_argument('--template', required=True, help='模板名称（如：saas）')
    parser.add_argument('--group-name', required=True, help='组织/公司英文名（如：your_group_name）')
    parser.add_argument('--project-name', required=True, help='项目英文名（如：fms, crm）')
    parser.add_argument('--project-desc', required=True, help='项目中文名（如：财务管理系统）')
    parser.add_argument('--target-path', required=True, help='目标代码工作区路径（项目将创建在该目录下）')
    
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
    
    # 构建实际目标路径：工作区 + {group-name}-{project-name}
    project_dir_name = f"{args.group_name}-{args.project_name}"
    target_path = os.path.join(args.target_path, project_dir_name)
    
    print("=" * 60)
    print("🚀 项目脚手架生成器")
    print("=" * 60)
    print(f"📦 模板名称: {args.template}")
    print(f"🏢 组织名称: {args.group_name}")
    print(f"📝 项目名称: {args.project_name}")
    print(f"📝 项目描述: {args.project_desc}")
    print(f"📂 模板路径: {template_path}")
    print(f"📂 工作区路径: {args.target_path}")
    print(f"📂 项目路径: {target_path}")
    print("=" * 60)
    
    # 验证模板存在
    if not os.path.exists(template_path):
        print(f"❌ 模板不存在: {template_path}")
        sys.exit(1)
    
    # 构建替换规则（使用项目名作为唯一标识）
    replacements = build_replacements(args.group_name, args.project_name, args.project_desc)
    
    print(f"\n📋 替换规则（前10条）:")
    for i, (old, new) in enumerate(sorted(replacements.items(), key=len, reverse=True)[:10]):
        print(f"  {old} → {new}")
    print(f"  ... 共 {len(replacements)} 条规则")
    
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
        replacements,
        args.group_name,
        args.project_name
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
    issues = validate_project(target_path, args.group_name, args.project_name)
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
    print(f"\n6. 安装前端依赖:")
    print(f"   cd {args.project_name}-admin && pnpm install")
    print("=" * 60)


if __name__ == '__main__':
    main()
