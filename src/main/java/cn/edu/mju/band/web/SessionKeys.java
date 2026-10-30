package cn.edu.mju.band.web;

/** Session 属性名常量，避免各处手写字符串导致拼写不一致。 */
public final class SessionKeys {

    /** 已登录用户 */
    public static final String LOGIN_USER = "loginUser";
    /** 登录前想访问的地址，登录成功后回跳 */
    public static final String LOGIN_REDIRECT = "loginRedirect";

    private SessionKeys() {
    }
}
