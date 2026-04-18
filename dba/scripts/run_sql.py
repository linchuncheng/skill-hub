#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL 执行器 - 支持 MySQL 和 PostgreSQL
自动处理依赖安装和配置初始化，无需手动操作

用法:
  python3 run_sql.py "SELECT * FROM users LIMIT 10;"
  python3 run_sql.py --file query.sql
  python3 run_sql.py --env dev "SELECT COUNT(*) FROM orders;"
  python3 run_sql.py --init  # 交互式配置数据库连接
"""

import json
import os
import sys
import argparse
import re
import subprocess

# 全局数据库驱动变量
pymysql = None
psycopg2 = None
psycopg2_extras = None

# ============================================
# 依赖管理
# ============================================

def ensure_mysql_driver():
    """确保 pymysql 已安装,未安装则自动安装"""
    global pymysql
    try:
        import pymysql as pm
        pymysql = pm
        return pymysql
    except ImportError:
        print("⚠ 检测到 pymysql 未安装,正在自动安装...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "pymysql",
                "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✓ pymysql 安装成功\n")
            import pymysql as pm
            pymysql = pm
            return pymysql
        except Exception as e:
            print(f"✗ 自动安装失败: {e}")
            print("\n请手动安装: pip install pymysql")
            sys.exit(1)

def ensure_pgsql_driver():
    """确保 psycopg2-binary 已安装,未安装则自动安装"""
    global psycopg2, psycopg2_extras
    try:
        import psycopg2 as ps
        import psycopg2.extras as pse
        psycopg2 = ps
        psycopg2_extras = pse
        return psycopg2
    except ImportError:
        print("⚠ 检测到 psycopg2-binary 未安装,正在自动安装...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "psycopg2-binary",
                "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✓ psycopg2-binary 安装成功\n")
            import psycopg2 as ps
            import psycopg2.extras as pse
            psycopg2 = ps
            psycopg2_extras = pse
            return psycopg2
        except Exception as e:
            print(f"✗ 自动安装失败: {e}")
            print("\n请手动安装: pip install psycopg2-binary")
            sys.exit(1)

def ensure_driver(db_type):
    """根据数据库类型确保对应的驱动已安装"""
    if db_type == 'mysql':
        return ensure_mysql_driver()
    elif db_type == 'postgresql':
        return ensure_pgsql_driver()
    else:
        print(f"✗ 不支持的数据库类型: {db_type}")
        print("支持的数据库类型: mysql, postgresql")
        sys.exit(1)

def load_config(config_file=None, env_name=None):
    """加载数据库配置,配置不存在时引导创建"""
    if config_file:
        config_path = os.path.expanduser(config_file)
    else:
        config_path = os.getenv('AGENT_MYSQL_CONFIG', 
                               os.path.expanduser('~/.config/dba/config.json'))
    
    if not os.path.exists(config_path):
        print(f"⚠ 配置文件不存在: {config_path}")
        print("\n📝 首次使用需要配置数据库连接信息\n")
        create_config(config_path)
        # 重新加载配置
        return load_config(config_path, env_name)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    env = env_name or config_data.get('current', 'local')
    
    if env not in config_data:
        print(f"错误: 环境 '{env}' 不存在")
        print(f"可用环境: {', '.join([k for k in config_data.keys() if k != 'current'])}")
        sys.exit(1)
    
    config = config_data[env].copy()
    db_type = config.pop('type', 'mysql')  # 移除 type 字段，避免传给数据库驱动
    
    # 根据数据库类型设置不同的连接参数
    if db_type == 'mysql':
        config['charset'] = 'utf8mb4'
        pymysql = ensure_driver(db_type)
        config['cursorclass'] = pymysql.cursors.DictCursor
    elif db_type == 'postgresql':
        ensure_driver(db_type)
        # PostgreSQL 不需要 cursorclass,会在连接时指定
    
    return config, env, db_type

def execute_transaction(sql_statements, config, max_rows=1000, db_type='mysql'):
    """执行事务(多条 SQL)"""
    connection = None
    try:
        if db_type == 'mysql':
            connection = pymysql.connect(**config)
        elif db_type == 'postgresql':
            # PostgreSQL 连接
            pg_config = {
                'host': config.get('host', 'localhost'),
                'port': config.get('port', 5432),
                'user': config.get('user', 'postgres'),
                'password': config.get('password', ''),
                'dbname': config.get('database', config.get('dbname', ''))
            }
            connection = psycopg2.connect(**pg_config)
        
        # 开启事务
        # MySQL 默认自动开启事务,PostgreSQL 需要显式开始
        if db_type == 'postgresql':
            connection.autocommit = False
        
        results = []
        for i, sql in enumerate(sql_statements, 1):
            sql = sql.strip()
            if not sql:
                continue
            
            print(f"\n[{i}/{len(sql_statements)}] 执行: {sql[:80]}{'...' if len(sql) > 80 else ''}")
            
            if db_type == 'mysql':
                with connection.cursor() as cursor:
                    is_select = sql.upper().startswith(('SELECT', 'SHOW', 'DESC', 'DESCRIBE', 'EXPLAIN'))
                    
                    try:
                        cursor.execute(sql)
                        
                        if is_select:
                            query_results = cursor.fetchmany(max_rows)
                            results.append({
                                'status': 'success',
                                'type': 'query',
                                'sql': sql,
                                'rows': len(query_results),
                                'data': query_results
                            })
                            print(f"  ✓ 查询成功 ({len(query_results)} 条)")
                        else:
                            rows_affected = cursor.rowcount
                            last_id = cursor.lastrowid
                            results.append({
                                'status': 'success',
                                'type': 'modify',
                                'sql': sql,
                                'rows_affected': rows_affected,
                                'last_insert_id': last_id if last_id else None
                            })
                            print(f"  ✓ 执行成功 (影响 {rows_affected} 行)")
                            
                    except Exception as e:
                        print(f"  ✗ 执行失败: {e}")
                        raise
            elif db_type == 'postgresql':
                # PostgreSQL 使用 DictCursor
                with connection.cursor(cursor_factory=psycopg2_extras.RealDictCursor) as cursor:
                    is_select = sql.upper().startswith(('SELECT', 'SHOW', 'DESC', 'DESCRIBE', 'EXPLAIN', '\\d'))
                    
                    try:
                        cursor.execute(sql)
                        
                        if is_select:
                            query_results = cursor.fetchmany(max_rows)
                            # 将 DictRow 转换为普通字典
                            query_results = [dict(row) for row in query_results]
                            results.append({
                                'status': 'success',
                                'type': 'query',
                                'sql': sql,
                                'rows': len(query_results),
                                'data': query_results
                            })
                            print(f"  ✓ 查询成功 ({len(query_results)} 条)")
                        else:
                            rows_affected = cursor.rowcount
                            # PostgreSQL 获取最后插入 ID
                            last_id = None
                            if sql.upper().startswith('INSERT'):
                                cursor.execute("SELECT LASTVAL()")
                                last_id_result = cursor.fetchone()
                                last_id = last_id_result[0] if last_id_result else None
                            
                            results.append({
                                'status': 'success',
                                'type': 'modify',
                                'sql': sql,
                                'rows_affected': rows_affected,
                                'last_insert_id': last_id
                            })
                            print(f"  ✓ 执行成功 (影响 {rows_affected} 行)")
                            
                    except Exception as e:
                        print(f"  ✗ 执行失败: {e}")
                        raise
        
        # 所有语句执行成功,提交事务
        connection.commit()
        print(f"\n✓ 事务提交成功")
        
        return {
            'status': 'success',
            'type': 'transaction',
            'committed': True,
            'statements': len(results),
            'results': results
        }
        
    except Exception as e:
        if connection:
            connection.rollback()
            print(f"\n✗ 事务已回滚: {e}")
        
        return {
            'status': 'error',
            'type': 'transaction',
            'committed': False,
            'error': str(e),
            'error_type': type(e).__name__
        }
    finally:
        if connection:
            connection.close()

def execute_sql(sql, config, max_rows=1000, db_type='mysql'):
    """执行 SQL 并返回结果"""
    connection = None
    try:
        if db_type == 'mysql':
            connection = pymysql.connect(**config)
        elif db_type == 'postgresql':
            # PostgreSQL 连接
            pg_config = {
                'host': config.get('host', 'localhost'),
                'port': config.get('port', 5432),
                'user': config.get('user', 'postgres'),
                'password': config.get('password', ''),
                'dbname': config.get('database', config.get('dbname', ''))
            }
            connection = psycopg2.connect(**pg_config)
        
        if db_type == 'mysql':
            with connection.cursor() as cursor:
                # 判断是否为 SELECT 查询
                is_select = sql.strip().upper().startswith(('SELECT', 'SHOW', 'DESC', 'DESCRIBE', 'EXPLAIN'))
                
                # 执行 SQL
                cursor.execute(sql)
                
                if is_select:
                    # 查询类语句
                    results = cursor.fetchmany(max_rows)
                    
                    output = {
                        'status': 'success',
                        'type': 'query',
                        'rows': len(results),
                        'data': results
                    }
                    
                    # 打印结果
                    if results:
                        print(f"\n查询结果 ({len(results)} 条记录):\n")
                        
                        # 表格化输出
                        headers = list(results[0].keys())
                        
                        # 计算列宽
                        col_widths = {}
                        for header in headers:
                            col_widths[header] = len(str(header))
                            for row in results[:10]:  # 只检查前10行
                                col_widths[header] = max(col_widths[header], len(str(row.get(header, ''))))
                            col_widths[header] = min(col_widths[header], 50)  # 最夔50字符
                        
                        # 打印表头
                        header_line = ' | '.join([str(h).ljust(col_widths[h]) for h in headers])
                        print(header_line)
                        print('-' * len(header_line))
                        
                        # 打印数据(最多10行)
                        for i, row in enumerate(results[:10]):
                            values = [str(row.get(h, '')).ljust(col_widths[h]) for h in headers]
                            print(' | '.join(values))
                        
                        if len(results) > 10:
                            print(f"\n... 还有 {len(results) - 10} 条记录(仅显示前10条)")
                    else:
                        print("\n查询结果为空")
                    
                    return output
                else:
                    # 非查询类语句(INSERT/UPDATE/DELETE)
                    connection.commit()
                    rows_affected = cursor.rowcount
                    last_id = cursor.lastrowid
                    
                    output = {
                        'status': 'success',
                        'type': 'modify',
                        'rows_affected': rows_affected
                    }
                    
                    if last_id:
                        output['last_insert_id'] = last_id
                    
                    print(f"\n执行成功!")
                    print(f"影响行数: {rows_affected}")
                    if last_id:
                        print(f"自增ID: {last_id}")
                    
                    return output
        
        elif db_type == 'postgresql':
            with connection.cursor(cursor_factory=psycopg2_extras.RealDictCursor) as cursor:
                # 判断是否为 SELECT 查询
                is_select = sql.strip().upper().startswith(('SELECT', 'SHOW', 'DESC', 'DESCRIBE', 'EXPLAIN', '\\d'))
                
                # 执行 SQL
                cursor.execute(sql)
                
                if is_select:
                    # 查询类语句
                    results = cursor.fetchmany(max_rows)
                    # 将 DictRow 转换为普通字典
                    results = [dict(row) for row in results]
                    
                    output = {
                        'status': 'success',
                        'type': 'query',
                        'rows': len(results),
                        'data': results
                    }
                    
                    # 打印结果
                    if results:
                        print(f"\n查询结果 ({len(results)} 条记录):\n")
                        
                        # 表格化输出
                        headers = list(results[0].keys())
                        
                        # 计算列宽
                        col_widths = {}
                        for header in headers:
                            col_widths[header] = len(str(header))
                            for row in results[:10]:  # 只检查前10行
                                col_widths[header] = max(col_widths[header], len(str(row.get(header, ''))))
                            col_widths[header] = min(col_widths[header], 50)  # 最夔50字符
                        
                        # 打印表头
                        header_line = ' | '.join([str(h).ljust(col_widths[h]) for h in headers])
                        print(header_line)
                        print('-' * len(header_line))
                        
                        # 打印数据(最多10行)
                        for i, row in enumerate(results[:10]):
                            values = [str(row.get(h, '')).ljust(col_widths[h]) for h in headers]
                            print(' | '.join(values))
                        
                        if len(results) > 10:
                            print(f"\n... 还有 {len(results) - 10} 条记录(仅显示前10条)")
                    else:
                        print("\n查询结果为空")
                    
                    connection.commit()
                    return output
                else:
                    # 非查询类语句(INSERT/UPDATE/DELETE)
                    connection.commit()
                    rows_affected = cursor.rowcount
                    
                    # PostgreSQL 获取最后插入 ID
                    last_id = None
                    if sql.strip().upper().startswith('INSERT'):
                        cursor.execute("SELECT LASTVAL()")
                        last_id_result = cursor.fetchone()
                        last_id = last_id_result[0] if last_id_result else None
                    
                    output = {
                        'status': 'success',
                        'type': 'modify',
                        'rows_affected': rows_affected
                    }
                    
                    if last_id:
                        output['last_insert_id'] = last_id
                    
                    print(f"\n执行成功!")
                    print(f"影响行数: {rows_affected}")
                    if last_id:
                        print(f"自增ID: {last_id}")
                    
                    return output
                
    except Exception as e:
        if connection:
            connection.rollback()
        
        error_output = {
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__
        }
        
        print(f"\n执行失败!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {e}")
        
        return error_output
    finally:
        if connection:
            connection.close()

def execute_sql_file(file_path, config, max_rows=1000, db_type='mysql'):
    """执行 SQL 文件"""
    if not os.path.exists(file_path):
        print(f"错误: SQL 文件不存在: {file_path}")
        sys.exit(1)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除注释
    content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # 分割 SQL 语句
    statements = [s.strip() for s in content.split(';') if s.strip()]
    
    print(f"执行 SQL 文件: {file_path}")
    print(f"共 {len(statements)} 条语句\n")
    
    results = []
    for i, sql in enumerate(statements, 1):
        print(f"\n[{i}/{len(statements)}] 执行:")
        # 打印 SQL(截断显示)
        sql_preview = sql[:100] + '...' if len(sql) > 100 else sql
        print(f"  {sql_preview}\n")
        
        result = execute_sql(sql, config, max_rows, db_type)
        results.append(result)
    
    # 总结
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"\n{'='*60}")
    print(f"执行完成: {success_count}/{len(statements)} 成功")
    print(f"{'='*60}")
    
    return results

def create_config(config_path):
    """引导创建配置文件"""
    # 确保目录存在
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)
    
    print("="*50)
    print("数据库配置向导")
    print("="*50)
    print("\n请选择数据库类型:")
    print("1. MySQL")
    print("2. PostgreSQL")
    
    db_choice = input("\n请选择 [1]: ").strip() or "1"
    if db_choice == "2":
        db_type = 'postgresql'
        print("\n已选择: PostgreSQL")
    else:
        db_type = 'mysql'
        print("\n已选择: MySQL")
    
    print("\n请输入数据库连接信息(直接回车使用默认值):\n")
    
    env_name = input("环境名称 [local]: ").strip() or "local"
    
    if db_type == 'mysql':
        host = input("主机地址 [localhost]: ").strip() or "localhost"
        port = input("端口号 [3306]: ").strip() or "3306"
        user = input("用户名 [root]: ").strip() or "root"
    elif db_type == 'postgresql':
        host = input("主机地址 [localhost]: ").strip() or "localhost"
        port = input("端口号 [5432]: ").strip() or "5432"
        user = input("用户名 [postgres]: ").strip() or "postgres"
    
    password = input("密码: ").strip()
    database = input("数据库名: ").strip()
    
    if not database:
        print("✗ 数据库名不能为空")
        sys.exit(1)
    
    # 构建配置
    config_data = {
        "current": env_name,
        env_name: {
            "type": db_type,
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
        print("\n配置内容:")
        print(json.dumps(config_data, indent=2, ensure_ascii=False))
        print("\n正在测试数据库连接...")
        
        # 测试连接
        ensure_driver(db_type)
        config = config_data[env_name].copy()
        
        try:
            if db_type == 'mysql':
                config['charset'] = 'utf8mb4'
                connection = pymysql.connect(**config)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT VERSION() as version;")
                    version = cursor.fetchone()
                    print(f"✓ 数据库连接成功 (MySQL {version['version']})")
                connection.close()
            elif db_type == 'postgresql':
                pg_config = {
                    'host': config.get('host', 'localhost'),
                    'port': config.get('port', 5432),
                    'user': config.get('user', 'postgres'),
                    'password': config.get('password', ''),
                    'dbname': config.get('database', '')
                }
                connection = psycopg2.connect(**pg_config)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()
                    print(f"✓ 数据库连接成功 (PostgreSQL {version[0]})")
                connection.close()
        except Exception as e:
            print(f"⚠ 连接测试失败: {e}")
            print("请检查配置是否正确,或重新运行 --init 修改配置")
        
    except Exception as e:
        print(f"✗ 创建配置文件失败: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='SQL 执行器 (支持 MySQL 和 PostgreSQL)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "SELECT * FROM users LIMIT 10;"
  %(prog)s --env dev "SELECT COUNT(*) FROM orders;"
  %(prog)s --file query.sql
  %(prog)s --config /path/to/config.json "SELECT 1;"
  %(prog)s --transaction "INSERT INTO ..." "UPDATE ..." "DELETE ..."
  %(prog)s --init  # 交互式配置数据库连接
        """
    )
    
    parser.add_argument('sql', nargs='*', help='要执行的 SQL 语句(支持多条)')
    parser.add_argument('--file', '-f', help='SQL 文件路径')
    parser.add_argument('--env', '-e', help='数据库环境名称')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--max-rows', '-m', type=int, default=1000, 
                       help='最大返回行数(默认: 1000)')
    parser.add_argument('--json', '-j', action='store_true', 
                       help='以 JSON 格式输出结果')
    parser.add_argument('--transaction', '-t', action='store_true',
                       help='启用事务模式(多条 SQL 在同一事务中执行)')
    parser.add_argument('--init', action='store_true',
                       help='交互式配置数据库连接')
    
    args = parser.parse_args()
    
    # 仅初始化配置
    if args.init:
        config_path = os.path.expanduser(args.config if args.config else '~/.config/dba/config.json')
        create_config(config_path)
        return
    
    if not args.sql and not args.file:
        parser.print_help()
        sys.exit(1)
    
    # 加载配置(自动处理依赖和配置缺失)
    config, env, db_type = load_config(args.config, args.env)
    
    if not args.json:
        print(f"环境: {env}")
        print(f"数据库类型: {db_type}")
        print(f"数据库: {config.get('database', 'N/A')}")
    
    # 执行 SQL
    if args.file:
        results = execute_sql_file(args.file, config, args.max_rows, db_type)
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
    elif args.transaction:
        # 事务模式(支持单条或多条 SQL)
        if not args.sql:
            print("错误: 事务模式需要提供 SQL 语句")
            sys.exit(1)
        result = execute_transaction(args.sql, config, args.max_rows, db_type)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        # 单条 SQL 模式
        if len(args.sql) == 1:
            result = execute_sql(args.sql[0], config, args.max_rows, db_type)
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            # 多条 SQL 但不使用事务(逐条执行)
            print(f"\n执行 {len(args.sql)} 条 SQL(非事务模式)\n")
            results = []
            for i, sql in enumerate(args.sql, 1):
                print(f"\n{'='*60}")
                print(f"[{i}/{len(args.sql)}] {sql[:80]}{'...' if len(sql) > 80 else ''}")
                print(f"{'='*60}")
                result = execute_sql(sql, config, args.max_rows, db_type)
                results.append(result)
            
            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False, default=str))

if __name__ == "__main__":
    main()
