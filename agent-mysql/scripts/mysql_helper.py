#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MySQL 辅助工具 - 安装依赖、测试连接等"""

import subprocess
import sys
import json
import os
import argparse

def install_pymysql():
    """安装 pymysql 依赖"""
    print("正在安装 pymysql...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "pymysql",
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])
        print("✓ pymysql 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 安装失败: {e}")
        return False

def check_pymysql():
    """检查 pymysql 是否已安装"""
    try:
        import pymysql
        version = pymysql.__version__
        print(f"✓ pymysql 已安装: v{version}")
        return True
    except ImportError:
        print("✗ pymysql 未安装")
        return False

def test_connection(config_file=None, env_name=None):
    """测试数据库连接"""
    try:
        import pymysql
    except ImportError:
        print("请先安装 pymysql: python3 scripts/mysql_helper.py --install")
        return False
    
    # 加载配置
    if config_file:
        config_path = os.path.expanduser(config_file)
    else:
        config_path = os.path.expanduser("~/.config/agent-mysql/config.json")
    
    if not os.path.exists(config_path):
        print(f"✗ 配置文件不存在: {config_path}")
        return False
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    # 选择环境
    if env_name:
        env = env_name
    else:
        env = config_data.get('current', 'local')
    
    if env not in config_data:
        print(f"✗ 环境 '{env}' 不存在")
        print(f"可用环境: {', '.join([k for k in config_data.keys() if k != 'current'])}")
        return False
    
    config = config_data[env]
    config['charset'] = 'utf8mb4'
    config['cursorclass'] = pymysql.cursors.DictCursor
    
    print(f"\n正在测试连接 [{env}]...")
    print(f"  主机: {config.get('host', 'localhost')}:{config.get('port', 3306)}")
    print(f"  数据库: {config.get('database', 'N/A')}")
    print(f"  用户: {config.get('user', 'N/A')}")
    
    try:
        connection = pymysql.connect(**config)
        print("✓ 数据库连接成功")
        
        # 获取数据库版本
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION() as version;")
            version = cursor.fetchone()
            print(f"  MySQL 版本: {version['version']}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False

def create_config(config_file=None):
    """引导创建配置文件"""
    if config_file:
        config_path = os.path.expanduser(config_file)
    else:
        config_path = os.path.expanduser("~/.config/agent-mysql/config.json")
    
    # 检查是否已存在
    if os.path.exists(config_path):
        print(f"⚠ 配置文件已存在: {config_path}")
        response = input("是否覆盖? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("已取消操作")
            return False
    
    # 确保目录存在
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)
    
    print(f"\n{'='*50}")
    print("MySQL 数据库配置向导")
    print(f"{'='*50}\n")
    
    # 引导用户输入
    print("请输入数据库连接信息（直接回车使用默认值）:\n")
    
    env_name = input("环境名称 [local]: ").strip() or "local"
    host = input("主机地址 [localhost]: ").strip() or "localhost"
    port = input("端口号 [3306]: ").strip() or "3306"
    user = input("用户名 [root]: ").strip() or "root"
    password = input("密码: ").strip()
    database = input("数据库名: ").strip()
    
    if not database:
        print("✗ 数据库名不能为空")
        return False
    
    # 构建配置
    config_data = {
        "current": env_name,
        env_name: {
            "host": host,
            "port": int(port),
            "user": user,
            "password": password,
            "database": database
        }
    }
    
    # 写入配置
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ 配置文件创建成功: {config_path}")
        print(f"\n配置内容:")
        print(json.dumps(config_data, indent=2, ensure_ascii=False))
        
        # 询问是否测试连接
        response = input("\n是否测试数据库连接? (Y/n): ").strip().lower()
        if response not in ['n', 'no']:
            return test_connection(config_path, env_name)
        
        return True
        
    except Exception as e:
        print(f"✗ 创建配置文件失败: {e}")
        return False

def list_environments(config_file=None):
    """列出所有可用的环境"""
    if config_file:
        config_path = os.path.expanduser(config_file)
    else:
        config_path = os.path.expanduser("~/.config/agent-mysql/config.json")
    
    if not os.path.exists(config_path):
        print(f"✗ 配置文件不存在: {config_path}")
        return
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    current = config_data.get('current', 'N/A')
    environments = [k for k in config_data.keys() if k != 'current']
    
    print(f"\n可用环境 (当前: {current}):")
    print("-" * 50)
    for env_name in environments:
        env = config_data[env_name]
        marker = " ← 当前" if env_name == current else ""
        print(f"  {env_name}{marker}")
        print(f"    主机: {env.get('host', 'localhost')}:{env.get('port', 3306)}")
        print(f"    数据库: {env.get('database', 'N/A')}")
        print(f"    用户: {env.get('user', 'N/A')}")
        print()

def switch_environment(env_name, config_file=None):
    """切换当前环境"""
    if config_file:
        config_path = os.path.expanduser(config_file)
    else:
        config_path = os.path.expanduser("~/.config/agent-mysql/config.json")
    
    if not os.path.exists(config_path):
        print(f"✗ 配置文件不存在: {config_path}")
        return False
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    if env_name not in config_data or env_name == 'current':
        print(f"✗ 环境 '{env_name}' 不存在")
        return False
    
    config_data['current'] = env_name
    
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)
    
    print(f"✓ 已切换到环境: {env_name}")
    return True

def main():
    parser = argparse.ArgumentParser(description='MySQL 辅助工具')
    parser.add_argument('--install', action='store_true', help='安装 pymysql 依赖')
    parser.add_argument('--check', action='store_true', help='检查 pymysql 是否已安装')
    parser.add_argument('--init', action='store_true', help='创建/初始化配置文件')
    parser.add_argument('--test', action='store_true', help='测试数据库连接')
    parser.add_argument('--list', action='store_true', help='列出所有环境')
    parser.add_argument('--switch', type=str, help='切换到指定环境')
    parser.add_argument('--env', type=str, help='指定环境名称')
    parser.add_argument('--config', type=str, help='指定配置文件路径')
    
    args = parser.parse_args()
    
    if args.install:
        install_pymysql()
    elif args.check:
        check_pymysql()
    elif args.init:
        create_config(args.config)
    elif args.test:
        test_connection(args.config, args.env)
    elif args.list:
        list_environments(args.config)
    elif args.switch:
        switch_environment(args.switch, args.config)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
