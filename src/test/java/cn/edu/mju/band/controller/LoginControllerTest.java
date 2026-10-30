package cn.edu.mju.band.controller;

import cn.edu.mju.band.buss.IUserBuss;
import cn.edu.mju.band.config.WebMvcConfig;
import cn.edu.mju.band.entity.User;
import cn.edu.mju.band.web.SessionKeys;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.test.web.servlet.MockMvc;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.model;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.redirectedUrl;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.view;

/**
 * 登录/退出控制层测试：覆盖表单回显、登录成功、登录失败、原地址回跳、会话销毁。
 */
@WebMvcTest(LoginController.class)
@Import(WebMvcConfig.class)
@DisplayName("LoginController 登录测试")
class LoginControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private IUserBuss userBuss;

    private static User admin() {
        return new User(1, "admin", "123456");
    }

    @Test
    @DisplayName("GET /login：未登录时展示登录表单")
    void loginPage_shouldShowForm() throws Exception {
        mockMvc.perform(get("/login"))
                .andExpect(status().isOk())
                .andExpect(view().name("login"))
                .andExpect(model().attributeExists("loginForm"));
    }

    @Test
    @DisplayName("GET /login?logout：展示退出成功提示")
    void loginPage_shouldShowLogoutMessage() throws Exception {
        mockMvc.perform(get("/login").param("logout", ""))
                .andExpect(status().isOk())
                .andExpect(view().name("login"))
                .andExpect(model().attribute("message", "已安全退出登录"));
    }

    @Test
    @DisplayName("GET /login：已登录用户直接进入任务列表")
    void loginPage_shouldRedirectWhenAlreadyLoggedIn() throws Exception {
        MockHttpSession session = new MockHttpSession();
        session.setAttribute(SessionKeys.LOGIN_USER, admin());

        mockMvc.perform(get("/login").session(session))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/task"));
    }

    @Test
    @DisplayName("POST /login：账号密码正确时写入 Session 并跳转 /task")
    void loginPost_shouldStoreUserAndRedirect() throws Exception {
        when(userBuss.login("admin", "123456")).thenReturn(admin());
        MockHttpSession session = new MockHttpSession();

        mockMvc.perform(post("/login")
                        .session(session)
                        .param("loginName", "admin")
                        .param("loginPwd", "123456"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/task"));

        assertThat(session.getAttribute(SessionKeys.LOGIN_USER)).isInstanceOf(User.class);
    }

    @Test
    @DisplayName("POST /login：登录成功后回到被拦截前的地址")
    void loginPost_shouldRedirectToSavedTarget() throws Exception {
        when(userBuss.login("admin", "123456")).thenReturn(admin());
        MockHttpSession session = new MockHttpSession();
        session.setAttribute(SessionKeys.LOGIN_REDIRECT, "/task?opt=add");

        mockMvc.perform(post("/login")
                        .session(session)
                        .param("loginName", "admin")
                        .param("loginPwd", "123456"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/task?opt=add"));
    }

    @Test
    @DisplayName("POST /login：站外地址不会被当作回跳目标（防 open redirect）")
    void loginPost_shouldIgnoreExternalRedirect() throws Exception {
        when(userBuss.login("admin", "123456")).thenReturn(admin());
        MockHttpSession session = new MockHttpSession();
        session.setAttribute(SessionKeys.LOGIN_REDIRECT, "//evil.example.com/steal");

        mockMvc.perform(post("/login")
                        .session(session)
                        .param("loginName", "admin")
                        .param("loginPwd", "123456"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/task"));
    }

    @Test
    @DisplayName("POST /login：密码错误时回到登录页并显示全局错误")
    void loginPost_shouldShowErrorWhenPasswordWrong() throws Exception {
        when(userBuss.login("admin", "bad")).thenReturn(null);

        mockMvc.perform(post("/login")
                        .param("loginName", "admin")
                        .param("loginPwd", "bad"))
                .andExpect(status().isOk())
                .andExpect(view().name("login"))
                .andExpect(model().attributeHasErrors("loginForm"));
    }

    @Test
    @DisplayName("POST /login：空登录名/空密码触发 @Valid 字段错误，不查数据库")
    void loginPost_shouldValidateBlankFields() throws Exception {
        mockMvc.perform(post("/login")
                        .param("loginName", " ")
                        .param("loginPwd", ""))
                .andExpect(status().isOk())
                .andExpect(view().name("login"))
                .andExpect(model().attributeHasFieldErrors("loginForm", "loginName", "loginPwd"));

        verify(userBuss, never()).login(anyString(), anyString());
    }

    @Test
    @DisplayName("POST /login：数据库不可用时异常交给全局处理器（500 错误页）")
    void loginPost_shouldShowErrorWhenUserServiceFails() throws Exception {
        when(userBuss.login("admin", "123456"))
                .thenThrow(new cn.edu.mju.band.exception.UserServiceException(
                        "用户数据访问失败，登录暂时不可用，请稍后重试", new RuntimeException("down")));

        mockMvc.perform(post("/login")
                        .param("loginName", "admin")
                        .param("loginPwd", "123456"))
                .andExpect(status().is5xxServerError())
                .andExpect(view().name("error"))
                .andExpect(model().attribute("error", "用户数据访问失败，登录暂时不可用，请稍后重试"));
    }

    @Test
    @DisplayName("POST /logout：销毁 Session 并回到登录页")
    void logout_shouldInvalidateSession() throws Exception {
        MockHttpSession session = new MockHttpSession();
        session.setAttribute(SessionKeys.LOGIN_USER, admin());

        mockMvc.perform(post("/logout").session(session))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/login?logout"));

        assertThat(session.isInvalid()).isTrue();
        verifyNoInteractions(userBuss);
    }
}
