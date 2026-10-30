package cn.edu.mju.band.buss.impl;

import cn.edu.mju.band.buss.IUserBuss;
import cn.edu.mju.band.entity.User;
import cn.edu.mju.band.exception.UserServiceException;
import cn.edu.mju.band.mapper.UserMapper;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/**
 * 用户登录业务。
 *
 * <p>查询同样使用 MyBatis-Plus 条件构造器，账号不存在 / 密码错误
 * 统一返回 null，由控制层给出同一条“用户名或密码错误”提示，避免枚举账号。
 */
@Service
public class UserBuss implements IUserBuss {

    private UserMapper userMapper;

    @Autowired
    public void setUserMapper(UserMapper userMapper) {
        this.userMapper = userMapper;
    }

    @Override
    public User login(String loginName, String loginPwd) {
        if (!StringUtils.hasText(loginName) || !StringUtils.hasText(loginPwd)) {
            return null;
        }
        try {
            User user = userMapper.selectOne(Wrappers.<User>lambdaQuery()
                    .eq(User::getLoginName, loginName.trim())
                    .last("LIMIT 1"));
            if (user == null || user.getLoginPwd() == null) {
                return null;
            }
            // 定长比较，避免按字符短路比较带来的时序差异（生产环境应改为 BCrypt 校验）
            boolean matched = MessageDigest.isEqual(
                    loginPwd.getBytes(StandardCharsets.UTF_8),
                    user.getLoginPwd().getBytes(StandardCharsets.UTF_8));
            return matched ? user : null;
        } catch (DataAccessException e) {
            throw new UserServiceException("用户数据访问失败，登录暂时不可用，请稍后重试", e);
        }
    }
}
