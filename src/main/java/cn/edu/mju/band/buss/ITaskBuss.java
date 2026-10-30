package cn.edu.mju.band.buss;

import cn.edu.mju.band.entity.Task;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;

import java.util.Collection;
import java.util.List;

/** 任务业务接口 */
public interface ITaskBuss {

    List<Task> list();

    boolean add(Task task);

    boolean update(Task task);

    Task findById(Integer id);

    boolean delete(Integer id);

    // ===== 多条件分页查询 =====

    /**
     * 页面侧使用的默认排序（创建时间倒序）。
     *
     * <p>保留四参签名，页面控制器与既有测试无需关心排序细节；
     * 需要自定义排序时调用下面的六参重载。
     */
    default Page<Task> findPage(String title, Byte status, int pageNum, int pageSize) {
        return findPage(title, status, pageNum, pageSize, TaskSort.CREATE_TIME, false);
    }

    /**
     * 多条件分页查询（带白名单排序）。
     *
     * @param sort      排序字段，只接受 {@link TaskSort} 枚举，杜绝 ORDER BY 注入
     * @param ascending true 升序 / false 降序
     */
    Page<Task> findPage(String title, Byte status, int pageNum, int pageSize,
                        TaskSort sort, boolean ascending);

    // ===== 批量修改状态 =====

    /**
     * 批量修改任务状态，使用一条 {@code UPDATE ... WHERE id IN (...)} 完成。
     *
     * @return 实际更新的行数
     */
    int updateStatusBatch(Collection<Integer> ids, Byte status);
}
