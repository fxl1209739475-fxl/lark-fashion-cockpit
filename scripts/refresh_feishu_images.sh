#!/usr/bin/env bash
# 重新把 README 里的图片插入到飞书 doc（每次 markdown overwrite 之后跑）
# 使用方法：从 lark-fashion-cockpit 根目录执行
set -e
DOC="SX8DdJv7Co1B9ixMAvIcWvbPn1f"

ins() {
  local anchor="$1"
  local file="$2"
  local cap="$3"
  echo "→ $file  anchor=「$anchor」"
  lark-cli docs +media-insert --doc "$DOC" \
    --file "$file" --type image \
    --selection-with-ellipsis "$anchor" \
    ${cap:+--caption "$cap"} \
    --align center 2>&1 | tail -1
}

# 头部 hero
ins "lark-fashion-cockpit · 电商航母驾驶舱" "./docs/images/architecture.svg" "整体架构"

# 老板娘困境插图
ins "打开浏览器跟系统说话，它帮我把事情办了" "./docs/images/architecture.svg" "统一指挥台示意"

# 板块构成下的总览
ins "合计 33 个 self-contained sub-skill" "./docs/images/architecture.svg" "架构总览"

# omnitask 卡片下
ins "今日总销售 ¥45,820" "./docs/images/demo-omnitask-bridge.png" "驾驶舱主页 demo"

# product-library 字段全景
ins "完整字段全景" "./docs/images/product-library-mindmap.png" "产品库 50 字段全景"

# 演示画廊
ins "### omnitask-bridge · 全员驾驶舱" "./docs/images/demo-omnitask-bridge.png" ""
ins "### im-collector · 跨平台消息汇集" "./docs/images/demo-wechat-monitor.png" ""
ins "### morning-report · 早 8:00 跨渠道情报早报" "./docs/images/demo-morning-report.png" ""
ins "### product-library · 服装电商产品库 + AI 分析" "./docs/images/demo-product-library.png" ""
ins "### blogger-monitor · 对标博主监控（含二创）" "./docs/images/demo-blogger-monitor.png" ""
ins "### im-broadcaster · 飞书指令通知供应商" "./docs/images/demo-wxauto-supplier.png" ""
ins "### stock-replenishment · 库存预警自动报警" "./docs/images/demo-stock-replenishment.png" ""
ins "### launch-decision · AI 上新方案评分" "./docs/images/demo-launch-decision.png" ""
ins "### personal-mirror · 员工今日真实贡献镜像" "./docs/images/demo-personal-mirror.png" ""

echo ""
echo "✅ 全部图片插入完成"
