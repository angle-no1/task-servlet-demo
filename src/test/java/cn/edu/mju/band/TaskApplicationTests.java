package cn.edu.mju.band;

import cn.edu.mju.band.audit.TaskAuditEntry;
import cn.edu.mju.band.audit.TaskAuditStore;
import cn.edu.mju.band.buss.ITaskBuss;
import cn.edu.mju.band.buss.IUserBuss;
import cn.edu.mju.band.config.TaskPageProperties;
import cn.edu.mju.band.entity.Task;
import cn.edu.mju.band.entity.User;
import cn.edu.mju.band.web.SessionKeys;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.env.Environment;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.transaction.annotation.Transactional;

import javax.sql.DataSource;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * 集成测试：以 test 环境（H2 内存库）启动完整 Spring 容器，
 * 验证“多环境配置真的生效”以及 MyBatis-Plus 分页、事务与登录的端到端行为。
 */
@SpringBootTest
@ActiveProfiles("test")
@AutoConfigureMockMvc
@Transactional
@DisplayName("SpringBoot 容器 + test 环境集成测试")
class TaskApplicationTests {

    @Autowired
    private Environment environment;

    @Autowired
    private ITaskBuss taskBuss;

    @Autowired
    private IUserBuss userBuss;

    @Autowired
    private TaskPageProperties pageProperties;

    @Autowired
    private DataSource dataSource;

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private TaskAuditStore auditStore;

    @Test
    @DisplayName("激活的 Profile 为 test")
    void shouldActivateTestProfile() {
        assertThat(environment.getActiveProfiles()).containsExactly("test");
    }

    @Test
    @DisplayName("test 环境的分页业务参数为 3（与 dev=5、prod=10 隔离）")
    void shouldLoadTestProfileBusinessParam() {
        assertThat(pageProperties.getDefaultSize()).isEqualTo(3);
    }

    @Test
    @DisplayName("test 环境数据源为 H2 内存库，而不是物理 MySQL")
    void shouldUseH2DataSource() throws Exception {
        try (Connection connection = dataSource.getConnection()) {
            assertThat(connection.getMetaData().getURL()).contains("jdbc:h2:mem:taskdb");
        }
    }

    @Test
    @DisplayName("MyBatis-Plus + 事务：新增 / 查询 / 修改状态 / 删除全链路可用")
    void shouldCompleteCrudFlow() {
        Task task = new Task();
        task.setTitle("集成测试任务");
        task.setContent("H2 内存库");
        task.setStatus(Task.STATUS_TODO);

        assertThat(taskBuss.add(task)).isTrue();
        assertThat(task.getId()).isNotNull();

        Task saved = taskBuss.findById(task.getId());
        assertThat(saved).isNotNull();
        assertThat(saved.getTitle()).isEqualTo("集成测试任务");

        saved.setStatus(Task.STATUS_DOING);
        assertThat(taskBuss.update(saved)).isTrue();
        assertThat(taskBuss.findById(task.getId()).getStatus()).isEqualTo(Task.STATUS_DOING);

        assertThat(taskBuss.delete(task.getId())).isTrue();
        assertThat(taskBuss.findById(task.getId())).isNull();
    }

    @Test
    @DisplayName("MyBatis-Plus 分页插件：3 条/页，7 条数据共 3 页，末页 1 条")
    void shouldPageWithMybatisPlus() {
        Page<Task> firstPage = taskBuss.findPage(null, null, 1, 3);

        assertThat(firstPage.getTotal()).isEqualTo(7);
        assertThat(firstPage.getPages()).isEqualTo(3);
        assertThat(firstPage.getRecords()).hasSize(3);
        assertThat(firstPage.getCurrent()).isEqualTo(1);
        assertThat(firstPage.getSize()).isEqualTo(3);

        Page<Task> lastPage = taskBuss.findPage(null, null, 3, 3);
        assertThat(lastPage.getRecords()).hasSize(1);
    }

    @Test
    @DisplayName("条件构造器：状态筛选与标题模糊查询都由 MyBatis-Plus 生成 SQL")
    void shouldFilterByStatusAndTitle() {
        Page<Task> doneTasks = taskBuss.findPage(null, Task.STATUS_DONE, 1, 3);
        assertThat(doneTasks.getTotal()).isEqualTo(2);

        Page<Task> matched = taskBuss.findPage("JaCoCo", null, 1, 3);
        assertThat(matched.getTotal()).isEqualTo(1);
        assertThat(matched.getRecords()).singleElement()
                .extracting(Task::getTitle).isEqualTo("生成 JaCoCo 报告");
    }

    @Test
    @DisplayName("登录：种子账号 admin/123456 可登录，错误密码与不存在的账号被拒绝")
    void shouldLoginWithSeededUsers() {
        User admin = userBuss.login("admin", "123456");
        assertThat(admin).isNotNull();
        assertThat(admin.getLoginName()).isEqualTo("admin");

        assertThat(userBuss.login("admin", "bad-password")).isNull();
        assertThat(userBuss.login("nobody", "123456")).isNull();
    }

    @Test
    @DisplayName("业务校验：空标题在进入 SQL 之前被拦截")
    void shouldRejectBlankTitleBeforeSql() {
        Task task = new Task();
        task.setTitle("   ");
        task.setStatus(Task.STATUS_TODO);

        assertThatThrownBy(() -> taskBuss.add(task))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("任务名称不能为空");
    }

    // =====================================================================
    // REST API 端到端：鉴权、CRUD、批量改状态、注入防护、异步审计
    // =====================================================================

    private MockHttpSession loggedInSession() {
        MockHttpSession session = new MockHttpSession();
        session.setAttribute(SessionKeys.LOGIN_USER, new User(1, "admin", null));
        return session;
    }

    private static int readId(MvcResult result, ObjectMapper objectMapper) throws Exception {
        return objectMapper.readTree(result.getResponse().getContentAsString(StandardCharsets.UTF_8))
                .path("data").path("id").asInt();
    }

    @Test
    @DisplayName("REST API：未登录返回 401 JSON，而不是 302 登录页")
    void apiShouldRequireLogin() throws Exception {
        mockMvc.perform(get("/api/tasks"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.code").value(40100));
    }

    @Test
    @DisplayName("REST API：新增 → 查询 → 批量改状态 → 删除 全链路")
    void apiShouldCompleteCrudFlow() throws Exception {
        MockHttpSession session = loggedInSession();

        MvcResult created = mockMvc.perform(post("/api/tasks")
                        .session(session)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"API 集成任务\",\"content\":\"H2\",\"status\":1}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.code").value(0))
                .andReturn();
        int id = readId(created, objectMapper);

        mockMvc.perform(get("/api/tasks/" + id).session(session))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.title").value("API 集成任务"))
                .andExpect(jsonPath("$.data.statusLabel").value("进行中"));

        mockMvc.perform(patch("/api/tasks/batch-status")
                        .session(session)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"ids\":[" + id + "],\"status\":2}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data").value(1));

        assertThat(taskBuss.findById(id).getStatus()).isEqualTo(Task.STATUS_DONE);

        mockMvc.perform(delete("/api/tasks/" + id).session(session))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").value("任务已删除"));

        mockMvc.perform(get("/api/tasks/" + id).session(session))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.code").value(40401));
    }

    @Test
    @DisplayName("REST API：sort 注入载荷返回 400，t_task 表与 7 条种子数据完好")
    void apiShouldRejectSqlInjectionAndKeepTableIntact() throws Exception {
        mockMvc.perform(get("/api/tasks")
                        .session(loggedInSession())
                        .param("sort", "createTime;DROP TABLE t_task;--"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(40001));

        Page<Task> page = taskBuss.findPage(null, null, 1, 3);
        assertThat(page.getTotal()).isEqualTo(7);
    }

    @Test
    @DisplayName("REST API：写操作触发异步审计，事件由 task-audit-* 线程写入")
    void apiShouldWriteAuditAsynchronously() throws Exception {
        MvcResult created = mockMvc.perform(post("/api/tasks")
                        .session(loggedInSession())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"异步审计任务\",\"status\":0}"))
                .andExpect(status().isCreated())
                .andReturn();
        int id = readId(created, objectMapper);

        List<TaskAuditEntry> entries = awaitAuditFor(id);
        assertThat(entries).anySatisfy(entry -> {
            assertThat(entry.action()).isEqualTo("CREATE");
            assertThat(entry.thread()).startsWith("task-audit-");
        });
    }

    /** 异步线程与测试线程并发，轮询等待审计事件出现（最多 2 秒） */
    private List<TaskAuditEntry> awaitAuditFor(int taskId) throws InterruptedException {
        long deadline = System.currentTimeMillis() + 2000;
        while (System.currentTimeMillis() < deadline) {
            List<TaskAuditEntry> matched = auditStore.recent(TaskAuditStore.MAX_ENTRIES).stream()
                    .filter(entry -> Integer.valueOf(taskId).equals(entry.taskId()))
                    .toList();
            if (!matched.isEmpty()) {
                return matched;
            }
            Thread.sleep(20);
        }
        return List.of();
    }
}
