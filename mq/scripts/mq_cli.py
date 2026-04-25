#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQ 操作工具
支持 Kafka、RabbitMQ、RocketMQ
支持多环境配置，按需安装驱动

用法:
  python3 mq_cli.py --init                          # 交互式配置
  python3 mq_cli.py --list                          # 列出 topics / queues
  python3 mq_cli.py --groups                        # 列出消费组
  python3 mq_cli.py --lag <topic>                   # 查看堆积
  python3 mq_cli.py --lag <topic> --group <gid>     # 查看指定消费组堆积
  python3 mq_cli.py --peek <topic>                  # 查看消息
  python3 mq_cli.py --peek <topic> --count 10       # 查看 10 条消息
  python3 mq_cli.py --info                          # 查看集群信息
  python3 mq_cli.py --env prod --list               # 切换环境
"""

import json
import os
import sys
import argparse
import subprocess
import socket
import struct
import random
import time
import re

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


def ensure_kafka_driver():
    """确保 kafka-python 已安装"""
    try:
        import kafka
        return kafka
    except ImportError:
        print("⚠ 检测到 kafka-python 未安装，正在自动安装...")
        install_package("kafka-python")
        import kafka
        print("✓ kafka-python 安装成功\n")
        return kafka


def ensure_rabbitmq_driver():
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


def ensure_rocketmq_driver():
    """尝试加载 RocketMQ Python 客户端"""
    try:
        import rocketmq
        return rocketmq
    except ImportError:
        return None


# ============================================
# 配置管理
# ============================================


def load_config(config_file=None, env_name=None):
    """加载 MQ 配置，不存在时引导创建"""
    if config_file:
        config_path = os.path.expanduser(config_file)
    else:
        config_path = os.getenv(
            'AGENT_MQ_CONFIG',
            os.path.expanduser('~/.config/mq/config.json')
        )

    if not os.path.exists(config_path):
        print(f"⚠ 配置文件不存在: {config_path}")
        print("\n📝 首次使用需要配置 MQ 连接信息\n")
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
    print("请选择 MQ 类型:")
    print("  1. Kafka")
    print("  2. RabbitMQ")
    print("  3. RocketMQ")
    choice = input("\n输入编号 (1/2/3): ").strip()

    mq_type = {"1": "kafka", "2": "rabbitmq", "3": "rocketmq"}.get(choice, "kafka")

    print(f"\n--- 配置 {mq_type.upper()} 连接 ---")

    if mq_type == "kafka":
        cfg = _prompt_kafka()
    elif mq_type == "rabbitmq":
        cfg = _prompt_rabbitmq()
    else:
        cfg = _prompt_rocketmq()

    config_data = {"current": "local", "local": cfg}

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 配置已保存: {config_path}")


def _prompt_kafka():
    servers = input("Bootstrap Servers (默认: localhost:9092): ").strip()
    return {
        "type": "kafka",
        "bootstrap_servers": servers or "localhost:9092",
        "sasl_mechanism": "",
        "sasl_plain_username": "",
        "sasl_plain_password": "",
        "security_protocol": "PLAINTEXT"
    }


def _prompt_rabbitmq():
    host = input("Host (默认: localhost): ").strip()
    port = input("AMQP Port (默认: 5672): ").strip()
    mport = input("Management Port (默认: 15672): ").strip()
    user = input("Username (默认: guest): ").strip()
    pwd = input("Password (默认: guest): ").strip()
    vhost = input("VHost (默认: /): ").strip()
    return {
        "type": "rabbitmq",
        "host": host or "localhost",
        "port": int(port) if port else 5672,
        "management_port": int(mport) if mport else 15672,
        "username": user or "guest",
        "password": pwd or "guest",
        "vhost": vhost or "/"
    }


def _prompt_rocketmq():
    ns = input("NameServer (默认: localhost:9876): ").strip()
    return {
        "type": "rocketmq",
        "nameserver": ns or "localhost:9876",
        "access_key": "",
        "secret_key": "",
        "group_id": ""
    }


# ============================================
# Adapter 抽象基类
# ============================================


class MQAdapter:
    """MQ 操作适配器基类"""

    def list_topics(self):
        raise NotImplementedError

    def list_groups(self):
        raise NotImplementedError

    def get_lag(self, name, group=None):
        raise NotImplementedError

    def peek_messages(self, name, count=5):
        raise NotImplementedError

    def info(self):
        raise NotImplementedError


# ============================================
# KafkaAdapter
# ============================================


class KafkaAdapter(MQAdapter):
    def __init__(self, config):
        self.config = config
        self.kafka = ensure_kafka_driver()
        self._admin = None

    def _build_auth_kwargs(self):
        kwargs = {}
        if self.config.get("sasl_mechanism"):
            kwargs["sasl_mechanism"] = self.config["sasl_mechanism"]
            kwargs["sasl_plain_username"] = self.config.get("sasl_plain_username", "")
            kwargs["sasl_plain_password"] = self.config.get("sasl_plain_password", "")
        if self.config.get("security_protocol"):
            kwargs["security_protocol"] = self.config["security_protocol"]
        return kwargs

    def _admin_client(self):
        if self._admin is None:
            kwargs = {
                "bootstrap_servers": self.config["bootstrap_servers"],
                **self._build_auth_kwargs()
            }
            self._admin = self.kafka.KafkaAdminClient(**kwargs)
        return self._admin

    def list_topics(self):
        client = self._admin_client()
        topics = client.list_topics()
        return [
            {"name": t} for t in topics
            if not t.startswith("__")
        ]

    def list_groups(self):
        client = self._admin_client()
        groups = client.list_consumer_groups()
        return [
            {"group_id": g[0], "protocol": g[1]}
            for g in groups
        ]

    def get_lag(self, topic, group_id=None):
        from kafka import TopicPartition, KafkaConsumer
        auth = self._build_auth_kwargs()
        bs = self.config["bootstrap_servers"]

        # 获取 partition 列表
        tmp_consumer = KafkaConsumer(bootstrap_servers=bs, **auth)
        ps = tmp_consumer.partitions_for_topic(topic)
        tmp_consumer.close()

        if not ps:
            return {"topic": topic, "error": "Topic 不存在或无 partition"}

        partitions = [TopicPartition(topic, p) for p in ps]

        # 获取 end offsets
        end_consumer = KafkaConsumer(bootstrap_servers=bs, **auth)
        end_offsets = end_consumer.end_offsets(partitions)
        end_consumer.close()

        def calc_for_group(gid):
            gc = KafkaConsumer(
                bootstrap_servers=bs,
                group_id=gid,
                enable_auto_commit=False,
                **auth
            )
            gc.assign(partitions)
            committed = {p: (gc.committed(p) or 0) for p in partitions}
            gc.close()
            parts = []
            total = 0
            for p in partitions:
                lag = end_offsets[p] - committed[p]
                total += lag
                parts.append({
                    "partition": p.partition,
                    "end_offset": end_offsets[p],
                    "committed_offset": committed[p],
                    "lag": lag
                })
            return {"group_id": gid, "total_lag": total, "partitions": parts}

        if group_id:
            return calc_for_group(group_id)

        groups = self.list_groups()
        result = {"topic": topic, "groups": []}
        for g in groups:
            try:
                result["groups"].append(calc_for_group(g["group_id"]))
            except Exception:
                pass
        return result

    def peek_messages(self, topic, count=5):
        from kafka import KafkaConsumer
        auth = self._build_auth_kwargs()
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.config["bootstrap_servers"],
            auto_offset_reset="earliest",
            consumer_timeout_ms=5000,
            max_poll_records=count,
            **auth
        )
        msgs = []
        for msg in consumer:
            val = msg.value
            if isinstance(val, bytes):
                try:
                    val = val.decode('utf-8')
                except UnicodeDecodeError:
                    val = val.hex()
            key = msg.key
            if isinstance(key, bytes):
                try:
                    key = key.decode('utf-8')
                except UnicodeDecodeError:
                    key = key.hex()
            msgs.append({
                "partition": msg.partition,
                "offset": msg.offset,
                "key": key,
                "value": val[:500] if isinstance(val, str) else val,
                "timestamp": msg.timestamp
            })
            if len(msgs) >= count:
                break
        consumer.close()
        return {"topic": topic, "messages": msgs}

    def info(self):
        client = self._admin_client()
        try:
            nodes = client.describe_cluster()
            return {
                "controller_id": nodes.get("controller_id"),
                "brokers": [{"id": b[0], "host": b[1], "port": b[2]}
                            for b in nodes.get("brokers", [])]
            }
        except Exception as e:
            return {"error": str(e)}


# ============================================
# RabbitMQAdapter
# ============================================


class RabbitMQAdapter(MQAdapter):
    def __init__(self, config):
        self.config = config
        self.requests = ensure_rabbitmq_driver()

    def _base_url(self):
        host = self.config.get("host", "localhost")
        port = self.config.get("management_port", 15672)
        return f"http://{host}:{port}/api"

    def _auth(self):
        return (self.config.get("username", "guest"),
                self.config.get("password", "guest"))

    def _api(self, path, method="GET", data=None):
        url = self._base_url() + path
        auth = self._auth()
        if method == "GET":
            r = self.requests.get(url, auth=auth, timeout=10)
        else:
            r = self.requests.post(url, auth=auth, json=data, timeout=10)
        r.raise_for_status()
        return r.json()

    def _vhost_path(self):
        vhost = self.config.get("vhost", "/")
        return vhost.replace("/", "%2F")

    def list_topics(self):
        # RabbitMQ 中返回 queues 作为主要列表
        return self.list_queues()

    def list_queues(self):
        queues = self._api(f"/queues/{self._vhost_path()}")
        return [
            {
                "name": q["name"],
                "messages_ready": q.get("messages_ready", 0),
                "messages_unacknowledged": q.get("messages_unacknowledged", 0),
                "total_messages": q.get("messages", 0),
                "consumers": q.get("consumers", 0)
            }
            for q in queues
            if not q["name"].startswith("amq.")
        ]

    def list_groups(self):
        consumers = self._api(f"/consumers/{self._vhost_path()}")
        return [
            {
                "consumer_tag": c.get("consumer_tag"),
                "queue": c.get("queue", {}).get("name"),
                "channel": c.get("channel_details", {}).get("name")
            }
            for c in consumers
        ]

    def get_lag(self, queue, group=None):
        q = self._api(f"/queues/{self._vhost_path()}/{queue}")
        return {
            "queue": queue,
            "messages_ready": q.get("messages_ready", 0),
            "messages_unacknowledged": q.get("messages_unacknowledged", 0),
            "total_messages": q.get("messages", 0),
            "consumers": q.get("consumers", 0)
        }

    def peek_messages(self, queue, count=5):
        data = {
            "count": count,
            "ackmode": "ack_requeue_true",
            "encoding": "auto"
        }
        msgs = self._api(
            f"/queues/{self._vhost_path()}/{queue}/get",
            method="POST",
            data=data
        )
        return {
            "queue": queue,
            "messages": [
                {
                    "payload": m.get("payload"),
                    "payload_bytes": m.get("payload_bytes"),
                    "redelivered": m.get("redelivered")
                }
                for m in msgs
            ]
        }

    def info(self):
        overview = self._api("/overview")
        return {
            "cluster_name": overview.get("cluster_name"),
            "rabbitmq_version": overview.get("rabbitmq_version"),
            "erlang_version": overview.get("erlang_version"),
            "object_totals": overview.get("object_totals", {})
        }


# ============================================
# RocketMQ Remoting 协议客户端
# ============================================


class RocketMQRemotingClient:
    """通过 RocketMQ Remoting 协议直接与 NameServer/Broker 通信"""

    # 请求码
    GET_BROKER_CLUSTER_INFO = 106
    GET_ROUTEINTO_BY_TOPIC = 105
    GET_ALL_TOPIC_LIST_FROM_NAMESERVER = 206
    GET_TOPIC_STATS_INFO = 102
    GET_CONSUMER_LIST_BY_GROUP = 53
    QUERY_CONSUMER_OFFSET = 14
    GET_MAX_OFFSET = 30  # RocketMQ 5.x Broker 支持

    # 语言码
    LANGUAGE_PYTHON = 8

    def __init__(self, nameserver_addr, timeout=5):
        self.nameservers = self._parse_addrs(nameserver_addr)
        self.timeout = timeout

    def _parse_addrs(self, addr_str):
        addrs = []
        for part in addr_str.split(';'):
            part = part.strip()
            if ':' in part:
                host, port = part.rsplit(':', 1)
                addrs.append((host.strip(), int(port.strip())))
            else:
                addrs.append((part, 9876))
        return addrs

    def _connect(self):
        """随机连接一个可用的 NameServer"""
        addrs = self.nameservers[:]
        random.shuffle(addrs)
        last_err = None
        for host, port in addrs:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                sock.connect((host, port))
                return sock
            except Exception as e:
                last_err = e
                continue
        raise ConnectionError(f"无法连接 NameServer: {last_err}")

    def _build_request(self, code, ext_fields=None, body=None):
        """构建 RemotingCommand 请求包"""
        cmd = {
            "code": code,
            "language": self.LANGUAGE_PYTHON,
            "version": 399,
            "opaque": random.randint(10000, 999999),
            "flag": 0,
            "remark": "",
            "extFields": ext_fields or {}
        }
        header_bytes = json.dumps(cmd, separators=(',', ':')).encode('utf-8')
        body_bytes = body or b''

        # 协议: [4字节总长度][4字节header长度][header][body]
        total_len = 4 + len(header_bytes) + len(body_bytes)
        packet = struct.pack('>I', total_len)
        packet += struct.pack('>I', len(header_bytes))
        packet += header_bytes
        packet += body_bytes
        return packet, cmd["opaque"]

    @staticmethod
    def fix_fastjson(s):
        """修复 FastJSON 格式（未加引号的键）为标准 JSON"""
        s = re.sub(r'([{,]\s*)(\d+)(\s*:)', r'\1"\2"\3', s)
        s = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', s)
        return s

    def _parse_response(self, sock, expected_opaque):
        """解析响应包"""
        len_data = self._recv_all(sock, 4)
        total_len = struct.unpack('>I', len_data)[0]

        header_len_data = self._recv_all(sock, 4)
        header_len = struct.unpack('>I', header_len_data)[0]

        header_data = self._recv_all(sock, header_len)
        header = json.loads(self.fix_fastjson(header_data.decode('utf-8')))

        body_len = total_len - 4 - header_len
        body = b''
        if body_len > 0:
            body = self._recv_all(sock, body_len)

        return header, body

    def _recv_all(self, sock, n):
        """确保读取 n 字节数据"""
        data = b''
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                raise ConnectionError("连接已关闭")
            data += chunk
        return data

    def _connect_addr(self, host, port):
        """连接指定地址"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect((host, port))
        return sock

    def invoke(self, code, ext_fields=None, body=None, target_addr=None):
        """发送请求并获取响应
        target_addr: (host, port) 元组，为 None 时连接 NameServer
        """
        sock = None
        try:
            if target_addr:
                sock = self._connect_addr(*target_addr)
            else:
                sock = self._connect()
            packet, opaque = self._build_request(code, ext_fields, body)
            sock.sendall(packet)
            header, body = self._parse_response(sock, opaque)

            if header.get("code") != 0:
                remark = header.get("remark", "未知错误")
                raise RuntimeError(f"请求失败: {remark}")

            return header, body
        finally:
            if sock:
                sock.close()

    def get_cluster_info(self):
        """获取集群信息"""
        try:
            _, body = self.invoke(self.GET_BROKER_CLUSTER_INFO)
            return json.loads(self.fix_fastjson(body.decode('utf-8')))
        except Exception as e:
            return {"error": str(e)}

    def get_all_topics(self):
        """获取所有 topic 列表"""
        try:
            _, body = self.invoke(self.GET_ALL_TOPIC_LIST_FROM_NAMESERVER)
            data = json.loads(self.fix_fastjson(body.decode('utf-8')))
            return data.get("topicList", [])
        except Exception as e:
            return {"error": str(e)}

    def get_topic_route(self, topic):
        """获取 topic 路由信息"""
        try:
            _, body = self.invoke(
                self.GET_ROUTEINTO_BY_TOPIC,
                ext_fields={"topic": topic}
            )
            return json.loads(self.fix_fastjson(body.decode('utf-8')))
        except Exception as e:
            return {"error": str(e)}

    def get_topic_stats(self, topic):
        """获取 topic 统计信息"""
        try:
            _, body = self.invoke(
                self.GET_TOPIC_STATS_INFO,
                ext_fields={"topic": topic}
            )
            return json.loads(self.fix_fastjson(body.decode('utf-8')))
        except Exception as e:
            return {"error": str(e)}


# ============================================
# RocketMQAdapter
# ============================================


class RocketMQAdapter(MQAdapter):
    def __init__(self, config):
        self.config = config
        self.driver = ensure_rocketmq_driver()
        self.client = RocketMQRemotingClient(config.get("nameserver", "localhost:9876"))

    def list_topics(self):
        topics = self.client.get_all_topics()
        if isinstance(topics, dict) and "error" in topics:
            return topics
        # 过滤系统 topic
        sys_prefixes = (
            "%RETRY%", "%DLQ%", "RMQ_SYS_", "rmq_sys_",
            "TBW102", "OFFSET_MOVED_EVENT", "SCHEDULE_TOPIC_XXXX",
            "DefaultCluster", "broker-"
        )
        filtered = [t for t in topics if not any(t.startswith(p) or t == p for p in sys_prefixes)]
        return [{"name": t} for t in sorted(filtered)]

    def list_groups(self):
        topics = self.client.get_all_topics()
        if isinstance(topics, dict) and "error" in topics:
            return topics
        groups = set()
        for topic in topics:
            if topic.startswith("%RETRY%"):
                # %RETRY%<group_name> 格式
                group = topic[7:]  # 去掉 %RETRY% 前缀
                groups.add(group)
        return [{"group_id": g} for g in sorted(groups)]

    def get_lag(self, topic, group=None):
        """查看 topic 堆积信息
        无 group: 返回 topic 路由信息（broker、queue 数量）
        有 group: 返回消费组在每个 queue 上的堆积
        """
        route = self.client.get_topic_route(topic)
        if isinstance(route, dict) and "error" in route:
            return route

        broker_datas = route.get("brokerDatas", [])
        queue_datas = route.get("queueDatas", [])

        if not broker_datas or not queue_datas:
            return {"topic": topic, "error": "Topic 不存在或没有路由信息"}

        if not group:
            # 只返回路由概览
            brokers = []
            for bd in broker_datas:
                addrs = bd.get("brokerAddrs", {})
                for bid, addr in addrs.items():
                    brokers.append({
                        "broker_name": bd.get("brokerName"),
                        "broker_id": bid,
                        "address": addr
                    })
            queues = []
            for qd in queue_datas:
                queues.append({
                    "broker": qd.get("brokerName"),
                    "read_queues": qd.get("readQueueNums", 0),
                    "write_queues": qd.get("writeQueueNums", 0)
                })
            return {
                "topic": topic,
                "brokers": brokers,
                "queues": queues,
                "note": "使用 --lag topic --group <group> 查看消费组堆积"
            }

        return self._get_group_lag(topic, group, broker_datas, queue_datas)

    def _get_group_lag(self, topic, group, broker_datas, queue_datas):
        """获取指定消费组在 topic 上的堆积"""
        # 构建 brokerName -> 地址映射
        broker_addrs = {}
        for bd in broker_datas:
            name = bd.get("brokerName")
            addrs = bd.get("brokerAddrs", {})
            # 优先用 brokerId=0 (master)
            if "0" in addrs:
                broker_addrs[name] = addrs["0"]
            elif addrs:
                broker_addrs[name] = list(addrs.values())[0]

        result = []
        total_lag = 0

        for qd in queue_datas:
            broker_name = qd.get("brokerName")
            read_queue_nums = qd.get("readQueueNums", 0)
            broker_addr = broker_addrs.get(broker_name)

            if not broker_addr:
                continue

            host, port = broker_addr.rsplit(":", 1)
            target = (host, int(port))

            for queue_id in range(read_queue_nums):
                try:
                    # 查询消费组 offset
                    consumer_hdr, _ = self.client.invoke(
                        RocketMQRemotingClient.QUERY_CONSUMER_OFFSET,
                        ext_fields={
                            "consumerGroup": group,
                            "topic": topic,
                            "queueId": str(queue_id),
                            "brokerName": broker_name
                        },
                        target_addr=target
                    )
                    consumer_offset = int(consumer_hdr.get("extFields", {}).get("offset", -1))

                    # 查询 broker 最大 offset
                    max_hdr, _ = self.client.invoke(
                        RocketMQRemotingClient.GET_MAX_OFFSET,
                        ext_fields={
                            "topic": topic,
                            "queueId": str(queue_id)
                        },
                        target_addr=target
                    )
                    max_offset = int(max_hdr.get("extFields", {}).get("offset", -1))

                    lag = max(max_offset - consumer_offset, 0) if max_offset >= 0 and consumer_offset >= 0 else -1
                    if lag >= 0:
                        total_lag += lag

                    result.append({
                        "broker": broker_name,
                        "queue_id": queue_id,
                        "max_offset": max_offset,
                        "consumer_offset": consumer_offset,
                        "lag": lag
                    })
                except Exception as e:
                    result.append({
                        "broker": broker_name,
                        "queue_id": queue_id,
                        "error": str(e)
                    })

        return {
            "topic": topic,
            "group": group,
            "total_lag": total_lag,
            "queues": result
        }

    def peek_messages(self, topic, count=5):
        return {"note": "RocketMQ 消息查看建议通过 Dashboard 或 mqadmin 查看"}

    def info(self):
        cluster = self.client.get_cluster_info()
        if isinstance(cluster, dict) and "error" in cluster:
            return {
                "nameserver": self.config.get("nameserver"),
                "error": cluster["error"]
            }

        brokers = []
        broker_addr_table = cluster.get("brokerAddrTable", {})
        for broker_name, info in broker_addr_table.items():
            addrs = info.get("brokerAddrs", {})
            for broker_id, addr in addrs.items():
                brokers.append({
                    "broker_name": broker_name,
                    "broker_id": broker_id,
                    "address": addr
                })

        return {
            "nameserver": self.config.get("nameserver"),
            "cluster_name": list(cluster.get("clusterAddrTable", {}).keys()),
            "broker_count": len(broker_addr_table),
            "brokers": brokers
        }


# ============================================
# 工厂函数 & 格式化
# ============================================


def create_adapter(config):
    mq_type = config.get("type", "kafka")
    if mq_type == "kafka":
        return KafkaAdapter(config)
    elif mq_type == "rabbitmq":
        return RabbitMQAdapter(config)
    elif mq_type == "rocketmq":
        return RocketMQAdapter(config)
    else:
        print(f"错误: 不支持的 MQ 类型 '{mq_type}'")
        sys.exit(1)


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
        if "note" in data:
            print(f"ℹ {data['note']}")
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
    parser = argparse.ArgumentParser(description="MQ 操作工具")
    parser.add_argument("--init", action="store_true", help="交互式配置")
    parser.add_argument("--env", "-e", help="环境")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 输出")
    parser.add_argument("--list", action="store_true", help="列出 topics / queues")
    parser.add_argument("--groups", action="store_true", help="列出消费组")
    parser.add_argument("--lag", help="查看堆积 (topic/queue)")
    parser.add_argument("--group", help="消费组（配合 --lag 使用）")
    parser.add_argument("--peek", help="查看消息 (topic/queue)")
    parser.add_argument("--count", type=int, default=5, help="查看消息数量")
    parser.add_argument("--info", action="store_true", help="查看集群信息")

    args = parser.parse_args()

    if args.init:
        config_path = os.getenv(
            'AGENT_MQ_CONFIG',
            os.path.expanduser('~/.config/mq/config.json')
        )
        create_config(config_path)
        return

    config, env = load_config(args.config, args.env)
    adapter = create_adapter(config)

    result = None
    try:
        if args.list:
            result = adapter.list_topics()
        elif args.groups:
            result = adapter.list_groups()
        elif args.lag:
            result = adapter.get_lag(args.lag, args.group)
        elif args.peek:
            result = adapter.peek_messages(args.peek, args.count)
        elif args.info:
            result = adapter.info()
        else:
            parser.print_help()
            return
    except Exception as e:
        result = {"error": str(e), "error_type": type(e).__name__}

    format_result(result, args.json)


if __name__ == "__main__":
    main()
