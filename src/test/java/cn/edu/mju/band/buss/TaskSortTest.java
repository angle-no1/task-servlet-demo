package cn.edu.mju.band.buss;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EmptySource;
import org.junit.jupiter.params.provider.NullSource;
import org.junit.jupiter.params.provider.ValueSource;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/** 排序字段白名单测试：重点验证注入载荷无法通过解析。 */
@DisplayName("TaskSort 排序白名单")
class TaskSortTest {

    @ParameterizedTest
    @NullSource
    @EmptySource
    @ValueSource(strings = {" ", "   "})
    @DisplayName("null / 空串 / 空白：回退到创建时间")
    void shouldFallbackToCreateTime(String raw) {
        assertThat(TaskSort.of(raw)).isEqualTo(TaskSort.CREATE_TIME);
    }

    @ParameterizedTest
    @ValueSource(strings = {"createTime", "CREATETIME", " title ", "status"})
    @DisplayName("白名单字段大小写不敏感、允许首尾空白")
    void shouldParseAllowedFields(String raw) {
        assertThat(TaskSort.of(raw)).isIn(TaskSort.CREATE_TIME, TaskSort.TITLE, TaskSort.STATUS);
    }

    @Test
    @DisplayName("title 映射到实体列引用而不是字符串")
    void shouldExposeColumnFunction() {
        assertThat(TaskSort.TITLE.getField()).isEqualTo("title");
        assertThat(TaskSort.TITLE.getColumn()).isNotNull();
    }

    @ParameterizedTest
    @ValueSource(strings = {
            "createTime;DROP TABLE t_task;--",
            "id",
            "password",
            "create_time",
            "createTime desc",
            "1"
    })
    @DisplayName("非白名单字段（含 SQL 注入载荷）一律抛 IllegalArgumentException")
    void shouldRejectUnknownFields(String raw) {
        assertThatThrownBy(() -> TaskSort.of(raw))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("不支持的排序字段");
    }
}
