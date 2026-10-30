package cn.edu.mju.band.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

/** 首页：根路径 / 重定向到任务列表 */
@Controller
public class HomeController {
    @GetMapping("/")
    public String index() {
        return "redirect:/task";
    }
}