package cn.edu.mju.band.controller;

import cn.edu.mju.band.buss.ITaskBuss;
import cn.edu.mju.band.config.TaskPageProperties;
import cn.edu.mju.band.config.WebMvcConfig;
import cn.edu.mju.band.entity.Task;
import cn.edu.mju.band.entity.User;
import cn.edu.mju.band.exception.TaskServiceException;
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
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.flash;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.model;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.redirectedUrl;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.view;

/**
 * 控制层切片测试（@WebMvcTest）：只装配 MVC 层，Service 用 @MockBean 打桩，
 * 不启动数据库、不渲染 Thymeleaf 模板，用于验证参数绑定、服务端校验、视图名与登录拦截。
 */
@WebMvcTest(TaskController.class)
@Import({TaskPageProperties.class, WebMvcConfig.class})
@DisplayName("TaskController 控制层测试（Thymeleaf + Validation + LoginInterceptor）")
class TaskControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ITaskBuss taskBuss;

    private MockHttpSession session;

    @BeforeEach
    void setUpLoginSession() {
        User user = new User(1, "admin", "123456");
        session = new MockHttpSession();
        session.setAttribute(SessionKeys.LOGIN_USER, user);
    }

    /** 所有业务请求都携带已登录 Session，避免被 LoginInterceptor 拦截 */
    private MockHttpServletRequestBuilder authed(MockHttpServletRequestBuilder builder) {
        return builder.session(session);
    }

    private static Page<Task> pageOf(List<Task> records, long total, long current, long size) {
        Page<Task> page = new Page<>(current, size);
        page.setRecords(records);
        page.setTotal(total);
        return page;
    }

    @Test
    @DisplayName("未登录访问 /task：被 LoginInterceptor 重定向到 /login")
    void list_shouldRedirectToLoginWhenNotAuthenticated() throws Exception {
        mockMvc.perform(get("/task"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/login"));

        verifyNoInteractions(taskBuss);
    }

    @Test
    @DisplayName("GET /task：未传分页参数时使用当前环境的默认每页条数")
    void list_shouldUseDefaultPageSizeFromProfile() throws Exception {
        when(taskBuss.findPage(null, null, 1, 5)).thenReturn(pageOf(List.of(), 0, 1, 5));

        mockMvc.perform(authed(get("/task")))
                .andExpect(status().isOk())
                .andExpect(view().name("task"))
                .andExpect(model().attributeExists("page"))
                .andExpect(model().attribute("searchTitle", (Object) null))
                .andExpect(model().attributeExists("pageNumbers"));

        verify(taskBuss).findPage(null, null, 1, 5);
    }

    @Test
    @DisplayName("GET /task：名称模糊 + 状态筛选 + 分页参数正确透传")
    void list_shouldForwardFilters() throws Exception {
        when(taskBuss.findPage("报告", (byte) 1, 2, 3))
                .thenReturn(pageOf(List.of(), 7, 2, 3));

        mockMvc.perform(authed(get("/task")
                        .param("title", "报告")
                        .param("status", "1")
                        .param("pageNum", "2")
                        .param("pageSize", "3")))
                .andExpect(status().isOk())
                .andExpect(view().name("task"))
                .andExpect(model().attribute("searchStatus", (byte) 1))
                .andExpect(model().attribute("searchTitle", "报告"));

        verify(taskBuss).findPage("报告", (byte) 1, 2, 3);
    }

    @Test
    @DisplayName("GET /task：空白查询条件归一化为 null（等价于“全部”）")
    void list_shouldNormalizeBlankFilters() throws Exception {
        when(taskBuss.findPage(null, null, 1, 5)).thenReturn(pageOf(List.of(), 0, 1, 5));

        mockMvc.perform(authed(get("/task").param("title", "   ").param("status", " ")))
                .andExpect(status().isOk())
                .andExpect(view().name("task"));

        verify(taskBuss).findPage(null, null, 1, 5);
    }

    @Test
    @DisplayName("GET /task：非法状态参数进入 error 页面并返回 400")
    void list_shouldShowErrorPageWhenStatusIsNotNumeric() throws Exception {
        mockMvc.perform(authed(get("/task").param("status", "abc")))
                .andExpect(status().isBadRequest())
                .andExpect(view().name("error"))
                .andExpect(model().attribute("error", "任务状态参数非法：abc"));
    }

    @Test
    @DisplayName("GET /task：数据库故障时展示统一业务异常文案并返回 500")
    void list_shouldShowErrorPageWhenServiceFails() throws Exception {
        when(taskBuss.findPage(null, null, 1, 5))
                .thenThrow(new TaskServiceException("任务数据访问失败，数据库暂时不可用，请稍后重试"));

        mockMvc.perform(authed(get("/task")))
                .andExpect(status().is5xxServerError())
                .andExpect(view().name("error"))
                .andExpect(model().attribute("error", "任务数据访问失败，数据库暂时不可用，请稍后重试"));
    }

    @Test
    @DisplayName("GET /task?opt=add：进入新增表单，默认状态为待办")
    void addForm_shouldPrepareTodoTask() throws Exception {
        mockMvc.perform(authed(get("/task").param("opt", "add")))
                .andExpect(status().isOk())
                .andExpect(view().name("add_update"))
                .andExpect(model().attribute("opt", "add"))
                .andExpect(model().attributeExists("task"));

        // 新增表单只拼装页面数据，不访问业务层
        verifyNoInteractions(taskBuss);
    }

    @Test
    @DisplayName("GET /task?opt=update：按编号回显任务")
    void updateForm_shouldLoadTaskById() throws Exception {
        Task task = new Task();
        task.setId(7);
        task.setTitle("待修改任务");
        when(taskBuss.findById(7)).thenReturn(task);

        mockMvc.perform(authed(get("/task").param("opt", "update").param("id", "7")))
                .andExpect(status().isOk())
                .andExpect(view().name("add_update"))
                .andExpect(model().attribute("opt", "update"))
                .andExpect(model().attribute("task", task));
    }

    @Test
    @DisplayName("GET /task?opt=update：任务不存在时进入 400 错误页")
    void updateForm_shouldShowErrorWhenTaskMissing() throws Exception {
        when(taskBuss.findById(404)).thenReturn(null);

        mockMvc.perform(authed(get("/task").param("opt", "update").param("id", "404")))
                .andExpect(status().isBadRequest())
                .andExpect(view().name("error"))
                .andExpect(model().attribute("error", "任务不存在或已被删除"));
    }

    @Test
    @DisplayName("POST /task?opt=add：新增请求参数正确封装为 Task 并重定向")
    void addPost_shouldBindParams() throws Exception {
        mockMvc.perform(authed(post("/task")
                        .param("opt", "add")
                        .param("title", "新任务")
                        .param("content", "内容")
                        .param("status", "1")))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/task"))
                .andExpect(flash().attribute("message", "任务「新任务」已创建"));

        ArgumentCaptor<Task> captor = ArgumentCaptor.forClass(Task.class);
        verify(taskBuss).add(captor.capture());
        assertThat(captor.getValue().getTitle()).isEqualTo("新任务");
        assertThat(captor.getValue().getContent()).isEqualTo("内容");
        assertThat(captor.getValue().getStatus()).isEqualTo((byte) 1);
    }

    @Test
    @DisplayName("POST /task?opt=add：标题为空时回到表单并回显字段错误，不调用业务层")
    void addPost_shouldReturnFormWhenTitleBlank() throws Exception {
        mockMvc.perform(authed(post("/task")
                        .param("opt", "add")
                        .param("title", "   ")
                        .param("status", "0")))
                .andExpect(status().isOk())
                .andExpect(view().name("add_update"))
                .andExpect(model().attributeHasFieldErrors("task", "title"))
                .andExpect(model().attribute("opt", "add"));

        verifyNoInteractions(taskBuss);
    }

    @Test
    @DisplayName("POST /task?opt=add：状态越界时回到表单并回显字段错误")
    void addPost_shouldReturnFormWhenStatusIllegal() throws Exception {
        mockMvc.perform(authed(post("/task")
                        .param("opt", "add")
                        .param("title", "合法标题")
                        .param("status", "9")))
                .andExpect(status().isOk())
                .andExpect(view().name("add_update"))
                .andExpect(model().attributeHasFieldErrors("task", "status"));

        verifyNoInteractions(taskBuss);
    }

    @Test
    @DisplayName("POST /task?opt=update：更新请求携带编号并重定向")
    void updatePost_shouldBindId() throws Exception {
        mockMvc.perform(authed(post("/task")
                        .param("opt", "update")
                        .param("id", "2")
                        .param("title", "改名后的任务")
                        .param("status", "2")))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/task"));

        ArgumentCaptor<Task> captor = ArgumentCaptor.forClass(Task.class);
        verify(taskBuss).update(captor.capture());
        assertThat(captor.getValue().getId()).isEqualTo(2);
        assertThat(captor.getValue().getStatus()).isEqualTo((byte) 2);
    }

    @Test
    @DisplayName("POST /task?opt=update：缺少编号时回到表单并给出全局错误")
    void updatePost_shouldReturnFormWhenIdMissing() throws Exception {
        mockMvc.perform(authed(post("/task")
                        .param("opt", "update")
                        .param("title", "没有编号")
                        .param("status", "0")))
                .andExpect(status().isOk())
                .andExpect(view().name("add_update"))
                .andExpect(model().attributeHasErrors("task"));

        verifyNoInteractions(taskBuss);
    }

    @Test
    @DisplayName("POST /task?opt=delete：删除后重定向到列表并给出提示")
    void deletePost_shouldRedirectToList() throws Exception {
        mockMvc.perform(authed(post("/task").param("opt", "delete").param("id", "9")))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/task"))
                .andExpect(flash().attribute("message", "任务已删除"));

        verify(taskBuss).delete(eq(9));
    }
}
