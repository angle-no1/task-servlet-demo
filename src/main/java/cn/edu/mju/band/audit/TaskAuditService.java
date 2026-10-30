package cn.edu.mju.band.audit;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;

/**
 * 异步审计服务。
 *
 * <p>课程报告的 Demo 要求展示「异步处理表现」：写操作（新增/修改/删除/批量改状态）
 * 只把审计事件丢给 {@code taskAuditExecutor} 线程池，HTTP 响应不必等待审计完成。
 * 方法返回 void，异常不会影响主请求，只会由异步异常处理器记录日志。
 *
 * <p>审计内容只包含任务编号与标题，不记录登录口令等敏感信息。
 */
@Service
public class TaskAuditService {

    public static final String ACTION_CREATE = "CREATE";
    public static final String ACTION_UPDATE = "UPDATE";
    public static final String ACTION_DELETE = "DELETE";
    public static final String ACTION_BATCH_STATUS = "BATCH_STATUS";

    private static final Logger log = LoggerFactory.getLogger(TaskAuditService.class);
    private static final DateTimeFormatter TIME_FORMAT = DateTimeFormatter.ISO_OFFSET_DATE_TIME;

    private final TaskAuditStore store;

    public TaskAuditService(TaskAuditStore store) {
        this.store = store;
    }

    /**
     * 记录一条审计事件（异步执行）。
     *
     * @param action 事件类型，见本类 {@code ACTION_*} 常量
     * @param taskId 任务编号；批量操作可为 null
     * @param detail 可读描述，不包含敏感信息
     */
    @Async("taskAuditExecutor")
    public void record(String action, Integer taskId, String detail) {
        String thread = Thread.currentThread().getName();
        TaskAuditEntry entry = new TaskAuditEntry(
                OffsetDateTime.now().withNano(0).format(TIME_FORMAT), thread, action, taskId, detail);
        store.add(entry);
        log.info("异步审计 action={} taskId={} detail={} thread={}", action, taskId, detail, thread);
    }
}
