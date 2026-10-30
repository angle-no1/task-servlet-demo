-- ===== test 环境初始化数据：7 条任务，便于验证 3 条/页 的分页与筛选 =====
INSERT INTO t_task (title, content, status, create_time) VALUES
('完成实验报告', '整理单元测试与覆盖率截图', 0, '2026-10-01 09:00:00'),
('迁移 SpringBoot', '删除 web.xml 与 applicationContext.xml', 2, '2026-10-02 09:00:00'),
('编写 JUnit 5 用例', '覆盖正常流、异常流与边界条件', 1, '2026-10-03 09:00:00'),
('Mockito 打桩', '模拟 Mapper 故障', 0, '2026-10-04 09:00:00'),
('生成 JaCoCo 报告', '分析未覆盖分支', 1, '2026-10-05 09:00:00'),
('配置多环境', 'dev / test / prod', 2, '2026-10-06 09:00:00'),
('代码评审', '消除坏味道', 0, '2026-10-07 09:00:00');

-- 登录演示账号：admin / 123456（教学示例，生产环境必须存 BCrypt 哈希）
INSERT INTO t_user (username, password) VALUES ('admin', '123456');
