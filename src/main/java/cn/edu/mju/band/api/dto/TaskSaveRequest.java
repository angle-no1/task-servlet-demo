package cn.edu.mju.band.api.dto;

import cn.edu.mju.band.entity.Task;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

/**
 * 新增 / 修改任务的入参。
 *
 * <p>校验注解与实体上的约束保持一致，但入参不接受 {@code id}、{@code createTime}：
 * 编号来自路径，创建时间由数据库生成，避免调用方伪造。
 */
public record TaskSaveRequest(

        @NotBlank(message = "任务标题不能为空")
        @Size(max = Task.TITLE_MAX_LENGTH, message = "任务标题不能超过 100 个字符")
        String title,

        @Size(max = 2000, message = "任务内容不能超过 2000 个字符")
        String content,

        @NotNull(message = "请选择任务状态")
        @Min(value = Task.STATUS_TODO, message = "任务状态只能是 0/1/2")
        @Max(value = Task.STATUS_DONE, message = "任务状态只能是 0/1/2")
        Byte status) {

    /** 转成持久层实体；id 为 null 表示新增，非 null 表示修改 */
    public Task toEntity(Integer id) {
        Task task = new Task();
        task.setId(id);
        task.setTitle(title == null ? null : title.trim());
        task.setContent(content);
        task.setStatus(status);
        return task;
    }
}
