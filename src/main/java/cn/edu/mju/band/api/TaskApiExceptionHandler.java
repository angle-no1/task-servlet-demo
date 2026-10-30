package cn.edu.mju.band.api;

import cn.edu.mju.band.exception.ServiceException;
import cn.edu.mju.band.exception.TaskNotFoundException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpStatus;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * REST 接口统一异常处理。
 *
 * <p>与页面侧的 {@code GlobalExceptionHandler}（返回 error.html）分工明确：
 * 本类只作用于 {@code cn.edu.mju.band.api} 包下的控制器，并设置最高优先级，
 * 保证 API 请求拿到 JSON 错误体而不是 HTML 错误页。
 */
@RestControllerAdvice(basePackages = "cn.edu.mju.band.api")
@Order(Ordered.HIGHEST_PRECEDENCE)
public class TaskApiExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(TaskApiExceptionHandler.class);

    /** Bean Validation 失败：返回 400 + 字段级错误明细 */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Map<String, String>> onValidationFailed(MethodArgumentNotValidException e) {
        Map<String, String> errors = new LinkedHashMap<>();
        for (FieldError fieldError : e.getBindingResult().getFieldErrors()) {
            errors.putIfAbsent(fieldError.getField(), fieldError.getDefaultMessage());
        }
        e.getBindingResult().getGlobalErrors()
                .forEach(error -> errors.putIfAbsent("_global", error.getDefaultMessage()));

        String message = errors.values().stream().findFirst()
                .orElse(ApiErrorCode.INVALID_PARAM.getDefaultMessage());
        log.warn("API 参数校验失败：{}", errors);
        return ApiResponse.error(ApiErrorCode.INVALID_PARAM, message, errors);
    }

    /** JSON 语法错误、字段类型不匹配、缺少查询参数 */
    @ExceptionHandler({
            HttpMessageNotReadableException.class,
            MethodArgumentTypeMismatchException.class,
            MissingServletRequestParameterException.class
    })
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> onMalformedRequest(Exception e) {
        log.warn("API 请求无法解析：{}", e.getMessage());
        return ApiResponse.error(ApiErrorCode.INVALID_PARAM, "请求参数格式错误，请检查 JSON 与字段类型");
    }

    /** 业务参数不合法：页码越界、非法状态、非法排序字段等 */
    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> onIllegalArgument(IllegalArgumentException e) {
        log.warn("API 业务参数不合法：{}", e.getMessage());
        return ApiResponse.error(ApiErrorCode.INVALID_PARAM, e.getMessage());
    }

    /** 任务不存在：404，而不是把 null 当正常结果或抛 NPE */
    @ExceptionHandler(TaskNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ApiResponse<Void> onTaskNotFound(TaskNotFoundException e) {
        log.warn("API 资源不存在：{}", e.getMessage());
        return ApiResponse.error(ApiErrorCode.NOT_FOUND, e.getMessage());
    }

    /** 数据库不可用等业务异常：500 + 稳定文案，不泄漏堆栈与 SQL */
    @ExceptionHandler(ServiceException.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiResponse<Void> onServiceException(ServiceException e) {
        log.error("API 业务处理失败：{}", e.getMessage(), e);
        return ApiResponse.error(ApiErrorCode.DB_UNAVAILABLE, e.getMessage());
    }

    /** 兜底：未预期异常只返回通用文案，细节留在服务端日志 */
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiResponse<Void> onUnexpectedException(Exception e) {
        log.error("API 未预期异常", e);
        return ApiResponse.error(ApiErrorCode.INTERNAL_ERROR);
    }
}
