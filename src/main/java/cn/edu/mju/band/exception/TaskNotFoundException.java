package cn.edu.mju.band.exception;

/**
 * 任务不存在。
 *
 * <p>继承 {@link ServiceException} 以便页面侧仍由统一异常处理器兜底；
 * REST 侧由 {@code TaskApiExceptionHandler} 单独映射为 404 + 业务码 40401，
 * 而不是笼统的 500。
 */
public class TaskNotFoundException extends ServiceException {

    public TaskNotFoundException(String message) {
        super(message);
    }
}
