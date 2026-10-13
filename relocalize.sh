#!/usr/bin/env bash
# LiteLLM UI 一键汉化（容器升级/重建后重跑此脚本即可恢复中文）
# 用法: bash relocalize.sh
# 默认容器名 litellm，不同请改 CONTAINER 变量

set -e
CONTAINER="${CONTAINER:-litellm}"
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[1/4] 推送补丁脚本进容器 $CONTAINER ..."
for f in $(ls "$DIR" | grep '^litellm_zh_patch.*\.py$'); do
  docker cp "$DIR/$f" "$CONTAINER:/tmp/"
done

echo "[2/4] 依次执行六步汉化 ..."
for i in "" 2 3 4 5 6; do
  docker exec "$CONTAINER" python3 /tmp/litellm_zh_patch$i.py
done

echo "[3/4] 重启 litellm 容器 ..."
docker restart "$CONTAINER"

echo "[4/4] 等待就绪并验证 ..."
sleep 30
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 25 "http://127.0.0.1:4000/health/liveliness" || echo "000")
echo "health: $code"
baks=$(docker exec "$CONTAINER" sh -c 'find /app -name "*.en.bak" 2>/dev/null | wc -l')
echo "备份文件数: $baks（>0 即补丁已生效）"
echo "完成。浏览器打开 http://<host>:4000/ui 强制刷新(Ctrl+Shift+R)即中文。"
