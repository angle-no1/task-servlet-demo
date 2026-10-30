package cn.edu.mju.band.config;

import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * MyBatis-Plus 配置。
 *
 * <p>用 {@code @MapperScan} 取代原 applicationContext.xml 中的 MapperScannerConfigurer，
 * 用分页插件取代手写的 {@code LIMIT offset,size} SQL：
 * <ul>
 *   <li>{@link PaginationInnerInterceptor} 自动识别 MySQL / H2 方言，并生成 count 语句；</li>
 *   <li>{@code maxLimit=100} 与业务层 MAX_PAGE_SIZE 保持一致，防止超大分页拖垮数据库；</li>
 *   <li>不写死 DbType，dev 的 MySQL 与 test 的 H2 可以共用同一份配置。</li>
 * </ul>
 *
 * <p>单独成类（而非写在启动类上）是为了让 {@code @WebMvcTest} 控制层切片测试
 * 不加载持久层，从而真正做到“只测 MVC”。
 */
@Configuration
@MapperScan("cn.edu.mju.band.mapper")
public class MybatisPlusConfig {

    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        PaginationInnerInterceptor pagination = new PaginationInnerInterceptor();
        // 与 TaskBuss.MAX_PAGE_SIZE 对齐：即使调用方绕过业务层，也不允许一次取超过 100 条
        pagination.setMaxLimit(100L);
        // 页码超过末页时返回空页，而不是回到第一页，便于前端明确提示
        pagination.setOverflow(false);
        interceptor.addInnerInterceptor(pagination);
        return interceptor;
    }
}
