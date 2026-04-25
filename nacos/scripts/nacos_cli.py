#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nacos 操作工具
支持服务注册与发现、配置中心查询
支持多环境配置

用法:
  python3 nacos_cli.py --init                           # 交互式配置
  python3 nacos_cli.py --namespaces                     # 查看命名空间
  python3 nacos_cli.py --services                       # 查看服务列表
  python3 nacos_cli.py --service order-service          # 查看服务详情
  python3 nacos_cli.py --instances order-service        # 查看服务实例
  python3 nacos_cli.py --configs                        # 查看配置列表
  python3 nacos_cli.py --config app.yaml                # 查看配置详情
  python3 nacos_cli.py --history app.yaml               # 查看配置历史
  python3 nacos_cli.py --env prod --services            # 切换环境
"""

import json
import os
import sys
import argparse
import subprocess

# ============================================
# 依赖管理
# ============================================


def install_package(pkg):
    """安装 Python 包"""
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", pkg,
         "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def ensure_requests():
    """确保 requests 已安装"""
    try:
        import requests
        return requests
    except ImportError:
        print("⚠ 检测到 requests 未安装，正在自动安装...")
        install_package("requests")
        import requests
        print("✓ requests 安装成功\n")
        return requests


# ============================================
# 配置管理
# ============================================


def load_config(config_file=None, env_name=None):
    """加载 Nacos 配置，不存在时引导创建"""
    if config_file:
        config_path = os.path.expanduser(config_file)
    else:
        config_path = os.getenv(
            'AGENT_NACOS_CONFIG',
            os.path.expanduser('~/.config/nacos/config.json')
        )

    if not os.path.exists(config_path):
        print(f"⚠ 配置文件不存在: {config_path}")
        print("\n📝 首次使用需要配置 Nacos 连接信息\n")
        create_config(config_path)
        return load_config(config_path, env_name)

    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    env = env_name or config_data.get('current', 'local')

    if env not in config_data:
        print(f"错误: 环境 '{env}' 不存在")
        available = [k for k in config_data.keys() if k != 'current']
        print(f"可用环境: {', '.join(available)}")
        sys.exit(1)

    env_config = config_data[env]
    env_config['_env_name'] = env
    return env_config, env


def create_config(config_path):
    """交互式创建配置"""
    print("--- 配置 Nacos 连接 ---")
    addr = input("Server Address (默认: localhost:8848): ").strip()
    ns = input("Namespace ID (默认空，即public): ").strip()
    user = input("Username (默认空): ").strip()
    pwd = input("Password (默认空): ").strip()
    group = input("Default Group (默认: DEFAULT_GROUP): ").strip()

    cfg = {
        "server_addr": addr or "localhost:8848",
        "namespace": ns or "",
        "username": user or "",
        "password": pwd or "",
        "group": group or "DEFAULT_GROUP"
    }

    config_data = {"current": "local", "local": cfg}

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 配置已保存: {config_path}")


# ============================================
# Nacos Client
# ============================================


class NacosClient:
    def __init__(self, config):
        self.config = config
        self.requests = ensure_requests()
        self.base_url = self._build_base_url()

    def _build_base_url(self):
        addr = self.config.get("server_addr", "localhost:8848")
        if not addr.startswith(("http://", "https://")):
            addr = f"http://{addr}"
        return addr.rstrip("/")

    def _auth(self):
        return {
            "username": self.config.get("username", ""),
            "password": self.config.get("password", "")
        }

    def _namespace_param(self):
        ns = self.config.get("namespace", "")
        return {"namespaceId": ns} if ns else {}

    def _tenant_param(self):
        ns = self.config.get("namespace", "")
        return {"tenant": ns} if ns else {}

    def _get(self, path, params=None):
        url = f"{self.base_url}{path}"
        p = params or {}
        auth = self._auth()
        if auth["username"]:
            p.update(auth)
        try:
            r = self.requests.get(url, params=p, timeout=10)
            r.raise_for_status()
            return r.json() if r.text else {}
        except self.requests.exceptions.HTTPError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}

    def list_namespaces(self):
        result = self._get("/nacos/v1/console/namespaces")
        if "error" in result:
            return result
        return result.get("data", [])

    def list_services(self, page_no=1, page_size=10):
        params = {
            "pageNo": page_no,
            "pageSize": page_size,
            **self._namespace_param()
        }
        return self._get("/nacos/v1/ns/service/list", params)

    def get_service(self, service_name, group=None):
        g = group or self.config.get("group", "DEFAULT_GROUP")
        params = {
            "serviceName": service_name,
            "groupName": g,
            **self._namespace_param()
        }
        return self._get("/nacos/v1/ns/service", params)

    def list_instances(self, service_name, group=None):
        g = group or self.config.get("group", "DEFAULT_GROUP")
        params = {
            "serviceName": service_name,
            "groupName": g,
            **self._namespace_param()
        }
        return self._get("/nacos/v1/ns/instance/list", params)

    def list_configs(self, page_no=1, page_size=10):
        params = {
            "dataId": "",
            "group": "",
            "search": "blur",
            "pageNo": page_no,
            "pageSize": page_size,
            **self._tenant_param()
        }
        return self._get("/nacos/v1/cs/configs", params)

    def get_config(self, data_id, group=None):
        g = group or self.config.get("group", "DEFAULT_GROUP")
        params = {
            "dataId": data_id,
            "group": g,
            **self._tenant_param()
        }
        result = self._get("/nacos/v1/cs/configs", params)
        if "error" in result:
            return result
        # 如果返回的是字符串（配置内容），包装成字典
        if isinstance(result, str):
            return {"dataId": data_id, "group": g, "content": result}
        return result

    def get_config_history(self, data_id, group=None):
        g = group or self.config.get("group", "DEFAULT_GROUP")
        params = {
            "dataId": data_id,
            "group": g,
            **self._tenant_param()
        }
        return self._get("/nacos/v1/cs/history/configs", params)


# ============================================
# 格式化输出
# ============================================


def format_result(data, use_json=False):
    if use_json:
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        return

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                line = " | ".join(f"{k}={v}" for k, v in item.items())
                print(line)
            else:
                print(item)
    elif isinstance(data, dict):
        if "error" in data:
            print(f"✗ 错误: {data['error']}")
            return
        _print_dict(data)
    else:
        print(data)


def _print_dict(d, indent=0):
    for k, v in d.items():
        if k in ("_env_name",):
            continue
        prefix = "  " * indent
        if isinstance(v, list):
            print(f"{prefix}{k}:")
            for item in v:
                if isinstance(item, dict):
                    line = "  " + " | ".join(f"{ik}={iv}" for ik, iv in item.items())
                    print(f"{prefix}{line}")
                else:
                    print(f"{prefix}  - {item}")
        elif isinstance(v, dict):
            print(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        else:
            print(f"{prefix}{k}: {v}")


# ============================================
# 主函数
# ============================================


def main():
    parser = argparse.ArgumentParser(description="Nacos 操作工具")
    parser.add_argument("--init", action="store_true", help="交互式配置")
    parser.add_argument("--env", "-e", help="环境")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 输出")
    parser.add_argument("--namespaces", action="store_true", help="查看命名空间列表")
    parser.add_argument("--services", action="store_true", help="查看服务列表")
    parser.add_argument("--service", help="查看服务详情")
    parser.add_argument("--instances", help="查看服务实例列表")
    parser.add_argument("--configs", action="store_true", help="查看配置列表")
    parser.add_argument("--config-item", dest="config_item", help="查看配置详情")
    parser.add_argument("--history", help="查看配置历史")
    parser.add_argument("--group", "-g", help="指定分组（默认读取配置）")
    parser.add_argument("--page", type=int, default=1, help="页码")
    parser.add_argument("--page-size", type=int, default=10, help="每页数量")

    args = parser.parse_args()

    if args.init:
        config_path = os.getenv(
            'AGENT_NACOS_CONFIG',
            os.path.expanduser('~/.config/nacos/config.json')
        )
        create_config(config_path)
        return

    config, env = load_config(args.config, args.env)
    client = NacosClient(config)

    result = None
    try:
        if args.namespaces:
            result = client.list_namespaces()
        elif args.services:
            result = client.list_services(args.page, args.page_size)
        elif args.service:
            result = client.get_service(args.service, args.group)
        elif args.instances:
            result = client.list_instances(args.instances, args.group)
        elif args.configs:
            result = client.list_configs(args.page, args.page_size)
        elif args.config_item:
            result = client.get_config(args.config_item, args.group)
        elif args.history:
            result = client.get_config_history(args.history, args.group)
        else:
            parser.print_help()
            return
    except Exception as e:
        result = {"error": str(e), "error_type": type(e).__name__}

    format_result(result, args.json)


if __name__ == "__main__":
    main()
