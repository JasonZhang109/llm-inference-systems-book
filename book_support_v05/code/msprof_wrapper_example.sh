#!/usr/bin/env bash
set -euo pipefail
: "${OUT:?请设置隔离的输出目录}"
: "${APP:?请设置待剖析应用的路径}"
command -v msprof >/dev/null || { echo "未找到 msprof" >&2; exit 1; }
[[ -f "$APP" ]] || { echo "APP 文件不存在" >&2; exit 1; }
mkdir -p "$OUT"
# 示例仅适用于已经验证依赖的 Python 应用。
# 其余应用形式、参数和采集开关应按所用版本指南改写。
msprof --output="$OUT" python3 "$APP"
