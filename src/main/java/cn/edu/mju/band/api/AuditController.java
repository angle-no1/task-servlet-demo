package cn.edu.mju.band.api;

import cn.edu.mju.band.audit.TaskAuditEntry;
import cn.edu.mju.band.audit.TaskAuditStore;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 审计事件查询接口，用于 Demo 观察异步结果。
 *
 * <p>事件由 {@code TaskAuditService} 在 {@code task-audit-*} 线程写入内存队列，
 * 这里按时间倒序读取最近 N 条；生产环境应改为查询持久化审计表/日志平台。
 */
@RestController
@RequestMapping("/api/audits")
public class AuditController {

    private static final int MAX_LIMIT = TaskAuditStore.MAX_ENTRIES;

    private final TaskAuditStore auditStore;

    public AuditController(TaskAuditStore auditStore) {
        this.auditStore = auditStore;
    }

    @GetMapping
    public ApiResponse<List<TaskAuditEntry>> recent(
            @RequestParam(value = "limit", defaultValue = "20") int limit) {
        if (limit < 1 || limit > MAX_LIMIT) {
            throw new IllegalArgumentException("limit 必须在 1 到 " + MAX_LIMIT + " 之间");
        }
        return ApiResponse.ok(auditStore.recent(limit));
    }
}
