package com.fengqun.scm.common.base;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;

import java.io.Serializable;
import java.time.LocalDateTime;

import lombok.Data;

/**
 * 实体基类。
 *
 * 包含所有业务表的公共字段：
 * - id: 主键（雪花ID）
 * - tenantId: 租户ID（多租户隔离）
 * - createdBy: 创建人 ID
 * - createdAt: 创建时间
 * - updatedBy: 更新人 ID
 * - updatedAt: 更新时间
 * - deleted: 逻辑删除标记（0: 未删除, 1: 已删除）
 *
 * 使用 Lombok @Data 生成 getter/setter，配合 MyBatis-Plus 注解
 */
@Data
public abstract class BaseEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 主键 ID（雪花 ID）。
     */
    @TableId(value = "id", type = IdType.ASSIGN_ID)
    private Long id;

    /**
     * 租户 ID（用于多租户隔离）。
     */
    private String tenantId;

    /**
     * 创建人 ID。
     */
    private Long createdBy;

    /**
     * 创建时间。
     */
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    /**
     * 更新人 ID。
     */
    private Long updatedBy;

    /**
     * 更新时间。
     */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    /**
     * 逻辑删除标记。
     * 0: 未删除（默认）
     * 1: 已删除
     */
    @TableLogic
    private Boolean deleted = false;
}
