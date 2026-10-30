package cn.edu.mju.band.exception;

/** 任务业务异常：数据库宕机、断网、超时等任务相关故障。 */
public class TaskServiceException extends ServiceException {

    public TaskServiceException(String message) {
        super(message);
    }

    public TaskServiceException(String message, Throwable cause) {
        super(message, cause);
    }
}
