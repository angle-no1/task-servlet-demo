package cn.edu.mju.band.mapper;

import cn.edu.mju.band.entity.Task;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;

/**
 * 任务数据访问接口 —— MyBatis-Plus 版。
 *
 * <p>继承 {@link BaseMapper} 后，CRUD 与分页所需的方法全部由框架动态生成，
 * 不再需要 TaskMapper.xml；条件查询统一由业务层用条件构造器拼装。
 */
public interface TaskMapper extends BaseMapper<Task> {
}
