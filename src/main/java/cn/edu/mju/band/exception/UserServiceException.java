package cn.edu.mju.band.exception;

/** 用户/登录业务异常：用户表不可用等故障。 */
public class UserServiceException extends ServiceException {

    public UserServiceException(String message, Throwable cause) {
        super(message, cause);
    }
}
