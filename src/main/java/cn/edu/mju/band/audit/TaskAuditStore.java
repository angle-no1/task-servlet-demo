package cn.edu.mju.band.audit;

import org.springframework.stereotype.Component;

import java.util.Deque;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedDeque;

/**
 * 进程内审计存储。
 *
 * <p>演示项目不引入 Kafka/ELK，用有界内存队列保留最近 {@value #MAX_ENTRIES} 条事件，
 * 既方便 Demo 立即看到异步结果，又不会无限增长。生产环境应替换为消息队列 + 持久化。
 */
@Component
public class TaskAuditStore {

    /** 最多保留的审计事件条数 */
    public static final int MAX_ENTRIES = 200;

    private final Deque<TaskAuditEntry> entries = new ConcurrentLinkedDeque<>();

    /** 新事件插入队首，超出上限时淘汰最旧的事件 */
    public void add(TaskAuditEntry entry) {
        if (entry == null) {
            return;
        }
        entries.addFirst(entry);
        while (entries.size() > MAX_ENTRIES) {
            entries.pollLast();
        }
    }

    /** 按时间倒序返回最近 limit 条事件 */
    public List<TaskAuditEntry> recent(int limit) {
        if (limit <= 0) {
            return List.of();
        }
        return entries.stream().limit(limit).toList();
    }

    public int size() {
        return entries.size();
    }

    public void clear() {
        entries.clear();
    }
}
