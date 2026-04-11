#!/usr/bin/env node

/**
 * publish.js - 发布 Markdown 到微信公众号草稿箱
 * 复用 ai-writer 的 styles.json 主题系统
 * 
 * 用法:
 *   node publish.js <markdown-file> [theme-name]
 * 
 * 示例:
 *   node publish.js article.md
 *   node publish.js article.md 灵动蓝
 *   node publish.js article.md 科技蓝
 */

const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// ─── 配置 ─────────────────────────────────────────────────
const STYLES_PATH = path.join(__dirname, '../styles.json');
const USER_CONFIG_PATH = path.join(os.homedir(), '.config', 'ai-writer', 'config.json');
const TOOLS_MD_PATHS = [
    path.join(os.homedir(), '.openclaw', 'workspace-xina-gongzhonghao', 'TOOLS.md'),
    path.join(os.homedir(), '.openclaw', 'workspace', 'TOOLS.md'),
];
const DEFAULT_THEME = 'default';
const THEMES_DIR = path.join(__dirname, 'themes'); // ai-writer 自己的主题目录

// ai-writer 主题名称到自定义 CSS 的映射（所有主题都使用自定义 CSS）
const THEME_MAPPING = {
    '灵动蓝': path.join(THEMES_DIR, '灵动蓝.css'),
    '锤子便签': path.join(THEMES_DIR, '锤子便签.css'),
    '柠檬黄': path.join(THEMES_DIR, '柠檬黄.css'),
    '科技蓝': path.join(THEMES_DIR, '科技蓝.css'),
    '雁栖湖': path.join(THEMES_DIR, '雁栖湖.css'),
    '极简黑': path.join(THEMES_DIR, '极简黑.css'),
    '橙心': path.join(THEMES_DIR, '橙心.css'),
    '绿意': path.join(THEMES_DIR, '绿意.css'),
    'Obsidian': path.join(THEMES_DIR, 'Obsidian.css'),
    '前端之巅同款': path.join(THEMES_DIR, '前端之巅同款.css'),
    '全栈蓝': path.join(THEMES_DIR, '全栈蓝.css'),
    '草原绿': path.join(THEMES_DIR, '草原绿.css'),
    '重影': path.join(THEMES_DIR, '重影.css'),
    '红绯': path.join(THEMES_DIR, '红绯.css'),
};

// ─── 颜色输出 ──────────────────────────────────────────────
const supportsColor = process.stdout.isTTY;
const color = {
    red:    (s) => supportsColor ? `\x1b[31m${s}\x1b[0m` : s,
    green:  (s) => supportsColor ? `\x1b[32m${s}\x1b[0m` : s,
    yellow: (s) => supportsColor ? `\x1b[33m${s}\x1b[0m` : s,
};

// ─── 加载主题 ──────────────────────────────────────────────
function loadThemes() {
    if (!fs.existsSync(STYLES_PATH)) {
        console.error(color.red(`❌ 主题文件不存在: ${STYLES_PATH}`));
        process.exit(1);
    }
    return JSON.parse(fs.readFileSync(STYLES_PATH, 'utf-8'));
}

function listThemes() {
    const themes = loadThemes();
    console.log(color.green('🎨 可用主题列表:\n'));
    
    const themeNames = Object.keys(themes);
    themeNames.forEach((name, index) => {
        const marker = name === DEFAULT_THEME ? ' (默认)' : '';
        console.log(`  ${index + 1}. ${name}${marker}`);
    });
    
    console.log(`\n共 ${themeNames.length} 个主题`);
    console.log(color.yellow('\n使用方式: node publish.js article.md 主题名称'));
}

// ─── 解析 Frontmatter ────────────────────────────────────
function parseFrontmatter(mdContent) {
    const frontmatterMatch = mdContent.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
    
    if (!frontmatterMatch) {
        return { frontmatter: {}, body: mdContent };
    }
    
    const fmLines = frontmatterMatch[1].split('\n');
    const frontmatter = {};
    
    fmLines.forEach(line => {
        const colonIndex = line.indexOf(':');
        if (colonIndex > 0) {
            const key = line.substring(0, colonIndex).trim();
            const value = line.substring(colonIndex + 1).trim();
            frontmatter[key] = value;
        }
    });
    
    return {
        frontmatter,
        body: frontmatterMatch[2]
    };
}

// ─── 移除正文中的 H1 标题 ─────────────────────────────────
function removeH1FromBody(body) {
    // 移除开头的 # 标题行（frontmatter 的 title 会作为标题）
    const lines = body.split('\n');
    const filteredLines = [];
    let skipNextEmpty = false;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // 跳过第一个 H1 标题
        if (line.startsWith('# ') && !line.startsWith('## ')) {
            skipNextEmpty = true;
            continue;
        }
        
        // 如果上一行是 H1，跳过紧随其后的空行
        if (skipNextEmpty && line === '') {
            skipNextEmpty = false;
            continue;
        }
        
        skipNextEmpty = false;
        filteredLines.push(lines[i]);
    }
    
    return filteredLines.join('\n').trim();
}

// ─── 应用主题样式并转换为 HTML ────────────────────────────
function applyThemeAndConvert(mdBody, themeData) {
    // 简化版 Markdown 转 HTML（实际应该复用 md-editor.html 的完整逻辑）
    // 这里做基础转换，wenyan-cli 会进一步处理样式
    
    let html = mdBody;
    
    // 转换图片路径为绝对路径
    html = html.replace(/\]\(\.\/images\//g, `](${path.dirname(process.argv[2])}/images/`);
    
    return html;
}

// ─── Markdown 转 HTML (复用 md-editor.html 的逻辑) ──────
function mdToHtml(mdContent, themeData) {
    // 简化的 Markdown 转 HTML 实现
    // 完整实现应该复用 md-editor.html 中的 MD2HTML 转换器
    
    let html = mdContent;
    
    // 提取 frontmatter
    const frontmatterMatch = html.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
    let frontmatter = {};
    let bodyContent = html;
    
    if (frontmatterMatch) {
        const fmLines = frontmatterMatch[1].split('\n');
        fmLines.forEach(line => {
            const [key, ...valueParts] = line.split(':');
            if (key && valueParts.length) {
                frontmatter[key.trim()] = valueParts.join(':').trim();
            }
        });
        bodyContent = frontmatterMatch[2];
    }
    
    // 基础转换 (实际应该使用完整的 MD2HTML 转换器)
    // 这里先做简单转换,完整转换需要嵌入 md-editor.html 的逻辑
    
    return {
        html: bodyContent,
        frontmatter,
        title: frontmatter.title || '未命名文章',
        cover: frontmatter.cover || ''
    };
}

// ─── 从配置文件读取凭证 ────────────────────────────────────
function loadCredentials() {
    let appId = process.env.WECHAT_APP_ID || '';
    let secret = process.env.WECHAT_APP_SECRET || '';

    // 优先从用户配置文件读取
    if (!appId || !secret) {
        if (fs.existsSync(USER_CONFIG_PATH)) {
            try {
                const userConfig = JSON.parse(fs.readFileSync(USER_CONFIG_PATH, 'utf-8'));
                if (userConfig.wechat?.app_id && !appId) {
                    appId = userConfig.wechat.app_id;
                }
                if (userConfig.wechat?.app_secret && !secret) {
                    secret = userConfig.wechat.app_secret;
                }
                if (appId && secret) {
                    console.log(color.yellow(`📖 凭证从 ${USER_CONFIG_PATH} 读取`));
                    return { appId, secret };
                }
            } catch (e) {
                console.error(color.yellow(`⚠️  读取配置文件失败: ${e.message}`));
            }
        }
    }

    // 如果环境变量已设置,直接返回
    if (appId && secret) {
        return { appId, secret };
    }

    // 备选: 从 TOOLS.md 读取
    for (const toolsPath of TOOLS_MD_PATHS) {
        if (!fs.existsSync(toolsPath)) continue;
        const content = fs.readFileSync(toolsPath, 'utf-8');
        for (const line of content.split('\n')) {
            const idMatch = line.match(/export\s+WECHAT_APP_ID=(\S+)/);
            if (idMatch) appId = idMatch[1];
            const secretMatch = line.match(/export\s+WECHAT_APP_SECRET=(\S+)/);
            if (secretMatch) secret = secretMatch[1];
        }
        if (appId && secret) {
            console.log(color.yellow(`📖 凭证从 ${toolsPath} 读取`));
            return { appId, secret };
        }
    }

    return { appId, secret };
}

// ─── 检查环境变量 ─────────────────────────────────────────
function checkEnv() {
    const { appId, secret } = loadCredentials();
    if (!appId || !secret) {
        console.error(color.red('❌ 微信公众号 API 凭证未设置！'));
        console.log(color.yellow('\n请先配置凭证，选择以下任一方式：\n'));
        console.log('方式1 (推荐): 写入配置文件');
        console.log(`  文件位置: ${USER_CONFIG_PATH}`);
        console.log('  添加内容:');
        console.log('  {');
        console.log('    "wechat": {');
        console.log('      "app_id": "your_app_id",');
        console.log('      "app_secret": "your_app_secret"');
        console.log('    }');
        console.log('  }\n');
        console.log('方式2: 设置环境变量');
        console.log('  export WECHAT_APP_ID=your_app_id');
        console.log('  export WECHAT_APP_SECRET=your_app_secret\n');
        console.log('方式3: 在 TOOLS.md 中添加');
        console.log('  文件位置: ~/.openclaw/workspace/TOOLS.md');
        console.log('  添加内容:');
        console.log('  export WECHAT_APP_ID=your_app_id');
        console.log('  export WECHAT_APP_SECRET=your_app_secret\n');
        process.exit(1);
    }
    return { appId, secret };
}

// ─── 检查 wenyan-cli ──────────────────────────────────────
function checkWenyan() {
    try {
        execFileSync('wenyan', ['--version'], { stdio: 'pipe' });
        return true;
    } catch {
        console.log(color.yellow('⚠️  wenyan-cli 未安装'));
        console.log(color.yellow('正在安装 @wenyan-md/cli...\n'));
        try {
            execFileSync('npm', ['install', '-g', '@wenyan-md/cli'], { stdio: 'inherit' });
            console.log(color.green('✅ wenyan-cli 安装成功！\n'));
            return true;
        } catch (e) {
            console.error(color.red('❌ 安装失败！请手动运行: npm install -g @wenyan-md/cli'));
            process.exit(1);
        }
    }
}

// ─── 发布到微信 ────────────────────────────────────────────
function publishToWechat(mdFile, themeName, appId, secret) {
    const themes = loadThemes();
    
    // 将 ai-writer 主题名称映射为 wenyan 主题 ID 或自定义 CSS 路径
    const themeValue = THEME_MAPPING[themeName] || DEFAULT_THEME;
    const isCustomCss = themeValue.endsWith('.css');
    
    if (!themes[themeName]) {
        console.error(color.red(`❌ 主题不存在: ${themeName}`));
        console.log(color.yellow(`\n可用主题: ${Object.keys(themes).join(', ')}`));
        process.exit(1);
    }
    
    console.log(color.green('📝 准备发布文章...'));
    console.log(`  文件: ${mdFile}`);
    console.log(`  主题: ${themeName}${isCustomCss ? ' (自定义 CSS)' : ` (wenyan: ${themeValue})`}`);
    console.log('');
    
    // 读取 Markdown 文件
    let mdContent = fs.readFileSync(mdFile, 'utf-8');
    
    // 解析 frontmatter
    const { frontmatter, body } = parseFrontmatter(mdContent);
    
    if (!frontmatter.title || !frontmatter.cover) {
        console.error(color.red('❌ Markdown 文件缺少必需的 frontmatter！'));
        console.log(color.yellow('\n文件顶部必须包含:\n'));
        console.log('---');
        console.log('title: 文章标题 (必填!)');
        console.log('cover: 封面图绝对路径 (必填!)');
        console.log('digest: 摘要 (选填，不填则自动提取正文前54字)');
        console.log('---\n');
        process.exit(1);
    }
    
    console.log(`  标题: ${frontmatter.title}`);
    console.log(`  封面: ${frontmatter.cover}`);
    if (frontmatter.digest) {
        console.log(`  摘要: ${frontmatter.digest}`);
    }
    console.log('');
    
    // 检查正文是否有 H1 标题（提醒用户）
    if (body.match(/^# /m)) {
        console.log(color.yellow('⚠️  警告: 正文中包含 H1 标题 (# )，可能导致标题重复！'));
        console.log(color.yellow('   建议在生成文章时不要使用 # 标题，frontmatter 的 title 会作为标题。\n'));
    }
    
    // 使用 wenyan-cli 发布
    const env = { ...process.env, WECHAT_APP_ID: appId, WECHAT_APP_SECRET: secret };
    
    try {
        // wenyan 发布命令，使用 -t 或 -c 参数
        let args;
        if (isCustomCss) {
            // 自定义 CSS 主题使用 -c 参数
            args = ['publish', '-f', mdFile, '-c', themeValue];
        } else {
            // wenyan 内置主题使用 -t 参数
            args = ['publish', '-f', mdFile, '-t', themeValue];
        }
        
        execFileSync('wenyan', args, {
            env,
            stdio: 'inherit',
        });
        
        console.log('');
        console.log(color.green('✅ 发布成功！'));
        console.log(color.yellow('📱 请前往微信公众号后台草稿箱查看：'));
        console.log('  https://mp.weixin.qq.com/');
    } catch (error) {
        console.log('');
        console.error(color.red('❌ 发布失败！'));
        console.log(color.yellow('\n💡 常见问题：'));
        console.log('  1. IP 未在白名单 → 添加到公众号后台');
        console.log('  2. Frontmatter 缺失 → 文件顶部添加 title + cover');
        console.log('  3. API 凭证错误 → 检查环境变量或 TOOLS.md');
        console.log('  4. 封面图路径错误 → 必须使用绝对路径');
        console.log('  5. 封面图尺寸错误 → 建议 1080×864 像素');
        console.log('  6. 自定义 CSS 路径错误 → 检查文件是否存在');
        process.exit(1);
    }
}

// ─── 主函数 ───────────────────────────────────────────────
function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0 || args[0] === '-h' || args[0] === '--help') {
        console.log(`用法: node publish.js <markdown-file> [theme-name]

示例:
  node publish.js article.md                    # 使用默认主题
  node publish.js article.md 灵动蓝              # 指定主题
  node publish.js article.md 科技蓝              # 指定主题
  node publish.js --list                        # 列出所有主题

可用主题: 见 styles.json 文件
默认主题: ${DEFAULT_THEME}

前置要求:
  1. 安装 wenyan-cli: npm install -g @wenyan-md/cli
  2. 配置微信凭证: export WECHAT_APP_ID 和 WECHAT_APP_SECRET
  3. Markdown 文件必须包含 frontmatter (title + cover)`);
        process.exit(0);
    }
    
    if (args[0] === '--list' || args[0] === '--list-themes') {
        listThemes();
        process.exit(0);
    }
    
    const mdFile = args[0];
    const themeName = args[1] || DEFAULT_THEME;
    
    // 检查文件
    if (!fs.existsSync(mdFile)) {
        console.error(color.red(`❌ 文件不存在: ${mdFile}`));
        process.exit(1);
    }
    
    // 检查 wenyan-cli
    checkWenyan();
    
    // 检查凭证
    const { appId, secret } = checkEnv();
    
    // 发布
    publishToWechat(mdFile, themeName, appId, secret);
}

main();
