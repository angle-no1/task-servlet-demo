package cn.edu.mju.band.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.io.Serializable;

/**
 * 登录用户实体 —— 对应 t_user 表。
 *
 * <p>表中实际列名为 username / password，这里用 {@code @TableField} 映射为
 * loginName / loginPwd，既保持 Java 侧语义清晰，又不用改动已有数据库结构。
 * 新增用户时主键由数据库自增。
 */
@TableName("t_user")
public class User implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    @TableField("username")
    private String loginName;

    /**
     * 教学示例使用明文口令，便于在报告里演示登录流程；
     * 生产环境必须改为 BCrypt / Argon2 等慢哈希存储，并在登录时校验哈希。
     */
    @TableField("password")
    private String loginPwd;

    public User() {
    }

    public User(Integer id, String loginName, String loginPwd) {
        this.id = id;
        this.loginName = loginName;
        this.loginPwd = loginPwd;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getLoginName() {
        return loginName;
    }

    public void setLoginName(String loginName) {
        this.loginName = loginName;
    }

    public String getLoginPwd() {
        return loginPwd;
    }

    public void setLoginPwd(String loginPwd) {
        this.loginPwd = loginPwd;
    }

    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", loginName='" + loginName + '\'' +
                '}';
    }
}
