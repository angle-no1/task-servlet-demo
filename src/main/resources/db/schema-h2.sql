-- ===== test 环境（H2 / MODE=MySQL）建表脚本，字段与 MySQL 的 t_task / t_user 保持一致 =====
DROP TABLE IF EXISTS t_user;
DROP TABLE IF EXISTS t_task;

CREATE TABLE t_task (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(100) NOT NULL,
    content     TEXT,
    status      TINYINT      DEFAULT 0,
    create_time TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- 与现有 MySQL 库保持一致：username / password
CREATE TABLE t_user (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    CONSTRAINT uk_user_username UNIQUE (username)
);
