#!/usr/bin/env python3
"""LiteLLM UI 汉化补丁 v2 —— 补充词典，覆盖侧边栏剩余导航和次级页面短语"""
import os, re, shutil

UI = "/app/.venv/lib/python3.13/site-packages/litellm/proxy/_experimental/out"

DICT2 = {
    # 侧边栏剩余导航
    "AI Hub": "AI 广场",
    "API Playground": "API 试用场",
    "Admin Settings": "管理员设置",
    "Agentic": "智能体",
    "Experimental": "实验功能",
    "Hide All Prompts": "隐藏全部提示",
    "Hide Blog Posts": "隐藏博客文章",
    "Hide Bouncing Icon": "隐藏跳动图标",
    "Hide New Feature Indicators": "隐藏新功能标记",
    "Learning Resources": "学习资源",
    "Logging & Alerts": "日志与告警",
    "Memory": "记忆",
    "Old Usage": "旧版使用量",
    "Organizations": "组织",
    "Playground": "试用场",
    "Prompts": "提示词",
    "Response Cache": "响应缓存",
    "Search Tools": "搜索工具",
    "Seats": "席位",
    "Tag Management": "标签管理",
    "Tool Policies": "工具策略",
    "UI Theme": "界面主题",
    "Workflow Runs": "工作流运行",
    "Logging and Alerts": "日志与告警",
    "General Settings": "通用设置",
    "Budget & Spend": "预算与消费",
    "Pass-through": "透传",
    "Pass-Through": "透传",
    "Pass Through Endpoints": "透传端点",
    "Model Settings": "模型设置",
    "Team Settings": "团队设置",
    "Organization Settings": "组织设置",
    "Router": "路由",
    "Fallbacks": "回退",
    "Retry Policy": "重试策略",
    "Cooldowns": "冷却",
    "Auto Router": "自动路由",
    "Filters": "筛选器",
    "Usage & Spend": "用量与消费",
    "Request Logs": "请求日志",
    "Key Spend": "密钥消费",
    "User Spend": "用户消费",
    "Team Spend": "团队消费",
    "Tag Spend": "标签消费",
    "Add Model": "添加模型",
    "Add Team": "添加团队",
    "Add User": "添加用户",
    "Add Key": "添加密钥",
    "Create Virtual Key": "创建虚拟密钥",
    "Create Key": "创建密钥",
    "Create Team": "创建团队",
    "Create Organization": "创建组织",
    "Full Access": "完全访问",
    "Read Only": "只读",
    "Copy Key": "复制密钥",
    "Regenerate Key": "重新生成密钥",
    "Delete Key": "删除密钥",
    "Delete User": "删除用户",
    "Delete Team": "删除团队",
    "Member Added": "成员已添加",
    "Member Removed": "成员已移除",
    "Created By": "创建者",
    "Last Used": "最后使用",
    "Spend Rate": "消费速率",
    "Current Spend": "当前消费",
    "Budget Reset": "预算重置",
    "Max Parallel Requests": "最大并发请求",
    "Requests Per Minute": "每分钟请求数",
    "Tokens Per Minute": "每分钟 Token 数",
    "Model Access": "模型访问",
    "Team Access": "团队访问",
    "Key Expiry": "密钥过期",
    "Never": "永不",
    "Expired": "已过期",
    "Valid": "有效",
    "Invalid": "无效",
    "All Time": "全部时间",
    "Today": "今天",
    "Yesterday": "昨天",
    "Last 7 Days": "近 7 天",
    "Last 30 Days": "近 30 天",
    "This Month": "本月",
    "Download CSV": "下载 CSV",
    "Export": "导出",
    "Import": "导入",
    "Back": "返回",
    "Previous": "上一步",
    "Finish": "完成",
    "Submit": "提交",
    "Clear": "清空",
    "Clear All": "全部清空",
    "Apply": "应用",
    "Applied": "已应用",
    "Success": "成功",
    "Error": "错误",
    "Warning": "警告",
    "Info": "信息",
    "Loading": "加载中",
    "Saving": "保存中",
    "Saved": "已保存",
    "Deleted": "已删除",
    "Created": "已创建",
    "Updated": "已更新",
    "No results found": "未找到结果",
    "No results": "无结果",
    "No data": "暂无数据",
    "No data available": "暂无数据",
    "No teams found": "未找到团队",
    "No users found": "未找到用户",
    "No keys found": "未找到密钥",
    "No logs found": "未找到日志",
    "Something went wrong": "出现问题",
    "Try again": "重试",
    "Are you sure you want to delete": "确定要删除吗",
    "This action cannot be undone": "此操作不可撤销",
}

ATTR_PATTERNS = [
    re.compile(r'(children:)"((?:[^"\\]|\\.){2,60})"'),
    re.compile(r'(label:)"((?:[^"\\]|\\.){2,60})"'),
    re.compile(r'(title:)"((?:[^"\\]|\\.){2,60})"'),
    re.compile(r'(placeholder:)"((?:[^"\\]|\\.){2,60})"'),
    re.compile(r'(description:)"((?:[^"\\]|\\.){2,60})"'),
    re.compile(r'(message:)"((?:[^"\\]|\\.){2,60})"'),
    re.compile(r'(heading:)"((?:[^"\\]|\\.){2,60})"'),
]

changed_files = 0
total = 0
report = {}

for root, dirs, files in os.walk(UI):
    for fn in files:
        if not (fn.endswith(".js") or fn.endswith(".html")):
            continue
        path = os.path.join(root, fn)
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue
        orig = content
        counter = [0]
        def repl(m):
            val = m.group(2)
            t = DICT2.get(val.strip())
            if t is None:
                return m.group(0)
            global total
            total += 1
            counter[0] += 1
            return m.group(1) + '"' + t + '"'
        for pat in ATTR_PATTERNS:
            counter[0] = 0
            content = pat.sub(repl, content)
        if content != orig:
            bak = path + ".en.bak"
            if not os.path.exists(bak):
                shutil.copy2(path, bak)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            changed_files += 1
            report[path] = counter[0]

print(f"v2 汉化: 修改 {changed_files} 个文件, {total} 处替换")
for p, c in sorted(report.items(), key=lambda x: -x[1])[:10]:
    print(f"  {c:3d} 处  {os.path.basename(p)}")
