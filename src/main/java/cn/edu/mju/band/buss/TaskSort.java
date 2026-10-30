package cn.edu.mju.band.buss;

import cn.edu.mju.band.entity.Task;
import com.baomidou.mybatisplus.core.toolkit.support.SFunction;

/**
 * 任务查询允许的排序字段白名单。
 *
 * <p>REST 接口允许调用方指定排序字段，但字段名绝不能直接拼进 SQL
 * （{@code ORDER BY ${sort}} 是典型的注入入口）。这里把「外部字符串 → 列」的映射
 * 收敛到枚举，非法字段在参数解析阶段就抛 {@link IllegalArgumentException}，
 * 只有枚举里声明的列才可能进入 SQL。
 */
public enum TaskSort {

    CREATE_TIME("createTime", Task::getCreateTime),
    TITLE("title", Task::getTitle),
    STATUS("status", Task::getStatus);

    private final String field;
    private final SFunction<Task, ?> column;

    TaskSort(String field, SFunction<Task, ?> column) {
        this.field = field;
        this.column = column;
    }

    /** 对外暴露的字段名（与 JSON / 查询参数一致） */
    public String getField() {
        return field;
    }

    /** 受信任的列引用，交给 MyBatis-Plus 生成 ORDER BY，不经过字符串拼接 */
    public SFunction<Task, ?> getColumn() {
        return column;
    }

    /**
     * 解析排序字段。
     *
     * @param field 外部传入的字段名，允许 null / 空白（回退到创建时间）
     * @return 白名单中的枚举项
     * @throws IllegalArgumentException 字段不在白名单内
     */
    public static TaskSort of(String field) {
        if (field == null || field.isBlank()) {
            return CREATE_TIME;
        }
        String normalized = field.trim();
        for (TaskSort sort : values()) {
            if (sort.field.equalsIgnoreCase(normalized)) {
                return sort;
            }
        }
        throw new IllegalArgumentException(
                "不支持的排序字段：" + field + "（可选：createTime、title、status）");
    }
}
