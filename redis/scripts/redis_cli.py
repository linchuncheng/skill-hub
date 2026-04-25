#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis 操作工具
支持键值查询、字符串、哈希、列表、集合、有序集合等数据类型的增删改查
支持 Pipeline 批量操作、键扫描、TTL 管理

用法:
  python3 run_redis.py GET user:1001
  python3 run_redis.py HGETALL user:1001
  python3 run_redis.py LRANGE mylist 0 -1
  python3 run_redis.py -p "GET key1" "GET key2"
  python3 run_redis.py --scan "user:*"
  python3 run_redis.py --init  # 交互式配置 Redis 连接
"""

import json
import os
import sys
import argparse
import subprocess
import re

# 全局 Redis 驱动
redis = None

# ============================================
# 依赖管理
# ============================================

def ensure_redis_driver():
    """确保 redis-py 已安装,未安装则自动安装"""
    global redis
    try:
        import redis as rd
        redis = rd
        return redis
    except ImportError:
        print("⚠ 检测到 redis-py 未安装,正在自动安装...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "redis",
                "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✓ redis-py 安装成功\n")
            import redis as rd
            redis = rd
            return redis
        except Exception as e:
            print(f"✗ 自动安装失败: {e}")
            print("\n请手动安装: pip install redis")
            sys.exit(1)

# ============================================
# 配置管理
# ============================================

def load_config(config_file=None, env_name=None):
    """加载 Redis 配置,配置不存在时引导创建"""
    if config_file:
        config_path = os.path.expanduser(config_file)
    else:
        config_path = os.getenv('AGENT_REDIS_CONFIG',
                               os.path.expanduser('~/.config/redis/config.json'))

    if not os.path.exists(config_path):
        print(f"⚠ 配置文件不存在: {config_path}")
        print("\n📝 首次使用需要配置 Redis 连接信息\n")
        create_config(config_path)
        return load_config(config_path, env_name)

    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    env = env_name or config_data.get('current', 'local')

    if env not in config_data:
        print(f"错误: 环境 '{env}' 不存在")
        print(f"可用环境: {', '.join([k for k in config_data.keys() if k != 'current'])}")
        sys.exit(1)

    config = config_data[env].copy()
    return config, env

def create_config(config_path):
    """引导创建配置文件"""
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)

    print("="*50)
    print("Redis 配置向导")
    print("="*50)
    print("\n请输入 Redis 连接信息(直接回车使用默认值):\n")

    env_name = input("环境名称 [local]: ").strip() or "local"
    host = input("主机地址 [localhost]: ").strip() or "localhost"
    port = input("端口号 [6379]: ").strip() or "6379"
    db = input("数据库编号 [0]: ").strip() or "0"
    password = input("密码(无密码直接回车): ").strip()

    config_data = {
        "current": env_name,
        env_name: {
            "host": host,
            "port": int(port),
            "db": int(db),
            "password": password if password else ""
        }
    }

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ 配置文件创建成功: {config_path}")
        print("\n配置内容:")
        print(json.dumps(config_data, indent=2, ensure_ascii=False))
        print("\n正在测试 Redis 连接...")

        # 测试连接
        ensure_redis_driver()
        config = config_data[env_name].copy()
        try:
            client = create_client(config)
            client.ping()
            info = client.info('server')
            print(f"✓ Redis 连接成功 ({info.get('redis_version', 'unknown')})")
            client.close()
        except Exception as e:
            print(f"⚠ 连接测试失败: {e}")
            print("请检查配置是否正确,或重新运行 --init 修改配置")

    except Exception as e:
        print(f"✗ 创建配置文件失败: {e}")
        sys.exit(1)

def create_client(config):
    """创建 Redis 客户端"""
    ensure_redis_driver()
    cfg = {
        'host': config.get('host', 'localhost'),
        'port': config.get('port', 6379),
        'db': config.get('db', 0),
        'decode_responses': True,
        'socket_connect_timeout': 5,
        'socket_timeout': 10,
    }
    password = config.get('password')
    if password:
        cfg['password'] = password
    return redis.Redis(**cfg)

# ============================================
# 命令执行
# ============================================

def execute_command(client, cmd_parts):
    """执行单条 Redis 命令"""
    if not cmd_parts:
        return {'status': 'error', 'error': '命令为空'}

    cmd = cmd_parts[0].upper()
    args = cmd_parts[1:]

    try:
        method = getattr(client, cmd.lower(), None)
        if method is None:
            # 尝试执行原始命令
            result = client.execute_command(cmd, *args)
            return format_result(result, cmd)

        result = method(*args)
        return format_result(result, cmd)

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__,
            'command': ' '.join(cmd_parts)
        }

def format_result(result, cmd=''):
    """格式化 Redis 返回结果"""
    if result is None:
        return {'status': 'success', 'type': 'nil', 'data': None}

    if isinstance(result, bool):
        return {'status': 'success', 'type': 'boolean', 'data': result}

    if isinstance(result, int):
        return {'status': 'success', 'type': 'integer', 'data': result}

    if isinstance(result, (str, bytes)):
        if isinstance(result, bytes):
            result = result.decode('utf-8', errors='replace')
        return {'status': 'success', 'type': 'string', 'data': result}

    if isinstance(result, list):
        # 处理列表结果
        formatted = []
        for item in result:
            if isinstance(item, bytes):
                formatted.append(item.decode('utf-8', errors='replace'))
            else:
                formatted.append(item)
        return {'status': 'success', 'type': 'list', 'length': len(formatted), 'data': formatted}

    if isinstance(result, dict):
        formatted = {}
        for k, v in result.items():
            key = k.decode('utf-8', errors='replace') if isinstance(k, bytes) else k
            val = v.decode('utf-8', errors='replace') if isinstance(v, bytes) else v
            formatted[key] = val
        return {'status': 'success', 'type': 'hash', 'length': len(formatted), 'data': formatted}

    if isinstance(result, set):
        formatted = []
        for item in result:
            if isinstance(item, bytes):
                formatted.append(item.decode('utf-8', errors='replace'))
            else:
                formatted.append(item)
        return {'status': 'success', 'type': 'set', 'length': len(formatted), 'data': formatted}

    return {'status': 'success', 'type': 'other', 'data': result}

def print_result(result, cmd_parts):
    """打印执行结果"""
    if result.get('status') == 'error':
        print(f"\n✗ 执行失败")
        print(f"命令: {result.get('command', ' '.join(cmd_parts))}")
        print(f"错误类型: {result.get('error_type')}")
        print(f"错误信息: {result.get('error')}")
        return

    cmd = cmd_parts[0].upper() if cmd_parts else ''
    data = result.get('data')
    result_type = result.get('type')

    if result_type == 'nil':
        print("(nil)")
    elif result_type == 'boolean':
        print("1" if data else "0")
    elif result_type == 'integer':
        print(f"(integer) {data}")
    elif result_type == 'string':
        print(f'"{data}"')
    elif result_type == 'list':
        if not data:
            print("(empty list or set)")
        else:
            for i, item in enumerate(data):
                print(f"{i+1}) \"{item}\"")
    elif result_type == 'hash':
        if not data:
            print("(empty hash)")
        else:
            for k, v in data.items():
                print(f"{k}\n\"{v}\"")
    elif result_type == 'set':
        if not data:
            print("(empty list or set)")
        else:
            for item in data:
                print(f"1) \"{item}\"")
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))

def scan_keys(client, pattern, count=100):
    """安全扫描键(使用 SCAN 替代 KEYS)"""
    results = []
    cursor = 0
    total_scanned = 0

    while True:
        cursor, keys = client.scan(cursor=cursor, match=pattern, count=count)
        total_scanned += count
        results.extend(keys)

        if cursor == 0:
            break

        # 限制扫描总量,防止无限扫描
        if total_scanned >= 10000:
            print(f"⚠ 已扫描 {total_scanned} 个键,结果可能不完整")
            break

    return results

def execute_pipeline(client, commands):
    """使用 Pipeline 批量执行命令"""
    pipe = client.pipeline()
    parsed_commands = []

    for cmd_str in commands:
        parts = cmd_str.split()
        if not parts:
            continue
        cmd = parts[0].upper()
        args = parts[1:]
        parsed_commands.append((cmd, args))

        method = getattr(pipe, cmd.lower(), None)
        if method is None:
            # 使用 execute_command
            pipe.execute_command(cmd, *args)
        else:
            method(*args)

    try:
        results = pipe.execute()
        formatted = []
        for i, (result, (cmd, args)) in enumerate(zip(results, parsed_commands), 1):
            formatted.append(format_result(result, cmd))
        return formatted
    except Exception as e:
        return [{
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__,
            'command': ' | '.join(commands)
        }]

# ============================================
# Key 设计分析
# ============================================

def analyze_keys(client, pattern="*", json_output=False):
    """分析 Redis key 设计合理性"""
    keys = scan_keys(client, pattern, count=100)

    if not keys:
        if json_output:
            print(json.dumps({"status": "success", "message": "未找到 key"}, ensure_ascii=False))
        else:
            print("未找到 key")
        return

    # 收集每个 key 的信息
    key_infos = []
    for k in keys:
        try:
            t = client.type(k)
            ttl = client.ttl(k)
            mem = client.memory_usage(k)
            strlen = client.strlen(k) if t == 'string' else None
            key_infos.append({
                'key': k,
                'type': t,
                'ttl': ttl,
                'memory': mem,
                'strlen': strlen,
            })
        except Exception:
            key_infos.append({
                'key': k,
                'type': 'unknown',
                'ttl': -1,
                'memory': 0,
                'strlen': None,
            })

    # 按前缀分组
    prefixes = {}
    for info in key_infos:
        k = info['key']
        idx = k.find(':')
        prefix = k[:idx] if idx != -1 else '(no_prefix)'
        prefixes.setdefault(prefix, []).append(info)

    # 统计
    ttls = [i['ttl'] for i in key_infos]
    mems = [i['memory'] for i in key_infos]
    has_ttl = sum(1 for t in ttls if t > 0)
    no_ttl = sum(1 for t in ttls if t == -1)
    expired = sum(1 for t in ttls if t == -2)

    # 采样异常 key（值大小差异大的）
    str_keys = [i for i in key_infos if i['type'] == 'string' and i['strlen'] is not None]
    if str_keys:
        strlen_values = [i['strlen'] for i in str_keys]
        avg_strlen = sum(strlen_values) / len(strlen_values)
        anomalies = [i for i in str_keys if abs(i['strlen'] - avg_strlen) > avg_strlen * 0.5 and i['strlen'] > 0]
    else:
        anomalies = []

    if json_output:
        report = {
            "status": "success",
            "summary": {
                "total_keys": len(keys),
                "prefix_count": len(prefixes),
                "ttl_stats": {
                    "has_ttl": has_ttl,
                    "no_ttl": no_ttl,
                    "expired": expired,
                    "avg_ttl_hours": round(sum(t for t in ttls if t > 0) / has_ttl / 3600, 2) if has_ttl else 0,
                    "min_ttl_hours": round(min(t for t in ttls if t > 0) / 3600, 2) if has_ttl else 0,
                    "max_ttl_hours": round(max(t for t in ttls if t > 0) / 3600, 2) if has_ttl else 0,
                },
                "memory_stats": {
                    "total_bytes": sum(mems),
                    "avg_bytes": round(sum(mems) / len(mems), 2) if mems else 0,
                    "min_bytes": min(mems) if mems else 0,
                    "max_bytes": max(mems) if mems else 0,
                },
                "prefixes": {
                    p: len(infos) for p, infos in prefixes.items()
                },
                "anomalies": [
                    {"key": i['key'], "strlen": i['strlen'], "avg_strlen": round(avg_strlen, 1)}
                    for i in anomalies[:10]
                ] if str_keys else [],
            },
            "keys": key_infos[:50],  # 最多返回 50 个详情
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    # 文本输出
    print(f"\n{'='*60}")
    print(f"Redis Key 设计分析报告")
    print(f"{'='*60}")
    print(f"\n扫描模式: {pattern}")
    print(f"Key 总数: {len(keys)}")

    print(f"\n{'─'*40}")
    print("前缀分布")
    print(f"{'─'*40}")
    for p, infos in sorted(prefixes.items(), key=lambda x: -len(x[1])):
        types = {}
        for i in infos:
            types[i['type']] = types.get(i['type'], 0) + 1
        type_str = ", ".join(f"{t}:{c}" for t, c in types.items())
        print(f"  {p}: {len(infos)}  ({type_str})")

    print(f"\n{'─'*40}")
    print("TTL 统计")
    print(f"{'─'*40}")
    print(f"  有过期时间: {has_ttl}")
    print(f"  无过期时间: {no_ttl}")
    print(f"  已过期:     {expired}")
    if has_ttl:
        ttl_vals = [t for t in ttls if t > 0]
        avg_ttl = sum(ttl_vals) / len(ttl_vals)
        print(f"  平均 TTL:   {avg_ttl/3600:.1f} 小时 ({avg_ttl/86400:.1f} 天)")
        print(f"  最短 TTL:   {min(ttl_vals)/3600:.1f} 小时")
        print(f"  最长 TTL:   {max(ttl_vals)/3600:.1f} 小时")

    print(f"\n{'─'*40}")
    print("内存统计")
    print(f"{'─'*40}")
    total_mem = sum(mems)
    print(f"  总内存:   {total_mem} bytes ({total_mem/1024:.1f} KB)")
    print(f"  平均内存: {sum(mems)/len(mems):.0f} bytes")
    print(f"  最小内存: {min(mems)} bytes")
    print(f"  最大内存: {max(mems)} bytes")

    if anomalies:
        print(f"\n{'─'*40}")
        print("异常 key (值大小与平均值偏差 >50%)")
        print(f"{'─'*40}")
        print(f"  平均 strlen: {avg_strlen:.1f} bytes")
        for i in anomalies[:10]:
            print(f"  ⚠ {i['key']}: strlen={i['strlen']} bytes")

    print(f"\n{'='*60}")

# ============================================
# 主程序
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description='Redis 操作工具 (支持字符串/哈希/列表/集合/有序集合)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s GET user:1001
  %(prog)s HGETALL user:1001
  %(prog)s LRANGE mylist 0 -1
  %(prog)s SMEMBERS myset
  %(prog)s ZRANGE myzset 0 -1 WITHSCORES
  %(prog)s -p "GET key1" "HGETALL hash1" "LRANGE list1 0 -1"
  %(prog)s --scan "user:*"
  %(prog)s --scan "*" --count 50
  %(prog)s -j GET user:1001
  %(prog)s --init  # 交互式配置 Redis 连接
  %(prog)s --analyze  # 分析所有 key 设计
  %(prog)s --analyze --scan "user:*"  # 分析指定模式 key
        """
    )

    parser.add_argument('command', nargs='*', help='Redis 命令及参数(如: GET key, HGETALL hash)')
    parser.add_argument('--env', '-e', help='Redis 环境名称')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--json', '-j', action='store_true', help='以 JSON 格式输出结果')
    parser.add_argument('--pipeline', '-p', action='store_true', help='启用 Pipeline 模式(批量执行)')
    parser.add_argument('--scan', '-s', help='扫描键模式(使用 SCAN,如: user:*)')
    parser.add_argument('--count', type=int, default=100, help='SCAN 每次扫描数量(默认: 100)')
    parser.add_argument('--init', action='store_true', help='交互式配置 Redis 连接')
    parser.add_argument('--analyze', '-a', action='store_true', help='分析 key 设计合理性')

    args = parser.parse_args()

    # 仅初始化配置
    if args.init:
        config_path = os.path.expanduser(args.config if args.config else '~/.config/redis/config.json')
        create_config(config_path)
        return

    # 分析模式
    if args.analyze:
        config, env = load_config(args.config, args.env)
        if not args.json:
            print(f"环境: {env}")
            print(f"Redis: {config.get('host', 'localhost')}:{config.get('port', 6379)}/{config.get('db', 0)}")
        client = create_client(config)
        try:
            analyze_keys(client, pattern=args.scan if args.scan else "*", json_output=args.json)
        except Exception as e:
            print(f"\n✗ 分析失败: {e}")
        finally:
            client.close()
        return

    # 必须有命令或扫描参数
    if not args.command and not args.scan:
        parser.print_help()
        sys.exit(1)

    # 加载配置
    config, env = load_config(args.config, args.env)

    if not args.json:
        print(f"环境: {env}")
        print(f"Redis: {config.get('host', 'localhost')}:{config.get('port', 6379)}/{config.get('db', 0)}")

    # 创建客户端
    client = create_client(config)

    try:
        # SCAN 模式
        if args.scan:
            if not args.json:
                print(f"\n扫描键模式: {args.scan}")
            keys = scan_keys(client, args.scan, args.count)
            result = {
                'status': 'success',
                'type': 'scan',
                'pattern': args.scan,
                'count': len(keys),
                'data': keys
            }
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                if not keys:
                    print("(empty list or set)")
                else:
                    for i, key in enumerate(keys):
                        print(f"{i+1}) \"{key}\"")
            return

        # Pipeline 模式
        if args.pipeline:
            if not args.json:
                print(f"\nPipeline 模式: 执行 {len(args.command)} 条命令\n")
            results = execute_pipeline(client, args.command)
            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
            else:
                for i, (result, cmd_str) in enumerate(zip(results, args.command), 1):
                    print(f"[{i}/{len(args.command)}] {cmd_str}")
                    print_result(result, cmd_str.split())
                    print()
            return

        # 单条命令模式
        result = execute_command(client, args.command)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            print()
            print_result(result, args.command)

    except Exception as e:
        error_result = {
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__
        }
        if args.json:
            print(json.dumps(error_result, indent=2, ensure_ascii=False))
        else:
            print(f"\n✗ 执行失败: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
