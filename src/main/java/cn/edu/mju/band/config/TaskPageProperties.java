package cn.edu.mju.band.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * 分页业务参数：随环境（dev/test/prod）在 application-*.yml 中覆盖，实现业务参数一键隔离。
 *
 * <p>字段给了默认值，即使某个环境未配置该属性也能正常启动。
 */
@ConfigurationProperties(prefix = "task.page")
public class TaskPageProperties {

    /** 默认每页条数：dev=5，test=3，prod=10 */
    private int defaultSize = 5;

    public int getDefaultSize() {
        return defaultSize;
    }

    public void setDefaultSize(int defaultSize) {
        this.defaultSize = defaultSize;
    }
}
