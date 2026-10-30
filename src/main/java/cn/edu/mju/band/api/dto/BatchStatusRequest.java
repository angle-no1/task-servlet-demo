package cn.edu.mju.band.api.dto;

import cn.edu.mju.band.entity.Task;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.util.List;

/**
 * 批量修改状态的入参。
 *
 * <p>{@code ids} 上限 100 与 {@code TaskBuss.MAX_BATCH_SIZE} 对齐：
 * 一次 IN 查询最多 100 个占位符，避免 SQL 过长和长事务。
 */
public record BatchStatusRequest(

        @NotEmpty(message = "待更新的任务编号不能为空")
        @Size(max = 100, message = "一次最多更新 100 条任务")
        List<@NotNull(message = "任务编号不能为空") Integer> ids,

        @NotNull(message = "请选择任务状态")
        @Min(value = Task.STATUS_TODO, message = "任务状态只能是 0/1/2")
        @Max(value = Task.STATUS_DONE, message = "任务状态只能是 0/1/2")
        Byte status) {
}
