#!/usr/bin/env python3
"""LiteLLM UI 汉化 v3 —— 补最后漏网导航词 + 二级页面高频短语"""
import os, re, shutil

# 动态发现 LiteLLM UI 目录（兼容不同 Python 版本的镜像）
def _find_ui_dir():
    """按优先级定位 UI 静态资源目录；找不到时抛错退出（宁可失败也不改错目录）"""
    import os as _os, glob as _glob, importlib.util as _ilu

    def _looks_like_ui(p):
        # UI 目录应包含 .next 或 html/js 静态资源
        if not _os.path.isdir(p):
            return False
        try:
            names = _os.listdir(p)
        except Exception:
            return False
        if "_next" in names:
            return True
        return any(n.endswith((".js", ".html")) for n in names)

    # 1) 通过已安装的 litellm 包定位（find_spec 支持命名空间包）
    try:
        spec = _ilu.find_spec("litellm")
        if spec is not None:
            for base in (spec.submodule_search_locations or []):
                p = _os.path.join(base, "proxy", "_experimental", "out")
                if _looks_like_ui(p):
                    return p
    except Exception:
        pass

    # 2) 兜底：glob 匹配任意 python 版本路径（仅取唯一候选，多个候选则要求恰好一个像 UI）
    cands = [p for p in _glob.glob("/app/.venv/lib/python*/site-packages/litellm/proxy/_experimental/out") if _looks_like_ui(p)]
    if len(cands) == 1:
        return cands[0]

    # 3) 历史硬编码路径（老镜像兼容），仍需校验
    legacy = "/app/.venv/lib/python3.13/site-packages/litellm/proxy/_experimental/out"
    if _looks_like_ui(legacy):
        return legacy

    raise SystemExit(
        "[litellm_zh_patch] 未找到 LiteLLM UI 目录（litellm 包未安装且 /app/.venv 下无候选）。"
        "若你的部署路径不同，请修改脚本顶部的 _find_ui_dir()。"
    )

UI = _find_ui_dir()

DICT3 = {
    "Models + Endpoints": "模型与端点",
    "Models & Endpoints": "模型与端点",
    "Endpoints": "端点",
    "My Models": "我的模型",
    "Proxy Models": "代理模型",
    "Add Models": "添加模型",
    "Add Endpoint": "添加端点",
    "Health": "健康",
    "Health Check": "健康检查",
    "Latency": "延迟",
    "Uptime": "在线率",
    "Requests": "请求数",
    "Tokens": "Token 数",
    "Failures": "失败数",
    "Success Rate": "成功率",
    "Cache Hit": "缓存命中",
    "Cache Miss": "缓存未命中",
    "Logs & Alerts": "日志与告警",
    "Alerts": "告警",
    "Callback": "回调",
    "Callbacks": "回调",
    "Notification": "通知",
    "Notifications": "通知",
    "Email Alerts": "邮件告警",
    "Slack Alerts": "Slack 告警",
    "Overview": "总览",
    "Dashboard": "控制台",
    "Main Dashboard": "主控制台",
    "Usage Dashboard": "用量控制台",
    "Virtual Key": "虚拟密钥",
    "Virtual Keys Page": "虚拟密钥页",
    "Spend Logs": "消费日志",
    "My Usage": "我的用量",
    "Team Usage": "团队用量",
    "Key Usage": "密钥用量",
    "Model Usage": "模型用量",
    "Usage Report": "用量报告",
    "Top Models": "模型排行",
    "Top Users": "用户排行",
    "Top Teams": "团队排行",
    "Top Tags": "标签排行",
    "Top Endpoints": "端点排行",
    "Slowest Requests": "最慢请求",
    "All Requests": "全部请求",
    "Request Details": "请求详情",
    "Request ID": "请求 ID",
    "Execution Details": "执行详情",
    "Time": "时间",
    "Timestamp": "时间戳",
    "Duration": "耗时",
    "Total Cost": "总成本",
    "API Base URL": "API 基址",
    "Base URL": "基址",
    "Redirect URL": "跳转 URL",
    "SSO": "单点登录",
    "SSO Setup": "单点登录配置",
    "Google SSO": "Google 单点登录",
    "Microsoft SSO": "微软单点登录",
    "Okta SSO": "Okta 单点登录",
    "Generic SSO": "通用单点登录",
    "User Management": "用户管理",
    "Team Management": "团队管理",
    "Key Management": "密钥管理",
    "Model Management": "模型管理",
    "Model Groups": "模型分组",
    "Wildcard Models": "通配模型",
    "Custom Model": "自定义模型",
    "Custom Models": "自定义模型",
    "Add Model Group": "添加模型分组",
    "Supported Models": "支持的模型",
    "Supported Parameters": "支持的参数",
    "Input Cost per Token": "输入成本/Token",
    "Output Cost per Token": "输出成本/Token",
    "Max Tokens": "最大 Token",
    "Max Input Tokens": "最大输入 Token",
    "Max Output Tokens": "最大输出 Token",
    "Temperature": "温度",
    "Timeout": "超时",
    "Stream": "流式",
    "Streaming": "流式输出",
    "Fallback Model": "回退模型",
    "Fallback Models": "回退模型",
    "Router Settings": "路由设置",
    "General": "通用",
    "Advanced": "高级",
    "Permissions": "权限",
    "All Permissions": "全部权限",
    "Admin": "管理员",
    "Viewer": "只读用户",
    "Owner": "所有者",
    "Admin Roles": "管理员角色",
    "Internal User": "内部用户",
    "External User": "外部用户",
    "User Role": "用户角色",
    "Member": "成员",
    "Members List": "成员列表",
    "Add Member": "添加成员",
    "Remove Member": "移除成员",
    "Budget Duration": "预算周期",
    "Budget Expiry": "预算过期",
    "Spend Limit": "消费上限",
    "Hard Limit": "硬上限",
    "Soft Limit": "软上限",
    "Total Budget": "总预算",
    "Remaining Budget": "剩余预算",
    "Used Budget": "已用预算",
    "Reset Period": "重置周期",
    "Monthly Reset": "每月重置",
    "Weekly Reset": "每周重置",
    "Daily Reset": "每日重置",
    "Enabled": "已启用",
    "Disabled": "已停用",
    "Enable": "启用",
    "Disable": "停用",
    "Turn On": "开启",
    "Turn Off": "关闭",
    "Toggle": "切换",
    "Active Keys": "活跃密钥",
    "Expired Keys": "过期密钥",
    "All Keys": "全部密钥",
    "All Users": "全部用户",
    "All Teams": "全部团队",
    "All Models": "全部模型",
    "All Logs": "全部日志",
    "Filter by": "筛选条件",
    "Sort by": "排序",
    "Group by": "分组",
    "View": "视图",
    "Columns": "列",
    "Rows per page": "每页行数",
    "Page": "页",
    "of": "/",
    "First": "首页",
    "Last": "末页",
}

ATTR_PATTERNS = [
    re.compile(r'((?<![\w$])children:)"((?:[^"\\]|\\.){2,60})"'),
    re.compile(r'((?<![\w$])label:)"((?:[^"\\]|\\.){2,60})"'),
    re.compile(r'((?<![\w$])title:)"((?:[^"\\]|\\.){2,60})"'),
    re.compile(r'((?<![\w$])placeholder:)"((?:[^"\\]|\\.){2,60})"'),
    re.compile(r'((?<![\w$])description:)"((?:[^"\\]|\\.){2,60})"'),
    re.compile(r'((?<![\w$])message:)"((?:[^"\\]|\\.){2,60})"'),
    re.compile(r'((?<![\w$])heading:)"((?:[^"\\]|\\.){2,60})"'),
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
            t = DICT3.get(val.strip())
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

print(f"v3 汉化: 修改 {changed_files} 个文件, {total} 处替换")
for p, c in sorted(report.items(), key=lambda x: -x[1])[:10]:
    print(f"  {c:3d} 处  {os.path.basename(p)}")
