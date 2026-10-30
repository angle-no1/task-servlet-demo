package cn.edu.mju.band.buss.impl;

import cn.edu.mju.band.buss.ITaskBuss;
import cn.edu.mju.band.buss.TaskSort;
import cn.edu.mju.band.entity.Task;
import cn.edu.mju.band.exception.TaskServiceException;
import cn.edu.mju.band.mapper.TaskMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.util.Collection;
import java.util.List;
import java.util.Objects;

/**
 * 任务业务实现（MyBatis-Plus 版）。
 *
 * <p>与手写 MyBatis 版相比，持久层代码从 6 个 Mapper 方法缩减为 BaseMapper 的 5 个内置方法，
 * 分页与条件查询由 {@link LambdaQueryWrapper} + {@link Page} 完成：
 * <ul>
 *   <li>SQL 由框架生成，业务层只描述“查什么”，不描述“怎么拼 SQL”；</li>
 *   <li>仍保留参数边界校验与异常翻译，避免封装后丢失业务语义；</li>
 *   <li>分页偏移量由 MP 计算，避免手写 (pageNum-1)*pageSize 的溢出风险。</li>
 * </ul>
 */
@Service
public class TaskBuss implements ITaskBuss {

    /** t_task.title 为 varchar(100)，业务层提前拦截超长标题 */
    public static final int TITLE_MAX_LENGTH = Task.TITLE_MAX_LENGTH;
    /** 单页最大条数，防止恶意 pageSize 拖垮数据库 */
    public static final int MAX_PAGE_SIZE = 100;
    /** 单次批量更新最大条数，与 SQL IN 占位符数量对齐 */
    public static final int MAX_BATCH_SIZE = 100;

    private TaskMapper taskMapper;

    @Autowired
    public void setTaskMapper(TaskMapper taskMapper) {
        this.taskMapper = taskMapper;
    }

    @Override
    public List<Task> list() {
        try {
            // 等价于 SELECT * FROM t_task ORDER BY create_time DESC
            return taskMapper.selectList(
                    Wrappers.<Task>lambdaQuery().orderByDesc(Task::getCreateTime));
        } catch (DataAccessException e) {
            throw wrap(e);
        }
    }

    @Override
    @Transactional
    public boolean add(Task task) {
        checkTask(task);
        // 状态未指定时按业务默认值“待办”处理，避免入库 NULL
        if (task.getStatus() == null) {
            task.setStatus(Task.STATUS_TODO);
        }
        try {
            // 主键由 @TableId(type = IdType.AUTO) 回填
            return taskMapper.insert(task) > 0;
        } catch (DataAccessException e) {
            throw wrap(e);
        }
    }

    @Override
    @Transactional
    public boolean update(Task task) {
        checkTask(task);
        if (task.getId() == null) {
            throw new IllegalArgumentException("更新任务时编号不能为空");
        }
        if (task.getStatus() == null) {
            throw new IllegalArgumentException("更新任务时状态不能为空");
        }
        try {
            // 只更新非 null 字段（create_time 不会被覆盖）
            return taskMapper.updateById(task) > 0;
        } catch (DataAccessException e) {
            throw wrap(e);
        }
    }

    @Override
    public Task findById(Integer id) {
        if (id == null) {
            throw new IllegalArgumentException("任务编号不能为空");
        }
        try {
            return taskMapper.selectById(id);
        } catch (DataAccessException e) {
            throw wrap(e);
        }
    }

    @Override
    @Transactional
    public boolean delete(Integer id) {
        if (id == null) {
            throw new IllegalArgumentException("任务编号不能为空");
        }
        try {
            return taskMapper.deleteById(id) > 0;
        } catch (DataAccessException e) {
            throw wrap(e);
        }
    }

    // ===== 分页 + 多条件查询 =====
    @Override
    public Page<Task> findPage(String title, Byte status, int pageNum, int pageSize,
                               TaskSort sort, boolean ascending) {
        checkPageArgs(pageNum, pageSize);
        checkStatus(status);

        Page<Task> page = new Page<>(pageNum, pageSize);

        // 条件构造器：标题模糊 + 状态精确，条件为空时自动省略对应 AND
        LambdaQueryWrapper<Task> wrapper = Wrappers.lambdaQuery(Task.class);
        if (StringUtils.hasText(title)) {
            wrapper.like(Task::getTitle, title.trim());
        }
        if (status != null) {
            wrapper.eq(Task::getStatus, status);
        }
        // 排序列来自 TaskSort 白名单（SFunction 引用），不接收外部拼接的 SQL 片段
        TaskSort order = sort == null ? TaskSort.CREATE_TIME : sort;
        wrapper.orderBy(true, ascending, order.getColumn());

        try {
            // 一条 selectPage 同时完成 count + 当前页数据，无需再写 countByCondition
            return taskMapper.selectPage(page, wrapper);
        } catch (DataAccessException e) {
            throw wrap(e);
        }
    }

    // ===== 批量修改状态 =====
    @Override
    @Transactional
    public int updateStatusBatch(Collection<Integer> ids, Byte status) {
        if (status == null) {
            throw new IllegalArgumentException("批量更新任务时状态不能为空");
        }
        checkStatus(status);
        if (ids == null || ids.isEmpty()) {
            throw new IllegalArgumentException("待更新的任务编号不能为空");
        }

        List<Integer> distinctIds = ids.stream()
                .filter(Objects::nonNull)
                .distinct()
                .toList();
        if (distinctIds.isEmpty()) {
            throw new IllegalArgumentException("待更新的任务编号不能为空");
        }
        if (distinctIds.size() > MAX_BATCH_SIZE) {
            throw new IllegalArgumentException("一次最多更新 " + MAX_BATCH_SIZE + " 条任务");
        }

        try {
            // 一条 UPDATE t_task SET status=? WHERE id IN (?, ?, ...)：
            // 既避免循环 updateById 的 N+1，也避免手写 SQL 的注入风险
            UpdateWrapper<Task> wrapper = Wrappers.update();
            wrapper.set("status", status).in("id", distinctIds);
            return taskMapper.update(null, wrapper);
        } catch (DataAccessException e) {
            throw wrap(e);
        }
    }

    // ===== 私有校验 =====

    private void checkTask(Task task) {
        if (task == null) {
            throw new IllegalArgumentException("任务对象不能为空");
        }
        if (task.getTitle() == null || task.getTitle().trim().isEmpty()) {
            throw new IllegalArgumentException("任务名称不能为空");
        }
        if (task.getTitle().trim().length() > TITLE_MAX_LENGTH) {
            throw new IllegalArgumentException("任务名称长度不能超过 " + TITLE_MAX_LENGTH + " 个字符");
        }
        checkStatus(task.getStatus());
    }

    /** 状态只能是 0 待办 / 1 进行中 / 2 已完成 */
    private void checkStatus(Byte status) {
        if (status != null
                && (status < Task.STATUS_TODO || status > Task.STATUS_DONE)) {
            throw new IllegalArgumentException("任务状态非法，只能是 0/1/2");
        }
    }

    /** 页码与每页条数边界校验，防止超大 LIMIT 或负数分页 */
    private void checkPageArgs(int pageNum, int pageSize) {
        if (pageNum < 1) {
            throw new IllegalArgumentException("页码必须大于等于 1");
        }
        if (pageSize < 1) {
            throw new IllegalArgumentException("每页条数必须大于等于 1");
        }
        if (pageSize > MAX_PAGE_SIZE) {
            throw new IllegalArgumentException("每页条数不能超过 " + MAX_PAGE_SIZE);
        }
    }

    private TaskServiceException wrap(DataAccessException e) {
        return new TaskServiceException("任务数据访问失败，数据库暂时不可用，请稍后重试", e);
    }
}
