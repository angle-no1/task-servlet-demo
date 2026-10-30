package cn.edu.mju.band.buss.impl;

import cn.edu.mju.band.buss.TaskSort;
import cn.edu.mju.band.entity.Task;
import cn.edu.mju.band.exception.TaskServiceException;
import cn.edu.mju.band.mapper.TaskMapper;
import com.baomidou.mybatisplus.core.MybatisConfiguration;
import com.baomidou.mybatisplus.core.conditions.AbstractWrapper;
import com.baomidou.mybatisplus.core.conditions.Wrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.core.metadata.TableInfoHelper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import org.apache.ibatis.builder.MapperBuilderAssistant;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.EmptySource;
import org.junit.jupiter.params.provider.NullSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.dao.DataAccessResourceFailureException;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

/**
 * TaskBuss 业务层单元测试（JUnit 5 + Mockito）。
 *
 * <p>全部用例均通过 {@code @Mock} 打桩 TaskMapper，不连接任何物理数据库。
 * MyBatis-Plus 的 LambdaQueryWrapper 需要实体元数据，因此在 @BeforeAll 中
 * 用 TableInfoHelper 初始化一次，之后即可在纯单元测试里验证条件构造器。
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("TaskBuss 业务层单元测试（MyBatis-Plus 版）")
class TaskBussTest {

    @Mock
    private TaskMapper taskMapper;

    @InjectMocks
    private TaskBuss taskBuss;

    @BeforeAll
    static void initMybatisPlusMetadata() {
        MybatisConfiguration configuration = new MybatisConfiguration();
        MapperBuilderAssistant assistant = new MapperBuilderAssistant(configuration, "");
        TableInfoHelper.initTableInfo(assistant, Task.class);
    }

    private static Task validTask() {
        Task task = new Task();
        task.setId(1);
        task.setTitle("完成实验报告");
        task.setContent("整理单元测试截图");
        task.setStatus(Task.STATUS_TODO);
        return task;
    }

    /** 让 selectPage 返回传入的 Page，并填充当前页数据与总数 */
    private void stubPage(long total, List<Task> records) {
        when(taskMapper.selectPage(any(Page.class), any())).thenAnswer(invocation -> {
            Page<Task> page = invocation.getArgument(0);
            page.setRecords(records);
            page.setTotal(total);
            return page;
        });
    }

    // =====================================================================
    // 一、正常流
    // =====================================================================

    @Test
    @DisplayName("list：返回 Mapper 查询到的全部任务")
    void list_shouldReturnAllTasks() {
        List<Task> tasks = List.of(validTask());
        when(taskMapper.selectList(any())).thenReturn(tasks);

        assertThat(taskBuss.list()).hasSize(1).first().extracting(Task::getTitle)
                .isEqualTo("完成实验报告");
        verify(taskMapper).selectList(any());
    }

    @Test
    @DisplayName("add：插入成功返回 true")
    void add_shouldReturnTrueWhenInsertAffectsOneRow() {
        Task task = validTask();
        when(taskMapper.insert(task)).thenReturn(1);

        assertThat(taskBuss.add(task)).isTrue();
        verify(taskMapper).insert(task);
    }

    @Test
    @DisplayName("add：插入 0 行返回 false")
    void add_shouldReturnFalseWhenInsertAffectsZeroRows() {
        Task task = validTask();
        when(taskMapper.insert(any(Task.class))).thenReturn(0);

        assertThat(taskBuss.add(task)).isFalse();
    }

    @Test
    @DisplayName("update：更新成功返回 true，调用 updateById 而不是手写 SQL")
    void update_shouldReturnTrueWhenUpdateAffectsOneRow() {
        Task task = validTask();
        when(taskMapper.updateById(task)).thenReturn(1);

        assertThat(taskBuss.update(task)).isTrue();
        verify(taskMapper).updateById(task);
    }

    @Test
    @DisplayName("update：目标记录不存在返回 false")
    void update_shouldReturnFalseWhenUpdateAffectsZeroRows() {
        Task task = validTask();
        when(taskMapper.updateById(any(Task.class))).thenReturn(0);

        assertThat(taskBuss.update(task)).isFalse();
    }

    @Test
    @DisplayName("findById：命中时返回任务对象")
    void findById_shouldReturnTask() {
        when(taskMapper.selectById(1)).thenReturn(validTask());

        assertThat(taskBuss.findById(1)).isNotNull()
                .extracting(Task::getTitle).isEqualTo("完成实验报告");
    }

    @Test
    @DisplayName("findById：未命中时返回 null")
    void findById_shouldReturnNullWhenNotFound() {
        when(taskMapper.selectById(99)).thenReturn(null);

        assertThat(taskBuss.findById(99)).isNull();
    }

    @Test
    @DisplayName("delete：删除 1 行返回 true")
    void delete_shouldReturnTrueWhenAffectedOneRow() {
        when(taskMapper.deleteById(1)).thenReturn(1);

        assertThat(taskBuss.delete(1)).isTrue();
    }

    @Test
    @DisplayName("delete：记录不存在返回 false")
    void delete_shouldReturnFalseWhenAffectedZeroRows() {
        when(taskMapper.deleteById(404)).thenReturn(0);

        assertThat(taskBuss.delete(404)).isFalse();
    }

    // =====================================================================
    // 二、异常流：参数校验先于持久层，Mapper 不会被调用
    // =====================================================================

    @Test
    @DisplayName("add：任务对象为 null 时抛 IllegalArgumentException")
    void add_shouldThrowWhenTaskIsNull() {
        assertThatThrownBy(() -> taskBuss.add(null))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("任务对象不能为空");
        verifyNoInteractions(taskMapper);
    }

    @ParameterizedTest(name = "标题=[{0}] 视为空标题")
    @NullSource
    @EmptySource
    @ValueSource(strings = {" ", "   ", "\t", "\n"})
    @DisplayName("add：标题为 null/空串/纯空白时抛 IllegalArgumentException")
    void add_shouldThrowWhenTitleIsBlank(String title) {
        Task task = validTask();
        task.setTitle(title);

        assertThatThrownBy(() -> taskBuss.add(task))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("任务名称不能为空");
        verifyNoInteractions(taskMapper);
    }

    @ParameterizedTest(name = "状态={0} 非法")
    @ValueSource(ints = {-1, 3, 127})
    @DisplayName("add：状态越界（非 0/1/2）时抛 IllegalArgumentException")
    void add_shouldThrowWhenStatusIllegal(int status) {
        Task task = validTask();
        task.setStatus((byte) status);

        assertThatThrownBy(() -> taskBuss.add(task))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("任务状态非法，只能是 0/1/2");
        verifyNoInteractions(taskMapper);
    }

    @Test
    @DisplayName("update：编号为 null 时抛 IllegalArgumentException")
    void update_shouldThrowWhenIdIsNull() {
        Task task = validTask();
        task.setId(null);

        assertThatThrownBy(() -> taskBuss.update(task))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("更新任务时编号不能为空");
        verifyNoInteractions(taskMapper);
    }

    @Test
    @DisplayName("update：状态为 null 时抛 IllegalArgumentException，避免把状态刷成 NULL")
    void update_shouldThrowWhenStatusIsNull() {
        Task task = validTask();
        task.setStatus(null);

        assertThatThrownBy(() -> taskBuss.update(task))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("更新任务时状态不能为空");
        verifyNoInteractions(taskMapper);
    }

    @Test
    @DisplayName("update：标题为空时抛 IllegalArgumentException")
    void update_shouldThrowWhenTitleIsBlank() {
        Task task = validTask();
        task.setTitle("   ");

        assertThatThrownBy(() -> taskBuss.update(task))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("任务名称不能为空");
        verifyNoInteractions(taskMapper);
    }

    @Test
    @DisplayName("findById：编号为 null 时抛 IllegalArgumentException")
    void findById_shouldThrowWhenIdIsNull() {
        assertThatThrownBy(() -> taskBuss.findById(null))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("任务编号不能为空");
        verifyNoInteractions(taskMapper);
    }

    @Test
    @DisplayName("delete：编号为 null 时抛 IllegalArgumentException")
    void delete_shouldThrowWhenIdIsNull() {
        assertThatThrownBy(() -> taskBuss.delete(null))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("任务编号不能为空");
        verifyNoInteractions(taskMapper);
    }

    // =====================================================================
    // 三、边界条件：标题长度 100/101，页码与每页条数上下界
    // =====================================================================

    @Test
    @DisplayName("add：标题长度 100（上限）可以正常提交")
    void add_shouldAcceptTitleWithMaxLength() {
        Task task = validTask();
        task.setTitle("任".repeat(TaskBuss.TITLE_MAX_LENGTH));
        when(taskMapper.insert(task)).thenReturn(1);

        assertThat(taskBuss.add(task)).isTrue();
    }

    @Test
    @DisplayName("add：标题长度 101（超出上限）被拦截")
    void add_shouldRejectTitleExceedingMaxLength() {
        Task task = validTask();
        task.setTitle("任".repeat(TaskBuss.TITLE_MAX_LENGTH + 1));

        assertThatThrownBy(() -> taskBuss.add(task))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("不能超过 100 个字符");
        verifyNoInteractions(taskMapper);
    }

    @Test
    @DisplayName("add：状态为 null 时按业务默认值 0（待办）落库")
    void add_shouldDefaultStatusToTodoWhenNull() {
        Task task = validTask();
        task.setStatus(null);
        when(taskMapper.insert(task)).thenReturn(1);

        assertThat(taskBuss.add(task)).isTrue();
        assertThat(task.getStatus()).isEqualTo(Task.STATUS_TODO);
    }

    @ParameterizedTest(name = "状态={0} 属于合法状态")
    @ValueSource(ints = {0, 1, 2})
    @DisplayName("add：0/1/2 三个合法状态均能提交")
    void add_shouldAcceptAllLegalStatus(int status) {
        Task task = validTask();
        task.setStatus((byte) status);
        when(taskMapper.insert(task)).thenReturn(1);

        assertThat(taskBuss.add(task)).isTrue();
    }

    @ParameterizedTest(name = "pageNum={0}, pageSize={1}")
    @CsvSource({
            "1, 5",
            "2, 5",
            "3, 5",
            "1, 10",
            "4, 20",
            "1, 100"
    })
    @DisplayName("findPage：当前页与每页条数原样交给 MyBatis-Plus Page")
    void findPage_shouldForwardPageArgs(int pageNum, int pageSize) {
        stubPage(0, List.of());

        taskBuss.findPage(null, null, pageNum, pageSize);

        ArgumentCaptor<Page<Task>> captor = ArgumentCaptor.forClass(Page.class);
        verify(taskMapper).selectPage(captor.capture(), any());
        assertThat(captor.getValue().getCurrent()).isEqualTo((long) pageNum);
        assertThat(captor.getValue().getSize()).isEqualTo((long) pageSize);
    }

    @ParameterizedTest(name = "total={0}, pageSize={1} => pages={2}")
    @CsvSource({
            "0, 5, 0",
            "1, 5, 1",
            "5, 5, 1",
            "6, 5, 2",
            "20, 5, 4",
            "21, 5, 5",
            "7, 3, 3"
    })
    @DisplayName("findPage：总页数由 MP Page 按总数向上取整，total=0 时为 0 页")
    void findPage_shouldComputePages(long total, int pageSize, int expectedPages) {
        stubPage(total, List.of());

        Page<Task> page = taskBuss.findPage(null, null, 1, pageSize);

        assertThat(page.getPages()).isEqualTo((long) expectedPages);
        assertThat(page.getTotal()).isEqualTo(total);
    }

    @ParameterizedTest(name = "pageNum={0} 非法")
    @ValueSource(ints = {0, -1, -100})
    @DisplayName("findPage：页码 < 1 时抛 IllegalArgumentException")
    void findPage_shouldRejectIllegalPageNum(int pageNum) {
        assertThatThrownBy(() -> taskBuss.findPage(null, null, pageNum, 5))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("页码必须大于等于 1");
        verifyNoInteractions(taskMapper);
    }

    @ParameterizedTest(name = "pageSize={0} 非法")
    @ValueSource(ints = {0, -1, 101})
    @DisplayName("findPage：每页条数 < 1 或 > 100 时抛 IllegalArgumentException")
    void findPage_shouldRejectIllegalPageSize(int pageSize) {
        assertThatThrownBy(() -> taskBuss.findPage(null, null, 1, pageSize))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("每页条数");
        verifyNoInteractions(taskMapper);
    }

    @Test
    @DisplayName("findPage：pageSize=100（上限）可以正常查询")
    void findPage_shouldAcceptMaxPageSize() {
        stubPage(0, List.of());

        Page<Task> page = taskBuss.findPage(null, null, 1, TaskBuss.MAX_PAGE_SIZE);

        assertThat(page.getSize()).isEqualTo((long) TaskBuss.MAX_PAGE_SIZE);
    }

    @Test
    @DisplayName("findPage：非法状态不会落到数据库")
    void findPage_shouldRejectIllegalStatus() {
        assertThatThrownBy(() -> taskBuss.findPage(null, (byte) 5, 1, 5))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("任务状态非法，只能是 0/1/2");
        verifyNoInteractions(taskMapper);
    }

    // =====================================================================
    // 四、条件构造器与分页结果的组合逻辑
    // =====================================================================

    @Test
    @DisplayName("findPage：标题模糊 + 状态精确条件被写入 SQL 片段")
    void findPage_shouldBuildLikeAndEqConditions() {
        stubPage(7, List.of(validTask()));

        taskBuss.findPage("报告", (byte) 1, 2, 3);

        ArgumentCaptor<Wrapper<Task>> captor = ArgumentCaptor.forClass(Wrapper.class);
        verify(taskMapper).selectPage(any(Page.class), captor.capture());
        String sql = captor.getValue().getSqlSegment();
        assertThat(sql).contains("title", "LIKE", "status");
        AbstractWrapper<?, ?, ?> wrapper = (AbstractWrapper<?, ?, ?>) captor.getValue();
        assertThat(wrapper.getParamNameValuePairs().values()).contains("%报告%");
    }

    @Test
    @DisplayName("findPage：条件为 null 时按“全部”查询，不生成 title/status 条件")
    void findPage_shouldSupportNullFilters() {
        stubPage(0, List.of());

        Page<Task> page = taskBuss.findPage(null, null, 1, 5);

        assertThat(page.getRecords()).isEmpty();
        assertThat(page.getPages()).isZero();
        verify(taskMapper).selectPage(any(Page.class), any());
    }

    @Test
    @DisplayName("findPage：把 Mapper 返回的记录与总数原样回填到 Page")
    void findPage_shouldKeepRecordsAndTotal() {
        Task t1 = validTask();
        Task t2 = validTask();
        t2.setId(2);
        stubPage(7, List.of(t1, t2));

        Page<Task> page = taskBuss.findPage("报告", (byte) 1, 2, 3);

        assertThat(page.getRecords()).containsExactly(t1, t2);
        assertThat(page.getCurrent()).isEqualTo(2L);
        assertThat(page.getSize()).isEqualTo(3L);
        assertThat(page.getTotal()).isEqualTo(7);
        assertThat(page.getPages()).isEqualTo(3L);
    }

    // =====================================================================
    // 五、数据库宕机：业务校验仍生效，持久层异常被翻译成统一业务异常
    // =====================================================================

    @Test
    @DisplayName("数据库宕机：list 抛出 TaskServiceException 并保留原始原因")
    void list_shouldWrapDataAccessException() {
        when(taskMapper.selectList(any()))
                .thenThrow(new DataAccessResourceFailureException("Connection refused"));

        assertThatThrownBy(() -> taskBuss.list())
                .isInstanceOf(TaskServiceException.class)
                .hasMessageContaining("数据库暂时不可用")
                .hasCauseInstanceOf(DataAccessResourceFailureException.class);
    }

    @Test
    @DisplayName("数据库宕机：add 抛出 TaskServiceException，事务仍会回滚")
    void add_shouldWrapDataAccessException() {
        Task task = validTask();
        when(taskMapper.insert(task))
                .thenThrow(new DataAccessResourceFailureException("Connection refused"));

        assertThatThrownBy(() -> taskBuss.add(task))
                .isInstanceOf(TaskServiceException.class)
                .hasMessageContaining("数据库暂时不可用")
                .hasCauseInstanceOf(DataAccessResourceFailureException.class);
    }

    @Test
    @DisplayName("数据库宕机：update 抛出 TaskServiceException")
    void update_shouldWrapDataAccessException() {
        Task task = validTask();
        when(taskMapper.updateById(task))
                .thenThrow(new DataAccessResourceFailureException("Connection refused"));

        assertThatThrownBy(() -> taskBuss.update(task))
                .isInstanceOf(TaskServiceException.class)
                .hasCauseInstanceOf(DataAccessResourceFailureException.class);
    }

    @Test
    @DisplayName("数据库宕机：findById 抛出 TaskServiceException")
    void findById_shouldWrapDataAccessException() {
        when(taskMapper.selectById(1))
                .thenThrow(new DataAccessResourceFailureException("Connection refused"));

        assertThatThrownBy(() -> taskBuss.findById(1))
                .isInstanceOf(TaskServiceException.class)
                .hasCauseInstanceOf(DataAccessResourceFailureException.class);
    }

    @Test
    @DisplayName("数据库宕机：delete 抛出 TaskServiceException")
    void delete_shouldWrapDataAccessException() {
        when(taskMapper.deleteById(1))
                .thenThrow(new DataAccessResourceFailureException("Connection refused"));

        assertThatThrownBy(() -> taskBuss.delete(1))
                .isInstanceOf(TaskServiceException.class)
                .hasCauseInstanceOf(DataAccessResourceFailureException.class);
    }

    @Test
    @DisplayName("数据库宕机：findPage 抛出 TaskServiceException")
    void findPage_shouldWrapDataAccessException() {
        when(taskMapper.selectPage(any(Page.class), any()))
                .thenThrow(new DataAccessResourceFailureException("Connection refused"));

        assertThatThrownBy(() -> taskBuss.findPage(null, null, 1, 5))
                .isInstanceOf(TaskServiceException.class)
                .hasCauseInstanceOf(DataAccessResourceFailureException.class);
    }

    @Test
    @DisplayName("数据库不可用时：非法参数仍然优先被业务校验拦截（不产生空指针/连接异常）")
    void validation_shouldStillWorkWhenDatabaseIsDown() {
        Task task = validTask();
        task.setTitle("");

        assertThatThrownBy(() -> taskBuss.add(task))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("任务名称不能为空");
        verifyNoInteractions(taskMapper);
    }

    // =====================================================================
    // 六、排序白名单：列引用由枚举提供，外部字符串不进入 SQL
    // =====================================================================

    @Test
    @DisplayName("findPage：默认按 create_time 降序（页面侧行为保持不变）")
    void findPage_shouldDefaultToCreateTimeDesc() {
        stubPage(0, List.of());

        taskBuss.findPage(null, null, 1, 5);

        ArgumentCaptor<Wrapper<Task>> captor = ArgumentCaptor.forClass(Wrapper.class);
        verify(taskMapper).selectPage(any(Page.class), captor.capture());
        assertThat(captor.getValue().getSqlSegment()).containsIgnoringCase("ORDER BY create_time DESC");
    }

    @Test
    @DisplayName("findPage：白名单字段 title + 升序生成 ORDER BY title ASC")
    void findPage_shouldOrderByWhitelistColumn() {
        stubPage(0, List.of());

        taskBuss.findPage(null, null, 1, 5, TaskSort.TITLE, true);

        ArgumentCaptor<Wrapper<Task>> captor = ArgumentCaptor.forClass(Wrapper.class);
        verify(taskMapper).selectPage(any(Page.class), captor.capture());
        assertThat(captor.getValue().getSqlSegment()).containsIgnoringCase("ORDER BY title ASC");
    }

    @Test
    @DisplayName("findPage：sort 为 null 时回退到创建时间倒序")
    void findPage_shouldFallbackWhenSortIsNull() {
        stubPage(0, List.of());

        taskBuss.findPage(null, null, 1, 5, null, true);

        ArgumentCaptor<Wrapper<Task>> captor = ArgumentCaptor.forClass(Wrapper.class);
        verify(taskMapper).selectPage(any(Page.class), captor.capture());
        assertThat(captor.getValue().getSqlSegment()).containsIgnoringCase("ORDER BY create_time ASC");
    }

    // =====================================================================
    // 七、批量改状态：一条 UPDATE ... IN，而不是循环 updateById（N+1）
    // =====================================================================

    @Test
    @DisplayName("updateStatusBatch：单条 UPDATE + IN 完成，重复/空编号先去重过滤")
    void updateStatusBatch_shouldIssueSingleUpdate() {
        when(taskMapper.update(isNull(), any())).thenReturn(3);

        int updated = taskBuss.updateStatusBatch(
                java.util.Arrays.asList(1, 2, 2, null, 3), Task.STATUS_DONE);

        assertThat(updated).isEqualTo(3);

        @SuppressWarnings("unchecked")
        ArgumentCaptor<UpdateWrapper<Task>> captor = ArgumentCaptor.forClass(UpdateWrapper.class);
        verify(taskMapper).update(isNull(), captor.capture());
        assertThat(captor.getValue().getSqlSet()).contains("status");
        assertThat(captor.getValue().getSqlSegment()).containsIgnoringCase("IN");
        // 关键断言：不再逐条 updateById
        verify(taskMapper, never()).updateById(any(Task.class));
    }

    @ParameterizedTest
    @NullSource
    @EmptySource
    @DisplayName("updateStatusBatch：编号集合为空时拒绝执行")
    void updateStatusBatch_shouldRejectEmptyIds(java.util.List<Integer> ids) {
        assertThatThrownBy(() -> taskBuss.updateStatusBatch(ids, Task.STATUS_DONE))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("待更新的任务编号不能为空");
        verifyNoInteractions(taskMapper);
    }

    @Test
    @DisplayName("updateStatusBatch：编号全是 null 时拒绝执行")
    void updateStatusBatch_shouldRejectAllNullIds() {
        assertThatThrownBy(() -> taskBuss.updateStatusBatch(
                java.util.Arrays.asList(null, null), Task.STATUS_DONE))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("待更新的任务编号不能为空");
        verifyNoInteractions(taskMapper);
    }

    @Test
    @DisplayName("updateStatusBatch：状态为 null 时拒绝执行")
    void updateStatusBatch_shouldRejectNullStatus() {
        assertThatThrownBy(() -> taskBuss.updateStatusBatch(List.of(1), null))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("批量更新任务时状态不能为空");
        verifyNoInteractions(taskMapper);
    }

    @Test
    @DisplayName("updateStatusBatch：状态越界时拒绝执行")
    void updateStatusBatch_shouldRejectIllegalStatus() {
        assertThatThrownBy(() -> taskBuss.updateStatusBatch(List.of(1), (byte) 5))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("任务状态非法，只能是 0/1/2");
        verifyNoInteractions(taskMapper);
    }

    @Test
    @DisplayName("updateStatusBatch：超过 100 条时拒绝执行，避免超长 IN 与长事务")
    void updateStatusBatch_shouldRejectTooManyIds() {
        List<Integer> ids = java.util.stream.IntStream.rangeClosed(1, TaskBuss.MAX_BATCH_SIZE + 1)
                .boxed().toList();

        assertThatThrownBy(() -> taskBuss.updateStatusBatch(ids, Task.STATUS_DONE))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("一次最多更新 100 条任务");
        verifyNoInteractions(taskMapper);
    }

    @Test
    @DisplayName("updateStatusBatch：数据库异常被翻译为 TaskServiceException")
    void updateStatusBatch_shouldWrapDataAccessException() {
        when(taskMapper.update(isNull(), any()))
                .thenThrow(new DataAccessResourceFailureException("Connection refused"));

        assertThatThrownBy(() -> taskBuss.updateStatusBatch(List.of(1, 2), Task.STATUS_DONE))
                .isInstanceOf(TaskServiceException.class)
                .hasCauseInstanceOf(DataAccessResourceFailureException.class);
    }
}

