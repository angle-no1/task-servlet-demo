package cn.edu.mju.band.mapper;

import cn.edu.mju.band.entity.User;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;

/** 用户数据访问接口：登录校验只需要按 login_name 查一条记录。 */
public interface UserMapper extends BaseMapper<User> {
}
