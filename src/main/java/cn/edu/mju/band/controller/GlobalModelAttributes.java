package cn.edu.mju.band.controller;

import cn.edu.mju.band.entity.User;
import cn.edu.mju.band.web.SessionKeys;
import jakarta.servlet.http.HttpSession;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ModelAttribute;

/**
 * 给所有 Thymeleaf 页面注入当前登录用户，模板里可直接使用 ${loginUser}。
 *
 * <p>用户不存在时为 null，模板用 th:if 判断即可，不会抛异常。
 */
@ControllerAdvice
public class GlobalModelAttributes {

    @ModelAttribute("loginUser")
    public User loginUser(HttpSession session) {
        return (User) session.getAttribute(SessionKeys.LOGIN_USER);
    }
}
