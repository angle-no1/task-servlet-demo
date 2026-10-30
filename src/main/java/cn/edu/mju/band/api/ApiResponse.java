package cn.edu.mju.band.api;

import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;

/**
 * REST 接口统一响应体。
 *
 * <pre>{@code
 * { "code": 0, "message": "成功", "data": { ... }, "timestamp": "2026-10-30T09:30:00+08:00" }
 * }</pre>
 *
 * <p>{@code code=0} 表示成功；非 0 时与 HTTP 状态码配合使用，取值见 {@link ApiErrorCode}。
 *
 * @param <T> 业务数据类型
 */
public record ApiResponse<T>(int code, String message, T data, String timestamp) {

    private static final DateTimeFormatter TIMESTAMP_FORMAT = DateTimeFormatter.ISO_OFFSET_DATE_TIME;

    /** 成功，附带业务数据 */
    public static <T> ApiResponse<T> ok(T data) {
        return new ApiResponse<>(ApiErrorCode.OK.getCode(), ApiErrorCode.OK.getDefaultMessage(), data, now());
    }

    /** 成功，自定义提示文案 */
    public static <T> ApiResponse<T> ok(String message, T data) {
        return new ApiResponse<>(ApiErrorCode.OK.getCode(), message, data, now());
    }

    /** 失败，使用错误码的默认文案 */
    public static <T> ApiResponse<T> error(ApiErrorCode errorCode) {
        return error(errorCode, errorCode.getDefaultMessage());
    }

    /** 失败，使用更具体的文案 */
    public static <T> ApiResponse<T> error(ApiErrorCode errorCode, String message) {
        return new ApiResponse<>(errorCode.getCode(), message, null, now());
    }

    /** 失败，附带结构化细节（例如字段校验错误集合） */
    public static <T> ApiResponse<T> error(ApiErrorCode errorCode, String message, T data) {
        return new ApiResponse<>(errorCode.getCode(), message, data, now());
    }

    private static String now() {
        // 截断到秒：与文档示例保持一致，避免响应里出现 7 位纳秒
        return OffsetDateTime.now().withNano(0).format(TIMESTAMP_FORMAT);
    }
}
