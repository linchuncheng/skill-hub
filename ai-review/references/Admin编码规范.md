# Admin工程编码规范

中后台前端代码开发规范与标准。

## 文件头注释

| 要求 | 说明 |
|------|------|
| 格式 | `/** ... */` |
| 必填 | `@Owners`（所有者）、`@Title`（标题/描述） |
| 可选 | `@Details`（详细信息） |

```typescript
/**
 * @Owners liyuanchuan
 * @Title 营销公司管理 => 服务公司管理
 */
```

**常见问题**：❌ 缺少文件头注释、❌ 字段缺失、❌ 格式不正确

---

## TypeScript 类型规范

| 规则 | 要求 |
|------|------|
| 禁止 `any` | 使用具体类型或 `unknown`；如需使用，通过 `fixToUnknown: true` 修复 |
| 禁止非空断言 `!` | 使用类型守卫或可选链操作符 |
| 访问修饰符 | 类成员必须显式声明 `public`/`private`/`protected` |
| 类型定义位置 | 通用类型在 `@types/declares`，文件名以 `d` 开头 |
| 命名空间 | 使用 `dFetch.TypeName` 方式组织 |
| 类型内容 | 只定义类型，不声明实际值 |

```typescript
// ✅ 正确
type Props = Caibird.dFetch.Api['AccountManage']['queryPage']['rsp']['list'][number];
type State = { visible: boolean };

// ❌ 错误
type Props = any;              // 禁止 any
const data: string! = value;   // 禁止非空断言
```

---

## 代码风格规范

| 规则 | 要求 |
|------|------|
| 缩进 | 4 个空格，禁止 Tab |
| 分号 | 必须使用 |
| 逗号 | 多行对象/数组末尾必须有逗号 |
| 换行符 | LF（Unix 风格） |
| 函数空格 | 匿名函数 `function ()`、命名函数 `function name()`、箭头函数 `() =>` |
| 对象简写 | 使用 `{ name }` 而非 `{ name: name }` |

```typescript
// ✅ 正确
const obj = { name: 'test', age: 18 };
const fn = function () { return true; };

// ❌ 错误
const obj = { name: 'test', age: 18 };  // 缺少末尾逗号
```

---

## React 组件规范

| 规则 | 要求 |
|------|------|
| 布尔值属性 | `<Component disabled />` 而非 `disabled={true}` |
| 自闭合标签 | `<Component />` 而非 `<Component></Component>` |
| 字符串 refs | ❌ 禁止，使用 `React.createRef()` 或回调 ref |
| key 属性 | 列表渲染必须提供唯一 `key` |
| 组件导出 | 公共组件在 `@components/index.ts` 导出；同时导出自身和默认导出；使用路径别名 `fq-ecmiddle-sys-web-components` |

```typescript
// ✅ 正确
export class MyComponent extends React.Component<Props, State> {
    public render() {
        return <div>{list.map(item => <Item key={item.id} disabled />)}</div>;
    }
}
export default MyComponent;

// ❌ 错误
{list.map(item => <Item disabled={true}></Item>)}  // 缺 key，布尔值错误，未自闭合
```

---

## 导入导出规范

| 规则 | 要求 |
|------|------|
| 模块限制 | `web` 与 `server` 互不可导入；禁止 `**/_config` 和 `**/@common/*` |
| 路径别名 | `fq-ecmiddle-sys-web-components` / `helpers` / `utils` / `consts` / `enums` |
| 导入顺序 | 第三方库 → 项目内部（按别名分组）→ 相对路径 |

```typescript
// ✅ 正确
import { Button, Input } from 'antd';
import { ATablePage } from 'fq-ecmiddle-sys-web-components';
import { hRequest } from 'fq-ecmiddle-sys-web-helpers';

// ❌ 错误
import { hRequest } from 'fq-ecmiddle-sys-server-helpers';  // web 不能导入 server
import { ATablePage } from '../../@components';            // 应使用路径别名
```

---

## 代码质量规范

| 规则 | 要求 |
|------|------|
| `console.log` | 生产代码避免使用，使用 `hReport` |
| `debugger` | ❌ 禁止 |
| 变量声明 | 优先 `const`，需重新赋值用 `let`，❌ 禁止 `var` |
| 箭头函数 | 优先使用 |
| 相等比较 | 使用 `===`/`!==`，特殊情况可用 `==` |
| 位运算 | ❌ 禁止 `&`、`|`、`^` |

```typescript
// ✅ 正确
const data = []; let count = 0;
const fn = () => {};
if (value === null) {}

// ❌ 错误
var data = [];            // 禁止 var
const fn = function() {}; // 应使用箭头函数
if (value == null) {}     // 应使用 ===
const result = a & b;     // 禁止位运算
```

---

## 异步处理规范

| 规则 | 要求 |
|------|------|
| Promise | 禁止在 executor 中使用 async |
| await | 避免在循环中使用（除非必要） |
| 错误处理 | 异步操作必须有 `try-catch` 或 `.catch()` |

```typescript
// ✅ 正确
const fetchData = async () => {
    try {
        const rsp = await hRequest.api.AccountManage.queryPage({});
        return rsp;
    } catch (error) {
        hPrompt.error('获取数据失败');
        throw error;
    }
};

// ❌ 错误
const fetchData = async () => {
    const rsp = await hRequest.api.AccountManage.queryPage({});  // 缺少错误处理
    return rsp;
};
```

---

## 组件结构规范

| 规则 | 要求 |
|------|------|
| 继承 | `AComponent` 或 `React.Component` |
| 泛型 | 定义 `Props` 和 `State` |
| 访问修饰符 | `public`（对外）、`protected`（子类）、`private`（私有） |
| 方法命名 | 事件处理 `onXxx`/`handleXxx`、数据获取 `getXxx`、数据设置 `setXxx` |

```typescript
class MyComponent extends ATablePage<Props, State, DataItem, ToolValue> {
    public constructor(props: Props) {
        super(props);
        this.initState({ visible: false });
    }

    protected readonly getDataSource = async () => { /* ... */ };

    public render() { /* ... */ }
}
```

---

## 类型定义规范

| 规则 | 要求 |
|------|------|
| 通用类型 | `@types/declares` 目录，文件名以 `d` 开头 |
| 第三方扩展 | `@types/extend` 目录 |
| 模块内部 | 直接在模块内定义 |
| 命名空间 | 使用 `dNamespace.TypeName` 方式调用 |
| 内容限制 | 只定义类型，不包含实际值 |

```typescript
// dFetch.d.ts
declare namespace dFetch {
    namespace Api {
        namespace AccountManage {
            namespace queryPage {
                type Req = { page: number; userName: string };
                type Rsp = { list: DataItem[]; pageCount: number };
            }
        }
    }
}

// 组件中使用
type DataItem = Caibird.dFetch.Api['AccountManage']['queryPage']['rsp']['list'][number];
```

---

## 请求处理规范

| 规则 | 说明 |
|------|------|
| 请求方式 | `hRequest.api.ControllerName.ActionName(req, options)` |
| 类型映射 | 参数和返回值类型自动映射 |

**请求选项**：

| 选项 | 说明 |
|------|------|
| `noHandle` | 返回原始回包 |
| `timeout` | 超时时间 |
| `contentType` | 内容类型（默认 json） |
| `isFormRequest` | 是否表单请求 |
| `type` | 请求类型（默认 POST） |
| `noReportError` | 不记录异常日志 |

```typescript
// ✅ 正确
const rsp = await hRequest.api.AccountManage.queryPage({
    page: pagination.current,
    userName: initFormValue.userName,
});

// ❌ 错误
const rsp = await fetch('/api/accountManage/queryPage', {  // 应使用 hRequest
    method: 'POST',
    body: JSON.stringify({}),
});
```

---

## 异常处理规范

| 规则 | 说明 |
|------|------|
| 异常类型 | 使用 `cError` 中定义的类型 |
| 常用方式 | `cError.Common('消息')` 抛出异常；`cError.Noop` 中断逻辑但不处理 |
| 全局处理 | 未处理异常收敛到 `onAppError` |

```typescript
import { cError } from 'fq-ecmiddle-sys-web-consts';

if (!data) {
    throw cError.Common('数据不存在');
}
```

---

## 参考资源

| 资源 | 路径 |
|------|------|
| 项目 README | `../README.md` |
| ESLint 配置 | `../.eslintrc.json` |
| TypeScript 配置 | `../tsconfig.json` |
