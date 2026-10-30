package cn.edu.mju.band.audit;

/**
 * 一条审计事件。
 *
 * <p>{@code thread} 记录实际执行线程名，Demo 时可据此证明审计逻辑
 * 运行在 {@code task-audit-*} 线程而不是 Tomcat 请求线程。
 */
public record TaskAuditEntry(String at, String thread, String action, Integer taskId, String detail) {
}
