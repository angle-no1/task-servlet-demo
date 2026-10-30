package cn.edu.mju.band.api;

import cn.edu.mju.band.api.dto.BatchStatusRequest;
import cn.edu.mju.band.api.dto.PageResult;
import cn.edu.mju.band.api.dto.SortSpec;
import cn.edu.mju.band.api.dto.TaskSaveRequest;
import cn.edu.mju.band.api.dto.TaskView;
import cn.edu.mju.band.audit.TaskAuditService;
import cn.edu.mju.band.buss.ITaskBuss;
import cn.edu.mju.band.entity.Task;
import cn.edu.mju.band.exception.TaskNotFoundException;
import cn.edu.mju.band.exception.TaskServiceException;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import jakarta.validation.Valid;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * 任务 REST 接口。
 *
 * <p>页面侧仍由 {@code TaskController} 渲染 Thymeleaf；这里为「API 手册 / Demo / 自动化验证」
 * 提供一套 JSON 契约，两者复用同一个 {@link ITaskBuss}，业务规则只有一份。
 *
 * <p>接口约定：
 * <ul>
 *   <li>统一响应体 {@link ApiResponse}，成功 {@code code=0}；</li>
 *   <li>错误由 {@link TaskApiExceptionHandler} 统一转换，业务码见 {@link ApiErrorCode}；</li>
 *   <li>排序字段只接受 {@code createTime / title / status} 白名单，防止 ORDER BY 注入；</li>
 *   <li>会话鉴权沿用 {@code LoginInterceptor}，未登录返回 401 JSON 而不是登录页。</li>
 * </ul>
 */
@RestController
@RequestMapping("/api/tasks")
public class TaskRestController {

    private final ITaskBuss taskBuss;
    private final TaskAuditService auditService;

    public TaskRestController(ITaskBuss taskBuss, TaskAuditService auditService) {
        this.taskBuss = taskBuss;
        this.auditService = auditService;
    }

    /** 分页查询：标题模糊 + 状态精确 + 白名单排序；默认第 1 页、每页 10 条 */
    @GetMapping
    public ApiResponse<PageResult<TaskView>> list(
            @RequestParam(value = "title", required = false) String title,
            @RequestParam(value = "status", required = false) Byte status,
            @RequestParam(value = "pageNum", defaultValue = "1") int pageNum,
            @RequestParam(value = "pageSize", defaultValue = "10") int pageSize,
            @RequestParam(value = "sort", defaultValue = SortSpec.DEFAULT_SORT) String sort) {

        SortSpec sortSpec = SortSpec.parse(sort);
        Page<Task> page = taskBuss.findPage(
                title, status, pageNum, pageSize, sortSpec.field(), sortSpec.ascending());
        return ApiResponse.ok(PageResult.of(page, TaskView::from));
    }

    /** 按编号查询；不存在时明确返回 404，而不是 200 + data=null */
    @GetMapping("/{id}")
    public ApiResponse<TaskView> get(@PathVariable("id") Integer id) {
        Task task = taskBuss.findById(id);
        if (task == null) {
            throw new TaskNotFoundException("任务不存在：" + id);
        }
        return ApiResponse.ok(TaskView.from(task));
    }

    /** 新增任务；成功返回 201 与 Location 头 */
    @PostMapping
    public ResponseEntity<ApiResponse<TaskView>> create(@Valid @RequestBody TaskSaveRequest request) {
        Task task = request.toEntity(null);
        if (!taskBuss.add(task)) {
            throw new TaskServiceException("任务创建失败，请稍后重试");
        }

        // 主键由 MyBatis-Plus 回填后重新查询，拿到数据库生成的 create_time
        Task saved = taskBuss.findById(task.getId());
        auditService.record(TaskAuditService.ACTION_CREATE, task.getId(), task.getTitle());

        return ResponseEntity.status(HttpStatus.CREATED)
                .header(HttpHeaders.LOCATION, "/api/tasks/" + task.getId())
                .body(ApiResponse.ok("任务已创建", TaskView.from(saved != null ? saved : task)));
    }

    /** 修改任务；记录不存在时返回 404 */
    @PutMapping("/{id}")
    public ApiResponse<TaskView> update(@PathVariable("id") Integer id,
                                        @Valid @RequestBody TaskSaveRequest request) {
        Task task = request.toEntity(id);
        if (!taskBuss.update(task)) {
            throw new TaskNotFoundException("任务不存在或已被删除：" + id);
        }

        Task saved = taskBuss.findById(id);
        auditService.record(TaskAuditService.ACTION_UPDATE, id, task.getTitle());
        return ApiResponse.ok("任务已更新", TaskView.from(saved != null ? saved : task));
    }

    /** 删除任务；记录不存在时返回 404 */
    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable("id") Integer id) {
        if (!taskBuss.delete(id)) {
            throw new TaskNotFoundException("任务不存在或已被删除：" + id);
        }
        auditService.record(TaskAuditService.ACTION_DELETE, id, null);
        return ApiResponse.ok("任务已删除", null);
    }

    /** 批量修改状态：一条 UPDATE ... WHERE id IN (...) 完成，避免 N+1 */
    @PatchMapping("/batch-status")
    public ApiResponse<Integer> batchStatus(@Valid @RequestBody BatchStatusRequest request) {
        int updated = taskBuss.updateStatusBatch(request.ids(), request.status());
        auditService.record(TaskAuditService.ACTION_BATCH_STATUS, null,
                "ids=" + request.ids() + ", status=" + request.status());
        return ApiResponse.ok("已更新 " + updated + " 条任务", updated);
    }
}
