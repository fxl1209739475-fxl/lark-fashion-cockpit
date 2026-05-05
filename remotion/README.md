# lark-fashion-cockpit · Remotion 视频生成

用 React 代码生成女装运营短视频（小红书/抖音风格）。

## 已包含模板

- **OutfitCard** — 9:16 竖屏穿搭灵感卡片（标题 + 副标题 + 标签云 + 价格弹跳）

## 用法

```bash
cd C:\Users\冯兴龙\lark-fashion-cockpit\remotion

# 首次：装依赖
npm install

# 启动 Remotion Studio（浏览器实时预览）
npm start

# 渲染成 mp4
npm run render OutfitCard out/outfit-card.mp4

# 自定义参数渲染
npm run render OutfitCard out/test.mp4 --props='{"title":"夏日新品","subtitle":"DRS-0501-WT","tags":["#显白","#纯棉"],"price":"¥359"}'
```

## 与 cockpit 其他 skill 联动场景

| 数据源 | 视频模板 | 输出场景 |
|---|---|---|
| 17_产品搭配组 | OutfitCard | 每日穿搭灵感（小红书发布）|
| 02_4平台销售 | SalesRanking（待做）| 周销量榜单（朋友圈/视频号）|
| 23_利润表 | TopProfitCard（待做）| 老板娘内部周报 |
| 24_直播记录 | LivestreamRecap（待做）| 直播复盘海报 |

## 添加新模板

1. 在 `src/` 新建一个 `.tsx`，写一个 React 组件
2. 在 `src/Root.tsx` 加一条 `<Composition id="..." component={...} ... />`
3. `npm start` Studio 里就能看到新组合

## 与 Python skill 集成

```python
import subprocess
subprocess.run(
    ["npm", "run", "render", "OutfitCard", "out/today.mp4",
     "--", f"--props={json.dumps(props)}"],
    cwd=r"C:\Users\冯兴龙\lark-fashion-cockpit\remotion",
    shell=True,
)
```
