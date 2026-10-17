#!/usr/bin/env python3
"""LiteLLM UI 深度汉化 v5 —— 收尾批次：剩余高频页面词"""
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

DICT5 = {
    "None": "无",
    "Enter metadata as JSON": "以 JSON 输入元数据",
    "Capability estimates": "能力估算",
    "Efficient model solve chance": "高效模型命中概率",
    "FUSE v2 estimates": "FUSE v2 估算",
    "Heuristic v2 estimates": "启发式 v2 估算",
    "Calibrated": "已校准",
    "See one-time setup →": "查看一次性配置 →",
    "One-time marketplace setup": "一次性市场配置",
    "Run this command in Claude Code to register the marketplace:": "在 Claude Code 中运行以下命令注册市场：",
    "Agent Settings": "智能体设置",
    "Agent": "智能体",
    "Beta": "测试版",
    "Auto-router usage": "自动路由用量",
    "Input Tokens": "输入 Token",
    "Output Tokens": "输出 Token",
    "Done": "完成",
    "Optional Settings": "可选设置",
    "Unlimited": "无限制",
    "Enter": "输入",
    "Assistant": "助手",
    "Toolsets": "工具集",
    "Endpoint": "端点",
    "Select MCP servers": "选择 MCP 服务器",
    "Custom Response Message": "自定义响应消息",
    "Message": "消息",
    "Result": "结果",
    "Block": "禁止",
    "Inherits From": "继承自",
    "Enter custom response...": "输入自定义响应...",
    "e.g. 10": "例如 10",
    "Transport:": "传输方式：",
    "Category": "分类",
    "Table": "表格",
    "Select vector stores": "选择向量库",
    "No vector stores configured": "未配置向量库",
    "No agents or access groups configured": "未配置智能体或访问组",
    "Search tools": "搜索工具",
    "No restriction — all configured search tools are allowed for this team.": "无限制——该团队可用全部搜索工具",
    "Access control for Vector Stores and MCP Servers": "向量库与 MCP 服务器的访问控制",
    "Auto-Rotation": "自动轮换",
    "Warning:": "警告：",
    "Status:": "状态：",
    "Error:": "错误：",
    "Get help on our github": "在 GitHub 获取帮助",
    "Loading...": "加载中...",
    "Total Spend": "总消费",
    "Total Requests": "总请求数",
    "API Key": "API 密钥",
    "API Keys": "API 密钥",
    "User Email": "用户邮箱",
    "Max Budget": "最大预算",
    "Reset Budget": "重置预算",
    "Add User": "添加用户",
    "Delete": "删除",
    "Edit": "编辑",
    "Save": "保存",
    "Cancel": "取消",
    "Create": "创建",
    "Update": "更新",
    "Close": "关闭",
    "Confirm": "确认",
    "Search": "搜索",
    "Refresh": "刷新",
    "Test": "测试",
    "Copy": "复制",
    "View": "查看",
    "Usage": "用量",
    "Cost": "成本",
    "Requests": "请求数",
    "Latency": "延迟",
    "Uptime": "在线率",
    "Failures": "失败数",
    "Success Rate": "成功率",
    "Cache Hits": "缓存命中",
    "Prompts": "提示词",
    "Models": "模型",
    "Teams": "团队",
    "Settings": "设置",
    "General Settings": "通用设置",
    "Advanced Settings": "高级设置",
    "Apply": "应用",
    "Reset": "重置",
    "Retry": "重试",
    "Next": "下一步",
    "Previous": "上一步",
    "Back": "返回",
    "Submit": "提交",
    "Are you sure you want to delete this": "确定要删除此项吗",
    "This action cannot be undone": "此操作不可撤销",
    "Are you sure you want to delete this?": "确定要删除吗？",
    "Yes, delete": "是，删除",
    "No, cancel": "否，取消",
    "Delete Team": "删除团队",
    "Delete User": "删除用户",
    "Delete Key": "删除密钥",
    "Are you sure you want to delete this user": "确定删除该用户吗",
    "Are you sure you want to delete this key": "确定删除该密钥吗",
    "Are you sure you want to delete this team": "确定删除该团队吗",
    "Are you sure you want to regenerate this key": "确定重新生成该密钥吗",
    "Copy API Key": "复制 API 密钥",
    "Copy Bearer Token": "复制 Bearer 令牌",
    "Regenerate Key": "重新生成密钥",
    "Regenerate": "重新生成",
    "New Key Created": "新密钥已创建",
    "Key created successfully": "密钥创建成功",
    "Budget set to": "预算设置为",
    "Max budget": "最大预算",
    "Reset budget": "重置预算",
    "Budget Duration": "预算周期",
    "Budget ID": "预算 ID",
    "TPM / RPM Limits": "TPM / RPM 上限",
    "Team ID": "团队 ID",
    "Organization": "组织",
    "Created At": "创建时间",
    "Updated At": "更新时间",
    "Expires At": "过期时间",
    "Last Updated": "最后更新",
    "Never Expires": "永不过期",
    "Never resets": "永不重置",
    "Created by": "创建者",
    "Team Admin": "团队管理员",
    "Daily budget": "每日预算",
    "Weekly budget": "每周预算",
    "Monthly budget": "每月预算",
    "Total budget": "总预算",
}

ATTR_PATTERNS = [
    re.compile(r'((?<![\w$])children:)"((?:[^"\\]|\\.){1,90})"'),
    re.compile(r'((?<![\w$])label:)"((?:[^"\\]|\\.){1,90})"'),
    re.compile(r'((?<![\w$])title:)"((?:[^"\\]|\\.){1,90})"'),
    re.compile(r'((?<![\w$])placeholder:)"((?:[^"\\]|\\.){1,90})"'),
    re.compile(r'((?<![\w$])description:)"((?:[^"\\]|\\.){1,90})"'),
    re.compile(r'((?<![\w$])message:)"((?:[^"\\]|\\.){1,90})"'),
    re.compile(r'((?<![\w$])heading:)"((?:[^"\\]|\\.){1,90})"'),
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
            t = DICT5.get(val.strip())
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

print(f"v5 收尾汉化: 修改 {changed_files} 个文件, {total} 处替换")
for p, c in sorted(report.items(), key=lambda x: -x[1])[:15]:
    print(f"  {c:3d} 处  {os.path.basename(p)}")
