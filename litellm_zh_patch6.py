#!/usr/bin/env python3
"""LiteLLM UI 深度汉化 v6 —— 补漏：凭据/嵌入/自定义配置等剩余高频词"""
import os, re, shutil

UI = "/app/.venv/lib/python3.13/site-packages/litellm/proxy/_experimental/out"

DICT6 = {
    "Existing Credentials": "已有凭据",
    "Credential Name": "凭据名称",
    "Credentials": "凭据",
    "Select an embedding model": "选择嵌入模型",
    "No matching categories": "无匹配分类",
    "Custom Configuration": "自定义配置",
    "Target URL": "目标 URL",
    "Target": "目标",
    "Path": "路径",
    "LiteLLM Model Name": "LiteLLM 模型名",
    "Heuristic": "启发式",
    "Run in Claude Code": "在 Claude Code 中运行",
    "Invite User": "邀请用户",
    "+ Invite User": "+ 邀请用户",
    "Deprecation discussion": "弃用讨论",
    "Estimated Time": "预计时间",
    "Enable All": "全部启用",
    "Disable All": "全部停用",
    "Add Group": "添加分组",
    "Groups": "分组",
    "Group": "分组",
    "Sessions": "会话",
    "Session": "会话",
    "Trace ID": "追踪 ID",
    "Trace": "追踪",
    "Debug": "调试",
    "Enabled Models": "已启用模型",
    "Disabled Models": "已停用模型",
    "Team Models": "团队模型",
    "Team Members": "团队成员",
    "Team Budget": "团队预算",
    "Organization Members": "组织成员",
    "Organization Budget": "组织预算",
    "Add Member": "添加成员",
    "Remove Member": "移除成员",
    "Add Team Member": "添加团队成员",
    "Member Added": "成员已添加",
    "Member Removed": "成员已移除",
    "Spend for this key": "此密钥的消费",
    "Spend for this user": "此用户的消费",
    "Spend for this team": "此团队的消费",
    "Request Timeout": "请求超时",
    "Num Retries": "重试次数",
    "Fallbacks": "回退",
    "Fallback": "回退",
    "Cooldown Time": "冷却时间",
    "Allowed Fails": "允许失败次数",
    "Cache Control": "缓存控制",
    "Redis Settings": "Redis 设置",
    "Redis Host": "Redis 主机",
    "Redis Port": "Redis 端口",
    "Redis Password": "Redis 密码",
    "Database Settings": "数据库设置",
    "General": "通用",
    "Notifications": "通知",
    "Model Hub Settings": "模型广场设置",
    "UI Settings": "界面设置",
    "Theme": "主题",
    "Dark Mode": "深色模式",
    "Light Mode": "浅色模式",
    "System": "跟随系统",
    "Language": "语言",
    "Profile": "个人信息",
    "Account": "账户",
    "Log out": "退出登录",
    "Sign out": "退出登录",
    "Welcome back": "欢迎回来",
    "Login to your account": "登录你的账户",
    "Username or Email": "用户名或邮箱",
    "Forgot password?": "忘记密码？",
    "Don't have an account?": "没有账户？",
    "Already have an account?": "已有账户？",
    "No results": "无结果",
    "No data to display": "暂无数据",
    "No logs found for this filter": "该筛选条件下无日志",
    "Select a date range": "选择日期范围",
    "Custom Range": "自定义范围",
    "Last hour": "近 1 小时",
    "Last 24 hours": "近 24 小时",
    "Last week": "近一周",
    "Last month": "近一月",
    "Request Started": "请求开始",
    "Request Ended": "请求结束",
    "Time to First Token": "首 Token 时间",
    "End-to-End Duration": "端到端耗时",
    "API Request": "API 请求",
    "API Response": "API 响应",
    "Response Headers": "响应头",
    "Request Body": "请求体",
    "Response Body": "响应体",
    "View Request": "查看请求",
    "View Response": "查看响应",
    "Hide Request": "隐藏请求",
    "Hide Response": "隐藏响应",
    "Expand All": "全部展开",
    "Collapse All": "全部收起",
    "Show More": "显示更多",
    "Show Less": "收起",
    "View All": "查看全部",
    "View Details": "查看详情",
    "More Details": "更多详情",
    "Filter by Tag": "按标签筛选",
    "Filter by Model": "按模型筛选",
    "Filter by Key": "按密钥筛选",
    "Filter by User": "按用户筛选",
    "Filter by Team": "按团队筛选",
    "Filter by Status": "按状态筛选",
    "Clear Filters": "清空筛选",
    "Apply Filters": "应用筛选",
    "Date Range": "日期范围",
    "Status Code": "状态码",
    "Response Time": "响应时间",
    "Cache Status": "缓存状态",
    "Cache TTL": "缓存 TTL",
    "Prompt": "提示词",
    "Completion": "补全",
    "System Prompt": "系统提示词",
    "Model Parameters": "模型参数",
    "Request Params": "请求参数",
    "Spend Logs": "消费日志",
    "View Logs": "查看日志",
    "Log Details": "日志详情",
    "Error Details": "错误详情",
    "Error Message": "错误信息",
    "Exception": "异常",
    "Stack Trace": "调用栈",
    "Retry After": "重试间隔",
}

ATTR_PATTERNS = [
    re.compile(r'(children:)"((?:[^"\\]|\\.){1,90})"'),
    re.compile(r'(label:)"((?:[^"\\]|\\.){1,90})"'),
    re.compile(r'(title:)"((?:[^"\\]|\\.){1,90})"'),
    re.compile(r'(placeholder:)"((?:[^"\\]|\\.){1,90})"'),
    re.compile(r'(description:)"((?:[^"\\]|\\.){1,90})"'),
    re.compile(r'(message:)"((?:[^"\\]|\\.){1,90})"'),
    re.compile(r'(heading:)"((?:[^"\\]|\\.){1,90})"'),
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
            t = DICT6.get(val.strip())
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

print(f"v6 补漏汉化: 修改 {changed_files} 个文件, {total} 处替换")
for p, c in sorted(report.items(), key=lambda x: -x[1])[:10]:
    print(f"  {c:3d} 处  {os.path.basename(p)}")
