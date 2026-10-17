# LiteLLM UI 中文汉化补丁

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![LiteLLM](https://img.shields.io/badge/LiteLLM-1.104.0-blue.svg)](https://github.com/BerriAI/litellm)
[![汉化词条](https://img.shields.io/badge/词条-%E2%89%883000-green.svg)](#文件说明)

给 **LiteLLM Dashboard（Proxy UI）** 打中文汉化补丁的一组脚本。官方 LiteLLM 的 Web 管理界面是纯英文 Next.js 应用，社区没有现成的中文语言包，本项目通过**直接替换容器内静态资源（JS/HTML）中的用户可见文案**实现汉化，无需修改 LiteLLM 源码、无需重新构建前端。

## 作用

- 将 LiteLLM Dashboard 界面汉化为中文，累计 **~2800 处**文案替换
- 覆盖范围：
  - 侧边栏导航（虚拟密钥、内部用户、团队、模型与端点、智能体、用量、日志、护栏等）
  - 表格表头（创建时间、状态、消费、模型、提供商等）
  - 按钮/操作（取消、删除、保存、创建、重置、确认等）
  - 确认弹窗、表单标签、placeholder
  - 二级页面：回退配置、预算、团队管理、MCP 服务器、技能、用量报表、请求日志详情、凭据、向量库、缓存设置等
- **幂等设计**：重复执行只会补新词，不会重复替换
- **安全性**：只替换 `children:/label:/title:/placeholder:/description:/message:/heading:` 等 JSX 属性值中的完整匹配，不碰代码标识符、函数名、CSS 类名，不会破坏 UI 功能
- 每个被修改的文件都会先备份为 `.en.bak`，可随时回滚

## 汉化效果

<!-- 截图：在 docs/ 下放 screenshots/01-sidebar.png、02-keys.png、03-logs.png 后取消注释
![侧边栏](docs/screenshots/01-sidebar.png)
![虚拟密钥页](docs/screenshots/02-keys.png)
![日志页](docs/screenshots/03-logs.png)
-->

| 位置 | 汉化前 | 汉化后 |
|---|---|---|
| 侧边栏 | Virtual Keys | 虚拟密钥 |
| 侧边栏 | Internal Users | 内部用户 |
| 侧边栏 | Models + Endpoints | 模型与端点 |
| 表头 | Created At / Spend / Status | 创建时间 / 消费 / 状态 |
| 按钮 | Save Changes / Delete | 保存更改 / 删除 |
| 用量页 | Last 7 days / Total Spend | 近 7 天 / 总消费 |

## 使用方法

### 环境要求

- LiteLLM Proxy 以 **Docker 官方镜像**（`ghcr.io/berriai/litellm`）运行
- 容器名默认为 `litellm`（不同请自行修改脚本中的容器名）
- 宿主机能 `docker cp` / `docker exec` 该容器

### 一键汉化

```bash
git clone https://github.com/Nginx1/litellm-ui-chinese.git
cd litellm-ui-chinese

# 直接跑（默认容器名 litellm、本机 docker）
bash relocalize.sh
```

脚本做的事：
1. 把补丁脚本推送到容器 `/tmp/`
2. 依次 `docker cp` 进容器执行（v1 基础导航/表头 → v2 侧边栏补充 → v3 二级页面 → v4 深度页面 → v5 弹窗/密钥 → v6 凭据/日志 → v7 高频残留补齐）
3. 重启 litellm 容器使静态资源生效
4. 健康检查 + 验证汉化标记

完成后浏览器打开 `http://<litellm-host>:4000/ui`，**强制刷新（Ctrl+Shift+R）** 即可看到中文界面。

### 手动分步执行

如果不想用一键脚本，在**宿主机**上：

```bash
# 1. 推送补丁进容器
docker cp litellm_zh_patch.py  litellm:/tmp/
docker cp litellm_zh_patch2.py litellm:/tmp/
docker cp litellm_zh_patch3.py litellm:/tmp/
docker cp litellm_zh_patch4.py litellm:/tmp/
docker cp litellm_zh_patch5.py litellm:/tmp/
docker cp litellm_zh_patch6.py litellm:/tmp/
docker cp litellm_zh_patch7.py litellm:/tmp/

# 2. 依次执行
docker exec litellm python3 /tmp/litellm_zh_patch.py
docker exec litellm python3 /tmp/litellm_zh_patch2.py
docker exec litellm python3 /tmp/litellm_zh_patch3.py
docker exec litellm python3 /tmp/litellm_zh_patch4.py
docker exec litellm python3 /tmp/litellm_zh_patch5.py
docker exec litellm python3 /tmp/litellm_zh_patch6.py
docker exec litellm python3 /tmp/litellm_zh_patch7.py

# 3. 重启
docker restart litellm
```

## 回滚

每个被修改的文件在容器内都有同目录的 `.en.bak` 备份：

```bash
# 批量回滚（容器内）
docker exec litellm sh -c '
cd /app/.venv/lib/python3.13/site-packages/litellm/proxy/_experimental/out
find /app -name "*.js" -o -name "*.html" | while read f; do
  [ -f "$f.en.bak" ] && cp "$f.en.bak" "$f"
done'

docker restart litellm
```

或者最简单：**重建容器**（汉化只改容器内文件，不持久化，重建即恢复英文原版）。

## 已知限制

- **容器升级/重建后汉化丢失**——静态资源在容器内不持久化。重跑 `relocalize.sh` 即可恢复（幂等，安全）
- **版本绑定**：补丁基于 LiteLLM `1.104.0`（`main-latest`，2026-10）的静态资源。LiteLLM 前端大版本更新后，部分文案位置可能变化，但词典按"整词匹配"工作，大部分词条仍会命中；未命中的保持英文，重跑无副作用
- **不做代码级 i18n**：这是静态替换方案，不是国际化框架。剩余未翻译的多为技术术语（URL/RPM/TPM/OAuth/JSON）、命令行示例、品牌词（LiteLLM/Claude Code）等**有意保留**的内容
- 汉化词典内置于各脚本，想增删词条直接编辑对应 `DICT` 后重跑

## 文件说明

| 文件 | 覆盖范围 |
|---|---|
| `litellm_zh_patch.py` | 侧边栏导航、高频表头、基础按钮/状态 |
| `litellm_zh_patch2.py` | 侧边栏剩余项、Playground/Workflow 等二级导航 |
| `litellm_zh_patch3.py` | 用量页、模型管理、权限、预算周期 |
| `litellm_zh_patch4.py` | 回退配置、团队/MCP/技能、安全能力说明 |
| `litellm_zh_patch5.py` | 确认弹窗、密钥管理、登录页 |
| `litellm_zh_patch6.py` | 凭据、向量库、日志详情、Redis/缓存、请求详情 |
| `litellm_zh_patch7.py` | 高频残留补齐：审核按钮、别名管理、向量库操作、空态提示、认证方式说明等 |
| `relocalize.sh` | 一键：前置检查 → 推送 → 执行 → 重启 → 端口自适应健康检查 |

## 适用版本与兼容性记录

| LiteLLM 版本 | 运行环境 | 状态 | 验证时间 |
|---|---|---|---|
| 1.104.0（Docker main-latest） | Ubuntu 24.04 / Docker | ✅ 实测汉化生效 | 2026-10 |
| 更早/更新相近版本 | Docker | ⚠️ 理论兼容（词典整词匹配，未命中保持英文，重跑无副作用） | - |

- 补丁脚本会**动态发现** UI 目录（先 `import litellm` 定位，再 glob `python*` 路径兜底），不再绑定镜像内 Python 版本
- LiteLLM 前端大版本更新后，部分文案位置可能变化，但词典按"整词匹配"工作，大部分词条仍会命中；未命中的保持英文，重跑无副作用
- 在新版本上验证过？欢迎提 PR 更新上表

## License

MIT
