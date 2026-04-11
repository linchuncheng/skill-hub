# Python工程编码规范

统一项目Python代码编写标准。

## 总体目标

| 目标 | 说明 |
|------|------|
| 一致性 | 代码风格统一，降低协作成本 |
| 可读性 | 命名清晰，新成员快速理解业务 |
| 可维护性 | 遵循设计原则，降低修改成本 |
| 高质量 | 减少编码错误和性能问题 |
| Pythonic | 遵循Python之禅 |

## 项目环境

| 项目 | 配置 |
|------|------|
| Python版本 | 3.10+ |
| Web框架 | Django 5.0.6 + DRF 3.16.0 |
| 包管理 | pip + requirements.txt |
| 代码格式化 | Black (line-length: 88) |
| 代码检查 | Ruff + MyPy |
| 异步支持 | Celery 5.4.0 + Channels 4.2.2 |

## 命名规范

### 模块/包命名

| 类型 | 规则 | 示例 |
|------|------|------|
| 模块 | 小写+下划线 | `user_service.py` |
| 包 | 小写，简短无下划线 | `services`, `utils` |
| Django App | 小写，语义清晰 | `aliyunApp`, `releaseApp` |

### 类命名（PascalCase）

```python
class AliyunAuth:
    """阿里云认证类"""
    pass

class CloudControlClient:
    """云控制客户端"""
    pass

class ProjectNotFoundError(Exception):
    """项目不存在异常"""
    pass
```

### 分层对象命名

| 层次 | 对象类型 | 后缀 | 示例 |
|------|---------|------|------|
| View层 | 视图函数 | 无后缀 | `user_login` |
| View层 | 类视图 | `View` | `ProjectListCreateView` |
| Service层 | 服务类 | `Service` | `JenkinsService` |
| Model层 | Django模型 | 无后缀 | `Project`, `Service` |
| Serializer层 | 序列化器 | `Serializer` | `ProjectSerializer` |
| Client层 | 客户端类 | `Client` | `K8sClient`, `SlsClient` |
| 任务层 | Celery任务 | 无后缀 | `sync_slow_sql` |

### 函数/方法命名（snake_case）

| 前缀 | 含义 | 示例 |
|------|------|------|
| `get_` | 获取单个对象 | `get_user_by_id()` |
| `list_` / `query_` | 查询列表 | `list_projects()` |
| `create_` | 新增数据 | `create_order()` |
| `update_` | 更新数据 | `update_service_info()` |
| `delete_` | 删除数据 | `delete_namespace()` |
| `build_` | 触发构建 | `build_job()` |
| `check_` / `validate_` | 校验逻辑 | `check_permission()` |
| `send_` | 发送通知 | `send_message()` |
| `sync_` | 同步数据 | `sync_slow_sql()` |
| `is_` / `has_` | 布尔判断 | `is_ready()`, `has_permission()` |

### 变量命名

| 类型 | 规则 | 示例 |
|------|------|------|
| 变量 | snake_case | `user_name`, `cluster_list` |
| 常量 | 全大写+下划线 | `DEFAULT_TIMEOUT = 30` |
| 私有变量 | 单下划线开头 | `_cache`, `_client` |
| Django settings | 全大写 | `SECRET_KEY`, `DATABASES` |

### 枚举命名

```python
from django.db import models

class PublishStatus(models.TextChoices):
    PENDING = 'pending', '待发布'
    RUNNING = 'running', '发布中'
    SUCCESS = 'success', '成功'
    FAILED = 'failed', '失败'
    ROLLBACK = 'rollback', '已回滚'
```

## 代码格式规范

### 缩进与换行

| 项目 | 规则 |
|------|------|
| 缩进 | 4个空格，禁止Tab |
| 行长度 | 不超过88字符（Black默认） |
| 长参数 | 每个参数独占一行 |

```python
def create_deployment(
    cluster_name: str,
    namespace: str,
    deployment_name: str,
    image: str,
    replicas: int = 1,
    env_vars: dict | None = None,
) -> dict:
    pass
```

### 空格使用

| 场景 | 规则 |
|------|------|
| 运算符两侧 | 加空格：`total = a + b` |
| 逗号后 | 加空格：`func(a, b, c)` |
| 类型注解冒号后 | 加空格：`name: str` |
| 函数默认参数 | 不加空格：`def func(x=1):` |

### 空行使用

| 场景 | 空行数 |
|------|--------|
| 顶层定义之间（类、函数） | 2行 |
| 类内方法之间 | 1行 |
| 逻辑块之间 | 适当加1行 |

### 导入规范

```python
# 标准库
import json
import os
from datetime import datetime
from typing import Optional

# 第三方库
from django.http import JsonResponse, HttpResponse
from rest_framework import generics
from celery import shared_task

# Django本地模块
from django.conf import settings
from django.contrib.auth.models import User

# 项目内部模块
from .models import Project, Service
from .serializers import ProjectSerializer
from ..utils.decorators import ajax_only
```

## 类型注解规范

### 基本规则

- **新代码**必须添加类型注解
- 复杂类型使用 `typing` 模块或Python 3.10+内置类型

```python
from typing import Optional
from django.db import models

def get_project_by_id(project_id: int) -> Optional[Project]:
    """根据ID获取项目"""
    try:
        return Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return None

def list_services(project_id: int, status: str | None = None) -> list[Service]:
    """列出项目下的服务"""
    queryset = Service.objects.filter(project_id=project_id)
    if status:
        queryset = queryset.filter(status=status)
    return list(queryset)
```

### Django模型类型注解

```python
from django.db import models

class Project(models.Model):
    name: str = models.CharField(max_length=100, verbose_name="项目名称")
    description: str = models.TextField(blank=True, verbose_name="项目描述")
    created_at: datetime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_active: bool = models.BooleanField(default=True, verbose_name="是否启用")
```

### DRF序列化器类型注解

```python
from rest_framework import serializers

class ProjectSerializer(serializers.ModelSerializer):
    """项目序列化器"""
    service_count: int = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'service_count', 'created_at']
    
    def get_service_count(self, obj: Project) -> int:
        return obj.services.count()
```

## 注释规范

### 模块/类/方法注释

| 类型 | 要求 |
|------|------|
| 模块 | 顶部包含职责说明 |
| 类 | 职责说明 + Attributes |
| 公共方法 | Google风格docstring |

```python
class JenkinsService:
    """
    Jenkins服务类
    
    封装Jenkins API调用，提供任务触发、构建查询、日志获取等功能。
    
    Attributes:
        server: Jenkins服务器连接实例
        base_url: Jenkins服务器地址
        username: 认证用户名
    """
    
    def build_job(self, job_name: str, parameters: dict | None = None) -> int:
        """
        触发Jenkins构建任务
        
        Args:
            job_name: Jenkins Job名称
            parameters: 构建参数，可选
            
        Returns:
            队列ID
            
        Raises:
            JenkinsException: 当任务触发失败时抛出
        """
        pass
```

### 行内注释与标记

```python
# 兼容旧数据: 之前的版本可能没有status字段
if status is None:
    status = PublishStatus.PENDING

total = price * quantity  # 计算总价(不含优惠)

# TODO: 后续需要支持批量构建
# FIXME: 此处超时时间需要根据压测结果调整
```

## 异常处理规范

### 自定义异常

```python
class BusinessError(Exception):
    """业务异常基类"""
    
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class ProjectNotFoundError(BusinessError):
    """项目不存在异常"""
    
    def __init__(self, project_id: int):
        super().__init__(
            code="PROJECT_NOT_FOUND",
            message=f"项目不存在: {project_id}",
        )
```

### 异常捕获规范

| 方式 | 说明 |
|------|------|
| ❌ `except:` | 禁止空except |
| ❌ `except Exception:` | 避免捕获所有异常 |
| ✅ 具体异常 | 优先捕获具体异常类型 |

```python
# ❌ 错误 - 捕获所有异常
except:
    pass

# ❌ 错误 - 使用print输出异常
except Exception as e:
    print(f"Error: {e}")

# ✅ 正确 - 使用logging记录异常
import logging
logger = logging.getLogger(__name__)

try:
    process_order(order_id)
except ProjectNotFoundError as e:
    logger.warning(f"项目不存在: {e}")
    raise
except BusinessError as e:
    logger.error(f"业务异常: {e}")
    return JsonResponse({'error': e.message}, status=400)
except Exception as e:
    logger.exception(f"处理订单异常: {e}")
    return JsonResponse({'error': '系统错误'}, status=500)
```

### Django视图异常处理

```python
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist, ValidationError

@csrf_exempt
def update_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        return JsonResponse({'message': '更新成功'})
    except ObjectDoesNotExist:
        return JsonResponse({'error': '项目不存在'}, status=404)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.exception(f"更新项目异常: {e}")
        return JsonResponse({'error': '系统错误'}, status=500)
```

## 日志规范

### 日志框架与级别

| 级别 | 用途 | 场景 |
|------|------|------|
| DEBUG | 调试信息 | 变量值、执行路径 |
| INFO | 关键业务流程 | 接口入参、业务节点、外部调用 |
| WARNING | 需警惕但不影响业务 | 降级逻辑、兼容处理 |
| ERROR | 需立即修复 | 异常堆栈、数据不一致 |

```python
import logging

logger = logging.getLogger(__name__)
```

### 日志内容规范

```python
# 入参日志
logger.info(f"创建发布记录, project_id={project_id}, service_id={service_id}")

# 业务节点日志
logger.info(f"Jenkins构建触发成功, queue_id={queue_id}")

# 异常日志（必须包含堆栈）
try:
    process_payment(order_id)
except Exception as e:
    logger.exception(f"支付处理异常, order_id={order_id}")
    # 或
    logger.error(f"支付处理异常, order_id={order_id}", exc_info=True)
```

### 日志禁忌

| ❌ 禁止 | ✅ 正确 |
|--------|--------|
| 使用 `print` | 使用logging框架 |
| 循环中打日志 | 批量记录：`logger.info(f"批量处理, count={len(items)}")` |
| 记录敏感信息 | 脱敏处理 |
| 异常不记录堆栈 | 使用 `exc_info=True` 或 `logger.exception()` |

## 分层架构规范

### 总体目标

| 目标 | 说明 |
|------|------|
| 职责分明 | 每层职责明确，避免交叉 |
| 单向依赖 | 上层依赖下层，避免循环依赖 |
| 高内聚低耦合 | 层内高内聚，层间低耦合 |
| 易于测试 | 各层职责清晰，便于测试 |

### Django项目分层结构

| 层级 | 职责 | 对应Django组件 |
|------|------|----------------|
| **View层** | 接收请求、参数校验、调用Service、返回响应 | views.py, DRF View |
| **Service层** | 业务逻辑编排、事务控制、协调各组件 | services/目录 |
| **Model层** | 数据模型定义、ORM操作 | models.py |
| **Serializer层** | 数据序列化/反序列化、参数校验 | serializers.py |
| **Task层** | 异步任务、定时任务 | tasks.py |
| **Client层** | 外部服务调用封装 | 阿里云SDK、K8s Client等 |

**调用方向**: View → Service → Model/Client

### 层间调用规则

| 规则 | 说明 |
|------|------|
| 单向依赖 | 上层调用下层，下层不调用上层 |
| 禁止跨层 | View层禁止直接调用Client层（复杂查询除外） |
| 避免循环 | 同层之间禁止相互依赖 |

**正确调用链路**:
```
View → Service → Model
            ↓
         Client（外部服务）
```

**错误调用**:
```
❌ View → Client (跨层调用，跳过Service)
❌ Model → View (下层调用上层)
❌ ServiceA → ServiceB → ServiceA (循环依赖)
```

### View层规范

#### 职责

| 职责 | 说明 |
|------|------|
| 接收HTTP请求 | 处理请求参数、文件上传等 |
| 参数校验 | 基础参数校验（业务校验下放Service层） |
| 调用Service | 业务逻辑委托给Service层 |
| 返回响应 | 统一响应格式、状态码 |

#### 设计原则

- ❌ **禁止在View中写业务逻辑**
- ❌ **禁止在View中直接调用外部API（Client层）**
- ✅ **View只做请求响应处理，业务逻辑下沉到Service**

#### 函数视图示例

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
import logging

from .services.project_service import ProjectService

logger = logging.getLogger(__name__)


@login_required
@permission_required("releaseApp.add_project", raise_exception=True)
def add_project(request):
    """
    添加项目
    
    View层职责：
    1. 校验请求方法和Content-Type
    2. 解析请求参数
    3. 调用Service层执行业务
    4. 返回统一格式响应
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if request.headers.get('content-type') != 'application/json':
        return JsonResponse({'error': 'Invalid Content-Type'}, status=415)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        
        project = ProjectService.create_project(
            name=data.get('projectname', ''),
            description=data.get('projectdesc', ''),
            zone_id=data.get('zone_id'),
            created_by=request.user
        )
        
        logger.info(f"项目创建成功, project_id={project.id}")
        return JsonResponse({'message': '创建成功', 'id': project.id}, status=201)
        
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.exception(f"创建项目异常: {e}")
        return JsonResponse({'error': '系统错误'}, status=500)
```

#### DRF类视图示例

```python
from rest_framework import generics
from rest_framework.permissions import DjangoModelPermissions

from .services.project_service import ProjectService


class ProjectListCreateView(generics.ListCreateAPIView):
    """项目列表/创建视图"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [DjangoModelPermissions]
    pagination_class = LayuiPagination
    
    def perform_create(self, serializer):
        """创建时调用Service层"""
        ProjectService.create_project(
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description', ''),
            created_by=self.request.user
        )
```

### Service层规范

#### 职责

| 职责 | 说明 |
|------|------|
| 业务逻辑 | 实现核心业务功能 |
| 流程编排 | 协调Model、Client、Cache等 |
| 事务控制 | 管理数据库事务边界 |
| 业务校验 | 校验业务规则，抛出业务异常 |

#### 命名规范

| 对象类型 | 命名规则 | 示例 |
|---------|---------|------|
| Service类 | `{业务对象}Service` | `ProjectService`, `JenkinsService` |
| Service模块 | `{业务对象}_service.py` | `project_service.py` |
| 方法 | 动词+业务动作 | `create_project`, `trigger_build` |

#### Service层示例

```python
import logging
from typing import Optional
from django.db import transaction

from ..models import Project, Service
from ..clients.jenkins_client import JenkinsClient
from ..tasks.notification_tasks import send_notification

logger = logging.getLogger(__name__)


class ProjectService:
    """
    项目服务类
    
    提供项目创建、更新、删除等业务功能。
    """
    
    @staticmethod
    @transaction.atomic
    def create_project(
        name: str,
        description: str = '',
        zone_id: Optional[int] = None,
        created_by=None
    ) -> Project:
        """
        创建项目
        
        Args:
            name: 项目名称
            description: 项目描述
            zone_id: 区域ID
            created_by: 创建人
            
        Returns:
            创建的项目对象
            
        Raises:
            ValueError: 当参数校验失败时抛出
        """
        # 业务校验
        if not name or len(name.strip()) < 3:
            raise ValueError("项目名称至少3个字符")
        
        if Project.objects.filter(name=name).exists():
            raise ValueError("项目名称已存在")
        
        # 创建项目
        project = Project.objects.create(
            name=name.strip(),
            description=description,
            zone_id=zone_id,
            created_by=created_by
        )
        
        logger.info(f"项目创建成功, project_id={project.id}, name={name}")
        return project
    
    @staticmethod
    def trigger_build(project_id: int, service_name: str, branch: str) -> dict:
        """触发项目构建"""
        project = Project.objects.filter(id=project_id).first()
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        service = project.services.filter(name=service_name).first()
        if not service:
            raise ValueError(f"服务不存在: {service_name}")
        
        # 调用Client层
        jenkins_client = JenkinsClient()
        queue_id = jenkins_client.build_job(
            job_name=service.jenkins_job,
            parameters={'BRANCH': branch}
        )
        
        # 创建构建记录
        build_record = BuildRecord.objects.create(
            project=project,
            service=service,
            branch=branch,
            queue_id=queue_id,
            status='pending'
        )
        
        # 异步发送通知
        send_notification.delay(
            user_ids=[project.owner_id],
            message=f"项目 {project.name} 开始构建"
        )
        
        return {
            'build_id': build_record.id,
            'queue_id': queue_id,
            'status': 'pending'
        }
```

#### Service层设计原则

1. **静态方法优先**：Service方法尽量使用 `@staticmethod`，减少状态依赖
2. **事务边界清晰**：使用 `@transaction.atomic` 或 `with transaction.atomic()`
3. **异常转换**：捕获底层异常，转换为业务异常抛出
4. **日志记录**：关键节点记录入参、出参、异常

### Client层规范

#### 职责

| 职责 | 说明 |
|------|------|
| 外部服务封装 | 封装第三方API调用（阿里云、Jenkins、K8s等） |
| 连接管理 | 管理连接池、认证信息 |
| 错误处理 | 处理超时、重试、降级 |

#### 命名规范

| 对象类型 | 命名规则 | 示例 |
|---------|---------|------|
| Client类 | `{服务名}Client` | `JenkinsClient`, `K8sClient`, `SlsClient` |
| Client模块 | `{服务名}_client.py` 或 `clients/{服务名}.py` | `jenkins_client.py` |

#### Client层示例

```python
import logging
import jenkins
from django.conf import settings

logger = logging.getLogger(__name__)


class JenkinsClient:
    """
    Jenkins客户端
    
    封装Jenkins API调用，提供任务触发、构建查询等功能。
    """
    
    def __init__(self, base_url: str = None, username: str = None, password: str = None):
        self.base_url = base_url or settings.JENKINS_URL
        self.username = username or settings.JENKINS_USER
        self.password = password or settings.JENKINS_TOKEN
        self._server = None
    
    @property
    def server(self):
        """懒加载Jenkins连接"""
        if self._server is None:
            self._server = jenkins.Jenkins(
                self.base_url,
                username=self.username,
                password=self.password
            )
        return self._server
    
    def build_job(self, job_name: str, parameters: dict = None) -> int:
        """
        触发Jenkins构建
        
        Args:
            job_name: Job名称
            parameters: 构建参数
            
        Returns:
            队列ID
            
        Raises:
            JenkinsException: 当触发失败时抛出
        """
        try:
            queue_id = self.server.build_job(job_name, parameters=parameters)
            logger.info(f"Jenkins构建触发成功, job={job_name}, queue_id={queue_id}")
            return queue_id
        except jenkins.JenkinsException as e:
            logger.error(f"Jenkins构建触发失败, job={job_name}, error={e}")
            raise
```

### Model层规范

#### 职责

| 职责 | 说明 |
|------|------|
| 数据模型定义 | 定义表结构、字段、关系 |
| 基础数据操作 | ORM提供的CRUD操作 |
| 模型方法 | 简单的模型级方法（可选） |

#### 设计原则

- ✅ **Model只含字段定义和基础方法**
- ❌ **Model中不写复杂业务逻辑**
- ❌ **Model中不调用外部服务**

#### Model示例

```python
from django.db import models

class Project(models.Model):
    """
    项目模型
    
    Attributes:
        name: 项目名称
        description: 项目描述
        zone: 所属区域
        status: 项目状态
        created_at: 创建时间
    """
    
    class Status(models.TextChoices):
        ACTIVE = 'active', '启用'
        DISABLED = 'disabled', '禁用'
        ARCHIVED = 'archived', '归档'
    
    name: str = models.CharField(max_length=100, verbose_name="项目名称")
    description: str = models.TextField(blank=True, verbose_name="项目描述")
    zone = models.ForeignKey(
        ZoneInfo, 
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name="所属区域"
    )
    status: str = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="状态"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "项目"
        verbose_name_plural = verbose_name
        db_table = 'release_project'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self) -> str:
        return self.name
    
    @property
    def service_count(self) -> int:
        """项目下的服务数量"""
        return self.services.count()
```

### 事务管理规范

#### 事务边界

| 规则 | 说明 |
|------|------|
| Service层控制 | 业务操作在Service层使用事务 |
| 避免跨服务 | 事务中不调用外部HTTP服务 |
| 事务尽量小 | 只包含必要的数据库操作 |

#### 事务示例

```python
from django.db import transaction

class ProjectService:
    
    @staticmethod
    @transaction.atomic
    def create_project_with_services(
        project_data: dict,
        services_data: list[dict]
    ) -> Project:
        """
        创建项目并初始化服务
        
        使用事务保证原子性。
        """
        # 创建项目
        project = Project.objects.create(**project_data)
        
        # 批量创建服务
        services = [
            Service(project=project, **service_data)
            for service_data in services_data
        ]
        Service.objects.bulk_create(services)
        
        # 外部调用在事务外执行
        return project

# 调用方
def create_project_view(request):
    try:
        with transaction.atomic():
            project = ProjectService.create_project_with_services(
                project_data={'name': 'Test'},
                services_data=[{'name': 'svc1'}, {'name': 'svc2'}]
            )
        
        # 事务提交后执行外部调用
        send_notification.delay(f"项目 {project.name} 创建成功")
        
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
```

## Django视图规范

### 函数视图

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from util.decorators import ajax_only
import logging

logger = logging.getLogger(__name__)


@login_required
@ajax_only
def project_manager(request):
    """项目管理页面"""
    return render(request, 'project_manager.html')


@csrf_exempt
@permission_required("releaseApp.add_project", raise_exception=True)
def add_project(request):
    """添加项目"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if request.headers.get('content-type') != 'application/json':
        return JsonResponse({'error': 'Invalid Content-Type'}, status=415)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        name = data.get('projectname', '').strip()
        
        if not name:
            return JsonResponse({'error': '项目名称不能为空'}, status=400)
        
        project = Project.objects.create(name=name)
        logger.info(f"项目创建成功, project_id={project.id}")
        return JsonResponse({'message': '创建成功', 'id': project.id})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.exception(f"创建项目异常: {e}")
        return JsonResponse({'error': '系统错误'}, status=500)
```

### DRF类视图

```python
from rest_framework import generics
from rest_framework.permissions import DjangoModelPermissions
from django.http import JsonResponse
from django.db.models.deletion import ProtectedError

class ProjectListCreateView(generics.ListCreateAPIView):
    """项目列表/创建视图"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [DjangoModelPermissions]
    pagination_class = LayuiPagination
    
    def get_queryset(self):
        queryset = Project.objects.all()
        zone_id = self.request.query_params.get('zone_id')
        if zone_id and zone_id != '-1':
            queryset = queryset.filter(zone_id=zone_id)
        return queryset


class ProjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """项目详情/更新/删除视图"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [DjangoModelPermissions]
    
    def handle_exception(self, exc):
        if isinstance(exc, ProtectedError):
            return JsonResponse(
                {"error": "无法删除：该项目被关联，请先删除关联数据"}, 
                status=400
            )
        return super().handle_exception(exc)
```

## Celery任务规范

### 任务定义

```python
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_slow_sql(self, rds_instance_id: str, start_time: str, end_time: str):
    """
    同步慢SQL数据
    
    Args:
        rds_instance_id: RDS实例ID
        start_time: 开始时间
        end_time: 结束时间
    """
    try:
        logger.info(f"开始同步慢SQL, rds_instance={rds_instance_id}")
        # 同步逻辑
        logger.info(f"慢SQL同步完成, rds_instance={rds_instance_id}")
    except Exception as exc:
        logger.exception(f"同步慢SQL异常: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def send_notification(user_id: int, message: str):
    """发送通知消息"""
    try:
        logger.info(f"发送通知, user_id={user_id}")
        # 发送逻辑
    except Exception as e:
        logger.exception(f"发送通知异常: {e}")
```

### 任务调用

```python
# 异步调用
sync_slow_sql.delay(rds_instance_id, start_time, end_time)

# 定时任务（配合django-celery-beat）
from celery import Celery
app = Celery('CycloneSite')

app.conf.beat_schedule = {
    'sync-slow-sql-every-hour': {
        'task': 'SlowsqlApp.tasks.sync_slow_sql',
        'schedule': 3600.0,  # 每小时
    },
}
```

## Django ORM规范

### 查询优化

```python
# ✅ 使用select_related减少查询次数
projects = Project.objects.select_related('zone').all()

# ✅ 使用prefetch_related处理多对多/反向关系
projects = Project.objects.prefetch_related('services').all()

# ✅ 只查询需要的字段
projects = Project.objects.only('id', 'name', 'status')

# ❌ 避免N+1查询
for project in Project.objects.all():  # 1次查询
    print(project.zone.name)  # N次查询

# ✅ 正确做法
for project in Project.objects.select_related('zone').all():
    print(project.zone.name)
```

### 批量操作

```python
# ✅ 批量创建
Project.objects.bulk_create([
    Project(name='project1'),
    Project(name='project2'),
])

# ✅ 批量更新
Project.objects.filter(status='pending').update(status='running')

# ✅ 批量删除（软删除优先）
Project.objects.filter(is_active=False).update(is_deleted=True)
```

### 事务处理

```python
from django.db import transaction

@transaction.atomic
def create_order_with_items(order_data, items_data):
    """原子性创建订单和订单项"""
    order = Order.objects.create(**order_data)
    for item_data in items_data:
        OrderItem.objects.create(order=order, **item_data)
    return order

# 或手动控制
from django.db import transaction

def process_data():
    with transaction.atomic():
        # 事务内的操作
        project = Project.objects.create(name='test')
        Service.objects.create(project=project, name='service1')
```

## 安全编码规范

### SQL注入防护

| ❌ 错误 | ✅ 正确 |
|--------|--------|
| `f"SELECT * FROM users WHERE id = {user_id}"` | ORM查询或参数化SQL |

```python
# ✅ ORM查询
user = User.objects.filter(id=user_id).first()

# ✅ 原生SQL参数化
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute(
        "SELECT * FROM users WHERE id = %s", 
        [user_id]
    )
```

### 参数校验

```python
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def create_user(request):
    data = json.loads(request.body)
    
    # 必填校验
    username = data.get('username', '').strip()
    if not username:
        return JsonResponse({'error': '用户名不能为空'}, status=400)
    
    # 长度校验
    if len(username) < 3 or len(username) > 50:
        return JsonResponse({'error': '用户名长度3-50字符'}, status=400)
    
    # 邮箱格式校验
    email = data.get('email', '')
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'error': '邮箱格式错误'}, status=400)
```

### 敏感信息处理

```python
import os

# ✅ 环境变量读取
SECRET_KEY = os.environ.get('SECRET_KEY')
ALIYUN_ACCESS_KEY = os.environ.get('ALIYUN_ACCESS_KEY')

# ✅ 密码加密存储
from django.contrib.auth.hashers import make_password, check_password

# 脱敏处理
def mask_phone(phone: str) -> str:
    """手机号脱敏: 138****8888"""
    if len(phone) == 11:
        return f"{phone[:3]}****{phone[-4:]}"
    return phone
```

## 性能优化规范

### 避免循环IO

```python
# ❌ 错误 - 循环中查询数据库
for user_id in user_ids:
    user = User.objects.get(id=user_id)  # N次查询
    users.append(user)

# ✅ 正确 - 批量查询
users = User.objects.filter(id__in=user_ids)  # 1次查询
```

### 缓存使用

```python
from django.core.cache import cache

def get_project_detail(project_id: int) -> dict:
    cache_key = f"project:detail:{project_id}"
    data = cache.get(cache_key)
    
    if data is None:
        project = Project.objects.get(id=project_id)
        data = {
            'id': project.id,
            'name': project.name,
            'services': list(project.services.values('id', 'name'))
        }
        cache.set(cache_key, data, timeout=300)  # 5分钟缓存
    
    return data
```

### 异步处理

```python
# 耗时操作放入Celery任务
@shared_task
def generate_report(project_id: int):
    """生成报表（耗时操作）"""
    pass

# 视图立即返回
def export_report(request, project_id):
    generate_report.delay(project_id)
    return JsonResponse({'message': '报表生成中，请稍后查看'})
```

## 测试规范

### 命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 测试文件 | `test_<模块>.py` | `test_project_service.py` |
| 测试类 | `Test<类名>` | `TestProjectService` |
| 测试方法 | `test_<方法>_<场景>` | `test_create_project_success` |

### Django测试

```python
class TestProjectService(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.login(username='testuser', password='testpass')

    def test_create_project_success(self):
        # Arrange
        data = {'projectname': 'Test Project', 'projectdesc': 'Description'}

        # Act
        response = self.client.post(
            '/api/projects/',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.objects.count(), 1)
```

## 代码评审检查点

### 基础规范

- [ ] 命名规范（模块、类、函数、变量）
- [ ] 类型注解（新代码必须）
- [ ] 注释完整（模块、类、方法）
- [ ] 异常处理（logging，禁print）
- [ ] 日志记录关键信息
- [ ] 无循环IO
- [ ] 无SQL注入风险
- [ ] 空值处理
- [ ] 无魔法值（用枚举/常量）
- [ ] 单一职责
- [ ] 无敏感信息暴露
- [ ] ORM查询优化
- [ ] 测试覆盖充分

### 分层架构

- [ ] View无业务逻辑
- [ ] View调用Service，不直接调Client
- [ ] Service聚焦业务编排
- [ ] Service控制事务边界
- [ ] Client只做外部封装
- [ ] Model只含字段定义
- [ ] 无跨层调用
- [ ] 无循环依赖
- [ ] 缓存在事务外执行

## 附录

### 常用工具

| 用途 | 工具 |
|------|------|
| HTTP请求 | requests, httpx |
| 日期处理 | datetime, django.utils.timezone |
| 缓存 | django.core.cache |
| 任务队列 | Celery |
| WebSocket | Django Channels |
| K8s操作 | kubernetes |
| 阿里云SDK | alibabacloud-* |

### 推荐配置

```toml
[tool.black]
line-length = 88
target-version = ['py310']

[tool.ruff]
line-length = 88
target-version = "py310"
select = ["E", "F", "W", "I", "N", "B", "C4", "UP"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

---

**文档版本**: v2.3（nice压缩版）  
**最后更新**: 2026-03-05  
**维护人员**: 蜂群技术中心
