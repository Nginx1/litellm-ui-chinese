#!/usr/bin/env python3
"""LiteLLM UI 深度汉化 v4 —— 覆盖次级页面全部高频英文（回退配置/预算/团队/MCP/技能/用量等）"""
import os, re, shutil

UI = "/app/.venv/lib/python3.13/site-packages/litellm/proxy/_experimental/out"

DICT4 = {
    # 字段/标签
    "Key Alias": "密钥别名",
    "User Alias": "用户别名",
    "Team Alias": "团队别名",
    "Alias": "别名",
    "Alias Name": "别名",
    "URL": "URL",
    "Description:": "描述：",
    "Spend:": "消费：",
    "Lifetime Spend": "累计消费",
    "Daily Spend": "每日消费",
    "Spend / Budget": "消费/预算",
    "Spend is bucketed by UTC day": "消费按 UTC 日统计",
    "Read": "读取",
    "Keys": "密钥",
    "Users": "用户",
    "Global Proxy Role": "全局代理角色",
    "Default Role": "默认角色",
    "Member Role": "成员角色",
    "All Roles": "全部角色",
    "Default Proxy Admin": "默认代理管理员",
    "Request": "请求",
    "Latency-Based Configuration": "延迟优先配置",
    "Fine-tune latency-based routing behavior": "微调基于延迟的路由行为",
    "Reliability & Retries": "可靠性与重试",
    "Configure retry logic and failure handling": "配置重试逻辑与失败处理",
    "Routing Settings": "路由设置",
    "Configure how requests are routed to deployments": "配置请求如何路由到部署",
    "Select a model to begin configuring fallbacks": "选择模型以开始配置回退",
    "No fallback models selected": "未选择回退模型",
    "Add models from the dropdown above": "从上方下拉添加模型",
    "No fallback groups configured": "未配置回退分组",
    "Select primary model": "选择主模型",
    "Property": "属性",
    "Headers": "请求头",
    "Cost Configuration": "成本配置",
    "Select All": "全选",
    "Deselect All": "取消全选",
    "Scope": "范围",
    "Mode:": "模式：",
    "Server Name": "服务器名称",
    "Public Model Name": "公开模型名",
    "Loading MCP servers...": "MCP 服务器加载中...",
    "Unable to load tools": "无法加载工具",
    "Unable to load MCP servers": "无法加载 MCP 服务器",
    "Unable to load toolsets": "无法加载工具集",
    "No MCP Servers": "无 MCP 服务器",
    "MCP Server": "MCP 服务器",
    "Block all": "全部禁止",
    "Organization ID": "组织 ID",
    "Organization Name": "组织名称",
    "Budget ID": "预算 ID",
    "Allowed Models": "允许的模型",
    "Tag Name": "标签名称",
    "Tag Name:": "标签名称：",
    "Group Name": "分组名称",
    "Need Help?": "需要帮助？",
    "Guardrail Name": "护栏名称",
    "Guardrail ID": "护栏 ID",
    "Default On": "默认开启",
    "Leave blank to keep existing": "留空保持不变",
    "Alias": "别名",
    "All Team Models": "全部团队模型",
    "Relative time": "相对时间",
    "Start and end dates": "起止日期",
    "Start date": "开始日期",
    "End date": "结束日期",
    "From:": "从：",
    "To:": "到：",
    "Routing": "路由",
    "Last 7 days": "近 7 天",
    "Last 30 days": "近 30 天",
    "Month to date": "本月至今",
    "Year to date": "今年至今",
    "Raw": "原始",
    "Boundary": "边界",
    "Rule": "规则",
    "Applied gap": "应用差距",
    "Allowed gap": "允许差距",
    "Decided by": "判定方",
    "Classifier model": "分类模型",
    "Probabilities": "概率",
    "Classifier cost": "分类成本",
    "Escalated": "已升级",
    "Success by tier": "分层成功率",
    "Predicted tier": "预测层级",
    "Signals": "信号",
    "Username": "用户名",
    "Available Tools": "可用工具",
    "Remove": "移除",
    "Details": "详情",
    "Spend is bucketed by UTC day": "消费按 UTC 日统计",
    "Cumulative": "累计",
    "Prompt Caching": "提示词缓存",
    "Method": "方法",
    "Response": "响应",
    "Action:": "动作：",
    "Model ID": "模型 ID",
    "API Base": "API 基址",
    "Skill Details": "技能详情",
    "Skill Name": "技能名称",
    "Skill ID": "技能 ID",
    "Metadata registered with this skill": "此技能注册的元数据",
    "Using this skill": "使用此技能",
    "How to Use": "使用方法",
    "Special Options": "特殊选项",
    "Wildcard Options": "通配选项",
    "Examples:": "示例：",
    "Agent ID": "智能体 ID",
    "No MCP servers, access groups, or toolsets configured": "未配置 MCP 服务器、访问组或工具集",
    "No default models": "无默认模型",
    "Results": "结果",
    "Policy": "策略",
    "Usage Example": "用法示例",
    "Copy to clipboard": "复制到剪贴板",
    "Health Status": "健康状态",
    "Auth Type": "认证类型",
    "Total Requests": "总请求数",
    "Successful Requests": "成功请求",
    "Failed Requests": "失败请求",
    "Email invitations": "邮件邀请",
    "Learn how to set up email notifications": "了解如何配置邮件通知",
    "Invite User": "邀请用户",
    "Create a User who can own keys": "创建可持有密钥的用户",
    "Per-Model Budgets": "按模型预算",
    "Servers reached through the selected toolsets are not listed below": "通过所选工具集到达的服务器不在下方列出",
    "All tools allowed, including tools added to this server later": "允许全部工具（含后续新增）",
    "Send invitation email": "发送邀请邮件",
    "Calendar month": "自然月",
    "Via tool permissions": "通过工具权限",
    "Select Organization": "选择组织",
    "If selected, user will be added as a 'user' role to the team.": "选择后用户将以 user 角色加入团队",
    "Models user has access to, outside of team scope.": "团队范围外用户可访问的模型",
    "Connected": "已连接",
    "Leave blank for no LiteLLM limit. Provider rate limits still apply.": "留空则不限（提供商限速仍生效）",
    "Connection Test Results": "连接测试结果",
    "Configuration": "配置",
    "Select or search for existing credentials": "选择或搜索已有凭据",
    "Select an option": "选择一项",
    "Server URL": "服务器 URL",
    "Authorization Endpoint": "授权端点",
    "Token Endpoint": "令牌端点",
    "Scopes": "授权范围",
    "Deleted At": "删除时间",
    "Vector Store ID": "向量库 ID",
    "Input Policy": "输入策略",
    "Output Policy": "输出策略",
    "Expire Key": "使密钥过期",
    "Model Aliases": "模型别名",
    "Disabled Callbacks": "已停用回调",
    "Management": "管理",
    "Select or enter tags": "选择或输入标签",
    "Reset to default": "恢复默认",
    "Avg. latency added": "平均增加延迟",
    "Passed": "通过",
    "Select or enter guardrails": "选择或输入护栏",
    "Not Set": "未设置",
    "Disconnect": "断开",
    "Token": "令牌",
    "Basic Auth": "Basic 认证",
    "OpenAPI Spec": "OpenAPI 规范",
    "Search servers...": "搜索服务器...",
    "Top Virtual Keys": "虚拟密钥排行",
    "Table View": "表格视图",
    "Chart View": "图表视图",
    "Enter Key ID…": "输入密钥 ID…",
    "Enter your API key": "输入你的 API 密钥",
    "Secret Manager Settings": "密钥管理器设置",
    "Optional": "可选",
    "Stop": "停止",
    "Weight": "权重",
    "Provider:": "提供商：",
    "Usage:": "用量：",
    "Select a team…": "选择团队…",
    "Select an organization…": "选择组织…",
    # 安全能力说明（四条）
    "Safe operations — fetch, list, search. No side effects.": "安全操作——读取、列出、搜索，无副作用",
    "Add new resources — insert, upload, register.": "新增资源——插入、上传、注册",
    "Modify existing resources — edit, patch, rename.": "修改资源——编辑、补丁、重命名",
    "Destructive operations — remove, purge, destroy.": "破坏性操作——移除、清除、销毁",
    "Operations that could not be automatically classified.": "无法自动分类的操作",
}

ATTR_PATTERNS = [
    re.compile(r'(children:)"((?:[^"\\]|\\.){2,90})"'),
    re.compile(r'(label:)"((?:[^"\\]|\\.){2,90})"'),
    re.compile(r'(title:)"((?:[^"\\]|\\.){2,90})"'),
    re.compile(r'(placeholder:)"((?:[^"\\]|\\.){2,90})"'),
    re.compile(r'(description:)"((?:[^"\\]|\\.){2,90})"'),
    re.compile(r'(message:)"((?:[^"\\]|\\.){2,90})"'),
    re.compile(r'(heading:)"((?:[^"\\]|\\.){2,90})"'),
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
            t = DICT4.get(val.strip())
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

print(f"v4 深度汉化: 修改 {changed_files} 个文件, {total} 处替换")
for p, c in sorted(report.items(), key=lambda x: -x[1])[:15]:
    print(f"  {c:3d} 处  {os.path.basename(p)}")
