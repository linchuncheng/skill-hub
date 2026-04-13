#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent-mysql 使用示例
演示如何使用 Python + pymysql 进行数据库操作
"""

import pymysql
import json
import os

# ============================================
# 1. 基础连接配置
# ============================================

def get_connection_config(env_name=None):
    """从配置文件加载数据库配置"""
    config_path = os.path.expanduser("~/.config/agent-mysql/config.json")
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    # 使用指定环境或当前环境
    env = env_name or config_data.get('current', 'local')
    config = config_data[env]
    
    # 添加必要参数
    config['charset'] = 'utf8mb4'
    config['cursorclass'] = pymysql.cursors.DictCursor
    
    return config, env


# ============================================
# 2. 查询数据
# ============================================

def example_query():
    """示例：查询数据"""
    config, env = get_connection_config()
    
    print(f"\n=== 查询示例 (环境: {env}) ===")
    
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            # 基础查询
            sql = "SELECT * FROM sys_permission LIMIT 5;"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            print(f"查询到 {len(results)} 条记录:\n")
            for row in results:
                print(f"ID: {row['id']}, 权限代码: {row['permission_code']}, 名称: {row['permission_name']}")
            
            # 统计查询
            cursor.execute("SELECT COUNT(*) as total FROM sys_permission;")
            total = cursor.fetchone()
            print(f"\n总计: {total['total']} 条权限记录")
            
    finally:
        connection.close()


# ============================================
# 3. 参数化查询（防止 SQL 注入）
# ============================================

def example_parameterized_query():
    """示例：参数化查询"""
    config, env = get_connection_config()
    
    print(f"\n=== 参数化查询示例 ===")
    
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            # 安全的参数化查询
            permission_id = 1
            sql = "SELECT * FROM sys_permission WHERE id = %s;"
            cursor.execute(sql, (permission_id,))
            result = cursor.fetchone()
            
            if result:
                print(f"找到权限: {result['permission_name']}")
                print(f"权限代码: {result['permission_code']}")
                print(f"资源类型: {result['resource_type']}")
            
    finally:
        connection.close()


# ============================================
# 4. 插入数据
# ============================================

def example_insert():
    """示例：插入数据"""
    config, env = get_connection_config()
    
    print(f"\n=== 插入数据示例 ===")
    
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            # 插入数据
            sql = """
                INSERT INTO sys_permission 
                (parent_id, permission_code, permission_name, resource_type, sort, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                0,
                'example:test',
                '测试权限',
                'MENU',
                999,
                1
            ))
            
            # 提交事务
            connection.commit()
            last_id = cursor.lastrowid
            print(f"✓ 插入成功，ID: {last_id}")
            
            # 清理：删除刚插入的数据
            cursor.execute("DELETE FROM sys_permission WHERE id = %s;", (last_id,))
            connection.commit()
            print(f"✓ 已清理测试数据")
            
    except Exception as e:
        connection.rollback()
        print(f"✗ 插入失败: {e}")
    finally:
        connection.close()


# ============================================
# 5. 更新数据
# ============================================

def example_update():
    """示例：更新数据"""
    config, env = get_connection_config()
    
    print(f"\n=== 更新数据示例 ===")
    
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            # 更新数据
            sql = "UPDATE sys_permission SET sort = %s WHERE id = %s;"
            cursor.execute(sql, (100, 1))
            connection.commit()
            
            rows_affected = cursor.rowcount
            print(f"✓ 更新了 {rows_affected} 条记录")
            
    except Exception as e:
        connection.rollback()
        print(f"✗ 更新失败: {e}")
    finally:
        connection.close()


# ============================================
# 6. 删除数据
# ============================================

def example_delete():
    """示例：删除数据"""
    config, env = get_connection_config()
    
    print(f"\n=== 删除数据示例 ===")
    
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            # 删除数据（软删除）
            sql = "UPDATE sys_permission SET deleted = 1 WHERE id = %s;"
            cursor.execute(sql, (1,))
            connection.commit()
            
            rows_affected = cursor.rowcount
            print(f"✓ 删除了 {rows_affected} 条记录")
            
            # 恢复数据
            cursor.execute("UPDATE sys_permission SET deleted = 0 WHERE id = %s;", (1,))
            connection.commit()
            print(f"✓ 已恢复数据")
            
    except Exception as e:
        connection.rollback()
        print(f"✗ 删除失败: {e}")
    finally:
        connection.close()


# ============================================
# 7. 事务操作
# ============================================

def example_transaction():
    """示例：事务操作"""
    config, env = get_connection_config()
    
    print(f"\n=== 事务操作示例 ===")
    
    connection = pymysql.connect(**config)
    try:
        # 开始事务
        connection.begin()
        
        with connection.cursor() as cursor:
            # 执行多个操作
            cursor.execute(
                "INSERT INTO sys_permission (parent_id, permission_code, permission_name, resource_type, sort, status) VALUES (%s, %s, %s, %s, %s, %s);",
                (0, 'tx:test1', '事务测试1', 'MENU', 999, 1)
            )
            id1 = cursor.lastrowid
            
            cursor.execute(
                "INSERT INTO sys_permission (parent_id, permission_code, permission_name, resource_type, sort, status) VALUES (%s, %s, %s, %s, %s, %s);",
                (0, 'tx:test2', '事务测试2', 'MENU', 999, 1)
            )
            id2 = cursor.lastrowid
            
            # 提交事务
            connection.commit()
            print(f"✓ 事务提交成功，插入 ID: {id1}, {id2}")
            
            # 清理
            cursor.execute("DELETE FROM sys_permission WHERE id IN (%s, %s);", (id1, id2))
            connection.commit()
            print(f"✓ 已清理测试数据")
            
    except Exception as e:
        connection.rollback()
        print(f"✗ 事务失败，已回滚: {e}")
    finally:
        connection.close()


# ============================================
# 8. 查看表结构
# ============================================

def example_describe_table():
    """示例：查看表结构"""
    config, env = get_connection_config()
    
    print(f"\n=== 查看表结构示例 ===")
    
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            # 查询表字段信息
            sql = """
                SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, COLUMN_COMMENT, IS_NULLABLE, COLUMN_KEY
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s 
                ORDER BY ORDINAL_POSITION
            """
            cursor.execute(sql, (config['database'], 'sys_permission'))
            columns = cursor.fetchall()
            
            print(f"\n表 sys_permission 的字段信息:\n")
            print(f"{'字段名':<25} {'类型':<20} {'注释':<20}")
            print("-" * 65)
            
            for col in columns:
                comment = col['COLUMN_COMMENT'] or '-'
                print(f"{col['COLUMN_NAME']:<25} {col['COLUMN_TYPE']:<20} {comment:<20}")
            
    finally:
        connection.close()


# ============================================
# 9. 导出为 JSON
# ============================================

def example_export_json():
    """示例：导出为 JSON"""
    config, env = get_connection_config()
    
    print(f"\n=== 导出 JSON 示例 ===")
    
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM sys_permission LIMIT 3;"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            # 转换为 JSON
            json_str = json.dumps(results, indent=2, ensure_ascii=False, default=str)
            print(json_str)
            
    finally:
        connection.close()


# ============================================
# 10. EXPLAIN 分析
# ============================================

def example_explain():
    """示例：EXPLAIN 查询分析"""
    config, env = get_connection_config()
    
    print(f"\n=== EXPLAIN 分析示例 ===")
    
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            sql = "EXPLAIN SELECT * FROM sys_permission WHERE permission_code = %s;"
            cursor.execute(sql, ('platform:user:list',))
            results = cursor.fetchall()
            
            print(f"\n查询执行计划:\n")
            for row in results:
                for key, value in row.items():
                    print(f"  {key}: {value}")
                print()
            
    finally:
        connection.close()


# ============================================
# 11. 批量执行 SQL 文件
# ============================================

import re

def example_execute_sql_file():
    """示例：批量执行 SQL 文件"""
    config, env = get_connection_config()
    
    print(f"\n=== 批量执行 SQL 文件示例 ===")
    
    connection = pymysql.connect(**config)
    try:
        with connection.cursor() as cursor:
            # 示例：执行 SQL 文件
            sql_file = "test.sql"
            
            # 创建测试 SQL 文件
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write("""
-- 测试 SQL 文件
-- 这是注释

INSERT INTO sys_permission (parent_id, permission_code, permission_name, resource_type, sort, status)
VALUES (0, 'sql:file:test', 'SQL文件测试', 'MENU', 999, 1);

/* 多行注释 */
SELECT LAST_INSERT_ID() as id;
""")
            
            # 读取并处理 SQL 文件
            with open(sql_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 移除注释
            content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            
            # 执行 SQL
            for statement in content.split(';'):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
                    result = cursor.fetchone()
                    if result:
                        print(f"执行结果: {result}")
            
            connection.commit()
            print("✓ SQL 文件执行成功")
            
            # 清理测试数据
            cursor.execute("DELETE FROM sys_permission WHERE permission_code = %s;", ('sql:file:test',))
            connection.commit()
            
            # 删除测试文件
            import os
            os.remove(sql_file)
            
    except Exception as e:
        connection.rollback()
        print(f"✗ 执行失败: {e}")
    finally:
        connection.close()


# ============================================
# 主函数 - 运行所有示例
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("  agent-mysql 使用示例集合")
    print("=" * 60)
    
    # 运行示例（取消注释需要运行的示例）
    example_query()
    # example_parameterized_query()
    # example_insert()
    # example_update()
    # example_delete()
    # example_transaction()
    # example_describe_table()
    # example_export_json()
    # example_explain()
    
    print("\n" + "=" * 60)
    print("  示例运行完成")
    print("=" * 60)
