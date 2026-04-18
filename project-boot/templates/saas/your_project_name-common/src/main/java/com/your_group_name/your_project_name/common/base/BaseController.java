package com.your_group_name.your_project_name.common.base;

import com.your_group_name.your_project_name.common.response.PageData;
import com.your_group_name.your_project_name.common.response.R;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 基础 Controller。
 *
 * 所有业务 Controller 都应继承此类，获得：
 * - 标准日志支持
 * - 统一的异常处理（由全局异常处理器处理）
 * - 统一的响应格式
 *
 * 示例：
 * 
 * <pre>
 * @RestController
 * &#64;RequestMapping("/api/users")
 * public class UserController extends BaseController {
 *     public R&lt;User&gt; getUser(Long id) {
 *         getLogger().info("获取用户");
 *         User user = userService.getById(id);
 *         return success(user);
 *     }
 * }
 * </pre>
 */
@RestController
public abstract class BaseController {
    private final Logger logger = LoggerFactory.getLogger(this.getClass());

    /**
     * 获取当前 Controller 的 Logger。
     *
     * @return Logger 实例
     */
    protected Logger getLogger() {
        return logger;
    }

    /**
     * 返回成功响应（带数据）。
     *
     * @param data 响应数据
     * @param <T>  数据类型
     * @return 成功响应
     */
    protected <T> R<T> success(T data) {
        return R.ok(data);
    }

    /**
     * 返回成功响应（带数据和自定义消息）。
     *
     * @param data    响应数据
     * @param message 自定义消息
     * @param <T>     数据类型
     * @return 成功响应
     */
    protected <T> R<T> success(T data, String message) {
        return R.ok(data, message);
    }

    /**
     * 返回成功响应（无数据）。
     *
     * @param <T> 数据类型
     * @return 成功响应
     */
    protected <T> R<T> success() {
        return R.ok();
    }

    /**
     * 返回失败响应（使用默认失败消息）。
     *
     * @param <T> 数据类型
     * @return 失败响应
     */
    protected <T> R<T> fail() {
        return R.fail();
    }

    /**
     * 返回失败响应。
     *
     * @param message 错误消息
     * @param <T>     数据类型
     * @return 失败响应
     */
    protected <T> R<T> fail(String message) {
        return R.fail(message);
    }

    /**
     * 返回失败响应（带错误码）。
     *
     * @param code    错误码
     * @param message 错误消息
     * @param <T>     数据类型
     * @return 失败响应
     */
    protected <T> R<T> fail(Integer code, String message) {
        return R.fail(code, message);
    }

    /**
     * 返回分页响应。
     *
     * @param records     数据列表
     * @param total       总记录数
     * @param pageSize    每页大小
     * @param currentPage 当前页码
     * @param <T>         数据类型
     * @return 分页响应
     */
    protected <T> R<PageData<T>> page(List<T> records, Long total, Long pageSize, Long currentPage) {
        PageData<T> pageData = new PageData<>(records, total, pageSize, currentPage);
        return R.ok(pageData);
    }
}
