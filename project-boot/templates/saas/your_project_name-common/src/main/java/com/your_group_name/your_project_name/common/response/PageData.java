package com.your_group_name.your_project_name.common.response;

import lombok.Data;

import java.io.Serializable;
import java.util.List;

/**
 * 分页响应体。
 *
 * @param <T> 数据项类型
 */
@Data
public class PageData<T> implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 数据列表。
     */
    private List<T> records;

    /**
     * 总记录数。
     */
    private Long total;

    /**
     * 每页大小。
     */
    private Long pageSize;

    /**
     * 当前页码。
     */
    private Long currentPage;

    /**
     * 总页数。
     */
    private Long totalPages;

    /**
     * 构造函数。
     *
     * @param records     数据列表
     * @param total       总记录数
     * @param pageSize    每页大小
     * @param currentPage 当前页码
     */
    public PageData(List<T> records, Long total, Long pageSize, Long currentPage) {
        this.records = records;
        this.total = total;
        this.pageSize = pageSize;
        this.currentPage = currentPage;
        this.totalPages = calculateTotalPages(total, pageSize);
    }

    /**
     * 计算总页数。
     *
     * @param total    总记录数
     * @param pageSize 每页大小
     * @return 总页数
     */
    private Long calculateTotalPages(Long total, Long pageSize) {
        if (total == 0 || pageSize == 0) {
            return 0L;
        }
        return (total + pageSize - 1) / pageSize; // 向上取整
    }
}
