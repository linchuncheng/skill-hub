# Flutter工程编码规范

## 项目环境

| 项目 | 版本 |
|------|------|
| Flutter | 3.7.12（stable） |
| 引擎 | 1a65d409c7 |
| Dart | 2.19.6 |
| DevTools | 2.20.1 |

审查涉及版本相关 API 时，应以上述版本组合为准。

---

## 项目架构

### 模块划分

```
lib/
├── common/          # 公共组件（弹窗、WebView、扫码等）
├── enum/            # 全局枚举定义
├── logic/           # 业务逻辑层
├── login/           # 登录模块
├── model/           # 数据模型
├── module/          # 业务功能模块
├── router/          # 路由配置
├── store/           # 全局状态存储
├── utils/           # 工具类
├── widget/          # 公共 Widget
├── main.dart        # 入口文件
└── page_index.dart  # 统一导出文件
```

### 模块依赖原则

| 层级 | 依赖方向 | 说明 |
|------|----------|------|
| module_business | → module_common | 业务模块依赖公共模块 |
| module_common | → common | 公共模块依赖基础库 |
| lib | → module_*/common | 主工程依赖所有模块 |

⚠️ 禁止循环依赖，禁止跨层级依赖

---

## 命名规范

| 类型 | 规则 | 示例 |
|------|------|------|
| 文件名 | snake_case，小写英文加下划线 | `constant.dart`、`icon_logo.png` |
| 类名 | PascalCase，大驼峰 | `CommonAppBar`、`CommonTabBarWidget` |
| 函数/变量/参数 | lowerCamelCase，小驼峰 | `getCommonAppBar()`、`userName` |
| 私有变量 | 以下划线 `_` 开头 | `_userName` |
| 文件夹名 | 全部小写，无下划线 | `page`、`model`、`netConnect` |
| 常量 | lowerCamelCase 或 UPPER_CASE | `colorPrimary`、`MAX_COUNT` |
| 枚举值 | camelCase | `VideoPlayRate.onePointFive` |

**文件名注意事项**：
- 单个关键词不加下划线
- 关键词数量建议不超过 4 个

**目录结构**：按功能分子目录，保持清晰，避免过深嵌套（建议不超过 4 层）

---

## Widget 开发规范

| 原则 | 要求 |
|------|------|
| 结构清晰 | 避免多层嵌套 Widget 写在同一方法；按区域/职责拆分；单个方法不超过 **100 行** |
| 代码复用 | 复杂/可复用 Widget 封装为独立组件，避免复制粘贴 |
| build 职责 | 少量代码组织整体结构；复杂组合拆分到私有方法如 `_buildHeader()`、`_buildBody()` |
| 通用组件 | 封装常用 UI 元素：通用弹窗、`CommonAppBar`、`CommonTabBarWidget` 等 |

### StatelessWidget vs StatefulWidget

| 场景 | 选择 |
|------|------|
| 纯展示、无内部状态 | StatelessWidget |
| 需要动画控制器、焦点管理等 | StatefulWidget |
| 需要响应式状态更新 | 结合状态管理框架的 StatelessWidget |

### const 构造函数

优先使用 `const` 构造函数提升性能：

```dart
// 推荐
class MyWidget extends StatelessWidget {
  const MyWidget({super.key, required this.title});
  
  final String title;
  
  @override
  Widget build(BuildContext context) {
    return Text(title);
  }
}

// 使用时
const MyWidget(title: 'Hello'),
```

---

## 状态管理规范

### GetX 使用规范

项目使用 GetX 作为主要状态管理方案。

| 场景 | 推荐方式 |
|------|----------|
| 页面状态 | `GetxController` + `Obx` 响应式更新 |
| 简单状态 | `Rx<T>` 类型变量（`RxInt`、`RxString`、`RxBool` 等） |
| 复杂状态 | 自定义 Controller 继承 `GetxController` |

**Controller 定义示例**：
```dart
class MyController extends GetxController {
  final count = 0.obs;
  final userName = ''.obs;
  
  void increment() {
    count.value++;
  }
  
  @override
  void onClose() {
    // 释放资源（非 Rx 类型）
    super.onClose();
  }
}
```

**页面使用示例**：
```dart
class MyPage extends StatelessWidget {
  final controller = Get.put(MyController());
  
  @override
  Widget build(BuildContext context) {
    return Obx(() => Text('${controller.count.value}'));
  }
}
```

### 生命周期管理

项目提供 `BaseLifeState` 基类，提供完整的生命周期回调：

| 方法 | 触发时机 | 对标 Android/iOS |
|------|----------|------------------|
| `onWillCreate` | initState 中，context 不可用 | - |
| `onCreate` | 首帧绘制完毕 | onCreate/viewDidLoad |
| `onStart` | 页面可见 | onStart/viewWillAppear |
| `onResumed` | 页面获得焦点 | onResume/viewDidAppear |
| `onPause` | 页面失去焦点 | onPause/viewWillDisappear |
| `onStop` | 页面不可见 | onStop/viewDidDisappear |
| `onDestroy` | dispose 前 | onDestroy/deinit |

---

## 路由管理规范

### 路由定义

路由 URL 统一定义在 `FlutterRouterUrl` 类中：

```dart
class FlutterRouterUrl {
  static const String HOME = '/home';
  static const String GOODS_DETAIL = '/goods/detail';
  // ...
}
```

### 路由注册

在 `NavigatorUtils.initRouter()` 中注册路由：

```dart
'${FlutterRouterUrl.GOODS_DETAIL}': withPage(() => GoodsDetailPage()),
```

### 页面跳转方式

| 方式 | 方法 | 使用场景 |
|------|------|----------|
| 普通跳转 | `Navigator.pushNamed(context, routeName)` | 原生 Flutter 跳转 |
| 带参数跳转 | `Navigator.pushNamed(context, routeName, arguments: data)` | 需要传参 |
| 替换当前页 | `Navigator.pushReplacementNamed(context, routeName)` | 登录后跳转首页 |
| 清空栈跳转 | `Navigator.of(context).pushAndRemoveUntil(...)` | 退出登录 |
| FlutterBoost | `BoostNavigator.instance.push(routeName)` | 混合栈跳转 |

### 参数传递

```dart
// 传递参数
Navigator.pushNamed(context, FlutterRouterUrl.GOODS_DETAIL, 
  arguments: {'goodsId': '123'});

// 接收参数
@override
void initState() {
  super.initState();
  final args = ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;
  final goodsId = args?['goodsId'];
}
```

---

## 数据模型规范

### Model 定义

项目支持两种 JSON 序列化方式：

| 方式 | 适用场景 | 特点 |
|------|----------|------|
| `json_annotation` | 新增 Model | 自动生成代码，类型安全 |
| 手写 `fromJson/toJson` | 简单 Model | 灵活可控 |

**推荐使用 `json_annotation`**：

```dart
import 'package:json_annotation/json_annotation.dart';
part 'user_entity.g.dart';

@JsonSerializable()
class UserEntity {
  @JsonKey(name: 'user_id')  // 字段映射
  final int userId;
  
  final String? nickname;  // 可空字段
  
  @JsonKey(defaultValue: 0)  // 默认值
  final int age;
  
  UserEntity({
    required this.userId,
    this.nickname,
    this.age = 0,
  });
  
  factory UserEntity.fromJson(Map<String, dynamic> json) =>
      _$UserEntityFromJson(json);
  
  Map<String, dynamic> toJson() => _$UserEntityToJson(this);
}
```

### 命名约定

| 类型 | 命名后缀 | 示例 |
|------|----------|------|
| 接口响应实体 | Entity | `UserEntity` |
| 请求数据模型 | Request | `LoginRequest` |
| 业务数据模型 | Bean/Model | `OrderBean` |

---

## 枚举规范

### 枚举定义

为枚举值添加注释说明业务含义：

```dart
/// 视频播放倍速
enum VideoPlayRate {
  three,        // 3 倍速
  two,          // 2 倍速
  onePointFive, // 1.5 倍速
  one,          // 正常速度
  pointFive,    // 0.5 倍速
}
```

### 枚举扩展

使用 `extension` 为枚举添加功能：

```dart
extension VideoPlayRateExt on VideoPlayRate {
  String get displayText {
    switch (this) {
      case VideoPlayRate.three:
        return '3';
      case VideoPlayRate.two:
        return '2';
      // ...
    }
  }
  
  double get value {
    switch (this) {
      case VideoPlayRate.three:
        return 3.0;
      case VideoPlayRate.two:
        return 2.0;
      // ...
    }
  }
}
```

### 增强枚举（Dart 2.17+）

支持带属性的枚举定义：

```dart
enum ScanFromType {
  verify(value: 'verify', emptyTip: '扫码失败，请确认核销码是否正确'),
  payment(value: 'payment', emptyTip: '扫码失败，请确认支付码是否正确');

  final String value;
  final String emptyTip;
  
  const ScanFromType({required this.value, required this.emptyTip});
}
```

---

## 扩展方法规范

项目已封装常用扩展方法，优先使用现有扩展：

### 空值判断扩展

```dart
// num 扩展
int? value;
if (value.isNotEmpty) { /* value != null && value != 0 */ }
if (value.isEmpty) { /* value == null || value == 0 */ }

// String? 扩展
String? name;
if (name.isNotEmptyPlus) { /* name != null && name.trim().isNotEmpty */ }
if (name.isEmptyPlus) { /* name == null || name.trim().isEmpty */ }

// List? 扩展
List<int>? list;
if (list.isNotEmptyPlus) { /* list != null && list.isNotEmpty */ }
if (list.isEmptyPlus) { /* list == null || list.isEmpty */ }
```

### 自定义扩展规范

```dart
extension DurationExt on Duration {
  /// 格式化为 hh:mm:ss 格式
  String get hhmmss {
    // 实现逻辑
  }
}

extension ListExt on List {
  /// 在列表元素间插入分隔符
  List<T> divide<T>(T divider, {bool addBefore = false, bool addAfter = false}) {
    // 实现逻辑
  }
}
```

---

## 其他代码规范

### 命名与注释

| 规则 | 要求 |
|------|------|
| 拒绝弱命名 | ❌ `a`、`b`、`c`；✅ `commentCount`、`likeCount` |
| 枚举注释 | 为每个值添加注释，说明业务含义和使用场景 |
| 代码注释 | 关键逻辑、复杂算法编写简明注释 |
| 文档注释 | 使用 `///` 与 `[]` 引用类名/变量名，如 `/// - [int]: [myString] 的长度。` |

### 代码风格与格式

| 规则 | 要求 |
|------|------|
| 代码格式化 | 统一使用 IDE `dartfmt` / "Reformat Code"，禁止个人随意风格 |
| 换行规则 | 函数间适当空行；长表达式/方法调用适当换行 |
| if-else | 业务逻辑必须使用 `{}`，`else` 与 `}` 同行（Widget 构建除外） |
| 条件运算符 | 短表达式一行；长表达式按逻辑换行 |

**if-else 示例**：
```dart
if (condition) {
  doSomething();
} else {
  doOther();
}
```

### 开发实践

| 规则 | 要求 |
|------|------|
| 拒绝硬编码 | ❌ `if (status == 1)`；✅ 使用常量/枚举/`static const` |
| 资源管理 | 组件创建的资源在 `dispose()` 中释放；清理无效资源文件及 `pubspec.yaml` 声明 |
| 常量管理 | 颜色、间距、字号等集中管理，使用 `static const` |
| 日志规范 | ❌ 生产环境使用 `print`；✅ 使用项目统一封装的日志方法 |
| 错误处理 | 及时处理 Dart Analysis 的错误与警告 |

---

## 常量管理规范

### 颜色常量

统一在 `MyColors` 类中定义：

```dart
class MyColors {
  // 主题色
  static const Color COLOR_00B68F = Color(0xff00B68F);
  
  // 文字颜色
  static const Color COLOR_333333 = Color(0xff333333);  // 主文字
  static const Color COLOR_666666 = Color(0xff666666);  // 次文字
  static const Color COLOR_999999 = Color(0xff999999);  // 辅助文字
  
  // 背景色
  static const Color COLOR_F5F5F5 = Color(0xfff5f5f5);  // 页面背景
}
```

### 尺寸常量

统一在 `Dimens` 类中定义：

```dart
class Dimens {
  static const double fontSp12 = 12;
  static const double fontSp14 = 14;
  static const double fontSp16 = 16;
  
  static const double gapDp8 = 8;
  static const double gapDp12 = 12;
  static const double gapDp16 = 16;
}
```

---

## 性能优化规范

### Widget 优化

| 规则 | 说明 |
|------|------|
| 避免 rebuild | 使用 `const` 构造函数；合理使用 `Obx` 局部刷新 |
| 列表优化 | 使用 `ListView.builder` 替代 `Column` + `List<Widget>` |
| 图片优化 | 使用 `CachedNetworkImage` 缓存网络图片；指定 `cacheWidth/cacheHeight` |
| 动画优化 | 使用 `AnimatedBuilder` 而非 `setState`；复用 `AnimationController` |

### 内存管理

| 场景 | 处理方式 |
|------|----------|
| AnimationController | `dispose()` 中调用 `controller.dispose()` |
| TextEditingController | `dispose()` 中调用 `controller.dispose()` |
| ScrollController | `dispose()` 中调用 `controller.dispose()` |
| StreamSubscription | `dispose()` 中调用 `subscription.cancel()` |
| Timer | `dispose()` 中调用 `timer.cancel()` |

---

## 审查额外规则

### 资源释放责任边界

以下场景 **不需要** 释放资源，**不应** 报告未调用 `dispose()`：

| 场景 | 说明 |
|------|------|
| 父组件传入 | 通过构造函数或其他方式传入的资源 |
| 依赖注入 | `Get.find()`、`Provider.of()` 等 DI 方式获取 |
| 全局管理 | 全局单例或全局管理器统一管理的资源 |

⚠️ 仅当组件 **自己创建并持有** 的资源，才需在 `dispose()` 中释放

### Widget 内单行 if-else 大括号豁免

| 适用场景 | 说明 |
|----------|------|
| ✅ 豁免 | `build` 方法中，`if` 仅包裹单个 Widget 用于 UI 构建 |
| ❌ 不豁免 | 业务逻辑、数据处理、控制流程代码 |

### 忽略未使用的代码/方法

以下情况未引用的代码可视为合理存在：

| 情况 | 说明 |
|------|------|
| 框架模板 | 脚手架生成的预留方法 |
| 扩展预留 | 明确用于后续扩展的方法或类 |
| 调试工具 | 条件编译控制的辅助方法或调试代码 |

### GetX 框架 Rx 对象的资源释放

| 对象类型 | 处理方式 |
|----------|----------|
| `RxInt`、`RxList`、`Rxn<T>` 等 | GetX 自动管理生命周期，**不需要** 显式调用 `close()`/`dispose()` |

⚠️ 审查时 **不应** 因 Rx 对象未手动释放而报错

### 已封装扩展方法的使用

项目已封装以下扩展方法：

```dart
extension ExNum on num? {
  bool get isEmpty => this == null || this == 0;
  bool get isNotEmpty => !isEmpty;
}

extension ExListN<E> on List<E>? {
  bool get isEmptyPlus => this == null || this!.isEmpty;
  bool get isNotEmptyPlus => !isEmptyPlus;
}

extension ExStringNull on String? {
  bool get isEmptyPlus => this == null || this!.trim().isEmpty;
  bool get isNotEmptyPlus => !isEmptyPlus;
}
```

**使用示例**：
```dart
int? value;
if (value.isNotEmpty || value.isEmpty) {
  // ...
}
```

✅ 上述写法 **合法且被允许**，审查时不应标记为错误

---

## 异常处理规范

### 异常捕获

```dart
try {
  final result = await fetchData();
} on NetworkException catch (e) {
  // 特定异常处理
  showErrorToast(e.message);
} on FormatException catch (e) {
  // 格式异常处理
  showErrorToast('数据格式错误');
} catch (e) {
  // 兜底异常处理
  showErrorToast('未知错误');
} finally {
  // 清理工作
  hideLoading();
}
```

### 异常处理原则

| 原则 | 说明 |
|------|------|
| 不吞异常 | 避免 `catch (e) {}` 空处理，至少记录日志 |
| 用户友好 | 异常信息转化为用户可理解的提示 |
| 区分类型 | 针对不同异常类型采取不同处理策略 |
| 记录日志 | 关键异常记录到日志系统，便于排查 |

---

## 安全规范

### 敏感数据处理

| 规则 | 要求 |
|------|------|
| 密码/Token | 禁止明文存储，使用安全存储方案 |
| 日志脱敏 | 禁止在日志中输出用户敏感信息 |
| HTTPS | 网络请求必须使用 HTTPS |

### 代码安全

| 规则 | 要求 |
|------|------|
| 输入校验 | 对用户输入进行合法性校验 |
| 权限最小化 | 仅申请必要的权限 |
| WebView 安全 | 禁用不必要的 JavaScript 接口 |

---

## 参考资料

| 资源 | 链接 |
|------|------|
| Effective Dart | https://dart.dev/guides/language/effective-dart |
| Flutter 官方文档 | https://flutter.dev/docs |
| GetX 文档 | https://github.com/jonataslaw/getx |
| Dart 代码风格 | https://github.com/dart-lang/linter |