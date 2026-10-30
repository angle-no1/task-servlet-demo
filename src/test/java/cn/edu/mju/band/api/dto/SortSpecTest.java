package cn.edu.mju.band.api.dto;

import cn.edu.mju.band.buss.TaskSort;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.EmptySource;
import org.junit.jupiter.params.provider.NullSource;
import org.junit.jupiter.params.provider.ValueSource;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/** 排序参数解析测试：字段、方向、格式错误。 */
@DisplayName("SortSpec 排序参数解析")
class SortSpecTest {

    @ParameterizedTest
    @NullSource
    @EmptySource
    @ValueSource(strings = {" ", "\t"})
    @DisplayName("不传 sort：默认 createTime 倒序")
    void shouldUseDefault(String raw) {
        SortSpec spec = SortSpec.parse(raw);
        assertThat(spec.field()).isEqualTo(TaskSort.CREATE_TIME);
        assertThat(spec.ascending()).isFalse();
    }

    @ParameterizedTest(name = "sort={0},{1} => asc={2}")
    @CsvSource({
            "createTime,desc,false",
            "createTime,asc,true",
            "title,asc,true",
            "STATUS,DESC,false"
    })
    @DisplayName("字段,方向 正常解析")
    void shouldParseFieldAndDirection(String field, String direction, boolean ascending) {
        SortSpec spec = SortSpec.parse(field + "," + direction);
        assertThat(spec.ascending()).isEqualTo(ascending);
    }

    @Test
    @DisplayName("只写字段时默认升序")
    void shouldDefaultToAscendingWhenDirectionMissing() {
        SortSpec spec = SortSpec.parse("title");
        assertThat(spec.field()).isEqualTo(TaskSort.TITLE);
        assertThat(spec.ascending()).isTrue();
    }

    @ParameterizedTest
    @ValueSource(strings = {
            "createTime,up",
            "createTime,",
            "createTime,desc,extra",
            "createTime;DROP TABLE t_task;--"
    })
    @DisplayName("方向或格式非法时抛 IllegalArgumentException")
    void shouldRejectMalformedSort(String raw) {
        assertThatThrownBy(() -> SortSpec.parse(raw))
                .isInstanceOf(IllegalArgumentException.class);
    }
}
