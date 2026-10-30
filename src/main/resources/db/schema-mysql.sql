-- =====================================================================
-- MySQL 初始化脚本（跨机部署时执行一次即可；脚本可重复执行）
--   mysql -u root -p taskmaster < src/main/resources/db/schema-mysql.sql
--   mysql -u root -p taskmaster < src/main/resources/db/data-mysql.sql
-- 也可以直接以 dev 环境启动应用，spring.sql.init 会自动执行本目录下的
-- schema-mysql.sql / data-mysql.sql（脚本均为幂等写法）。
-- =====================================================================
CREATE TABLE IF NOT EXISTS t_task (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(100) NOT NULL,
    content     TEXT,
    status      TINYINT      NOT NULL DEFAULT 0,
    create_time TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- 与 TaskMaster 既有库保持一致：username / password
CREATE TABLE IF NOT EXISTS t_user (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    UNIQUE KEY uk_user_username (username)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
