package cn.edu.mju.band.controller;

import cn.edu.mju.band.exception.ServiceException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.support.DefaultMessageSourceResolvable;
import org.springframework.http.HttpStatus;
import org.springframework.ui.Model;
import org.springframework.validation.BindException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;

/**
 * 全局异常处理：替代旧 web.xml 里 error-page 的粗粒度跳转。
 *
 * <p>参数校验失败 → 400 + 提示用户改正；持久层不可用 → 500 + 提示稍后重试，
 * 页面不再抛出 Whitelabel 500 堆栈。
 */
@ControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /** 业务参数不合法（空标题、非法状态、页码越界、任务不存在等） */
    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public String handleIllegalArgument(IllegalArgumentException e, Model model) {
        log.warn("请求参数不合法：{}", e.getMessage());
        model.addAttribute("error", e.getMessage());
        return "error";
    }

    /** 表单绑定/校验失败（例如未携带 BindingResult 的 @Valid 参数） */
    @ExceptionHandler(BindException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public String handleBindException(BindException e, Model model) {
        String message = e.getBindingResult().getAllErrors().stream()
                .findFirst()
                .map(DefaultMessageSourceResolvable::getDefaultMessage)
                .orElse("请求参数不合法");
        log.warn("表单校验失败：{}", message);
        model.addAttribute("error", message);
        return "error";
    }

    /** 数据库宕机 / 网络异常等持久层故障（任务、用户共用同一套错误页） */
    @ExceptionHandler(ServiceException.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public String handleServiceException(ServiceException e, Model model) {
        log.error("业务处理失败：{}", e.getMessage(), e);
        model.addAttribute("error", e.getMessage());
        return "error";
    }
}
