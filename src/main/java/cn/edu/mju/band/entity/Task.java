package cn.edu.mju.band.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.util.Date;

/**
 * 任务实体类 —— MyBatis-Plus 版。
 *
 * <p>与旧版相比只多了两类注解：
 * <ul>
 *   <li>{@code @TableName / @TableId / @TableField}：声明表名、主键策略与字段映射，
 *       不再需要 mapper XML 里的 resultType / useGeneratedKeys；</li>
 *   <li>Jakarta Validation 注解：控制层 {@code @Valid} 直接复用，实现服务端校验。</li>
 * </ul>
 * 字段仍对齐 t_task：id,title,content,status,create_time。
 */
@TableName("t_task")
public class Task {

    /** 状态常量：0 待办 */
    public static final byte STATUS_TODO = 0;
    /** 状态常量：1 进行中 */
    public static final byte STATUS_DOING = 1;
    /** 状态常量：2 已完成 */
    public static final byte STATUS_DONE = 2;

    /** 标题最大长度，与 t_task.title varchar(100) 对齐 */
    public static final int TITLE_MAX_LENGTH = 100;

    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;        // 任务编号

    @NotBlank(message = "任务标题不能为空")
    @Size(max = TITLE_MAX_LENGTH, message = "任务标题不能超过 100 个字符")
    private String title;      // 任务标题

    private String content;    // 任务内容（content 字段）

    @NotNull(message = "请选择任务状态")
    @Min(value = STATUS_TODO, message = "任务状态只能是 0/1/2")
    @Max(value = STATUS_DONE, message = "任务状态只能是 0/1/2")
    private Byte status;       // 状态：0待办 1进行中 2已完成

    /** 数据库默认值 CURRENT_TIMESTAMP；插入时留空即可，更新时也不会被覆盖 */
    @TableField("create_time")
    private Date createTime;   // 创建时间

    public Task() {}

    public Task(Integer id, String title, String content, Byte status, Date createTime) {
        this.id = id;
        this.title = title;
        this.content = content;
        this.status = status;
        this.createTime = createTime;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public Byte getStatus() { return status; }
    public void setStatus(Byte status) { this.status = status; }
    public Date getCreateTime() { return createTime; }
    public void setCreateTime(Date createTime) { this.createTime = createTime; }

    @Override
    public String toString() {
        return "Task{id=" + id + ", title='" + title + "', content='" + content
                + "', status=" + status + ", createTime=" + createTime + "}";
    }
}
