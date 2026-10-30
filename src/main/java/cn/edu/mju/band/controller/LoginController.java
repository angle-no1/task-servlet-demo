package cn.edu.mju.band.controller;

import cn.edu.mju.band.buss.IUserBuss;
import cn.edu.mju.band.controller.form.LoginForm;
import cn.edu.mju.band.entity.User;
import cn.edu.mju.band.web.SessionKeys;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import jakarta.validation.Valid;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

/**
 * 登录/退出控制器（环节五）。
 *
 * <p>登录成功后把 User 放入 Session，后续请求由 {@code LoginInterceptor} 校验；
 * 登录前被拦截的 GET 地址保存在 Session 中，登录后自动回跳。
 */
@Controller
public class LoginController {

    private final IUserBuss userBuss;

    public LoginController(IUserBuss userBuss) {
        this.userBuss = userBuss;
    }

    /** 登录页；已登录用户直接进入任务列表 */
    @GetMapping("/login")
    public String loginPage(@RequestParam(value = "logout", required = false) String logout,
                            HttpSession session,
                            Model model) {
        if (session.getAttribute(SessionKeys.LOGIN_USER) != null) {
            return "redirect:/task";
        }
        if (!model.containsAttribute("loginForm")) {
            model.addAttribute("loginForm", new LoginForm());
        }
        if (logout != null) {
            model.addAttribute("message", "已安全退出登录");
        }
        return "login";
    }

    /** 提交登录：@Valid 校验空用户名/空密码，失败时回到登录页回显 */
    @PostMapping("/login")
    public String login(@Valid @ModelAttribute("loginForm") LoginForm loginForm,
                        BindingResult bindingResult,
                        HttpServletRequest request) {
        if (bindingResult.hasErrors()) {
            return "login";
        }

        User user = userBuss.login(loginForm.getLoginName(), loginForm.getLoginPwd());
        if (user == null) {
            // 不区分“账号不存在/密码错误”，避免账号枚举
            bindingResult.reject("login.failed", "用户名或密码错误");
            return "login";
        }

        HttpSession session = request.getSession(true);
        // 登录成功后更换 Session ID，防御会话固定攻击
        request.changeSessionId();
        String redirect = (String) session.getAttribute(SessionKeys.LOGIN_REDIRECT);
        session.removeAttribute(SessionKeys.LOGIN_REDIRECT);
        // Session 里只保留身份信息，不保存口令
        user.setLoginPwd(null);
        session.setAttribute(SessionKeys.LOGIN_USER, user);

        // 只允许站内相对路径，防止 open redirect
        if (redirect != null && redirect.startsWith("/")
                && !redirect.startsWith("//") && !redirect.startsWith("/login")) {
            return "redirect:" + redirect;
        }
        return "redirect:/task";
    }

    /** 退出登录：销毁 Session 后回到登录页 */
    @PostMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/login?logout";
    }
}
