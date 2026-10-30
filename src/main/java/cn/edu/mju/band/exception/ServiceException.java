package cn.edu.mju.band.exception;

/**
 * 业务层统一异常基类。
 *
 * <p>把 DataAccessException 等基础设施异常翻译成面向用户的业务异常后，
 * 由 {@code GlobalExceptionHandler} 统一渲染错误页，避免持久层细节泄漏到页面。
 */
public class ServiceException extends RuntimeException {

    public ServiceException(String message) {
        super(message);
    }

    public ServiceException(String message, Throwable cause) {
        super(message, cause);
    }
}
