#!/usr/bin/env python3
"""
微信公众号文章图片下载脚本
提取 Markdown 中的图片链接，下载到本地并替换为本地路径

用法:
    python3 download_images.py <md_file> [--output-dir <dir>]
"""

import re
import sys
import argparse
import hashlib
import requests
from pathlib import Path
from urllib.parse import urlparse, unquote


def extract_images_from_md(md_content: str) -> list:
    """
    从 Markdown 内容中提取所有图片链接
    支持格式: ![alt](url) 和 <img src="url">
    """
    images = []
    
    # 匹配 Markdown 图片语法: ![alt](url)
    md_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    for match in re.finditer(md_pattern, md_content):
        alt_text = match.group(1)
        url = match.group(2)
        images.append({
            'type': 'markdown',
            'alt': alt_text,
            'url': url,
            'match': match.group(0),
            'start': match.start(),
            'end': match.end()
        })
    
    # 匹配 HTML img 标签: <img src="url" ...>
    html_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
    for match in re.finditer(html_pattern, md_content):
        url = match.group(1)
        images.append({
            'type': 'html',
            'url': url,
            'match': match.group(0),
            'start': match.start(),
            'end': match.end()
        })
    
    return images


def get_image_extension(url: str, content_type: str = None) -> str:
    """根据 URL 或 Content-Type 获取图片扩展名"""
    # 从 URL 路径中提取
    parsed = urlparse(url)
    path = unquote(parsed.path)
    
    # 尝试从路径获取扩展名
    if '.' in path:
        ext = path.split('.')[-1].lower()
        if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp']:
            return ext if ext != 'jpeg' else 'jpg'
    
    # 从 Content-Type 获取
    if content_type:
        content_type = content_type.lower()
        if 'jpeg' in content_type or 'jpg' in content_type:
            return 'jpg'
        elif 'png' in content_type:
            return 'png'
        elif 'gif' in content_type:
            return 'gif'
        elif 'webp' in content_type:
            return 'webp'
        elif 'svg' in content_type:
            return 'svg'
    
    # 默认返回 jpg
    return 'jpg'


def download_image(url: str, output_path: Path, headers: dict = None) -> bool:
    """
    下载单个图片
    """
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://mp.weixin.qq.com/'
        }
    
    try:
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存图片
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"  ❌ 下载失败: {url[:60]}... - {e}")
        return False


def extract_title_from_md(content: str) -> str:
    """从 Markdown 内容中提取标题（第一个 # 开头的行）"""
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('# ') and len(line) > 2:
            return line[2:].strip()
    return "untitled"


def process_markdown(md_file: Path, output_dir: Path = None, articles_base_dir: Path = None) -> tuple:
    """
    处理 Markdown 文件，下载图片并替换链接
    图片保存规则：
    - 图片保存在 ~/Documents/文章/images/文章标题_images/ 目录下
    - 原稿和改写后的文章共用同一套图片
    - 使用相对路径 ./images/文章标题_images/xxx.webp
    
    Args:
        md_file: Markdown 文件路径
        output_dir: 指定图片输出目录（可选）
        articles_base_dir: 文章根目录，用于计算相对路径（默认为 ~/Documents/文章）
    
    Returns:
        (new_content, downloaded_count, failed_count)
    """
    # 读取原文件
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取图片
    images = extract_images_from_md(content)
    
    if not images:
        print(f"📄 未发现图片: {md_file.name}")
        return content, 0, 0
    
    print(f"🖼 发现 {len(images)} 张图片: {md_file.name}")
    
    # 设置文章根目录
    if articles_base_dir is None:
        articles_base_dir = Path.home() / 'Documents' / '文章'
    else:
        articles_base_dir = Path(articles_base_dir)
    
    # 设置图片保存目录
    # 使用文章标题作为目录名，保存在 images/ 下
    if output_dir is None:
        # 从内容中提取标题
        title = extract_title_from_md(content)
        # 清理标题中的特殊字符，作为目录名
        safe_title = re.sub(r'[^\w\u4e00-\u9fff\-]', '_', title)[:50]
        output_dir = articles_base_dir / 'images' / safe_title
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 图片保存目录: {output_dir}")
    
    # 下载图片并替换链接
    new_content = content
    downloaded = 0
    failed = 0
    
    for idx, img in enumerate(images, 1):
        url = img['url']
        
        # 跳过已经是本地路径的图片
        if url.startswith('./') or url.startswith('../') or url.startswith('/'):
            # 检查是否是已下载的图片
            if '/images/' in url:
                print(f"  ⏭ 已下载: {url}")
            else:
                print(f"  ⏭ 跳过本地图片: {url[:60]}...")
            continue
        
        # 生成文件名
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # 先尝试获取内容类型以确定扩展名
        try:
            head_resp = requests.head(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://mp.weixin.qq.com/'
            }, timeout=10)
            content_type = head_resp.headers.get('Content-Type', '')
        except:
            content_type = None
        
        ext = get_image_extension(url, content_type)
        filename = f"img_{idx:03d}_{url_hash}.{ext}"
        local_path = output_dir / filename
        
        # 下载图片
        if download_image(url, local_path):
            downloaded += 1
            # 使用统一的相对路径格式，这样原稿和改写后的文章都能正确引用
            # 路径格式: ./images/文章标题/img_001_xxx.webp
            relative_path = f"./images/{output_dir.name}/{filename}"
            
            # 替换链接
            if img['type'] == 'markdown':
                new_img_tag = f"![{img['alt']}]({relative_path})"
            else:
                # HTML img 标签，保留其他属性
                old_tag = img['match']
                new_img_tag = old_tag.replace(url, relative_path)
            
            # 在 new_content 中替换
            old_match = img['match']
            new_content = new_content.replace(old_match, new_img_tag, 1)
            
            print(f"  ✅ 已下载: {filename}")
        else:
            failed += 1
    
    return new_content, downloaded, failed


def main():
    parser = argparse.ArgumentParser(description='下载 Markdown 中的图片到本地')
    parser.add_argument('input', help='输入 Markdown 文件路径')
    parser.add_argument('-o', '--output-dir', help='图片输出目录 (默认: <md文件目录>/images/)')
    parser.add_argument('--in-place', action='store_true', help='直接修改原文件')
    parser.add_argument('--dry-run', action='store_true', help='仅显示要下载的图片，不实际下载')
    
    args = parser.parse_args()
    
    md_file = Path(args.input)
    if not md_file.exists():
        print(f"❌ 文件不存在: {md_file}")
        sys.exit(1)
    
    # 仅预览模式
    if args.dry_run:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        images = extract_images_from_md(content)
        print(f"📋 发现 {len(images)} 张图片:")
        for img in images:
            print(f"  - {img['url'][:80]}...")
        return
    
    # 处理文件
    new_content, downloaded, failed = process_markdown(md_file, args.output_dir)
    
    # 保存结果
    if args.in_place:
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"\n✅ 已更新文件: {md_file}")
    else:
        # 生成新文件名
        new_file = md_file.parent / f"{md_file.stem}_local{md_file.suffix}"
        with open(new_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"\n✅ 已保存到新文件: {new_file}")
    
    print(f"📊 下载统计: 成功 {downloaded} 张, 失败 {failed} 张")


if __name__ == '__main__':
    main()
