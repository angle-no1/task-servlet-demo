package cn.edu.mju.band.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.ThreadPoolExecutor;

/**
 * 异步任务线程池配置。
 *
 * <p>只给审计使用一个独立线程池，避免和 Tomcat 请求线程共用一个池导致互相拖垮：
 * <ul>
 *   <li>核心 2、最大 4、队列 100：课堂演示足够，且资源可控；</li>
 *   <li>{@code task-audit-} 线程前缀：日志里一眼能看出异步执行；</li>
 *   <li>{@link ThreadPoolExecutor.CallerRunsPolicy}：队列满时退化为调用方线程执行，
 *       宁可慢一点也不丢审计事件；</li>
 *   <li>优雅停机等待 5 秒，应用退出前尽量把审计写完。</li>
 * </ul>
 */
@Configuration
@EnableAsync
public class AsyncConfig {

    public static final String TASK_AUDIT_EXECUTOR = "taskAuditExecutor";

    @Bean(name = TASK_AUDIT_EXECUTOR)
    public ThreadPoolTaskExecutor taskAuditExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(2);
        executor.setMaxPoolSize(4);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("task-audit-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(5);
        executor.initialize();
        return executor;
    }
}
