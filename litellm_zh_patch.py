#!/usr/bin/env python3
"""LiteLLM UI 汉化补丁生成器
思路：
1. 扫描所有 js/html 中的用户可见英文（children/label/title/placeholder/description 属性 + html 文本节点）
2. 按词典整词替换（只替换属性值/文本节点里的完整匹配，不碰代码标识符）
3. 输出汉化统计报告
"""
import os, re, json, sys, shutil, time

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

# ============ 汉化词典（覆盖导航+高频UI短语）============
DICT = {
    # 侧边栏导航
    "Virtual Keys": "虚拟密钥",
    "Internal Users": "内部用户",
    "Teams": "团队",
    "Models": "模型",
    "Usage": "使用量",
    "Settings": "设置",
    "Logs": "日志",
    "Overview": "总览",
    "Cost Tracking": "成本追踪",
    "Cost Optimization": "成本优化",
    "Caching": "缓存",
    "Budgets": "预算",
    "Guardrails": "护栏",
    "Guardrails Monitor": "护栏监控",
    "API Keys": "API 密钥",
    "API Reference": "API 参考",
    "Admin Panel": "管理面板",
    "Access Groups": "访问组",
    "Access Group": "访问组",
    "MCP Servers": "MCP 服务器",
    "Agents": "智能体",
    "Model Hub": "模型广场",
    "Models and Endpoints": "模型与端点",
    "Login": "登录",
    "Sign in": "登录",
    "Sign Out": "退出登录",
    "Log Out": "退出登录",
    "Chat": "聊天",
    "Connect": "连接",
    "Onboarding": "入门引导",
    "Change Password": "修改密码",
    "Logging and Alerts": "日志与告警",
    "Login to LiteLLM": "登录 LiteLLM",
    "LiteLLM Dashboard": "LiteLLM 控制台",
    # 表头/字段
    "Actions": "操作",
    "Description": "描述",
    "Created At": "创建时间",
    "Updated At": "更新时间",
    "Last Updated": "最后更新",
    "Name": "名称",
    "Created": "创建",
    "User ID": "用户 ID",
    "Status": "状态",
    "Team": "团队",
    "Provider": "提供商",
    "Model": "模型",
    "Metadata": "元数据",
    "Skills": "技能",
    "Source": "来源",
    "Email": "邮箱",
    "Team ID": "团队 ID",
    "Organization": "组织",
    "Created By": "创建者",
    "Tags": "标签",
    "Filters": "筛选",
    "User": "用户",
    "Type": "类型",
    "Action": "动作",
    "Cost": "成本",
    "Mode": "模式",
    "Key ID": "密钥 ID",
    "Rate Limits": "速率限制",
    "Spend": "消费",
    "User Email": "用户邮箱",
    "Active": "活跃",
    "Team Name": "团队名称",
    "Reset Budget": "重置预算",
    "Default": "默认",
    "Toolset": "工具集",
    "Key": "密钥",
    "Threshold": "阈值",
    "TPM Limit": "TPM 上限",
    "RPM Limit": "RPM 上限",
    "API Key": "API 密钥",
    "Max Budget": "最大预算",
    "Edit Settings": "编辑设置",
    "Role": "角色",
    "Version": "版本",
    "Public": "公开",
    "Calibration": "校准",
    "Request type": "请求类型",
    "Value": "值",
    "Score": "得分",
    "Members": "成员",
    "Expires": "过期",
    "Other": "其他",
    "Next": "下一步",
    "Display Name": "显示名称",
    "Authentication": "认证",
    "Group": "分组",
    "Policies": "策略",
    "Client ID": "客户端 ID",
    "Client Secret": "客户端密钥",
    "Total Tokens": "总 Token 数",
    "Budget": "预算",
    "Total": "合计",
    "Total Spend": "总消费",
    "Tokens": "Token 数",
    "Transport": "传输方式",
    "Object Permissions": "对象权限",
    "Embedding Model": "嵌入模型",
    "Pending Review": "待审核",
    "Rejected": "已拒绝",
    "Proxy Base URL": "代理基址 URL",
    "Blocked": "已封禁",
    "Tier": "层级",
    "Confidence": "置信度",
    "Routed to": "路由至",
    "Key Name": "密钥名称",
    "Connection ID": "连接 ID",
    "Password": "密码",
    "Daily": "每日",
    "Monthly": "每月",
    "Weekly": "每周",
    "Hourly": "每小时",
    "Savings": "节省",
    "Tools": "工具",
    "Capabilities": "能力",
    "Vector Stores": "向量库",
    "Last Active": "最后活跃",
    "Model Name": "模型名称",
    "Agent Name": "智能体名称",
    # 按钮/状态
    "Cancel": "取消",
    "Close": "关闭",
    "Delete": "删除",
    "Save Changes": "保存更改",
    "Save": "保存",
    "Update": "更新",
    "Add": "添加",
    "Create": "创建",
    "Create User": "创建用户",
    "Reset": "重置",
    "Retry": "重试",
    "Edit": "编辑",
    "Yes": "是",
    "No": "否",
    "Search or select a team": "搜索或选择团队",
    "Select model": "选择模型",
    "Select models": "选择模型",
    "Select Models": "选择模型",
    "Enter custom model name": "输入自定义模型名",
    "Enter custom model": "输入自定义模型",
    "Loading...": "加载中...",
    "Loading tools...": "工具加载中...",
    "No models found": "未找到模型",
    "No Default Models": "无默认模型",
    "No tools available": "无可用工具",
    "Not set": "未设置",
    "Not configured": "未配置",
    "All statuses": "全部状态",
    "All Proxy Models": "全部代理模型",
    "All proxy models": "全部代理模型",
    "All Proxy MCP Servers": "全部代理 MCP 服务器",
    "Never resets": "永不重置",
    "Learn more": "了解更多",
    "Advanced Settings": "高级设置",
    "Logging Settings": "日志设置",
    "Router Settings": "路由设置",
    "No data found": "未找到数据",
    "Search...": "搜索...",
    "Search": "搜索",
    "Confirm": "确认",
    "Confirm Delete": "确认删除",
    "Are you sure": "确定吗",
    "Copy": "复制",
    "Copied": "已复制",
    "Refresh": "刷新",
    "Test": "测试",
    "New Key": "新建密钥",
    "Generate Key": "生成密钥",
}

# 只在以下属性值里替换（避免误伤代码）
ATTR_PATTERNS = [
    (re.compile(r'((?<![\w$])children:)"((?:[^"\\]|\\.){2,60})"'), 'children'),
    (re.compile(r'((?<![\w$])label:)"((?:[^"\\]|\\.){2,60})"'), 'label'),
    (re.compile(r'((?<![\w$])title:)"((?:[^"\\]|\\.){2,60})"'), 'title'),
    (re.compile(r'((?<![\w$])placeholder:)"((?:[^"\\]|\\.){2,60})"'), 'placeholder'),
    (re.compile(r'((?<![\w$])description:)"((?:[^"\\]|\\.){2,60})"'), 'description'),
    (re.compile(r'((?<![\w$])message:)"((?:[^"\\]|\\.){2,60})"'), 'message'),
    (re.compile(r'((?<![\w$])heading:)"((?:[^"\\]|\\.){2,60})"'), 'heading'),
]

def translate_attr_value(val):
    """整词匹配词典；值必须完全等于词条才替换（保安全）"""
    v = val.strip()
    if v in DICT:
        return DICT[v]
    return None

changed_files = 0
total_replacements = 0
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
        file_count = 0
        counter = [0]
        def repl(m):
            val = m.group(2)
            t = translate_attr_value(val)
            if t is None:
                return m.group(0)
            global total_replacements
            total_replacements += 1
            counter[0] += 1
            return m.group(1) + '"' + t + '"'
        for pat, attr in ATTR_PATTERNS:
            counter[0] = 0
            content = pat.sub(repl, content)
            file_count += counter[0]
        if content != orig:
            # 备份
            bak = path + ".en.bak"
            if not os.path.exists(bak):
                shutil.copy2(path, bak)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            changed_files += 1
            report[path] = file_count

print(f"汉化完成: 修改 {changed_files} 个文件, 共 {total_replacements} 处替换")
print("\n=== 修改文件 TOP20 ===")
for p, c in sorted(report.items(), key=lambda x: -x[1])[:20]:
    print(f"  {c:4d} 处  {os.path.basename(p)}")
