# Java工程编码规范

统一 Java 代码编写标准，涵盖命名、格式、异常处理、日志、并发编程等核心规则。

---

## 总体目标

| 目标 | 说明 |
|------|------|
| **一致性** | 代码风格统一，降低协作成本 |
| **可读性** | 命名清晰，新成员快速理解 |
| **可维护性** | 降低修改成本和缺陷风险 |
| **高质量** | 减少编码错误和性能问题 |

---

## 命名规范

### 包命名

| 规则 | 格式 | 示例 |
|------|------|------|
| 全部小写，`.`分隔 | `com.{公司}.{项目}.{模块}.{子模块}` | `com.fengqun.cart.service` |

### 类命名

- 使用 **大驼峰命名法(PascalCase)**
- 类名必须是**名词或名词短语**
- 禁止使用拼音、无意义缩写

#### 分层对象命名

| 层次 | 对象类型 | 后缀 | 示例 |
|------|---------|------|------|
| API层 | Dubbo服务接口 | `Service` | `CartService` |
| API层 | 请求DTO | `ReqDTO` | `ShoppingCartQueryReqDTO` |
| API层 | 响应DTO | `RespDTO` | `CartSkuInfoRespDTO` |
| API层 | 业务异常 | `BussinessException` | `CartBussinessException` |
| API层 | 业务枚举 | `Enum` 或 `Code` | `ShoppingCartTypeEnum`, `CartBussinessCode` |
| Service层 | 服务实现类 | `ServiceImpl` | `CartServiceImpl` |
| Service层 | 内部业务对象 | `BO` | `GetCartSkuInfoDTOListBO` |
| Service层 | 业务Service | `BizService` | `ShoppingCartBizService` |
| Manager层 | 通用业务处理 | `Manager` | `SlaveDbManager` |
| 数据访问层 | Mapper接口 | `Mapper` | `ShoppingCartMapper` |
| 数据访问层 | 实体对象 | 实体类名 | `ShoppingCart` |
| 缓存层 | 缓存类 | `Cache` | `UserShoppingCartCache` |
| 消息层 | 消息发送 | `Sender` | `OrderMessageSender` |
| 消息层 | 消息体 | `Msg` | `GroupPurchaseDataMsg` |
| 工具类 | 工具类 | `Utils` 或 `Util` | `ChannelUtils`, `NumberUtils` |

**强制要求**:
- **禁止在接口/响应体中暴露 `VO`、`DTO`、`BO` 等技术后缀**,应使用业务语义的名称。
  - ❌ 错误: `SkuResponseVO`、`PicResponseDTO`
  - ✅ 正确: `labelIds`、`picSources`

### 方法命名

- 使用 **小驼峰命名法(camelCase)**
- 方法名必须是**动词或动词短语**

#### 常用动词前缀

| 前缀 | 含义 | 示例 |
|------|------|------|
| `get` | 获取单个对象 | `getCartById()` |
| `query` | 查询数据(可能多条) | `queryCartSkus()` |
| `list` | 列表查询 | `listCartItems()` |
| `add` | 新增数据 | `addItemToCart()` |
| `update` | 更新数据 | `updateCartSku()` |
| `delete` / `remove` | 删除数据 | `deleteCartSku()`, `removeCartItem()` |
| `batch` | 批量操作 | `batchAddToCart()` |
| `check` | 校验逻辑 | `checkStock()`, `checkCanAddCart()` |
| `build` / `create` | 构建对象 | `buildShoppingCart()` |
| `convert` / `trans` | 转换对象 | `convertToDTO()` |
| `is` / `has` | 布尔判断 | `isNormalLive()`, `hasStock()` |

### 变量命名

- 使用 **小驼峰命名法**
- 禁止使用单字母（循环变量 `i`, `j`, `k` 除外）

| 类型 | 规则 | 示例 |
|------|------|------|
| **常量** | 全部大写，下划线分隔 | `DEFAULT_BIZ_SOURCE = "MALL"` |
| **成员变量** | 禁止 `m` 前缀 | `private Long userId;` |
| **局部变量** | 简洁有意义 | `Long skuId = reqDTO.getSkuId();` |

### 枚举命名

| 项 | 规则 | 示例 |
|----|------|------|
| 枚举类名 | `Enum` 后缀 | `ShoppingCartTypeEnum` |
| 枚举值 | 全部大写，下划线分隔 | `SHOPPING(1, "普通购物车")` |

---

## 代码格式规范

### 缩进与换行

| 规则 | 要求 |
|------|------|
| 缩进 | **4个空格**，禁止 Tab |
| 行长度 | 不超过 **120字符** |
| 参数换行 | 每个参数独占一行 |

```java
public void updateCartSku(
    Long userId,
    Long shopId,
    Long skuId,
    Integer skuNum
) {
    // ...
}
```

### 空格使用

| 场景 | 规则 |
|------|------|
| 运算符两侧 | 加空格：`a + b` |
| 逗号后 | 加空格：`foo(a, b)` |
| 关键字后 | 加空格：`if (condition)` |
| 方法名与括号 | 不加空格：`method()` |

### 大括号

- **强制使用大括号**，即使只有一行代码
- **左大括号不换行**

```java
// ❌ 错误
if (flag) return;

// ✅ 正确
if (flag) {
    return;
}
```

### 空行使用

| 场景 | 规则 |
|------|------|
| 逻辑块之间 | 加一空行 |
| 字段与方法间 | 加一空行 |
| 连续空行 | 最多保留一个 |

---

## 注释规范

### 类注释

必须包含：职责说明、作者、创建日期

```java
/**
 * 购物车服务实现类
 * 提供购物车增删改查、批量操作等功能
 * 
 * @author wei.dong
 * @date 2024-01-15
 */
@Service
public class CartServiceImpl implements CartService {
    // ...
}
```

### 方法注释

公共方法必须注释：职责、参数、返回值、异常

```java
/**
 * 更新购物车商品数量
 * 
 * @param reqDTO 更新请求参数
 * @throws CartBussinessException 库存不足或超出限购时抛出
 */
public void updateCartSku(ShoppingCartUpdateReqDTO reqDTO) throws CartBussinessException {
    // ...
}
```

### 行内注释

复杂逻辑必须注释业务背景或特殊处理原因

```java
// 兼容旧数据：前端可能不传购物车类型，默认为普通购物车
if (Objects.isNull(reqDTO.getCartType())) {
    reqDTO.setCartType(ShoppingCartTypeEnum.SHOPPING.getCode());
}
```

### TODO/FIXME标记

| 标记 | 用途 |
|------|------|
| `TODO` | 待实现的功能 |
| `FIXME` | 需要修复的问题 |

```java
// TODO: 后续支持多规格批量加购
// FIXME: 锁超时时间需根据压测调整
```

---

## 异常处理规范

### 异常分类

| 类型 | 用途 | 处理 |
|------|------|------|
| **业务异常** | 业务规则校验失败 | 继承 `BusinessException`，反馈给用户 |
| **系统异常** | 网络超时、数据库异常等 | 记录堆栈，返回通用错误提示 |

```java
public class CartBussinessException extends BusinessException {
    public CartBussinessException(CartBussinessCode code) {
        super();
        this.code = code.getCode();
        this.message = code.getDesc();
        this.analysis = "BE";
        this.locate = APPLICATION;
    }
}
```

### 异常抛出规范

| 规则 | 说明 |
|------|------|
| 方法签名声明 | 可能抛出业务异常必须在签名中声明 |
| 使用错误码 | 抛出异常必须传入业务错误码枚举 |

```java
public void updateCartSku(ShoppingCartUpdateReqDTO reqDTO) throws CartBussinessException {
    throw new CartBussinessException(CartBussinessCode.ADD_TO_CART_FAIL);
}
```

### 异常捕获规范

| 规则 | 说明 |
|------|------|
| 禁止空catch | 捕获后必须处理或记录日志 |
| 细粒度捕获 | 优先捕获具体异常类型 |

```java
// ❌ 错误
} catch (Exception e) {
    // 什么都不做
}

// ✅ 正确
} catch (Exception e) {
    log.error("调用失败, param={}", param, e);
    throw new CartBussinessException(CartBussinessCode.ADD_TO_CART_FAIL);
}
```

### 异常传递规范

- 跨服务异常传递：保留 `code`、`message`、`locate` 信息
- 异常转换：必要时将底层异常转换为业务异常

```java
try {
    stockMallService.checkStock(skuId, num);
} catch (Exception e) {
    throw new CartBussinessException(CartBussinessCode.STOCK_SELL_OUT);
}
```

---

## 日志规范

### 日志框架

统一使用 `MyLogger`（基于 Log4j2 封装）

```java
private static final MyLogger log = LogFactory.getLogger(CartServiceImpl.class);
```

### 日志级别

| 级别 | 用途 | 场景 |
|------|------|------|
| `info` | 关键业务流程 | 接口入参、核心业务节点 |
| `warn` | 需警惕但不影响业务 | 降级逻辑、参数异常 |
| `error` | 需要立即修复 | 异常堆栈、数据不一致 |

### 日志内容规范

| 类型 | 规则 | 示例 |
|------|------|------|
| 入参日志 | 必须记录接口入口参数 | `log.info("param={}", JSON.toJSONString(reqDTO))` |
| 异常日志 | 必须包含堆栈 | `log.error("异常, userId={}", userId, e)` |
| 关键节点 | 记录数据变更 | `log.info("加购成功, userId={}, skuId={}", userId, skuId)` |

### 日志禁忌

| 禁忌 | 说明 |
|------|------|
| ❌ `System.out.println` | 必须使用日志框架 |
| ❌ 循环中打日志 | 避免日志量暴增，改为批量记录 |
| ❌ 记录敏感信息 | 密码、手机号等需脱敏 |

```java
// ❌ 错误
for (ShoppingCart cart : cartList) {
    log.info("cart={}", cart);
}

// ✅ 正确
log.info("购物车列表, size={}, cartList={}", cartList.size(), JSON.toJSONString(cartList));
```

---

## 对象设计与分层规范

### 分层职责

| 层次 | 职责 | 禁止行为 |
|------|------|---------|
| **API层** | 定义接口、DTO、异常、枚举 | 禁止包含业务逻辑 |
| **Service层** | 核心业务逻辑、事务控制 | 禁止直接操作数据库 |
| **Manager层** | 通用业务封装、外部服务调用 | 禁止包含具体业务规则 |
| **Mapper层** | 数据访问 | 禁止包含业务逻辑 |
| **Cache层** | 缓存读写 | 禁止包含复杂业务逻辑 |

### 对象转换规范

| 转换 | 所在层 |
|------|--------|
| VO → DTO | Controller层 |
| DTO → BO | Service层 |
| BO → PO | Manager/Mapper层 |

⚠️ **禁止跨层传递**：不允许将 `PO` 直接返回到 Controller

### DTO设计规范

**请求DTO**：必须继承基类或实现校验注解

```java
@Data
public class ShoppingCartUpdateReqDTO {
    @NotNull(message = "用户ID不能为空")
    private Long userId;
    
    @NotNull(message = "商品ID不能为空")
    private Long skuId;
    
    @Min(value = 1, message = "商品数量至少为1")
    private Integer skuNum;
}
```

**响应DTO**：只包含当前场景需要的字段，避免冗余数据

---

## 并发编程规范

### 线程池使用

- ❌ **禁止直接使用 `Executors`**，必须使用 `MyThreadPool`
- 线程池必须指定有意义的名称

```java
private final MyThreadPool executorService = new MyThreadPool(
    8, 16, 60, "cart-async-pool"
);
```

### 异步任务规范

必须处理异步任务抛出的异常

```java
try {
    executorService.submit2(() -> {
        customerActionReportService.report(msg);
    });
} catch (MyThreadPool.ThreadPoolFullException e) {
    log.warn("线程池已满, msg={}", msg);
}
```

### 分布式锁规范

| 规则 | 说明 |
|------|------|
| 必须设置超时 | 避免死锁 |
| 必须释放锁 | 在 `finally` 块中释放 |

```java
String lockKey = String.format("cart:%s:%s:%s", userId, shopId, skuId);
Lock lock = myRedis.getLock(lockKey);
boolean flag = lock.tryLock(2000, 10000);
if (!flag) {
    throw new CartBussinessException(CartBussinessCode.ADD_TO_CART_FAIL);
}
try {
    // 业务逻辑
} finally {
    lock.unLock();
}
```

### CompletableFuture使用

推荐用于 IO 密集型任务，如并行调用多个 RPC 服务

```java
CompletableFuture<UserRespDTO> userFuture = CompletableFuture.supplyAsync(() -> 
    userService.getUserById(userId)
);
CompletableFuture<StockRespDTO> stockFuture = CompletableFuture.supplyAsync(() -> 
    stockService.getStock(skuId)
);
CompletableFuture.allOf(userFuture, stockFuture).join();
```

---

## 集合与Stream规范

### 集合初始化

能预估大小时，必须指定初始容量

```java
List<Long> skuIds = new ArrayList<>(cartList.size());
Map<Long, ShoppingCart> cartMap = new HashMap<>(16);
```

### 集合判空

推荐使用工具类 `CollUtil.isEmpty()`

```java
if (CollUtil.isEmpty(cartList)) {
    return Collections.emptyList();
}
```

### Stream使用

| 规则 | 说明 |
|------|------|
| 避免过度嵌套 | Stream 嵌套不超过 3 层 |
| 禁止修改外部变量 | 违反函数式编程原则 |

```java
// ❌ 错误
int count = 0;
list.stream().forEach(item -> count++);

// ✅ 正确
long count = list.stream().count();
```

---

## 性能优化规范

### 避免循环中调用RPC

将循环内的单次 RPC 调用改为批量调用

```java
// ❌ 错误
for (Long skuId : skuIds) {
    SkuDetail detail = goodsService.getSkuDetail(skuId);
}

// ✅ 正确
List<SkuDetail> details = goodsService.batchGetSkuDetails(skuIds);
```

### 避免循环中查数据库

使用 `IN` 查询或 MyBatis-Plus 的批量方法

### 合理使用缓存

- 热点数据必须使用缓存，减轻数据库压力
- 缓存更新采用失效策略，而非主动更新

---

## 安全编码规范

### SQL注入防护

❌ **禁止拼接 SQL**，必须使用预编译（MyBatis 的 `#{}`）

```java
// ❌ 错误
String sql = "SELECT * FROM cart WHERE user_id = " + userId;

// ✅ 正确
@Select("SELECT * FROM cart WHERE user_id = #{userId}")
List<ShoppingCart> selectByUserId(Long userId);
```

### 参数校验

入口参数必须使用 JSR-303 注解或手动校验

```java
Assert.notNull(reqDTO.getUserId(), "用户ID不能为空");
Assert.notNull(reqDTO.getSkuId(), "商品ID不能为空");
```

### 敏感信息处理

- 日志中禁止记录密码、手机号等敏感信息
- 敏感数据必须加密传输

---

## 其他最佳实践

### 魔法值

❌ **禁止硬编码**，所有魔法值必须定义为常量或枚举

```java
// ❌ 错误
if (status == 1) { ... }

// ✅ 正确
if (ShoppingCartTypeEnum.SHOPPING.getCode().equals(status)) { ... }
```

### 空指针防护

| 方式 | 示例 |
|------|------|
| Optional | `Optional.ofNullable(cart).map(...).orElse(0L)` |
| Objects.nonNull | `if (Objects.nonNull(cart) && ...)` |

### 重复代码

- 重复逻辑必须提取为私有方法或工具类
- 使用设计模式（策略模式、模板方法模式）消除重复

---

## 代码评审检查点

| 检查项 | 说明 |
|--------|------|
| 命名规范 | 类、方法、变量命名是否符合规范 |
| 注释 | 类、方法、复杂逻辑是否有注释 |
| 异常处理 | 捕获、抛出、日志是否完善 |
| 日志 | 入参、异常、业务节点是否记录 |
| 性能 | 是否存在循环中调用 RPC/数据库 |
| 安全 | 是否有 SQL 注入、空指针、魔法值风险 |
| 并发 | 并发场景是否加锁 |
| 资源 | 锁、连接、流是否正确释放 |

---

## MyBatis Plus 实践规范

### 条件构造器使用

| 规则 | 说明 |
|------|------|
| 优先使用 LambdaQuery | `LambdaQueryWrapper` 确保类型安全 |
| 空值安全检查 | 使用 `eqIfPresent` 等方法避免 null 参数 |

```java
// ❌ 错误
new QueryWrapper<ShoppingCart>().eq("user_id", userId);

// ✅ 正确
new LambdaQueryWrapper<ShoppingCart>().eq(ShoppingCart::getUserId, userId);
```

### Mapper 与 Service 职责

| 规则 | 说明 |
|------|------|
| BaseMapper 继承 | 所有 Mapper 必须继承 `BaseMapper<T>`，禁止简单 CRUD 手写 XML |
| Repository 层组合 | 推荐继承 `ServiceImpl` 并注入 `Mapper`，解耦数据访问逻辑 |

```java
public interface ShoppingCartMapper extends BaseMapper<ShoppingCart> {
    // 仅在复杂查询场景下扩展自定义方法
}
```

---

## 附录

### 常用工具类

| 工具类 | 用途 |
|--------|------|
| `CollUtil` | 集合工具 |
| `StringUtils` | 字符串工具 |
| `Objects` | 对象判空、比较 |
| `JSONUtil` | JSON 序列化/反序列化 |
| `Assert` | 参数断言 |
| `BeanUtil` | 对象拷贝 |

### 常用注解

| 注解 | 用途 |
|------|------|
| `@Service` | 标记 Service 实现类 |
| `@DubboService` | 暴露 Dubbo 服务 |
| `@DubboReference` | 引用 Dubbo 服务 |
| `@Autowired` | 依赖注入 |
| `@Transactional` | 事务控制 |
| `@Data` | Lombok 生成 getter/setter |
| `@Slf4j` | Lombok 生成日志对象 |

---

**文档版本**: v1.1  
**最后更新**: 2026-03-04  
**维护人员**: 蜂群技术中心
