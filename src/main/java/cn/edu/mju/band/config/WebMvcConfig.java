package cn.edu.mju.band.config;

import cn.edu.mju.band.interceptor.LoginInterceptor;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * MVC 配置：注册登录拦截器（环节五）。
 *
 * <p>放行登录/退出、静态资源、错误页与 OpenAPI 规范；首页 "/" 只做重定向，也放行，
 * 由它跳到 /task 后再触发拦截，避免浏览器首次访问出现两条重定向链。
 * 拦截器需要 {@link ObjectMapper} 来输出 API 401 的 JSON 错误体。
 */
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    private final ObjectMapper objectMapper;

    public WebMvcConfig(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @Bean
    public LoginInterceptor loginInterceptor() {
        return new LoginInterceptor(objectMapper);
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(loginInterceptor())
                .addPathPatterns("/**")
                .excludePathPatterns(
                        "/",
                        "/login",
                        "/logout",
                        "/error",
                        "/favicon.ico",
                        "/openapi.yaml",
                        "/css/**",
                        "/js/**",
                        "/images/**",
                        "/webjars/**"
                );
    }
}
