package cn.edu.mju.band.controller;

import cn.edu.mju.band.buss.ITaskBuss;
import cn.edu.mju.band.config.TaskPageProperties;
import cn.edu.mju.band.entity.Task;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.ArrayList;
import java.util.List;

/**
 * 任务控制器（Thymeleaf + MyBatis-Plus + Validation 版）。
 *
 * <p>与 JSP 版相比：
 * <ul>
 *   <li>视图名不变，由 Thymeleaf 解析到 classpath:/templates/；</li>
 *   <li>分页对象改为 MyBatis-Plus 的 {@link Page}，模板直接读取 records/current/pages；</li>
 *   <li>新增/修改用 {@code @Valid} + BindingResult，校验失败回到表单并回显错误；</li>
 *   <li>写操作成功后用 Flash 属性提示，刷新页面不会重复提交。</li>
 * </ul>
 */
@Controller
@RequestMapping("/task")
public class TaskController {

    @Autowired
    private ITaskBuss buss;

    /** 分页业务参数来自 application-*.yml，随环境切换（dev=5 / test=3 / prod=10） */
    @Autowired
    private TaskPageProperties pageProperties;

    /** GET 任务列表：支持名称模糊 + 状态筛选 + 分页 */
    @GetMapping
    public String list(
            @RequestParam(value = "title", required = false) String title,
            @RequestParam(value = "status", required = false) String status,
            @RequestParam(value = "pageNum", defaultValue = "1") Integer pageNum,
            @RequestParam(value = "pageSize", required = false) Integer pageSize,
            Model model) {

        // 未显式传 pageSize 时取当前环境的业务默认值，实现“业务参数随环境切换”
        if (pageSize == null) {
            pageSize = pageProperties.getDefaultSize();
        }

        // 空串转 null，条件构造器据此省略对应 AND
        if (title != null) {
            title = title.trim();
            if (title.isEmpty()) {
                title = null;
            }
        }

        Byte statusByte = null;
        if (status != null && !status.trim().isEmpty()) {
            try {
                statusByte = Byte.valueOf(status.trim());
            } catch (NumberFormatException e) {
                throw new IllegalArgumentException("任务状态参数非法：" + status);
            }
        }

        Page<Task> pageData = buss.findPage(title, statusByte, pageNum, pageSize);
        model.addAttribute("page", pageData);
        // 回显查询条件，搜索/翻页后保留
        model.addAttribute("searchTitle", title);
        model.addAttribute("searchStatus", statusByte);
        // 只渲染当前页附近的页码，避免总页数很大时生成成千上万个链接
        model.addAttribute("pageNumbers", pageNumbers(pageData));
        return "task";
    }

    /** GET 新增表单 */
    @GetMapping(params = "opt=add")
    public String addForm(Model model) {
        Task task = new Task();
        task.setStatus(Task.STATUS_TODO);
        model.addAttribute("opt", "add");
        model.addAttribute("task", task);
        return "add_update";
    }

    /** GET 修改表单 */
    @GetMapping(params = "opt=update")
    public String updateForm(@RequestParam("id") Integer id, Model model) {
        Task task = buss.findById(id);
        if (task == null) {
            throw new IllegalArgumentException("任务不存在或已被删除");
        }
        model.addAttribute("opt", "update");
        model.addAttribute("task", task);
        return "add_update";
    }

    /** POST 新增：校验失败回到表单并回显字段错误 */
    @PostMapping(params = "opt=add")
    public String add(@Valid @ModelAttribute("task") Task task,
                      BindingResult bindingResult,
                      Model model,
                      RedirectAttributes redirectAttributes) {
        if (bindingResult.hasErrors()) {
            model.addAttribute("opt", "add");
            return "add_update";
        }
        buss.add(task);
        redirectAttributes.addFlashAttribute("message", "任务「" + task.getTitle() + "」已创建");
        return "redirect:/task";
    }

    /** POST 修改：校验失败保留用户输入 */
    @PostMapping(params = "opt=update")
    public String update(@Valid @ModelAttribute("task") Task task,
                         BindingResult bindingResult,
                         Model model,
                         RedirectAttributes redirectAttributes) {
        if (task.getId() == null) {
            bindingResult.reject("task.id.required", "任务编号不能为空");
        }
        if (bindingResult.hasErrors()) {
            model.addAttribute("opt", "update");
            return "add_update";
        }
        buss.update(task);
        redirectAttributes.addFlashAttribute("message", "任务「" + task.getTitle() + "」已更新");
        return "redirect:/task";
    }

    /** POST 删除：写操作只允许 POST，避免被浏览器预取或爬虫误删 */
    @PostMapping(params = "opt=delete")
    public String delete(@RequestParam("id") Integer id, RedirectAttributes redirectAttributes) {
        buss.delete(id);
        redirectAttributes.addFlashAttribute("message", "任务已删除");
        return "redirect:/task";
    }

    /** 当前页附近的页码窗口（最多 5 个），供模板渲染页码链接 */
    private List<Long> pageNumbers(Page<Task> page) {
        long current = Math.max(1, page.getCurrent());
        long pages = page.getPages();
        long start = Math.max(1, current - 2);
        long end = Math.min(pages, start + 4);
        start = Math.max(1, end - 4);

        List<Long> numbers = new ArrayList<>();
        for (long i = start; i <= end; i++) {
            numbers.add(i);
        }
        return numbers;
    }
}
