-- ===== MySQL 演示数据（幂等）：账号只补一次，任务只在空表时补 3 条 =====
INSERT INTO t_user (username, password)
SELECT 'admin', '123456'
WHERE NOT EXISTS (SELECT 1 FROM t_user WHERE username = 'admin');

INSERT INTO t_task (title, content, status, create_time)
SELECT * FROM (
    SELECT '熟悉 SpringBoot 部署' AS title, '使用 java -jar 启动并访问 /task' AS content,
           0 AS status, NOW() AS create_time
    UNION ALL
    SELECT '体验 Thymeleaf 模板', '查看网页源代码，确认输出是纯 HTML', 1, NOW()
    UNION ALL
    SELECT '验证登录拦截', '退出后访问 /task 应跳转到 /login', 2, NOW()
) AS seed
WHERE NOT EXISTS (SELECT 1 FROM t_task);
