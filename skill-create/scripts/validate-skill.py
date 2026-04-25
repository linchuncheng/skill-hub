#!/usr/bin/env python3
"""
技能创建质量验证脚本

验证技能目录是否符合 skill-check 规范，确保一次性通过审查。

用法:
    python3 scripts/validate-skill.py <skill-dir>

示例:
    python3 scripts/validate-skill.py ./my-new-skill
"""

import sys
import json
import re
from pathlib import Path


class SkillValidator:
    """技能验证器"""
    
    def __init__(self, skill_dir):
        self.skill_dir = Path(skill_dir).resolve()
        self.skill_name = self.skill_dir.name
        self.skill_md = self.skill_dir / "SKILL.md"
        self.manifest = self.skill_dir / "manifest.json"
        self.scripts_dir = self.skill_dir / "scripts"
        self.references_dir = self.skill_dir / "references"
        self.assets_dir = self.skill_dir / "assets"
        
        self.issues = []  # (priority, category, message)
        self.content = ""
        
    def validate(self):
        """执行所有验证"""
        print(f"🔍 开始验证技能: {self.skill_name}")
        print(f"📁 路径: {self.skill_dir}\n")
        
        self.check_structure()
        self.check_frontmatter()
        self.check_content()
        self.check_scripts()
        self.check_references()
        self.check_assets()
        self.check_agent_compatibility()
        self.check_execution_determinism()
        self.check_logic_completeness()
        
        self.print_report()
        return len([i for i in self.issues if i[0] in ['P0', 'P1']]) == 0
    
    def check_structure(self):
        """检查目录结构"""
        # SKILL.md 必须存在
        if not self.skill_md.exists():
            self.issues.append(('P0', '结构', 'SKILL.md 不存在'))
            return
        
        # manifest.json 应该存在
        if not self.manifest.exists():
            self.issues.append(('P1', '结构', 'manifest.json 不存在'))
        
        # 检查目录命名
        for dir_path in [self.scripts_dir, self.references_dir, self.assets_dir]:
            if dir_path.exists() and not dir_path.is_dir():
                self.issues.append(('P0', '结构', f'{dir_path.name} 应该是目录'))
    
    def check_frontmatter(self):
        """检查 frontmatter"""
        if not self.skill_md.exists():
            return
        
        with open(self.skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            self.content = content
        
        # 检查 frontmatter 是否存在
        if not content.startswith('---'):
            self.issues.append(('P0', 'Frontmatter', '缺少 frontmatter（以 --- 开头）'))
            return
        
        # 提取 frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            self.issues.append(('P0', 'Frontmatter', 'frontmatter 格式不正确'))
            return
        
        frontmatter = parts[1]
        
        # 检查 name 字段
        name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
        if not name_match:
            self.issues.append(('P0', 'Frontmatter', 'frontmatter 缺少 name 字段'))
        else:
            name = name_match.group(1).strip()
            if name != self.skill_name:
                self.issues.append(('P0', 'Frontmatter', 
                    f'name 字段 ({name}) 与目录名 ({self.skill_name}) 不一致'))
        
        # 检查 description 字段
        desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
        if not desc_match:
            self.issues.append(('P0', 'Frontmatter', 'frontmatter 缺少 description 字段'))
        else:
            desc = desc_match.group(1).strip()
            if '触发' not in desc and '当用户' not in desc:
                self.issues.append(('P1', 'Frontmatter', 
                    'description 缺少触发场景说明（应包含「当用户...时触发」）'))
    
    def check_content(self):
        """检查内容规范"""
        if not self.content:
            return
        
        lines = self.content.split('\n')
        line_count = len(lines)
        
        # 检查行数
        if line_count > 500:
            self.issues.append(('P1', '内容', f'SKILL.md 共 {line_count} 行，超过 500 行限制'))
        
        # 检查章节层级
        max_level = 0
        for line in lines:
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                max_level = max(max_level, level)
        
        if max_level > 3:
            self.issues.append(('P2', '内容', f'章节层级过深（最多 {max_level} 级，建议不超过 3 级）'))
    
    def check_scripts(self):
        """检查脚本规范"""
        if not self.scripts_dir.exists():
            return
        
        scripts = list(self.scripts_dir.glob('*.py')) + list(self.scripts_dir.glob('*.sh'))
        
        if not scripts:
            self.issues.append(('P2', '脚本', 'scripts/ 目录存在但没有脚本文件'))
            return
        
        for script in scripts:
            with open(script, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查参数校验
            if 'sys.argv' in content or 'argparse' in content:
                if 'len(sys.argv)' not in content and 'add_argument' not in content:
                    self.issues.append(('P2', '脚本', f'{script.name} 缺少参数校验'))
            
            # 检查错误处理
            if script.suffix == '.sh' and 'set -euo pipefail' not in content:
                self.issues.append(('P2', '脚本', f'{script.name} 缺少错误处理（set -euo pipefail）'))
    
    def check_references(self):
        """检查参考文档"""
        if not self.references_dir.exists():
            return
        
        docs = list(self.references_dir.glob('*.md'))
        
        if not docs:
            self.issues.append(('P2', '参考文档', 'references/ 目录存在但没有文档文件'))
            return
        
        for doc in docs:
            # 检查命名规范
            if not re.match(r'^[a-z0-9_\-]+\.md$', doc.name):
                self.issues.append(('P2', '参考文档', f'{doc.name} 命名不规范（应使用小写、连字符或下划线）'))
    
    def check_assets(self):
        """检查资源文件"""
        if not self.assets_dir.exists():
            return
        
        assets = list(self.assets_dir.iterdir())
        
        if not assets:
            self.issues.append(('P2', '资源文件', 'assets/ 目录存在但没有资源文件'))
    
    def check_agent_compatibility(self):
        """检查 Agent 兼容性"""
        if not self.content:
            return
        
        # 检查工具名硬编码
        tool_names = ['Qoder', 'ClaudeCode', 'OpenClaw', 'Cursor']
        for tool in tool_names:
            if tool in self.content:
                self.issues.append(('P0', '兼容性', f'硬编码了工具名: {tool}'))
        
        # 检查特定工具路径
        tool_paths = ['.qoder/', '.claude/', '.cursor/']
        for path in tool_paths:
            if path in self.content:
                self.issues.append(('P0', '兼容性', f'使用了特定工具路径: {path}'))
    
    def check_execution_determinism(self):
        """检查执行确定性"""
        if not self.content:
            return
        
        # 检查模糊目录指代
        vague_dirs = ['合适的目录', '相关目录', '目标目录', '适当的位置', '合适的路径']
        for vague in vague_dirs:
            if vague in self.content:
                self.issues.append(('P1', '确定性', f'使用模糊目录指代: "{vague}"'))
        
        # 检查模糊脚本引用
        vague_scripts_patterns = [
            r'运行脚本(?!/)',
            r'执行脚本(?!/)',
            r'相关脚本(?!/)',
        ]
        for pattern in vague_scripts_patterns:
            if re.search(pattern, self.content):
                self.issues.append(('P1', '确定性', f'使用模糊脚本引用'))
                break
        
        # 检查模糊工具指令
        vague_tools_patterns = [
            r'使用工具(?!:)',
            r'调用工具(?!:)',
            r'合适的工具',
        ]
        for pattern in vague_tools_patterns:
            if re.search(pattern, self.content):
                self.issues.append(('P1', '确定性', f'使用模糊工具指令'))
                break
        
        # 检查程度副词
        vague_adverbs = ['可能', '也许', '适当', '尽量', '大约', '左右']
        found_adverbs = []
        for adverb in vague_adverbs:
            if adverb in self.content:
                found_adverbs.append(adverb)
        
        if found_adverbs:
            self.issues.append(('P2', '确定性', f'使用程度副词: {", ".join(found_adverbs)}'))
    
    def check_logic_completeness(self):
        """检查逻辑完整性"""
        if not self.content:
            return
        
        # 检查工作流
        if '工作流' not in self.content:
            self.issues.append(('P1', '逻辑', '缺少「技能工作流」章节'))
        
        # 检查使用说明
        if '使用说明' not in self.content:
            self.issues.append(('P1', '逻辑', '缺少「使用说明」章节'))
        
        # 检查错误处理
        if '错误处理' not in self.content and '异常处理' not in self.content:
            self.issues.append(('P2', '逻辑', '缺少「错误处理」章节'))
        
        # 检查禁止事项
        if '禁止事项' not in self.content and '禁止' not in self.content:
            self.issues.append(('P2', '逻辑', '缺少「禁止事项」章节'))
    
    def print_report(self):
        """打印验证报告"""
        print("=" * 60)
        print(f"📊 技能验证报告: {self.skill_name}")
        print("=" * 60)
        
        # 结构概览
        print("\n## 结构概览")
        print(f"| 目录/文件 | 状态 | 说明 |")
        print(f"|-----------|------|------|")
        print(f"| manifest.json | {'✅' if self.manifest.exists() else '❌'} | {'存在' if self.manifest.exists() else '不存在'} |")
        
        if self.skill_md.exists():
            line_count = len(self.content.split('\n'))
            print(f"| SKILL.md | {'✅' if line_count <= 500 else '⚠️'} | {line_count} 行 |")
        else:
            print(f"| SKILL.md | ❌ | 不存在 |")
        
        if self.scripts_dir.exists():
            script_count = len(list(self.scripts_dir.iterdir()))
            print(f"| scripts/ | ✅ | {script_count} 个文件 |")
        else:
            print(f"| scripts/ | - | 不存在 |")
        
        if self.references_dir.exists():
            ref_count = len(list(self.references_dir.iterdir()))
            print(f"| references/ | ✅ | {ref_count} 个文件 |")
        else:
            print(f"| references/ | - | 不存在 |")
        
        if self.assets_dir.exists():
            asset_count = len(list(self.assets_dir.iterdir()))
            print(f"| assets/ | ✅ | {asset_count} 个文件 |")
        else:
            print(f"| assets/ | - | 不存在 |")
        
        # 问题清单
        if not self.issues:
            print("\n✅ 所有检查项通过！技能质量优秀。")
        else:
            print(f"\n## 问题清单 (共 {len(self.issues)} 个)")
            print(f"\n| 优先级 | 类别 | 问题 |")
            print(f"|--------|------|------|")
            
            for priority, category, message in sorted(self.issues, key=lambda x: x[0]):
                print(f"| {priority} | {category} | {message} |")
            
            # 统计
            p0_count = len([i for i in self.issues if i[0] == 'P0'])
            p1_count = len([i for i in self.issues if i[0] == 'P1'])
            p2_count = len([i for i in self.issues if i[0] == 'P2'])
            
            print(f"\n## 统计")
            print(f"- P0 (阻塞性): {p0_count} 个")
            print(f"- P1 (结构): {p1_count} 个")
            print(f"- P2 (优化): {p2_count} 个")
            
            if p0_count > 0:
                print(f"\n❌ 存在 {p0_count} 个阻塞性问题，必须修复")
            elif p1_count > 0:
                print(f"\n⚠️ 存在 {p1_count} 个结构问题，建议修复")
            else:
                print(f"\n✅ 无阻塞性问题，可以交付")
        
        print("\n" + "=" * 60)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 scripts/validate-skill.py <skill-dir>")
        print("示例: python3 scripts/validate-skill.py ./my-new-skill")
        sys.exit(1)
    
    skill_dir = sys.argv[1]
    
    if not Path(skill_dir).exists():
        print(f"❌ 错误: 目录不存在: {skill_dir}")
        sys.exit(1)
    
    if not Path(skill_dir).is_dir():
        print(f"❌ 错误: 路径不是目录: {skill_dir}")
        sys.exit(1)
    
    validator = SkillValidator(skill_dir)
    success = validator.validate()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
