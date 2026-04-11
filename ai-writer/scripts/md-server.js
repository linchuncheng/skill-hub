#!/usr/bin/env node
/**
 * Markdown Editor Server
 * 提供文章列表API和静态文件服务
 * 用法: node md-server.js [端口] [文章目录]
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = process.argv[2] || 3456;
const ARTICLES_DIR = process.argv[3] || path.join(require('os').homedir(), 'Documents', '文章');
const STYLES_FILE = path.join(__dirname, 'styles.json');

// 图片服务配置 - 统一使用 ~/Documents/文章/images/
const IMAGES_DIR = path.join(require('os').homedir(), 'Documents', '文章', 'images');

// 自动停止配置
const AUTO_SHUTDOWN_MINUTES = 30;
let lastAccessTime = Date.now();
let shutdownTimer = null;

// MIME 类型映射
const MIME_TYPES = {
    '.html': 'text/html',
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

/**
 * 获取文章列表（按时间倒序）
 */
function getArticlesList() {
    try {
        if (!fs.existsSync(ARTICLES_DIR)) {
            return { success: false, error: '文章目录不存在: ' + ARTICLES_DIR };
        }

        const entries = fs.readdirSync(ARTICLES_DIR, { withFileTypes: true });
        const articles = [];

        for (const entry of entries) {
            if (entry.isFile() && entry.name.endsWith('.md')) {
                const filePath = path.join(ARTICLES_DIR, entry.name);
                const stats = fs.statSync(filePath);
                articles.push({
                    name: entry.name,
                    title: entry.name.replace(/\.md$/i, ''),
                    modifiedTime: stats.mtime.getTime(),
                    modifiedTimeStr: stats.mtime.toLocaleString('zh-CN'),
                    size: stats.size
                });
            }
        }

        // 按修改时间倒序排列
        articles.sort((a, b) => b.modifiedTime - a.modifiedTime);

        return { success: true, articles, directory: ARTICLES_DIR };
    } catch (err) {
        return { success: false, error: err.message };
    }
}

/**
 * 读取文章内容
 */
function getArticleContent(filename) {
    try {
        // 安全检查：防止目录遍历
        const sanitizedName = path.basename(filename);
        const filePath = path.join(ARTICLES_DIR, sanitizedName);

        if (!fs.existsSync(filePath)) {
            return { success: false, error: '文件不存在' };
        }

        const content = fs.readFileSync(filePath, 'utf-8');
        return { success: true, content, name: sanitizedName };
    } catch (err) {
        return { success: false, error: err.message };
    }
}

/**
 * 保存文章内容
 */
function saveArticleContent(filename, content) {
    try {
        const sanitizedName = path.basename(filename);
        const filePath = path.join(ARTICLES_DIR, sanitizedName);

        fs.writeFileSync(filePath, content, 'utf-8');
        return { success: true, name: sanitizedName };
    } catch (err) {
        return { success: false, error: err.message };
    }
}

/**
 * 获取主题列表
 */
function getThemes() {
    try {
        if (!fs.existsSync(STYLES_FILE)) {
            return { success: false, error: '样式文件不存在' };
        }
        
        const content = fs.readFileSync(STYLES_FILE, 'utf-8');
        const themes = JSON.parse(content);
        
        return { success: true, themes };
    } catch (err) {
        return { success: false, error: err.message };
    }
}

/**
 * 处理 API 请求
 */
function handleAPIRequest(req, res, pathname, query) {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.setHeader('Access-Control-Allow-Origin', '*');

    if (pathname === '/api/articles') {
        const result = getArticlesList();
        res.end(JSON.stringify(result));
        return true;
    }

    if (pathname === '/api/article') {
        const filename = query.name;
        if (!filename) {
            res.statusCode = 400;
            res.end(JSON.stringify({ success: false, error: '缺少文件名参数' }));
            return true;
        }
        const result = getArticleContent(filename);
        res.statusCode = result.success ? 200 : 404;
        res.end(JSON.stringify(result));
        return true;
    }

    if (pathname === '/api/save' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                const result = saveArticleContent(data.name, data.content);
                res.statusCode = result.success ? 200 : 500;
                res.end(JSON.stringify(result));
            } catch (err) {
                res.statusCode = 400;
                res.end(JSON.stringify({ success: false, error: '无效的请求数据' }));
            }
        });
        return true;
    }

    if (pathname === '/api/themes') {
        const result = getThemes();
        res.statusCode = result.success ? 200 : 500;
        res.end(JSON.stringify(result));
        return true;
    }

    return false;
}

/**
 * 处理图片文件请求
 * 支持路径格式：
 * 1. /images/xxx - 旧格式，从统一的 images 目录提供
 * 2. /images/文章标题_images/xxx - 新格式，按文章标题分组的图片目录
 */
function handleImageRequest(req, res, pathname) {
    // 解码 URL
    const decodedPath = decodeURIComponent(pathname);
    
    // 安全检查：防止目录遍历
    if (decodedPath.includes('..')) {
        return false;
    }
    
    // 只处理 /images/ 开头的路径
    if (!pathname.startsWith('/images/')) {
        return false;
    }
    
    // 移除 /images/ 前缀
    const imagePath = decodedPath.replace(/^\/images\//, '');
    const filePath = path.join(IMAGES_DIR, imagePath);
    
    const resolvedPath = path.resolve(filePath);
    const resolvedImagesDir = path.resolve(IMAGES_DIR);
    
    // 安全检查：确保文件在图片目录下
    if (!resolvedPath.startsWith(resolvedImagesDir)) {
        return false;
    }
    
    if (fs.existsSync(filePath)) {
        const ext = path.extname(filePath).toLowerCase();
        const contentType = MIME_TYPES[ext] || 'image/jpeg';
        
        res.setHeader('Content-Type', contentType);
        res.setHeader('Cache-Control', 'public, max-age=86400');
        fs.createReadStream(filePath).pipe(res);
        return true;
    }
    
    return false;
}

/**
 * 处理静态文件请求
 */
function handleStaticFile(req, res, pathname) {
    // 处理图片请求 /images/xxx
    if (pathname.startsWith('/images/')) {
        if (handleImageRequest(req, res, pathname)) {
            return;
        }
        // 图片未找到，返回 404
        res.statusCode = 404;
        res.end('Image Not Found');
        return;
    }
    
    // 默认返回 md-editor.html
    let filePath;
    if (pathname === '/' || pathname === '/index.html') {
        filePath = path.join(__dirname, 'md-editor.html');
    } else {
        // 移除开头的 /，防止路径遍历
        const safePath = pathname.replace(/^\//, '');
        filePath = path.join(__dirname, safePath);
    }

    // 安全检查：确保文件在脚本目录下
    const resolvedPath = path.resolve(filePath);
    const scriptDir = path.resolve(__dirname);
    if (!resolvedPath.startsWith(scriptDir)) {
        res.statusCode = 403;
        res.end('Forbidden');
        return;
    }

    if (!fs.existsSync(filePath)) {
        res.statusCode = 404;
        res.end('Not Found');
        return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    res.setHeader('Content-Type', contentType + '; charset=utf-8');
    fs.createReadStream(filePath).pipe(res);
}

// 创建 HTTP 服务器
const server = http.createServer((req, res) => {
    // 记录访问并重置计时器
    logAccess(req);
    resetShutdownTimer();
    
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    const query = parsedUrl.query;

    // 处理 API 请求
    if (pathname.startsWith('/api/')) {
        if (handleAPIRequest(req, res, pathname, query)) {
            return;
        }
    }

    // 处理静态文件
    handleStaticFile(req, res, pathname);
});

// 重置自动停止计时器
function resetShutdownTimer() {
    lastAccessTime = Date.now();
    
    if (shutdownTimer) {
        clearTimeout(shutdownTimer);
    }
    
    shutdownTimer = setTimeout(() => {
        const idleMinutes = (Date.now() - lastAccessTime) / 1000 / 60;
        if (idleMinutes >= AUTO_SHUTDOWN_MINUTES) {
            console.log(`\n⏰ ${AUTO_SHUTDOWN_MINUTES}分钟无访问，自动停止服务`);
            process.exit(0);
        }
    }, AUTO_SHUTDOWN_MINUTES * 60 * 1000);
}

// 记录访问日志
function logAccess(req) {
    const now = new Date().toLocaleTimeString('zh-CN');
    const pathname = url.parse(req.url).pathname;
    console.log(`[${now}] ${req.method} ${pathname}`);
}

server.listen(PORT, () => {
    console.log(`\n✅ Markdown Editor Server 已启动`);
    console.log(`📁 文章目录: ${ARTICLES_DIR}`);
    console.log(`🌐 访问地址: http://localhost:${PORT}`);
    console.log(`⏰ 自动停止: ${AUTO_SHUTDOWN_MINUTES}分钟无访问后`);
    console.log(`\n按 Ctrl+C 停止服务\n`);
    
    // 启动自动停止计时器
    resetShutdownTimer();
});

// 优雅退出
process.on('SIGINT', () => {
    console.log('\n👋 服务已停止');
    process.exit(0);
});
