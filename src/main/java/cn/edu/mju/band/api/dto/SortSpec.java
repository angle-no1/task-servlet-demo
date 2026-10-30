package cn.edu.mju.band.api.dto;

import cn.edu.mju.band.buss.TaskSort;

import java.util.Locale;

/**
 * 排序参数解析结果。
 *
 * <p>接口约定 {@code sort=字段,方向}，例如 {@code sort=title,asc}；
 * 只写字段时默认升序，完全不传时默认 {@code createTime,desc}。
 * 字段必须命中 {@link TaskSort} 白名单，方向只能是 asc / desc。
 */
public record SortSpec(TaskSort field, boolean ascending) {

    public static final String DEFAULT_SORT = "createTime,desc";

    public static SortSpec parse(String raw) {
        if (raw == null || raw.isBlank()) {
            return new SortSpec(TaskSort.CREATE_TIME, false);
        }

        String[] parts = raw.trim().split(",", -1);
        if (parts.length > 2) {
            throw new IllegalArgumentException("排序参数格式应为 field,asc|desc，例如 createTime,desc");
        }

        TaskSort field = TaskSort.of(parts[0]);
        if (parts.length == 1) {
            return new SortSpec(field, true);
        }

        String direction = parts[1].trim().toLowerCase(Locale.ROOT);
        if ("asc".equals(direction)) {
            return new SortSpec(field, true);
        }
        if ("desc".equals(direction)) {
            return new SortSpec(field, false);
        }
        throw new IllegalArgumentException("排序方向只能是 asc 或 desc，收到：" + parts[1]);
    }
}
