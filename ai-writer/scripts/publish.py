#!/usr/bin/env python3
"""
publish.py - 发布 Markdown 到微信公众号草稿箱
使用 WeChat MD Publisher 提供 6 种精美主题

用法:
  python3 ai-writer/scripts/publish.py <markdown-file> [theme-name]

示例:
  python3 ai-writer/scripts/publish.py article.md
  python3 ai-writer/scripts/publish.py article.md orangesun
  python3 ai-writer/scripts/publish.py article.md greenmint
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# ─── 配置 ─────────────────────────────────────────────────
USER_CONFIG_PATH = Path.home() / '.config' / 'ai-writer' / 'config.json'
DEFAULT_THEME = 'default'

# WeChat MD Publisher 内置的 6 种主题
THEMES = {
    'default': {'name': '简约默认', 'desc': '简洁清爽的默认样式,适合各类文章'},
    'orangesun': {'name': '橙光', 'desc': '温暖明亮的橙色阳光风格'},
    'redruby': {'name': '红宝石', 'desc': '优雅醒目的红宝石红色'},
    'greenmint': {'name': '薄荷绿', 'desc': '清新舒适的薄荷绿'},
    'purplerain': {'name': '紫雨', 'desc': '梦幻柔和的紫色渐变'},
    'blackink': {'name': '墨黑', 'desc': '深色模式配靛蓝accent,适合夜间阅读'}
}

# ─── 颜色输出 ──────────────────────────────────────────────
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def success(msg):
    print(f"{Colors.GREEN}{msg}{Colors.RESET}")

def warning(msg):
    print(f"{Colors.YELLOW}{msg}{Colors.RESET}")

def error(msg):
    print(f"{Colors.RED}{msg}{Colors.RESET}")

# ─── 从配置文件读取配置 ────────────────────────────────────
def load_config():
    """从配置文件读取微信凭证和默认主题"""
    config = {
        'app_id': '',
        'app_secret': '',
        'default_theme': DEFAULT_THEME
    }
    
    if USER_CONFIG_PATH.exists():
        try:
            with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            if 'wechat' in user_config:
                config['app_id'] = user_config['wechat'].get('app_id', '')
                config['app_secret'] = user_config['wechat'].get('app_secret', '')
            
            if 'publish' in user_config:
                config['default_theme'] = user_config['publish'].get('default_theme', DEFAULT_THEME)
        except Exception as e:
            warning(f'⚠️  读取配置文件失败: {e}')
    
    return config

# ─── 检查配置 ─────────────────────────────────────────
def check_config():
    """检查微信凭证是否配置"""
    config = load_config()
    
    if not config['app_id'] or not config['app_secret']:
        error('❌ 微信公众号 API 凭证未设置！')
        warning('\n请按以下步骤配置凭证：\n')
        print('1. 创建配置目录:')
        print('   mkdir -p ~/.config/ai-writer\n')
        print('2. 创建配置文件:')
        print(f'   文件位置: {USER_CONFIG_PATH}\n')
        print('3. 添加以下内容:')
        print('   {')
        print('     "wechat": {')
        print('       "app_id": "你的app_id",')
        print('       "app_secret": "你的app_secret"')
        print('     },')
        print('     "publish": {')
        print('       "default_theme": "default"  // 可选,默认主题')
        print('     }')
        print('   }\n')
        warning('💡 提示: app_id 和 app_secret 可从微信公众号后台获取')
        sys.exit(1)
    
    return config

# ─── 主题列表 ──────────────────────────────────────────────
def list_themes():
    """显示可用主题列表"""
    success('🎨 可用主题列表:\n')
    
    for idx, (theme_id, theme_info) in enumerate(THEMES.items(), 1):
        marker = ' (默认)' if theme_id == DEFAULT_THEME else ''
        print(f"  {idx}. {theme_id} - {theme_info['name']}{marker}")
        print(f"     {theme_info['desc']}")
    
    print(f"\n共 {len(THEMES)} 个主题")
    warning('\n使用方式: python3 publish.py article.md 主题ID')

# ─── 初始化 wechat-pub 账号 ───────────────────────────────
def init_wechat_pub(config):
    """初始化 wechat-pub 账号配置"""
    success('⚙️  正在配置 wechat-pub 账号...\n')
    
    try:
        cmd = [
            'wechat-pub', 'account', 'add',
            '--name', 'AI Writer',
            '--app-id', config['app_id'],
            '--app-secret', config['app_secret'],
            '--default'
        ]
        subprocess.run(cmd, check=True)
        success('\n✅ 账号配置成功！现在可以发布文章了')
    except subprocess.CalledProcessError:
        # 账号已存在,说明已经配置过了
        warning('\nℹ️  账号已存在,无需重复配置')
        success('✅ 可以直接发布文章了')

# ─── 发布到微信 ────────────────────────────────────────────
def publish_to_wechat(md_file, theme_name, config):
    """发布 Markdown 文件到微信公众号"""
    # 验证主题是否存在
    if theme_name not in THEMES:
        error(f'❌ 主题不存在: {theme_name}')
        warning(f"\n可用主题: {', '.join(THEMES.keys())}")
        sys.exit(1)
    
    # 读取 Markdown 文件
    if not os.path.exists(md_file):
        error(f'❌ 文件不存在: {md_file}')
        sys.exit(1)
    
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 解析 frontmatter
    if not md_content.startswith('---'):
        error('❌ Markdown 文件缺少 frontmatter！')
        warning('\n文件顶部必须包含:\n')
        print('---')
        print('title: 文章标题 (必填!)')
        print('cover: 封面图绝对路径 (必填!)')
        print('digest: 摘要 (选填，不填则自动提取正文前54字)')
        print('---\n')
        sys.exit(1)
    
    # 提取 frontmatter
    parts = md_content.split('---', 2)
    if len(parts) < 3:
        error('❌ frontmatter 格式错误！')
        sys.exit(1)
    
    fm_content = parts[1].strip()
    frontmatter = {}
    for line in fm_content.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()
    
    if not frontmatter.get('title') or not frontmatter.get('cover'):
        error('❌ Markdown 文件缺少必需的 frontmatter！')
        warning('\n文件顶部必须包含:\n')
        print('---')
        print('title: 文章标题 (必填!)')
        print('cover: 封面图绝对路径 (必填!)')
        print('digest: 摘要 (选填，不填则自动提取正文前54字)')
        print('---\n')
        sys.exit(1)
    
    success('📝 准备发布文章...')
    print(f"  文件: {md_file}")
    print(f"  主题: {theme_name} ({THEMES[theme_name]['name']})")
    print(f"  标题: {frontmatter['title']}")
    print(f"  封面: {frontmatter['cover']}")
    if frontmatter.get('digest'):
        print(f"  摘要: {frontmatter['digest']}")
    print()
    
    # 检查正文是否有 H1 标题
    body = parts[2] if len(parts) > 2 else ''
    if body.strip().startswith('# ') or '\n# ' in body:
        warning('⚠️  警告: 正文中包含 H1 标题 (# )，可能导致标题重复！')
        warning('   建议在生成文章时不要使用 # 标题，frontmatter 的 title 会作为标题。\n')
    
    # 使用 WeChat MD Publisher 发布
    effective_theme = theme_name or config.get('default_theme') or DEFAULT_THEME
    
    try:
        # wechat-pub 发布命令
        cmd = ['wechat-pub', 'publish', 'create', '-f', md_file, '-t', effective_theme]
        
        warning('ℹ️  正在发布到公众号...\n')
        
        subprocess.run(cmd, check=True)
        
        print()
        success('✅ 发布成功！')
        warning('📱 请前往微信公众号后台草稿箱查看：')
        print('  https://mp.weixin.qq.com/')
    except subprocess.CalledProcessError as e:
        print()
        error('❌ 发布失败！')
        warning('\n💡 常见问题：')
        print('  1. 未配置账号 → 运行 python3 publish.py --init 配置')
        print('  2. Frontmatter 缺失 → 文件顶部添加 title + cover')
        print('  3. API 凭证错误 → 检查账号配置')
        print('  4. 封面图路径错误 → 必须使用URL或绝对路径')
        print('  5. 封面图尺寸错误 → 建议 1080×864 像素')
        sys.exit(1)

# ─── 主函数 ────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    
    if not args:
        print(f"""用法: python3 publish.py <markdown-file> [theme-name]

示例:
  python3 publish.py article.md                    # 使用默认主题
  python3 publish.py article.md orangesun          # 使用橙光主题
  python3 publish.py article.md greenmint          # 使用薄荷绿主题
  python3 publish.py --list                        # 列出所有主题
  python3 publish.py --init                        # 初始化 wechat-pub 账号

可用主题: {', '.join(THEMES.keys())}
默认主题: {DEFAULT_THEME}

前置要求:
  1. 安装 wechat-md-publisher: npm install -g wechat-md-publisher
  2. 首次配置: python3 ai-writer/scripts/publish.py --init
  3. 配置微信凭证: 创建 ~/.config/ai-writer/config.json
  4. Markdown 文件必须包含 frontmatter (title + cover)""")
        sys.exit(0)
    
    # 列出主题
    if args[0] in ['--list', '--list-themes']:
        list_themes()
        sys.exit(0)
    
    # 首次配置:初始化 wechat-pub 账号
    if args[0] == '--init':
        config = check_config()
        init_wechat_pub(config)
        sys.exit(0)
    
    md_file = args[0]
    
    # 检查文件
    if not os.path.exists(md_file):
        error(f'❌ 文件不存在: {md_file}')
        sys.exit(1)
    
    # 获取主题(从参数或配置文件)
    theme_name = args[1] if len(args) > 1 else None
    
    # 检查配置
    config = check_config()
    
    # 如果没有指定主题,使用配置文件中的默认主题
    if not theme_name:
        theme_name = config.get('default_theme', DEFAULT_THEME)
    
    # 发布
    publish_to_wechat(md_file, theme_name, config)

if __name__ == '__main__':
    main()
