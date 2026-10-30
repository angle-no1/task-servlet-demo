package cn.edu.mju.band.controller.form;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/** 登录表单：把视图字段与 User 实体解耦，避免把口令字段直接暴露给页面绑定。 */
public class LoginForm {

    @NotBlank(message = "请输入登录名")
    @Size(max = 50, message = "登录名不能超过 50 个字符")
    private String loginName;

    @NotBlank(message = "请输入密码")
    @Size(max = 100, message = "密码不能超过 100 个字符")
    private String loginPwd;

    public String getLoginName() {
        return loginName;
    }

    public void setLoginName(String loginName) {
        this.loginName = loginName;
    }

    public String getLoginPwd() {
        return loginPwd;
    }

    public void setLoginPwd(String loginPwd) {
        this.loginPwd = loginPwd;
    }
}
