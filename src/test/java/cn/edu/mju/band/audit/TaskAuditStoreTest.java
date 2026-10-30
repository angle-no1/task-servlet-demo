package cn.edu.mju.band.audit;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

/** 有界审计队列测试：顺序、上限淘汰、空入参。 */
@DisplayName("TaskAuditStore 有界审计队列")
class TaskAuditStoreTest {

    private static TaskAuditEntry entry(int id) {
        return new TaskAuditEntry("2026-10-30T09:00:00+08:00", "test-thread", "CREATE", id, "title-" + id);
    }

    @Test
    @DisplayName("按时间倒序返回（最后写入的在最前）")
    void shouldReturnNewestFirst() {
        TaskAuditStore store = new TaskAuditStore();
        store.add(entry(1));
        store.add(entry(2));

        assertThat(store.recent(10)).extracting(TaskAuditEntry::taskId)
                .containsExactly(2, 1);
    }

    @Test
    @DisplayName("超过上限时淘汰最旧事件，最多保留 200 条")
    void shouldEvictOldestBeyondLimit() {
        TaskAuditStore store = new TaskAuditStore();
        for (int i = 1; i <= TaskAuditStore.MAX_ENTRIES + 30; i++) {
            store.add(entry(i));
        }

        assertThat(store.size()).isEqualTo(TaskAuditStore.MAX_ENTRIES);
        List<TaskAuditEntry> recent = store.recent(TaskAuditStore.MAX_ENTRIES);
        assertThat(recent).hasSize(TaskAuditStore.MAX_ENTRIES);
        assertThat(recent.get(0).taskId()).isEqualTo(TaskAuditStore.MAX_ENTRIES + 30);
        assertThat(recent).extracting(TaskAuditEntry::taskId)
                .doesNotContain(1, 2, 3);
    }

    @Test
    @DisplayName("limit<=0 返回空列表，null 事件被忽略")
    void shouldHandleEdgeCases() {
        TaskAuditStore store = new TaskAuditStore();
        store.add(null);
        store.add(entry(1));

        assertThat(store.recent(0)).isEmpty();
        assertThat(store.recent(-1)).isEmpty();
        assertThat(store.recent(1)).hasSize(1);
    }

    @Test
    @DisplayName("clear 清空全部事件")
    void shouldClear() {
        TaskAuditStore store = new TaskAuditStore();
        store.add(entry(1));
        store.clear();

        assertThat(store.size()).isZero();
        assertThat(store.recent(10)).isEmpty();
    }
}
