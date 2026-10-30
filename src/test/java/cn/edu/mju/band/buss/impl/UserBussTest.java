package cn.edu.mju.band.buss.impl;

import cn.edu.mju.band.entity.User;
import cn.edu.mju.band.exception.UserServiceException;
import cn.edu.mju.band.mapper.UserMapper;
import com.baomidou.mybatisplus.core.MybatisConfiguration;
import com.baomidou.mybatisplus.core.metadata.TableInfoHelper;
import org.apache.ibatis.builder.MapperBuilderAssistant;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EmptySource;
import org.junit.jupiter.params.provider.NullSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.dao.DataAccessResourceFailureException;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

/**
 * UserBuss 登录业务单元测试。
 *
 * <p>覆盖：正常登录、密码错误、账号不存在、空参数，以及用户表不可用时的异常翻译。
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("UserBuss 登录业务单元测试")
class UserBussTest {

    @Mock
    private UserMapper userMapper;

    @InjectMocks
    private UserBuss userBuss;

    @BeforeAll
    static void initMybatisPlusMetadata() {
        MybatisConfiguration configuration = new MybatisConfiguration();
        MapperBuilderAssistant assistant = new MapperBuilderAssistant(configuration, "");
        TableInfoHelper.initTableInfo(assistant, User.class);
    }

    private static User admin() {
        return new User(1, "admin", "123456");
    }

    @Test
    @DisplayName("login：账号密码正确时返回用户")
    void login_shouldReturnUserWhenPasswordMatches() {
        when(userMapper.selectOne(any())).thenReturn(admin());

        User user = userBuss.login("admin", "123456");

        assertThat(user).isNotNull();
        assertThat(user.getLoginName()).isEqualTo("admin");
    }

    @Test
    @DisplayName("login：登录名两侧空白会被 trim")
    void login_shouldTrimLoginName() {
        when(userMapper.selectOne(any())).thenReturn(admin());

        assertThat(userBuss.login("  admin  ", "123456")).isNotNull();
    }

    @Test
    @DisplayName("login：密码错误返回 null")
    void login_shouldReturnNullWhenPasswordWrong() {
        when(userMapper.selectOne(any())).thenReturn(admin());

        assertThat(userBuss.login("admin", "654321")).isNull();
    }

    @Test
    @DisplayName("login：账号不存在返回 null")
    void login_shouldReturnNullWhenUserNotFound() {
        when(userMapper.selectOne(any())).thenReturn(null);

        assertThat(userBuss.login("nobody", "123456")).isNull();
    }

    @Test
    @DisplayName("login：数据库中的密码为 null 时安全返回 null")
    void login_shouldReturnNullWhenStoredPasswordIsNull() {
        User broken = admin();
        broken.setLoginPwd(null);
        when(userMapper.selectOne(any())).thenReturn(broken);

        assertThat(userBuss.login("admin", "123456")).isNull();
    }

    @ParameterizedTest(name = "loginName=[{0}]")
    @NullSource
    @EmptySource
    @ValueSource(strings = {" ", "   ", "\t"})
    @DisplayName("login：登录名空白时不查询数据库")
    void login_shouldRejectBlankLoginName(String loginName) {
        assertThat(userBuss.login(loginName, "123456")).isNull();
        verifyNoInteractions(userMapper);
    }

    @ParameterizedTest(name = "loginPwd=[{0}]")
    @NullSource
    @EmptySource
    @ValueSource(strings = {" ", "   "})
    @DisplayName("login：密码空白时不查询数据库")
    void login_shouldRejectBlankPassword(String loginPwd) {
        assertThat(userBuss.login("admin", loginPwd)).isNull();
        verifyNoInteractions(userMapper);
    }

    @Test
    @DisplayName("用户表不可用：登录抛出 UserServiceException 并保留原因")
    void login_shouldWrapDataAccessException() {
        when(userMapper.selectOne(any()))
                .thenThrow(new DataAccessResourceFailureException("Connection refused"));

        assertThatThrownBy(() -> userBuss.login("admin", "123456"))
                .isInstanceOf(UserServiceException.class)
                .hasMessageContaining("登录暂时不可用")
                .hasCauseInstanceOf(DataAccessResourceFailureException.class);
    }
}
