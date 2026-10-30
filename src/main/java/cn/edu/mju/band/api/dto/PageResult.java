package cn.edu.mju.band.api.dto;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;

import java.util.List;
import java.util.function.Function;

/**
 * 分页响应结构：只暴露调用方需要的字段，避免把 MyBatis-Plus 的 {@code Page} 内部字段
 * （optimizeCountSql、searchCount 等）直接序列化到接口里。
 *
 * @param records 当前页数据
 * @param total   总记录数
 * @param current 当前页码（从 1 开始）
 * @param size    每页条数
 * @param pages   总页数
 */
public record PageResult<T>(List<T> records, long total, long current, long size, long pages) {

    public static <S, T> PageResult<T> of(Page<S> page, Function<S, T> mapper) {
        List<S> source = page.getRecords() == null ? List.of() : page.getRecords();
        return new PageResult<>(
                source.stream().map(mapper).toList(),
                page.getTotal(),
                page.getCurrent(),
                page.getSize(),
                page.getPages());
    }
}
