package cn.edu.mju.band.buss;

import cn.edu.mju.band.entity.User;

/** 用户业务接口 */
public interface IUserBuss {

    /**
     * 登录校验。
     *
     * @return 校验通过返回用户对象；账号不存在或密码错误返回 {@code null}
     */
    User login(String loginName, String loginPwd);
}
