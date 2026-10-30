package cn.edu.mju.band.api;

import org.springframework.http.HttpStatus;

/**
 * REST 接口统一错误码。
 *
 * <p>HTTP 状态码表达「哪一类错误」，业务码 {@code code} 表达「具体原因」，
 * 两者一起出现在响应体里，前端既可以用 HTTP 状态做统一处理，也可以按业务码精确提示。
 * 完整定义见 {@code docs/api/API.md} 与 {@code openapi.yaml}。
 */
public enum ApiErrorCode {

    /** 成功 */
    OK(0, HttpStatus.OK, "成功"),
    /** 参数缺失、格式错误、校验失败、页码越界等 */
    INVALID_PARAM(40001, HttpStatus.BAD_REQUEST, "请求参数不合法"),
    /** 未登录或会话过期 */
    UNAUTHORIZED(40100, HttpStatus.UNAUTHORIZED, "未登录或会话已过期"),
    /** 任务不存在或已被删除 */
    NOT_FOUND(40401, HttpStatus.NOT_FOUND, "资源不存在"),
    /** 数据库连接失败、SQL 执行异常 */
    DB_UNAVAILABLE(50001, HttpStatus.INTERNAL_SERVER_ERROR, "数据库暂时不可用"),
    /** 未预期的服务端异常 */
    INTERNAL_ERROR(50000, HttpStatus.INTERNAL_SERVER_ERROR, "服务器内部错误");

    private final int code;
    private final HttpStatus httpStatus;
    private final String defaultMessage;

    ApiErrorCode(int code, HttpStatus httpStatus, String defaultMessage) {
        this.code = code;
        this.httpStatus = httpStatus;
        this.defaultMessage = defaultMessage;
    }

    public int getCode() {
        return code;
    }

    public HttpStatus getHttpStatus() {
        return httpStatus;
    }

    public String getDefaultMessage() {
        return defaultMessage;
    }
}
