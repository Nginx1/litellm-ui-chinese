#!/usr/bin/env bash
# LiteLLM UI 一键汉化（容器升级/重建后重跑此脚本即可恢复中文）
# 用法: bash relocalize.sh [--dry-run]
#   CONTAINER 环境变量可指定容器名（默认 litellm）
#   --dry-run 只做检查（docker 可用性、补丁文件存在），不执行汉化
set -e

CONTAINER="${CONTAINER:-litellm}"
DIR="$(cd "$(dirname "$0")" && pwd)"
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

say()  { echo -e "[relocalize] $*"; }
die()  { echo -e "[relocalize][错误] $*" >&2; exit 1; }

# ---- 0. 前置检查 ----
command -v docker >/dev/null 2>&1 || die "宿主机未安装 docker"
docker info >/dev/null 2>&1 || die "docker daemon 不可用"
docker inspect "$CONTAINER" >/dev/null 2>&1 || die "容器 $CONTAINER 不存在（可用 CONTAINER=xxx bash relocalize.sh 指定）"

PATCHES=$(ls "$DIR" | grep '^litellm_zh_patch.*\.py$' | sort -V)
[ -n "$PATCHES" ] || die "当前目录未找到 litellm_zh_patch*.py 补丁脚本"

if [ "$DRY_RUN" = "1" ]; then
  say "dry-run 检查通过：容器 $CONTAINER 在运行，发现 $(echo "$PATCHES" | wc -l) 个补丁脚本"
  echo "$PATCHES" | sed 's/^/  - /'
  say "如需执行汉化：bash relocalize.sh"
  exit 0
fi

# ---- 1. 推送补丁脚本进容器 ----
say "[1/4] 推送补丁脚本进容器 $CONTAINER ..."
for f in $PATCHES; do
  docker cp "$DIR/$f" "$CONTAINER:/tmp/" || die "推送 $f 失败"
done

# ---- 2. 依次执行汉化（失败会指出是哪一步） ----
say "[2/4] 依次执行 $(echo "$PATCHES" | wc -l) 步汉化 ..."
for f in $PATCHES; do
  say "  执行 $f ..."
  docker exec "$CONTAINER" python3 "/tmp/$f" || die "补丁 $f 执行失败。可查看容器内 /tmp/$f 手动重试；已改文件有 .en.bak 备份，docker restart $CONTAINER 后可回滚"
done

# ---- 3. 重启容器 ----
say "[3/4] 重启 $CONTAINER 使静态资源生效 ..."
docker restart "$CONTAINER"

# ---- 4. 健康检查（自动探测端口映射） ----
say "[4/4] 等待就绪并验证 ..."
sleep 30
# 从容器端口映射里取宿主机端口：优先取容器内 4000/tcp 的映射，取不到再看 0.0.0.0 绑定，最后才回退 4000
PORT=$(docker port "$CONTAINER" 2>/dev/null | awk '/^4000\/tcp|: 4000\/tcp|^0\.0\.0\.0:4000/{print; exit}' | awk -F'[:/[:space:]]+' '{for(i=NF;i>0;i--) if($i ~ /^[0-9]+$/ && $i != 4000){print $i; exit}}')
[ -n "$PORT" ] || PORT=4000
HEALTH_URL="http://127.0.0.1:${PORT}/health/liveliness"
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 25 "$HEALTH_URL" || echo "000")
say "health($HEALTH_URL): $code"
[ "$code" = "200" ] || say "注意：健康检查未返回 200（可能容器仍在启动或端口非 ${PORT}），请稍后手动确认"

baks=$(docker exec "$CONTAINER" sh -c 'find /app -name "*.en.bak" 2>/dev/null | wc -l')
if [ "$baks" -gt 0 ]; then
  say "备份文件数: $baks（>0 即补丁已生效）"
else
  say "警告：未发现 .en.bak 备份文件，补丁可能未生效，请检查上方各步输出"
fi

say "完成。浏览器打开 http://<host>:${PORT}/ui 强制刷新(Ctrl+Shift+R)即中文。"
