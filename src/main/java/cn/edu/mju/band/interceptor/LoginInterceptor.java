package cn.edu.mju.band.interceptor;

import cn.edu.mju.band.api.ApiErrorCode;
import cn.edu.mju.band.api.ApiResponse;
import cn.edu.mju.band.web.SessionKeys;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.servlet.HandlerInterceptor;

import java.nio.charset.StandardCharsets;

/**
 * 登录拦截器（环节五 + 环节二 API 契约）。
 *
 * <p>除登录页、静态资源、错误页和 OpenAPI 规范外，其余请求都要求 Session 中存在登录用户。
 * 未登录时：
 * <ul>
 *   <li>页面请求：记录原始 GET 地址后重定向到 /login，登录成功自动回跳；</li>
 *   <li>API 请求（{@code /api/**}）：返回 401 + JSON 错误体，
 *       不把 JSON 调用方重定向到 HTML 登录页，避免前端拿到 302/HTML 而无法解析。</li>
 * </ul>
 * POST 请求不记录回跳地址，避免把表单数据（尤其口令）拼进重定向 URL。
 */
public class LoginInterceptor implements HandlerInterceptor {

    private final ObjectMapper objectMapper;

    public LoginInterceptor(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response,
                             Object handler) throws Exception {
        HttpSession session = request.getSession(true);
        if (session.getAttribute(SessionKeys.LOGIN_USER) != null) {
            return true;
        }

        if (isApiRequest(request)) {
            response.setStatus(HttpStatus.UNAUTHORIZED.value());
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            response.setCharacterEncoding(StandardCharsets.UTF_8.name());
            objectMapper.writeValue(response.getWriter(), ApiResponse.error(ApiErrorCode.UNAUTHORIZED));
            return false;
        }

        if ("GET".equalsIgnoreCase(request.getMethod())) {
            String target = request.getRequestURI();
            String query = request.getQueryString();
            if (query != null && !query.isEmpty()) {
                target = target + "?" + query;
            }
            session.setAttribute(SessionKeys.LOGIN_REDIRECT, target);
        }

        response.sendRedirect(request.getContextPath() + "/login");
        return false;
    }

    /** 去掉 context-path 后判断是否属于 REST 接口 */
    private boolean isApiRequest(HttpServletRequest request) {
        String uri = request.getRequestURI();
        String contextPath = request.getContextPath();
        String path = (contextPath == null || contextPath.isEmpty())
                ? uri
                : uri.substring(contextPath.length());
        return "/api".equals(path) || path.startsWith("/api/");
    }
}
