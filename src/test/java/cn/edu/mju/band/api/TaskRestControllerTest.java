package cn.edu.mju.band.api;

import cn.edu.mju.band.api.dto.PageResult;
import cn.edu.mju.band.audit.TaskAuditService;
import cn.edu.mju.band.buss.ITaskBuss;
import cn.edu.mju.band.buss.TaskSort;
import cn.edu.mju.band.config.WebMvcConfig;
import cn.edu.mju.band.entity.Task;
import cn.edu.mju.band.entity.User;
import cn.edu.mju.band.web.SessionKeys;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;

import java.util.Date;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * REST 接口切片测试：验证统一响应体、错误码、字段校验、404 语义与排序白名单。
 * Service 全部 Mock，不连接数据库，也不真正创建异步线程。
 */
@WebMvcTest(TaskRestController.class)
@Import(WebMvcConfig.class)
@DisplayName("TaskRestController REST 接口测试")
class TaskRestControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ITaskBuss taskBuss;

    @MockBean
    private TaskAuditService auditService;

    private MockHttpSession session;

    @BeforeEach
    void setUpLoginSession() {
        session = new MockHttpSession();
        session.setAttribute(SessionKeys.LOGIN_USER, new User(1, "admin", "123456"));
    }

    private MockHttpServletRequestBuilder authed(MockHttpServletRequestBuilder builder) {
        return builder.session(session);
    }

    private static Task task(int id, String title, byte status) {
        Task task = new Task(id, title, "内容-" + id, status, new Date(1730000000000L));
        return task;
    }

    private static Page<Task> pageOf(List<Task> records, long total, long current, long size) {
        Page<Task> page = new Page<>(current, size);
        page.setRecords(records);
        page.setTotal(total);
        return page;
    }

    // ----- 鉴权 -----

    @Test
    @DisplayName("未登录：返回 401 JSON + 业务码 40100（不重定向登录页）")
    void shouldReturn401JsonWhenNotAuthenticated() throws Exception {
        mockMvc.perform(get("/api/tasks"))
                .andExpect(status().isUnauthorized())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.code").value(40100))
                .andExpect(jsonPath("$.message").value("未登录或会话已过期"));

        verifyNoInteractions(taskBuss);
    }

    // ----- 查询 -----

    @Test
    @DisplayName("GET /api/tasks：默认第 1 页、每页 10 条、createTime 倒序，返回统一分页结构")
    void shouldListWithDefaults() throws Exception {
        when(taskBuss.findPage(null, null, 1, 10, TaskSort.CREATE_TIME, false))
                .thenReturn(pageOf(List.of(task(1, "任务一", (byte) 0)), 1, 1, 10));

        mockMvc.perform(authed(get("/api/tasks")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.total").value(1))
                .andExpect(jsonPath("$.data.current").value(1))
                .andExpect(jsonPath("$.data.size").value(10))
                .andExpect(jsonPath("$.data.pages").value(1))
                .andExpect(jsonPath("$.data.records[0].id").value(1))
                .andExpect(jsonPath("$.data.records[0].title").value("任务一"))
                .andExpect(jsonPath("$.data.records[0].statusLabel").value("待办"));
    }

    @Test
    @DisplayName("GET /api/tasks：标题/状态/分页/排序参数全部透传")
    void shouldForwardQueryParams() throws Exception {
        when(taskBuss.findPage("报告", (byte) 1, 2, 5, TaskSort.TITLE, true))
                .thenReturn(pageOf(List.of(), 0, 2, 5));

        mockMvc.perform(authed(get("/api/tasks")
                        .param("title", "报告")
                        .param("status", "1")
                        .param("pageNum", "2")
                        .param("pageSize", "5")
                        .param("sort", "title,asc")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0));

        verify(taskBuss).findPage("报告", (byte) 1, 2, 5, TaskSort.TITLE, true);
    }

    @Test
    @DisplayName("GET /api/tasks：ORDER BY 注入载荷被白名单拦截（400 + 40001），不触达业务层")
    void shouldRejectSqlInjectionInSort() throws Exception {
        mockMvc.perform(authed(get("/api/tasks")
                        .param("sort", "createTime;DROP TABLE t_task;--")))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(40001))
                .andExpect(jsonPath("$.message").value(org.hamcrest.Matchers.containsString("不支持的排序字段")));

        verifyNoInteractions(taskBuss);
    }

    @Test
    @DisplayName("GET /api/tasks：pageSize 越界由业务层拒绝，接口映射为 400")
    void shouldMapPageSizeOverflowTo400() throws Exception {
        when(taskBuss.findPage(any(), any(), anyInt(), eq(101), any(), anyBoolean()))
                .thenThrow(new IllegalArgumentException("每页条数不能超过 100"));

        mockMvc.perform(authed(get("/api/tasks").param("pageSize", "101")))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(40001))
                .andExpect(jsonPath("$.message").value("每页条数不能超过 100"));
    }

    @Test
    @DisplayName("GET /api/tasks/{id}：命中返回任务")
    void shouldGetTaskById() throws Exception {
        when(taskBuss.findById(7)).thenReturn(task(7, "任务七", (byte) 2));

        mockMvc.perform(authed(get("/api/tasks/7")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.id").value(7))
                .andExpect(jsonPath("$.data.statusLabel").value("已完成"));
    }

    @Test
    @DisplayName("GET /api/tasks/{id}：不存在返回 404 + 40401，而不是 NPE / 200")
    void shouldReturn404WhenTaskMissing() throws Exception {
        when(taskBuss.findById(404)).thenReturn(null);

        mockMvc.perform(authed(get("/api/tasks/404")))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.code").value(40401))
                .andExpect(jsonPath("$.message").value("任务不存在：404"));
    }

    @Test
    @DisplayName("GET /api/tasks/{id}：id 非数字由类型转换异常映射为 400")
    void shouldMapPathTypeMismatchTo400() throws Exception {
        mockMvc.perform(authed(get("/api/tasks/abc")))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(40001));

        verifyNoInteractions(taskBuss);
    }

    // ----- 新增 -----

    @Test
    @DisplayName("POST /api/tasks：成功返回 201 + Location + 回填 id，并触发异步审计")
    void shouldCreateTask() throws Exception {
        when(taskBuss.add(any(Task.class))).thenAnswer(invocation -> {
            Task toSave = invocation.getArgument(0);
            toSave.setId(42);
            return true;
        });
        when(taskBuss.findById(42)).thenReturn(task(42, "新任务", (byte) 1));

        mockMvc.perform(authed(post("/api/tasks"))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"新任务\",\"content\":\"内容\",\"status\":1}"))
                .andExpect(status().isCreated())
                .andExpect(header().string("Location", "/api/tasks/42"))
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.id").value(42))
                .andExpect(jsonPath("$.data.title").value("新任务"));

        ArgumentCaptor<Task> captor = ArgumentCaptor.forClass(Task.class);
        verify(taskBuss).add(captor.capture());
        assertThat(captor.getValue().getTitle()).isEqualTo("新任务");

        verify(auditService).record(eq(TaskAuditService.ACTION_CREATE), eq(42), eq("新任务"));
    }

    @Test
    @DisplayName("POST /api/tasks：空标题 / 非法状态返回 400 + 字段级错误")
    void shouldRejectInvalidCreatePayload() throws Exception {
        mockMvc.perform(authed(post("/api/tasks"))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"   \",\"status\":9}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(40001))
                .andExpect(jsonPath("$.data.title").value("任务标题不能为空"))
                .andExpect(jsonPath("$.data.status").value("任务状态只能是 0/1/2"));

        verifyNoInteractions(taskBuss);
    }

    @Test
    @DisplayName("POST /api/tasks：JSON 格式错误返回 400，而不是 500")
    void shouldRejectMalformedJson() throws Exception {
        mockMvc.perform(authed(post("/api/tasks"))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"未闭合"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(40001));

        verifyNoInteractions(taskBuss);
    }

    // ----- 修改 / 删除 -----

    @Test
    @DisplayName("PUT /api/tasks/{id}：成功返回更新后的任务")
    void shouldUpdateTask() throws Exception {
        when(taskBuss.update(any(Task.class))).thenReturn(true);
        when(taskBuss.findById(7)).thenReturn(task(7, "改名后", (byte) 2));

        mockMvc.perform(authed(put("/api/tasks/7"))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"改名后\",\"status\":2}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.title").value("改名后"));

        verify(auditService).record(eq(TaskAuditService.ACTION_UPDATE), eq(7), eq("改名后"));
    }

    @Test
    @DisplayName("PUT /api/tasks/{id}：目标不存在返回 404")
    void shouldReturn404WhenUpdatingMissingTask() throws Exception {
        when(taskBuss.update(any(Task.class))).thenReturn(false);

        mockMvc.perform(authed(put("/api/tasks/404"))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"改不动\",\"status\":0}"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.code").value(40401));
    }

    @Test
    @DisplayName("DELETE /api/tasks/{id}：成功返回提示并触发审计")
    void shouldDeleteTask() throws Exception {
        when(taskBuss.delete(9)).thenReturn(true);

        mockMvc.perform(authed(delete("/api/tasks/9")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.message").value("任务已删除"));

        verify(auditService).record(eq(TaskAuditService.ACTION_DELETE), eq(9), isNull());
    }

    @Test
    @DisplayName("DELETE /api/tasks/{id}：目标不存在返回 404")
    void shouldReturn404WhenDeletingMissingTask() throws Exception {
        when(taskBuss.delete(404)).thenReturn(false);

        mockMvc.perform(authed(delete("/api/tasks/404")))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.code").value(40401));

        verify(auditService, never()).record(anyString(), any(), anyString());
    }

    // ----- 批量 -----

    @Test
    @DisplayName("PATCH /api/tasks/batch-status：返回实际更新行数并触发审计")
    void shouldBatchUpdateStatus() throws Exception {
        when(taskBuss.updateStatusBatch(List.of(1, 2), (byte) 2)).thenReturn(2);

        mockMvc.perform(authed(patch("/api/tasks/batch-status"))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"ids\":[1,2],\"status\":2}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data").value(2))
                .andExpect(jsonPath("$.message").value("已更新 2 条任务"));

        verify(auditService).record(eq(TaskAuditService.ACTION_BATCH_STATUS), isNull(), anyString());
    }

    @Test
    @DisplayName("PATCH /api/tasks/batch-status：空 ids 返回 400")
    void shouldRejectEmptyBatchIds() throws Exception {
        mockMvc.perform(authed(patch("/api/tasks/batch-status"))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"ids\":[],\"status\":2}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(40001));

        verifyNoInteractions(taskBuss);
    }

    @Test
    @DisplayName("PageResult 转换：空 records 不返回 null")
    void pageResultShouldHandleNullRecords() {
        Page<Task> page = new Page<>(1, 10);
        page.setRecords(null);
        page.setTotal(0);

        PageResult<String> result = PageResult.of(page, Task::getTitle);

        assertThat(result.records()).isEmpty();
    }
}
