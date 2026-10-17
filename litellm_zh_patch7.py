#!/usr/bin/env python3
"""LiteLLM UI 汉化补丁 v7：词典补充——覆盖上一版残留的高频英文
来源：对实际部署（LiteLLM 1.104.0 main-latest）UI 静态资源全量扫描，
提取 children/label/title/placeholder 属性中仍为英文的高频词条。
与 v1-v6 相同的整词匹配 + 幂等 + 备份机制。
"""
import os, re, shutil

# 动态发现 LiteLLM UI 目录（兼容不同 Python 版本的镜像）
def _find_ui_dir():
    import os as _os, glob as _glob
    # 1) 通过已安装的 litellm 包定位
    try:
        import litellm
        p = _os.path.join(_os.path.dirname(_os.path.abspath(litellm.__file__ or ".")), "proxy", "_experimental", "out")
        if _os.path.isdir(p):
            return p
    except Exception:
        pass
    # 2) 兜底：glob 匹配任意 python 版本路径
    for p in _glob.glob("/app/.venv/lib/python*/site-packages/litellm/proxy/_experimental/out"):
        if _os.path.isdir(p):
            return p
    # 3) 最后兜底：旧版硬编码路径
    return "/app/.venv/lib/python3.13/site-packages/litellm/proxy/_experimental/out"
UI = _find_ui_dir()

DICT = {
    # 审核/操作按钮
    "Approve": "批准",
    "Reject": "驳回",
    "Approved": "已批准",
    "Rejected": "已驳回",
    "Flagged": "已标记",
    "Not run": "未运行",
    "Preview": "预览",
    # 信息面板/表单
    "Basic Info": "基本信息",
    "Basic Information": "基本信息",
    "Advanced Configuration": "高级配置",
    "Index Name": "索引名称",
    "Prompt ID": "提示词 ID",
    "Memory ID": "记忆 ID",
    "Target Model": "目标模型",
    "Judge model": "评审模型",
    "Reasoning": "推理",
    "Calibration": "校准",
    "Per-user": "按用户",
    "Per team": "按团队",
    "Per-team": "按团队",
    "Connection": "连接",
    "Configuration": "配置",
    "Configuration Example": "配置示例",
    "Sample:": "示例：",
    "Loadbalancing": "负载均衡",
    "MCP Settings": "MCP 设置",
    "Skill Settings": "技能设置",
    "Logging Integrations": "日志集成",
    "No logging integrations configured": "未配置日志集成",
    "Evaluation settings": "评测设置",
    "AI APIs": "AI API",
    "Fail Rate": "失败率",
    "How this cost is calculated": "此成本如何计算",
    "Startup Nodes": "启动节点",
    "All Actions": "全部操作",
    "All Tables": "全部数据表",
    "All Input Policies": "全部输入策略",
    "All Output Policies": "全部输出策略",
    "All auto-routers": "全部自动路由器",
    "Heuristic first": "启发式优先",
    "Hybrid": "混合",
    "Every request": "每次请求",
    "Every new user message": "每条新用户消息",
    "Once per session": "每会话一次",
    "session total": "会话总量",
    # 别名/模型管理
    "Add New Alias": "新增别名",
    "Manage Existing Aliases": "管理已有别名",
    "No aliases added yet. Add a new alias above.": "暂无别名，请在上方添加。",
    # 空态提示
    "No logs to display. Adjust filters or date range.": "暂无日志，请调整筛选或时间范围。",
    "Select key type": "选择密钥类型",
    "Select MCP servers or access groups (optional)": "选择 MCP 服务器或访问组（可选）",
    "Select access groups (optional)": "选择访问组（可选）",
    "Select agents or access groups (optional)": "选择智能体或访问组（可选）",
    "Select vector stores (optional)": "选择向量库（可选）",
    "Select skills (optional)": "选择技能（可选）",
    "Scopes (optional)": "权限范围（可选）",
    "Add scopes": "添加权限范围",
    "Allowed MCP Servers": "允许的 MCP 服务器",
    "Team IDs JWT Field": "团队 ID JWT 字段",
    # 向量库
    "Test Vector Store": "测试向量库",
    "Edit Vector Store": "编辑向量库",
    "Add Vector Store": "添加向量库",
    # 认证方式（保留技术缩写，翻译说明部分）
    "Bearer Token": "Bearer 令牌",
    "True Passthrough (no LiteLLM auth)": "完全透传（不经 LiteLLM 认证）",
    "Streamable HTTP (Recommended)": "Streamable HTTP（推荐）",
    "Server-Sent Events (SSE)": "服务器推送事件（SSE）",
    "Standard Input/Output (stdio)": "标准输入/输出（stdio）",
    "PII Protection": "PII 保护",
    # 频段/预算
    "Hourly": "每小时",
    "Daily": "每日",
    "Weekly": "每周",
    "Monthly": "每月",
    # 企业功能标识
    "✨ Enterprise Feature": "✨ 企业版功能",
    # Token 限制
    "Input TPM Limit": "输入 TPM 上限",
    "Output TPM Limit": "输出 TPM 上限",
    "Tokens per minute Limit (TPM)": "每分钟 Token 上限（TPM）",
    "Requests per minute Limit (RPM)": "每分钟请求数上限（RPM）",
    # 高频单词（限属性值整词匹配，安全）
    "here": "此处",
    "invitation": "邀请",
    "deprecation discussion": "弃用讨论",
    "e.g., gpt-4o": "例如 gpt-4o",
}

ATTR_PATTERNS = [
    (re.compile(r'(children:)\"((?:[^\"\\\\]|\\\\.){2,60})\"'), 'children'),
    (re.compile(r'(label:)\"((?:[^\"\\\\]|\\\\.){2,60})\"'), 'label'),
    (re.compile(r'(title:)\"((?:[^\"\\\\]|\\\\.){2,60})\"'), 'title'),
    (re.compile(r'(placeholder:)\"((?:[^\"\\\\]|\\\\.){2,60})\"'), 'placeholder'),
    (re.compile(r'(description:)\"((?:[^\"\\\\]|\\\\.){2,60})\"'), 'description'),
    (re.compile(r'(message:)\"((?:[^\"\\\\]|\\\\.){2,60})\"'), 'message'),
    (re.compile(r'(heading:)\"((?:[^\"\\\\]|\\\\.){2,60})\"'), 'heading'),
]

def translate_attr_value(val):
    v = val.strip()
    return DICT.get(v)

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
            t = translate_attr_value(m.group(2))
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
