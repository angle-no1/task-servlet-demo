package cn.edu.mju.band.api.dto;

import cn.edu.mju.band.entity.Task;

import java.util.Date;

/**
 * 任务的接口出参。
 *
 * <p>不复用 {@link Task} 实体，避免把「实体字段 = 接口契约」绑死：
 * 实体以后可以加 {@code deleted}、{@code version} 等内部字段，而接口契约保持稳定。
 */
public record TaskView(Integer id, String title, String content, Byte status, String statusLabel, Date createTime) {

    public static TaskView from(Task task) {
        if (task == null) {
            return null;
        }
        return new TaskView(
                task.getId(),
                task.getTitle(),
                task.getContent(),
                task.getStatus(),
                label(task.getStatus()),
                task.getCreateTime());
    }

    private static String label(Byte status) {
        if (status == null) {
            return "未知";
        }
        return switch (status) {
            case Task.STATUS_TODO -> "待办";
            case Task.STATUS_DOING -> "进行中";
            case Task.STATUS_DONE -> "已完成";
            default -> "未知";
        };
    }
}
