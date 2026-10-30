package cn.edu.mju.band;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

/**
 * Spring Boot 统一启动类（TaskMaster 现代化版）。
 *
 * <p>旧项目的 web.xml + applicationContext.xml + springmvc.xml + db.properties + TaskMapper.xml
 * 已全部移除，改为：
 * <ul>
 *   <li>spring-boot-starter-web：自动装配 DispatcherServlet、编码过滤器、内嵌 Tomcat；</li>
 *   <li>spring-boot-starter-thymeleaf：classpath:/templates/ 下的纯 HTML 模板；</li>
 *   <li>mybatis-plus-spring-boot3-starter：DataSource、SqlSessionFactory、事务管理器与 BaseMapper；</li>
 *   <li>spring-boot-starter-validation：@Valid 服务端校验；</li>
 *   <li>{@code cn.edu.mju.band.config.WebMvcConfig}：注册 LoginInterceptor 登录拦截；</li>
 *   <li>Maven 打包为可执行 JAR，java -jar 即可部署到另一台机器。</li>
 * </ul>
 */
@SpringBootApplication
@ConfigurationPropertiesScan("cn.edu.mju.band.config")
public class TaskApplication {

    public static void main(String[] args) {
        SpringApplication.run(TaskApplication.class, args);
    }
}
