package com.your_group_name.your_project_name.platform.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.your_group_name.your_project_name.platform.entity.SysTenant;

import org.apache.ibatis.annotations.Mapper;

/**
 * 租户 Mapper
 */
@Mapper
public interface SysTenantMapper extends BaseMapper<SysTenant> {
}
