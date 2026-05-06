---
name: lark-fashion-cockpit-wechat-monitor
version: 1.1.0
description: "个人微信消息总览/总结 — 三条路径：① 主窗口扫红点速览（自动 ✅）② 长截图 AI 总结（半自动 ✅）③ 第三方导出 .txt 文件 AI 总结（半自动 ✅）。0 微信感知，全微信版本通用，不依赖 wxauto。当用户说「扫微信群 / 微信速览 / 总结这张图 / 导入聊天记录 / 看下微信谁找我了」时使用。"
metadata:
  requires:
    bins: ["lark-cli", "python"]
    pip: ["pyautogui", "pygetwindow", "openai", "Pillow", "opencv-python", "numpy", "pyperclip", "pywin32"]
    env: ["DOUBAO_API_KEY", "DEEPSEEK_API_KEY", "LARK_FASHION_COCKPIT_BOSS_CHAT"]
---

# 微信监控 · 三条路径覆盖个人微信消息分析

> **🎯 痛点：** 工作微信群多、信息分散、未读积压。
> **核心价值：** 三种触发方式 → 都能让 AI 帮你扫一遍微信、总结重点，**完全跳过**桌面 RPA / 数据库 hook 的不稳定坑。

---

## 一、四条路径对比

| 路径 | 自动化程度 | 微信感知 | 兼容微信 4.1.x | 风险 | 状态 |
|---|---|---|---|---|---|
| **A. 主窗口扫红点** (`scan-wechat.py`) | ✅ 全自动 | ❌ OS 截图 | ✅ 全版本 | 0 | ✅ **已跑通** |
| **B. 长截图 AI 总结** (`summarize-image.py`) | 🟡 半自动（30s 用户操作） | ❌ | ✅ | 0 | ✅ **已跑通** |
| **C. 导出文件 AI 总结** (`summarize-export.py`) | 🟡 半自动（用户先用第三方导出）| ❌ | ✅ | 0 | ✅ **已跑通** |
| **D. 桌面 RPA 进群细看** (`scan-person.py`) | ⚠️ 半自动 | ⚠️ 模拟键鼠 | ⚠️ Win11 焦点限制 | 低 | 🟡 **实验性** |

**为什么 B/C 是主推**：跳过 Win11 + 微信 4.x 的所有坑，一次手动 + AI 自动总结，30 秒内拿到摘要。

---

## 二、路径 A：主窗口扫红点（自动）

### 用法
```
飞书发: 扫微信群
飞书发: 扫微信群 关键词=DRS-0429,出货延期
```

### 原理
```
pygetwindow 找微信主窗口 → pyautogui 截屏（不动微信进程）
  → DOUBAO 视觉识别左侧群列表
  → 输出 JSON：哪些群有红点 / 谁@你 / 关键词命中
  → 飞书卡片
```

### 输出示例
```
📱 微信群速览  ·  09:32

摘要：你有 3 个工作群有未读消息，1 条提到 DRS-0429 出货，2 个营销号已忽略。

🚨 紧急
🚨 ZC 工厂群：DRS-0429 雪纺面料卡在染色环节，预计延 2 天
🚨 朱健豪@你：直播脚本 V2 待审

未读群
• 老板娘合伙人群 [3]
• ZC 工厂沟通群 [12] 🔔@你
```

### 局限
仅看到每个群"最后一条预览"。要看完整对话上下文 → 用路径 B 或 C。

---

## 三、路径 B：长截图 AI 总结（半自动，主推）

### 工作流
```
1. 你打开任意聊天工具（微信/Discord/钉钉/...）进群
2. 按飞书快捷键 Ctrl+Shift+A → 选择"滚动截屏"
3. 框选聊天区 → 滚到 N 小时前停 → 完成（约 30 秒）
4. 把生成的长图发给 cockpit 飞书机器人
   附文字：「总结这张图过去 72 小时」
   ↓
5. cockpit 收到 → summarize-image.py
   ↓
6. 长图按宽度切段（每段 1076×3500）→ 一次喂 DOUBAO
   ↓
7. 飞书卡片回执
```

### 实测能力
```
原图 1076×21180 px (4 MB)
  ↓ 切 7 段
  ↓ DOUBAO 一次调用（总 1.4 MB）
  ↓
识别 98 条消息
  ↓
提取：4 个主要发言人 / 4 个话题 / 6 句完整摘要 / 12 条原文摘录
所有消息时间精确（5/4 12:51 → 5/5 23:44）
```

### 命令
```bash
python skills/wechat-monitor/scripts/summarize-image.py \
  --image "C:\path\to\screenshot.png" \
  --hint "终极目标实现群 5/4-5/6" \
  --label "终极目标实现群"
```

### 集成到 event-listener
飞书机器人收到图片消息 + 触发关键词（"总结这张" / "扫这张图"）→ 自动调用此脚本。

---

## 四、路径 C：第三方导出文件 AI 总结（半自动）

### 适用场景
淘宝/eBay/亚马逊/Facebook 上有商业软件能把微信聊天记录导出成 `.txt` / `.json`。把导出文件喂给 cockpit → DEEPSEEK 文本分析。

### 优势 vs 路径 B
- **比图片便宜 20 倍**（DEEPSEEK 文本输入 ~0.5 元/百万 token vs DOUBAO 视觉 ~10 元/百万）
- **能精确按时间窗过滤**（图不能精确控制时间）
- **能装数千条消息**（图视觉装不下这么多）

### 支持格式
1. **WeChatExporter / 留痕** 等 .txt：
   ```
   2026-05-04 14:30:00 张三:
     消息内容
   ```
2. **简单 .txt**：`[2026-05-04 14:30] 张三: 内容`
3. **JSON 数组**：`[{"time": "...", "from": "...", "content": "..."}]`

### 命令
```bash
python skills/wechat-monitor/scripts/summarize-export.py \
  --file "C:\path\to\group-export.txt" \
  --hours 72 \
  --label "ZC 工厂沟通群"
```

---

## 五、路径 D：桌面 RPA 进群细看（实验性）

`scan-person.py` —— 自动控制微信窗口：搜索群名 → 进入 → 滚屏 → 截图 → DOUBAO 总结。

### 当前状态：⚠️ 实验性

**已跑通的部分**：
- ✅ DOUBAO 视觉定位搜索框
- ✅ 自动输入群名 + Enter 进群
- ✅ 滚屏到时间窗外
- ✅ OpenCV 拼接多张滚屏截图为长图
- ✅ DOUBAO 长图分段总结

**核心限制**：
- ⚠️ Win11 反抢焦点机制 + 微信 Qt 渲染 → 必须**用户每次跑前 Alt+Tab 切到微信**
- ⚠️ 必须从**独立 PowerShell** 跑，不能从 Cursor 终端跑（Cursor 子窗口会盖住微信）

### 仅在以下情况建议用
- 你没装第三方导出工具
- 你不想用飞书滚动截屏
- 你能接受"启动前 Alt+Tab 切微信一次"

否则推荐路径 B / C。

### 命令
```bash
# 必须从独立 PowerShell 跑
cd C:\Users\冯兴龙\lark-fashion-cockpit
python skills\wechat-monitor\scripts\scan-person.py --name "终极目标实现群" --hours 72 --debug
```

---

## 六、安全 & 隐私

- 路径 A/B/D 截图**完全不写盘**（用完即 GC）
- 路径 C 的导出文件读完即销毁（不持久化）
- AI 识别后只持久化"脱敏摘要文本"到飞书
- **不调微信任何接口、不读微信本地文件、不 hook 微信进程** → 0 风险

---

## 七、文件清单

| 文件 | 路径 | 状态 |
|---|---|---|
| 主窗口扫红点 | `scripts/scan-wechat.py` | ✅ |
| 长截图总结 | `scripts/summarize-image.py` | ✅ |
| 导出文件总结 | `scripts/summarize-export.py` | ✅ |
| 桌面 RPA 进群 | `scripts/scan-person.py` | 🟡 实验性 |
| 截屏 + UIA 探测（开发用） | `scripts/snap-wechat.py` / `probe-wechat-uia.py` | 工具 |
| 唤起微信（被托盘隐藏时） | `scripts/wake-wechat.py` | 工具 |

---

## 八、与其他 skill 的关系

- **`wecom-bridge`**（企业微信 API）= 互补，B 端走企微，C 端朋友型走 wechat-monitor
- **`cross-platform-im-agent`**（综合智能体）= 父级 skill，编排本 skill + wecom-bridge + 飞书自有
- **`wxauto-supplier-bridge`**（主动发消息）= 兄弟 skill，本 skill 负责"读"，那个负责"发"
- **`auto-scheduler`** = 调度本 skill 跑定时扫描（30 分钟一次主窗口扫红点）
- **`morning-report`** = 早 8:00 把本 skill 摘要并入早报卡片
