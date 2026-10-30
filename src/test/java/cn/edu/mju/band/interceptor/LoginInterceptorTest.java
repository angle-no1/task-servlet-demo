package cn.edu.mju.band.interceptor;

import cn.edu.mju.band.entity.User;
import cn.edu.mju.band.web.SessionKeys;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

import static org.assertj.core.api.Assertions.assertThat;

/** 登录拦截器单元测试：不启动 Spring 容器，直接验证 preHandle 的放行/重定向与回跳记录。 */
@DisplayName("LoginInterceptor 单元测试")
class LoginInterceptorTest {

    private final LoginInterceptor interceptor = new LoginInterceptor(new ObjectMapper());

    @Test
    @DisplayName("已登录：直接放行")
    void shouldPassWhenUserInSession() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/task");
        request.getSession().setAttribute(SessionKeys.LOGIN_USER,
                new User(1, "admin", "123456"));

        boolean allowed = interceptor.preHandle(request, new MockHttpServletResponse(), new Object());

        assertThat(allowed).isTrue();
    }

    @Test
    @DisplayName("未登录 GET：重定向 /login，并记录原始地址（含查询串）")
    void shouldRedirectAndRememberTargetForGet() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/task");
        request.setQueryString("status=2&pageNum=2");
        MockHttpServletResponse response = new MockHttpServletResponse();

        boolean allowed = interceptor.preHandle(request, response, new Object());

        assertThat(allowed).isFalse();
        assertThat(response.getRedirectedUrl()).isEqualTo("/login");
        assertThat(request.getSession().getAttribute(SessionKeys.LOGIN_REDIRECT))
                .isEqualTo("/task?status=2&pageNum=2");
    }

    @Test
    @DisplayName("未登录 POST：不记录回跳地址，避免把表单数据拼进 URL")
    void shouldNotRememberTargetForPost() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/task");
        MockHttpServletResponse response = new MockHttpServletResponse();

        boolean allowed = interceptor.preHandle(request, response, new Object());

        assertThat(allowed).isFalse();
        assertThat(response.getRedirectedUrl()).isEqualTo("/login");
        assertThat(request.getSession().getAttribute(SessionKeys.LOGIN_REDIRECT)).isNull();
    }

    @Test
    @DisplayName("未登录访问 /api/**：返回 401 JSON（业务码 40100），不重定向到登录页")
    void shouldReturnJson401ForUnauthenticatedApi() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/tasks");
        MockHttpServletResponse response = new MockHttpServletResponse();

        boolean allowed = interceptor.preHandle(request, response, new Object());

        assertThat(allowed).isFalse();
        assertThat(response.getStatus()).isEqualTo(401);
        assertThat(response.getContentType()).startsWith("application/json");
        assertThat(response.getContentAsString(java.nio.charset.StandardCharsets.UTF_8))
                .contains("\"code\":40100")
                .contains("未登录或会话已过期");
        assertThat(response.getRedirectedUrl()).isNull();
    }

    @Test
    @DisplayName("未登录访问 /api（无尾斜杠）同样按 API 处理")
    void shouldTreatApiRootAsApiRequest() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api");
        MockHttpServletResponse response = new MockHttpServletResponse();

        assertThat(interceptor.preHandle(request, response, new Object())).isFalse();
        assertThat(response.getStatus()).isEqualTo(401);
    }

    @Test
    @DisplayName("带 context-path 时仍能识别 /api/** 请求")
    void shouldRecognizeApiWithContextPath() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/taskmaster/api/tasks");
        request.setContextPath("/taskmaster");
        MockHttpServletResponse response = new MockHttpServletResponse();

        assertThat(interceptor.preHandle(request, response, new Object())).isFalse();
        assertThat(response.getStatus()).isEqualTo(401);
    }
}
