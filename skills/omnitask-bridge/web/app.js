const platforms = [
  { id: "taobao", name: "淘宝", color: "#9c2f45" },
  { id: "douyin", name: "抖音", color: "#0f766e" },
  { id: "xiaohongshu", name: "小红书", color: "#c47a1d" },
  { id: "shipinhao", name: "视频号", color: "#6b5b95" },
];

const dailySales = [
  { date: "04/23", taobao: 68200, douyin: 51400, xiaohongshu: 22600, shipinhao: 12400, orders: 812 },
  { date: "04/24", taobao: 72100, douyin: 58600, xiaohongshu: 25100, shipinhao: 14700, orders: 896 },
  { date: "04/25", taobao: 76300, douyin: 62200, xiaohongshu: 29300, shipinhao: 16900, orders: 943 },
  { date: "04/26", taobao: 80600, douyin: 71800, xiaohongshu: 31800, shipinhao: 18400, orders: 1048 },
  { date: "04/27", taobao: 84100, douyin: 69400, xiaohongshu: 34200, shipinhao: 21100, orders: 1086 },
  { date: "04/28", taobao: 92800, douyin: 78100, xiaohongshu: 38900, shipinhao: 24600, orders: 1218 },
  { date: "04/29", taobao: 98600, douyin: 85400, xiaohongshu: 42100, shipinhao: 26300, orders: 1325 },
];

const productStorageKey = "modaops.products.v1";
const productApiPath = "/api/products";
const productSyncState = {
  mode: "local",
  updatedAt: null,
  lastError: "",
};

const defaultProducts = [
  {
    id: "P001",
    name: "法式收腰碎花连衣裙",
    sku: "DRS-0429-FL",
    category: "连衣裙",
    status: "selling",
    platforms: ["淘宝", "抖音", "小红书"],
    price: 299,
    swatchA: "#b93c56",
    swatchB: "#f1c2cc",
    colors: [
      { name: "莓果红", hex: "#b93c56", sizes: { XS: { made: 60, stock: 12 }, S: { made: 120, stock: 18 }, M: { made: 180, stock: 21 }, L: { made: 110, stock: 20 }, XL: { made: 50, stock: 14 } } },
      { name: "奶油白", hex: "#f1e7da", sizes: { XS: { made: 40, stock: 8 }, S: { made: 90, stock: 16 }, M: { made: 130, stock: 24 }, L: { made: 80, stock: 15 }, XL: { made: 35, stock: 10 } } },
    ],
  },
  {
    id: "P002",
    name: "通勤垂感西装裤",
    sku: "PNT-0418-SU",
    category: "裤装",
    status: "selling",
    platforms: ["淘宝", "视频号"],
    price: 239,
    swatchA: "#2d3137",
    swatchB: "#8b949e",
    colors: [
      { name: "炭黑", hex: "#2d3137", sizes: { XS: { made: 50, stock: 9 }, S: { made: 100, stock: 20 }, M: { made: 160, stock: 36 }, L: { made: 110, stock: 31 }, XL: { made: 70, stock: 22 } } },
      { name: "雾灰", hex: "#8b949e", sizes: { XS: { made: 30, stock: 7 }, S: { made: 80, stock: 19 }, M: { made: 120, stock: 35 }, L: { made: 80, stock: 22 }, XL: { made: 40, stock: 14 } } },
    ],
  },
  {
    id: "P003",
    name: "短款针织开衫",
    sku: "KNT-0402-CD",
    category: "针织",
    status: "history",
    platforms: ["小红书", "抖音"],
    price: 189,
    swatchA: "#c47a1d",
    swatchB: "#f3d8b2",
    colors: [
      { name: "焦糖", hex: "#c47a1d", sizes: { XS: { made: 45, stock: 11 }, S: { made: 90, stock: 24 }, M: { made: 120, stock: 39 }, L: { made: 85, stock: 31 }, XL: { made: 40, stock: 18 } } },
      { name: "燕麦", hex: "#d6c1a1", sizes: { XS: { made: 35, stock: 10 }, S: { made: 75, stock: 26 }, M: { made: 105, stock: 42 }, L: { made: 70, stock: 29 }, XL: { made: 30, stock: 16 } } },
    ],
  },
  {
    id: "P004",
    name: "轻薄防晒衬衫",
    sku: "SHT-0420-SP",
    category: "衬衫",
    status: "selling",
    platforms: ["淘宝", "抖音", "视频号"],
    price: 169,
    swatchA: "#5d9aa6",
    swatchB: "#e1f0f1",
    colors: [
      { name: "海盐蓝", hex: "#5d9aa6", sizes: { XS: { made: 70, stock: 13 }, S: { made: 150, stock: 27 }, M: { made: 210, stock: 43 }, L: { made: 150, stock: 38 }, XL: { made: 80, stock: 22 } } },
      { name: "云白", hex: "#edf4f2", sizes: { XS: { made: 50, stock: 12 }, S: { made: 120, stock: 32 }, M: { made: 160, stock: 45 }, L: { made: 110, stock: 35 }, XL: { made: 60, stock: 21 } } },
    ],
  },
  {
    id: "P005",
    name: "高腰 A 字半身裙",
    sku: "SKT-0328-A",
    category: "半裙",
    status: "soldout",
    platforms: ["淘宝", "小红书"],
    price: 199,
    swatchA: "#733b4a",
    swatchB: "#d6aab4",
    colors: [
      { name: "酒红", hex: "#733b4a", sizes: { XS: { made: 30, stock: 0 }, S: { made: 90, stock: 0 }, M: { made: 130, stock: 2 }, L: { made: 70, stock: 0 }, XL: { made: 30, stock: 0 } } },
      { name: "黑色", hex: "#252525", sizes: { XS: { made: 30, stock: 0 }, S: { made: 80, stock: 1 }, M: { made: 120, stock: 0 }, L: { made: 70, stock: 1 }, XL: { made: 30, stock: 0 } } },
    ],
  },
];

function cloneData(data) {
  return JSON.parse(JSON.stringify(data));
}

function normalizeProduct(product) {
  const colors = Array.isArray(product.colors) && product.colors.length ? product.colors : [];
  return {
    id: product.id || `P${Date.now().toString(36).toUpperCase()}`,
    name: product.name || "未命名产品",
    sku: product.sku || "NEW-SKU",
    category: product.category || "未分类",
    status: ["selling", "soldout", "history"].includes(product.status) ? product.status : "selling",
    platforms: Array.isArray(product.platforms) && product.platforms.length ? product.platforms : ["淘宝"],
    price: Number(product.price) || 0,
    swatchA: product.swatchA || colors[0]?.hex || "#9c2f45",
    swatchB: product.swatchB || colors[1]?.hex || colors[0]?.hex || "#f1c2cc",
    operations: product.operations && typeof product.operations === "object" ? { ...product.operations } : {},
    colors: colors.map((color) => ({
      name: color.name || "默认色",
      hex: color.hex || "#9c2f45",
      sizes: Object.entries(color.sizes || {}).reduce((rows, [size, row]) => {
        if (!size) return rows;
        rows[size] = {
          made: Math.max(0, Number(row?.made) || 0),
          stock: Math.max(0, Number(row?.stock) || 0),
        };
        return rows;
      }, {}),
    })),
  };
}

function loadProducts() {
  try {
    const saved = localStorage.getItem(productStorageKey);
    if (!saved) return cloneData(defaultProducts);
    const parsed = JSON.parse(saved);
    if (!Array.isArray(parsed)) return cloneData(defaultProducts);
    return parsed.map(normalizeProduct);
  } catch (error) {
    console.warn("产品库本地数据读取失败，已使用示例数据。", error);
    return cloneData(defaultProducts);
  }
}

function saveProductsLocal() {
  try {
    localStorage.setItem(productStorageKey, JSON.stringify(products));
  } catch (error) {
    console.warn("产品库本地数据保存失败。", error);
  }
}

function canUseProductApi() {
  return ["http:", "https:"].includes(window.location.protocol);
}

async function syncProductsToServer(source = "browser") {
  if (!canUseProductApi()) return false;
  try {
    const response = await fetch(productApiPath, {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ source, products }),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    productSyncState.mode = "server";
    productSyncState.updatedAt = payload.updatedAt || new Date().toISOString();
    productSyncState.lastError = "";
    renderProductPersistenceBadge();
    return true;
  } catch (error) {
    productSyncState.mode = "local";
    productSyncState.lastError = error.message;
    renderProductPersistenceBadge();
    console.warn("Product API sync failed; localStorage copy is still available.", error);
    return false;
  }
}

function saveProducts(source = "browser") {
  saveProductsLocal();
  syncProductsToServer(source);
}

let products = loadProducts();

async function hydrateProductsFromServer() {
  if (!canUseProductApi()) return;
  try {
    const response = await fetch(productApiPath, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    const serverProducts = Array.isArray(payload.products) ? payload.products.map(normalizeProduct) : [];
    if (serverProducts.length) {
      products = serverProducts;
      saveProductsLocal();
      productSyncState.mode = "server";
      productSyncState.updatedAt = payload.updatedAt || null;
      productSyncState.lastError = "";
      renderAll();
      if (currentProductId && document.querySelector("#modalBackdrop").classList.contains("show")) {
        openProduct(currentProductId);
      }
      return;
    }
    if (products.length) {
      await syncProductsToServer("seed-from-browser");
    }
  } catch (error) {
    productSyncState.mode = "local";
    productSyncState.lastError = error.message;
    renderProductPersistenceBadge();
    console.warn("Product API load failed; using localStorage products.", error);
  }
}

const contentPlatforms = [
  { name: "抖音", views: 482000, interactions: 38200, conversion: 2.8, sales: 85400, color: "#0f766e" },
  { name: "小红书", views: 216000, interactions: 29400, conversion: 1.9, sales: 42100, color: "#c47a1d" },
  { name: "视频号", views: 128000, interactions: 8600, conversion: 1.4, sales: 26300, color: "#6b5b95" },
  { name: "淘宝短视频", views: 93000, interactions: 5200, conversion: 3.1, sales: 37200, color: "#9c2f45" },
];

const contentTopics = [
  { title: "春夏连衣裙显瘦 3 套穿搭", stage: "idea", owner: "小雅", due: "05/02", progress: 15, product: "法式收腰碎花连衣裙", channel: "小红书" },
  { title: "通勤裤一周不重样", stage: "script", owner: "阿宁", due: "05/03", progress: 35, product: "通勤垂感西装裤", channel: "抖音" },
  { title: "防晒衬衫户外实测", stage: "shooting", owner: "小唐", due: "05/01", progress: 58, product: "轻薄防晒衬衫", channel: "视频号" },
  { title: "半身裙梨形身材试穿", stage: "editing", owner: "米粒", due: "04/30", progress: 78, product: "高腰 A 字半身裙", channel: "小红书" },
  { title: "针织开衫老客返场预告", stage: "publish", owner: "阿宁", due: "04/29", progress: 92, product: "短款针织开衫", channel: "淘宝短视频" },
  { title: "五一出游胶囊衣橱", stage: "script", owner: "小雅", due: "05/04", progress: 42, product: "多款组合", channel: "抖音" },
  { title: "直播间 30 秒爆品口播", stage: "shooting", owner: "小唐", due: "05/02", progress: 60, product: "法式收腰碎花连衣裙", channel: "淘宝短视频" },
];

const productKnowledge = {
  P001: {
    videos: [
      { title: "春夏连衣裙显瘦 3 套穿搭", platform: "小红书", status: "脚本中", views: 82000, interactions: 9600, sales: 32600, conversion: 2.7, linkedUnits: ["莓果红-S", "莓果红-M", "奶油白-M"] },
      { title: "直播间 30 秒爆品口播", platform: "淘宝短视频", status: "拍摄中", views: 36000, interactions: 2200, sales: 18400, conversion: 3.4, linkedUnits: ["莓果红-M", "奶油白-S"] },
      { title: "通勤约会两穿试衣间", platform: "抖音", status: "已发布", views: 142000, interactions: 11800, sales: 51700, conversion: 2.9, linkedUnits: ["莓果红-L", "奶油白-M", "奶油白-L"] },
    ],
    assets: [
      { type: "主图", title: "正面站姿主图", note: "用于淘宝首图，突出收腰和裙摆", a: "#b93c56", b: "#f1c2cc" },
      { type: "细节图", title: "领口与腰线细节", note: "强调法式 V 领、腰部线条", a: "#f1c2cc", b: "#fff5f7" },
      { type: "场景图", title: "咖啡店外景", note: "适合小红书种草封面", a: "#c47a1d", b: "#f1c2cc" },
      { type: "色卡", title: "莓果红 / 奶油白", note: "用于详情页颜色说明", a: "#b93c56", b: "#f1e7da" },
    ],
    detailBlocks: [
      { title: "商品详情页首屏", copy: "法式收腰剪裁，腰线抬高 3cm，适合通勤、约会、度假三种场景。" },
      { title: "卖点模块", copy: "碎花不显杂、裙摆有余量、上身显腰细，主推 25-35 岁轻熟客群。" },
      { title: "尺码建议", copy: "S/M 为主销尺码；莓果红适合直播间氛围，奶油白适合图文种草。" },
    ],
    paidCampaigns: [
      { name: "小红书搜索种草加热", platform: "小红书", content: "春夏连衣裙显瘦 3 套穿搭", spend: 8600, paidUnits: 46, paidGmv: 13754, refundUnits: 7, refundAmount: 2093, exposure: 92000, clicks: 3800, verdict: "观察放量", note: "支付 ROI 尚可，退款后 ROI 偏紧，适合继续测封面和人群。" },
      { name: "抖音短视频随心推", platform: "抖音", content: "通勤约会两穿试衣间", spend: 12800, paidUnits: 79, paidGmv: 23621, refundUnits: 9, refundAmount: 2691, exposure: 168000, clicks: 6200, verdict: "可放量", note: "莓果红 M/L 成交集中，素材里腰线和上身转身镜头有效。" },
      { name: "淘宝短视频站内推广", platform: "淘宝", content: "直播间 30 秒爆品口播", spend: 5200, paidUnits: 31, paidGmv: 9269, refundUnits: 5, refundAmount: 1495, exposure: 41000, clicks: 1800, verdict: "小额保留", note: "站内成交稳定，但净 ROI 受退款影响，需要优化尺码说明。" },
    ],
    liveSessions: [
      { title: "主理人直播上新讲解", hostGroup: "主理人直播", host: "主理人安安", date: "04/29 20:18", scene: "上新日", clip: "00:18:32-00:22:10", units: 38, gmv: 11362, conversion: 8.6, tryOn: "163cm / S 码莓果红", visual: "近景转身 + 腰线手势", verdict: "适合强推", script: "这条不是普通碎花裙，重点看腰线，它把腰往上提了三公分，梨形姐妹穿会更显比例。莓果红上镜更有氛围，奶油白适合日常通勤。", analysis: ["开场直接讲身材痛点", "手势指向腰线，画面信息明确", "尺码建议不足导致后续退款偏高"], signals: [{ time: "20:19", event: "讲腰线显瘦", units: 12 }, { time: "20:20", event: "主播转身展示裙摆", units: 16 }, { time: "20:21", event: "尺码建议", units: 10 }] },
      { title: "店铺主播1 温柔场景讲解", hostGroup: "店铺主播1", host: "店铺主播1-米粒", date: "05/01 14:06", scene: "日常店播", clip: "01:05:14-01:08:40", units: 21, gmv: 6279, conversion: 5.1, tryOn: "158cm / S 码奶油白", visual: "半身近景 + 侧身腰线", verdict: "适合奶油白", script: "如果你想要一条不挑场景的裙子，奶油白会更温柔，外面搭针织开衫也可以。它的裙摆不是贴腿的，所以坐下不会紧。", analysis: ["场景感强，适合温柔客群", "成交峰值低于莓果红", "建议补充深色内衣透感提醒"], signals: [{ time: "14:07", event: "讲奶油白通勤", units: 7 }, { time: "14:08", event: "坐下不紧演示", units: 9 }, { time: "14:08", event: "搭配开衫", units: 5 }] },
      { title: "店铺主播2 价格利益点讲解", hostGroup: "店铺主播2", host: "店铺主播2-阿宁", date: "05/02 16:32", scene: "日常店播", clip: "00:32:12-00:35:24", units: 13, gmv: 3887, conversion: 3.8, tryOn: "165cm / M 码莓果红", visual: "中景站姿 + 优惠信息口播", verdict: "不建议主讲", script: "今天这个价格是比较合适的，喜欢法式碎花的可以看一下，上身不会很夸张，直播间这波库存不多。", analysis: ["价格利益点多，产品差异讲得少", "画面没有充分展示腰线", "成交低且停留弱，暂不适合作主讲"], signals: [{ time: "16:33", event: "讲直播间优惠", units: 4 }, { time: "16:34", event: "讲库存不多", units: 5 }, { time: "16:35", event: "简单试穿展示", units: 4 }] },
      { title: "店铺主播3 身材痛点讲解", hostGroup: "店铺主播3", host: "店铺主播3-小雅", date: "05/02 20:48", scene: "晚间店播", clip: "02:18:10-02:22:36", units: 32, gmv: 9568, conversion: 7.4, tryOn: "160cm / S 码莓果红", visual: "全身镜 + 腰胯对比", verdict: "可重点培养", script: "梨形姐妹看这里，这个裙摆不是直筒贴胯，它有一个自然展开，所以胯部不会被卡住。腰这里收得很明显，但不是勒的感觉。", analysis: ["人群痛点准确", "全身镜画面对比强", "适合继续训练尺码和材质解释"], signals: [{ time: "20:49", event: "梨形胯部痛点", units: 11 }, { time: "20:50", event: "全身镜对比", units: 13 }, { time: "20:51", event: "腰部不勒解释", units: 8 }] },
      { title: "达人客串试穿", hostGroup: "达人客串", host: "达人小唐", date: "05/03 21:42", scene: "达人客串", clip: "00:42:05-00:45:18", units: 29, gmv: 8671, conversion: 6.9, tryOn: "168cm / M 码莓果红", visual: "全身远景 + 走动裙摆", verdict: "适合做素材切片", script: "这件我觉得高个子穿更能撑起来，它走动的时候裙摆很好看，而且这个红不是艳红，是有点莓果感的红。", analysis: ["全身远景强化裙摆动态", "高个子试穿带动 M/L", "少讲面料和透感，退款风险未被提前消化"], signals: [{ time: "21:43", event: "走动展示裙摆", units: 15 }, { time: "21:44", event: "强调莓果红不艳", units: 8 }, { time: "21:45", event: "高个子建议", units: 6 }] },
    ],
    elements: {
      色彩元素: ["莓果红", "奶油白", "低饱和碎花", "暖调春夏"],
      款式元素: ["法式 V 领", "高腰收腰", "A 字裙摆", "中长裙"],
      材质元素: ["轻薄雪纺感", "垂顺", "微透需内衬", "适合春夏"],
      场景元素: ["通勤", "约会", "旅行", "咖啡店外景"],
      内容关键词: ["显瘦", "法式", "氛围感", "梨形友好"],
    },
  },
  P002: {
    videos: [
      { title: "通勤裤一周不重样", platform: "抖音", status: "脚本中", views: 68000, interactions: 5200, sales: 21900, conversion: 2.1, linkedUnits: ["炭黑-M", "雾灰-M"] },
    ],
    assets: [
      { type: "主图", title: "直筒垂感主图", note: "突出腿型修饰", a: "#2d3137", b: "#8b949e" },
      { type: "细节图", title: "腰头与裤线", note: "展示通勤质感", a: "#8b949e", b: "#e5e7eb" },
    ],
    detailBlocks: [
      { title: "详情页卖点", copy: "垂感面料、直筒版型、适配衬衫和针织上衣。" },
    ],
    elements: {
      色彩元素: ["炭黑", "雾灰", "低调中性色"],
      款式元素: ["高腰", "直筒", "西装裤线"],
      材质元素: ["垂感", "抗皱", "通勤面料"],
      场景元素: ["上班", "面试", "差旅"],
      内容关键词: ["显腿直", "胶囊衣橱", "一周穿搭"],
    },
  },
  P004: {
    videos: [
      { title: "防晒衬衫户外实测", platform: "视频号", status: "拍摄中", views: 128000, interactions: 8600, sales: 26300, conversion: 1.4, linkedUnits: ["海盐蓝-M", "云白-M"] },
    ],
    assets: [
      { type: "主图", title: "海盐蓝挂拍", note: "突出清爽防晒感", a: "#5d9aa6", b: "#e1f0f1" },
      { type: "场景图", title: "户外阳光场景", note: "适合视频号与小红书", a: "#f3d8b2", b: "#5d9aa6" },
    ],
    detailBlocks: [
      { title: "防晒场景", copy: "通勤路上、旅行外搭、空调房薄外套三种场景复用。" },
    ],
    elements: {
      色彩元素: ["海盐蓝", "云白", "清爽冷色"],
      款式元素: ["宽松衬衫", "轻薄外搭", "防晒袖长"],
      材质元素: ["轻薄", "透气", "微皱肌理"],
      场景元素: ["通勤", "户外", "旅行"],
      内容关键词: ["防晒", "轻薄", "不闷", "外搭"],
    },
  },
};

const topicStages = [
  { id: "idea", name: "选题", color: "#9c2f45" },
  { id: "script", name: "脚本", color: "#c47a1d" },
  { id: "shooting", name: "拍摄", color: "#0f766e" },
  { id: "editing", name: "剪辑", color: "#6b5b95" },
  { id: "publish", name: "待发布", color: "#4b5563" },
];

const salesTargets = {
  annualTarget: 12000000,
  currentMonth: "04",
  quarters: [
    { name: "Q1", target: 2400000, actual: 2180000 },
    { name: "Q2", target: 3200000, actual: 1980000 },
    { name: "Q3", target: 3400000, actual: 0 },
    { name: "Q4", target: 3000000, actual: 0 },
  ],
  months: [
    { month: "01", target: 720000, actual: 690000 },
    { month: "02", target: 760000, actual: 710000 },
    { month: "03", target: 920000, actual: 780000 },
    { month: "04", target: 980000, actual: 812000 },
    { month: "05", target: 1050000, actual: 0 },
    { month: "06", target: 1170000, actual: 0 },
    { month: "07", target: 1080000, actual: 0 },
    { month: "08", target: 1160000, actual: 0 },
    { month: "09", target: 1160000, actual: 0 },
    { month: "10", target: 1040000, actual: 0 },
    { month: "11", target: 1120000, actual: 0 },
    { month: "12", target: 1260000, actual: 0 },
  ],
  channels: [
    { name: "淘宝", target: 5200000, actual: 1810000, color: "#9c2f45" },
    { name: "抖音", target: 3900000, actual: 1340000, color: "#0f766e" },
    { name: "小红书", target: 1900000, actual: 620000, color: "#c47a1d" },
    { name: "视频号", target: 1000000, actual: 320000, color: "#6b5b95" },
  ],
};

const dataSources = [
  { name: "淘宝销售数据", type: "销售", mode: "网页采集", status: "synced", lastSync: "今日 09:02", rows: 1280, color: "#9c2f45" },
  { name: "抖音订单数据", type: "销售", mode: "表格导入", status: "synced", lastSync: "今日 09:08", rows: 846, color: "#0f766e" },
  { name: "小红书内容数据", type: "内容", mode: "网页采集", status: "warning", lastSync: "昨日 22:15", rows: 216, color: "#c47a1d" },
  { name: "视频号内容数据", type: "内容", mode: "手动导入", status: "synced", lastSync: "今日 08:40", rows: 94, color: "#6b5b95" },
  { name: "SKU 库存表", type: "库存", mode: "Excel 导入", status: "error", lastSync: "2 天前", rows: 895, color: "#4b5563" },
];

const syncLogs = [
  { title: "淘宝销售页采集完成", time: "今日 09:02", detail: "新增 1280 行，销售额 ¥98,600", status: "成功" },
  { title: "抖音订单表导入完成", time: "今日 09:08", detail: "新增 846 行，订单 432 笔", status: "成功" },
  { title: "小红书内容页需重新登录", time: "昨日 22:15", detail: "页面跳转到登录页，等待授权", status: "待处理" },
  { title: "SKU 库存表未更新", time: "2 天前", detail: "建议上传最新库存表", status: "缺失" },
];

const productionStages = ["打样", "面辅料", "裁剪", "车缝", "后整质检", "发货入仓"];

const productionOrders = [
  { product: "法式收腰碎花连衣裙", sku: "DRS-0429-FL", supplier: "杭州云裳服饰", stage: "车缝", quantity: 1200, finished: 620, eta: "05/08", onTimeRate: 86, risk: "正常", color: "#9c2f45" },
  { product: "轻薄防晒衬衫", sku: "SHT-0420-SP", supplier: "广州青禾制衣", stage: "后整质检", quantity: 900, finished: 760, eta: "05/03", onTimeRate: 92, risk: "正常", color: "#0f766e" },
  { product: "通勤垂感西装裤", sku: "PNT-0418-SU", supplier: "宁波简线工厂", stage: "面辅料", quantity: 800, finished: 120, eta: "05/15", onTimeRate: 64, risk: "需跟进", color: "#c47a1d" },
  { product: "短款针织开衫", sku: "KNT-0402-CD", supplier: "桐乡织造合作社", stage: "发货入仓", quantity: 600, finished: 600, eta: "04/30", onTimeRate: 98, risk: "即将到仓", color: "#6b5b95" },
  { product: "高腰 A 字半身裙", sku: "SKT-0328-A", supplier: "杭州云裳服饰", stage: "裁剪", quantity: 700, finished: 260, eta: "05/10", onTimeRate: 73, risk: "面料补单", color: "#4b5563" },
];

const suppliers = [
  { name: "杭州云裳服饰", city: "杭州", category: "连衣裙 / 半裙", styles: ["法式收腰碎花连衣裙", "高腰 A 字半身裙"], finishedRate: 96.8, defectRate: 2.1, onTimeRate: 88, leadTime: 16, producing: 1900, score: "稳定主力" },
  { name: "广州青禾制衣", city: "广州", category: "衬衫 / 外套", styles: ["轻薄防晒衬衫", "短袖罩衫"], finishedRate: 98.2, defectRate: 1.3, onTimeRate: 94, leadTime: 13, producing: 900, score: "交付优秀" },
  { name: "宁波简线工厂", city: "宁波", category: "裤装", styles: ["通勤垂感西装裤"], finishedRate: 94.1, defectRate: 3.6, onTimeRate: 72, leadTime: 21, producing: 800, score: "需盯交期" },
  { name: "桐乡织造合作社", city: "桐乡", category: "针织", styles: ["短款针织开衫"], finishedRate: 97.4, defectRate: 1.8, onTimeRate: 91, leadTime: 18, producing: 600, score: "适合返单" },
];

const privateDomain = {
  totalCustomers: 68420,
  newToday: 842,
  activeToday: 5120,
  conversations: 3280,
  segments: [
    { name: "大客户", count: 1420, arpu: 1860, repurchase: 68, action: "新品优先试穿、专属搭配顾问", color: "#9c2f45" },
    { name: "中客户", count: 8460, arpu: 620, repurchase: 42, action: "上新提醒、套装搭配、会员券", color: "#0f766e" },
    { name: "小客户", count: 28600, arpu: 188, repurchase: 19, action: "爆款种草、首单后复购引导", color: "#c47a1d" },
    { name: "新客", count: 21300, arpu: 96, repurchase: 8, action: "欢迎语、尺码助手、低门槛福利", color: "#6b5b95" },
    { name: "沉默客户", count: 8640, arpu: 240, repurchase: 5, action: "唤醒活动、补货通知、内容召回", color: "#4b5563" },
  ],
  channels: [
    { name: "企业微信", target: 30000, actual: 24600, color: "#0f766e" },
    { name: "淘宝会员", target: 26000, actual: 21800, color: "#9c2f45" },
    { name: "抖音粉丝群", target: 16000, actual: 12800, color: "#6b5b95" },
    { name: "小红书私信", target: 8000, actual: 5220, color: "#c47a1d" },
  ],
  actions: [
    { title: "补货通知", value: "680 人", detail: "碎花连衣裙 M/L 码到货提醒" },
    { title: "搭配推荐", value: "1,240 次", detail: "按产品元素推荐成套搭配" },
    { title: "会员召回", value: "420 人", detail: "30 天未购客户唤醒" },
    { title: "高客单维护", value: "86 人", detail: "大客户一对一新品预览" },
  ],
};

const serviceExperience = {
  totalTickets: 1860,
  responseMinutes: 3.8,
  satisfaction: 96.2,
  refundRate: 4.6,
  platforms: [
    { name: "淘宝客服", inquiries: 860, response: 2.6, satisfaction: 97.1, afterSales: 128, color: "#9c2f45" },
    { name: "抖音客服", inquiries: 520, response: 4.2, satisfaction: 95.4, afterSales: 86, color: "#0f766e" },
    { name: "小红书私信", inquiries: 280, response: 6.8, satisfaction: 93.8, afterSales: 24, color: "#c47a1d" },
    { name: "视频号客服", inquiries: 200, response: 5.1, satisfaction: 94.6, afterSales: 31, color: "#6b5b95" },
  ],
  issues: [
    { name: "尺码咨询", target: 600, actual: 520, color: "#9c2f45" },
    { name: "物流进度", target: 420, actual: 390, color: "#0f766e" },
    { name: "退换货", target: 300, actual: 286, color: "#c47a1d" },
    { name: "面料/色差", target: 220, actual: 184, color: "#6b5b95" },
    { name: "售后赔付", target: 120, actual: 96, color: "#4b5563" },
  ],
};

const executiveMetrics = {
  sales: 252400,
  grossProfit: 112800,
  netProfitRate: 18.6,
  cashGap: 186000,
  alerts: [
    { title: "通勤垂感西装裤生产交期偏慢", level: "需跟进", detail: "面辅料阶段停留 3 天，预计影响 05/15 到仓。" },
    { title: "高腰 A 字半身裙售罄但库存不足", level: "补货判断", detail: "售罄率 99.4%，剩余 4 件，需要判断是否返单或转清仓。" },
    { title: "小红书内容数据需重新登录", level: "数据源", detail: "昨日 22:15 采集失败，可能影响内容归因。" },
    { title: "Q2 销售进度低于时间进度", level: "目标缺口", detail: "Q2 完成 61.9%，缺口 ¥1,220,000。" },
  ],
  health: [
    { name: "销售达成", target: 100, actual: 84, color: "#9c2f45" },
    { name: "利润健康", target: 100, actual: 76, color: "#0f766e" },
    { name: "库存周转", target: 100, actual: 68, color: "#c47a1d" },
    { name: "供应链履约", target: 100, actual: 82, color: "#6b5b95" },
    { name: "服务体验", target: 100, actual: 91, color: "#4b5563" },
  ],
};

const productHealth = [
  { name: "法式收腰碎花连衣裙", status: "主推爆款", profit: 36.8, stockDays: 9, content: 3, risk: "补货窗口", note: "内容表现强，库存消耗快，适合加拍和返单。" },
  { name: "轻薄防晒衬衫", status: "稳定上升", profit: 31.4, stockDays: 14, content: 1, risk: "可加码", note: "防晒场景进入旺季，适合做户外内容。" },
  { name: "通勤垂感西装裤", status: "交期风险", profit: 28.2, stockDays: 18, content: 1, risk: "供应链", note: "销售稳定但生产偏慢，需盯面辅料。" },
];

const platformProfit = [
  { name: "淘宝", sales: 98600, gross: 42600, ads: 8600, commission: 5200, netRate: 21.5, color: "#9c2f45" },
  { name: "抖音", sales: 85400, gross: 36500, ads: 12200, commission: 9800, netRate: 12.8, color: "#0f766e" },
  { name: "小红书", sales: 42100, gross: 19600, ads: 4200, commission: 3600, netRate: 18.1, color: "#c47a1d" },
  { name: "视频号", sales: 26300, gross: 11400, ads: 1900, commission: 1600, netRate: 22.4, color: "#6b5b95" },
];

const costStructure = [
  { name: "商品成本", target: 100, actual: 42, color: "#9c2f45" },
  { name: "平台扣点", target: 100, actual: 8, color: "#0f766e" },
  { name: "投放成本", target: 100, actual: 13, color: "#c47a1d" },
  { name: "达人佣金", target: 100, actual: 9, color: "#6b5b95" },
  { name: "物流仓储", target: 100, actual: 6, color: "#4b5563" },
];

const productProfit = [
  { name: "法式收腰碎花连衣裙", sales: 98600, margin: 36.8, net: 21400, role: "利润主推" },
  { name: "轻薄防晒衬衫", sales: 74200, margin: 31.4, net: 15600, role: "旺季增长" },
  { name: "高腰 A 字半身裙", sales: 15700, margin: 18.2, net: 1800, role: "售罄清尾" },
];

const launchWaves = [
  { name: "五一出游波段", date: "05/01-05/07", products: 8, status: "拍摄中", target: 920000, progress: 64 },
  { name: "初夏通勤波段", date: "05/10-05/20", products: 12, status: "打样确认", target: 1380000, progress: 38 },
  { name: "618 第一波", date: "05/25-06/05", products: 16, status: "企划中", target: 2200000, progress: 22 },
];

const categoryMix = [
  { name: "连衣裙", target: 100, actual: 32, color: "#9c2f45" },
  { name: "衬衫/外搭", target: 100, actual: 24, color: "#0f766e" },
  { name: "裤装", target: 100, actual: 18, color: "#c47a1d" },
  { name: "半裙", target: 100, actual: 14, color: "#6b5b95" },
  { name: "针织", target: 100, actual: 12, color: "#4b5563" },
];

const developmentStyles = [
  { name: "夏季通勤无袖连衣裙", stage: "打样", price: "¥299-339", role: "主推利润款", owner: "商品组" },
  { name: "防晒轻外套二代", stage: "面料测试", price: "¥199-239", role: "旺季引流款", owner: "产品组" },
  { name: "松弛感阔腿裤", stage: "版型调整", price: "¥239-269", role: "通勤基础款", owner: "商品组" },
  { name: "度假印花半裙", stage: "企划", price: "¥189-229", role: "内容种草款", owner: "内容组" },
];

const stockAlerts = [
  { title: "高腰 A 字半身裙", level: "缺货", detail: "剩余 4 件，售罄率 99.4%，建议判断返单或下架替换。" },
  { title: "法式收腰碎花连衣裙 M 码", level: "补货", detail: "内容带动明显，M 码 21 件，预计 9 天售罄。" },
  { title: "短款针织开衫", level: "滞销", detail: "剩余占比偏高，建议私域老客返场或组合清仓。" },
];

const stockAllocation = [
  { name: "淘宝", target: 100, actual: 38, color: "#9c2f45" },
  { name: "抖音直播", target: 100, actual: 26, color: "#0f766e" },
  { name: "小红书种草", target: 100, actual: 14, color: "#c47a1d" },
  { name: "视频号", target: 100, actual: 10, color: "#6b5b95" },
  { name: "私域", target: 100, actual: 12, color: "#4b5563" },
];

const replenishmentAdvice = [
  { name: "法式收腰碎花连衣裙", action: "返单 800 件", reason: "内容转化高，库存 9 天内见底", priority: "高" },
  { name: "轻薄防晒衬衫", action: "补货 600 件", reason: "旺季防晒需求上升，供应商交付稳定", priority: "中" },
  { name: "通勤垂感西装裤", action: "暂缓加单", reason: "供应链交期偏慢，先保证现有订单", priority: "观察" },
];

const campaigns = [
  { name: "五一出游穿搭", platform: "小红书/抖音", budget: 68000, spent: 41200, roi: 3.6, product: "连衣裙 / 防晒衬衫" },
  { name: "直播间爆款返场", platform: "淘宝直播", budget: 36000, spent: 22000, roi: 4.2, product: "碎花连衣裙" },
  { name: "618 预热种草", platform: "全平台", budget: 120000, spent: 18000, roi: 2.1, product: "待定波段款" },
];

const liveSchedules = [
  { name: "淘宝直播晚场", host: "安安", time: "20:00", product: "法式收腰碎花连衣裙", target: 180000 },
  { name: "抖音午间快闪", host: "小唐", time: "12:30", product: "轻薄防晒衬衫", target: 96000 },
  { name: "视频号老客场", host: "米粒", time: "19:30", product: "针织开衫返场", target: 52000 },
];

const fulfillmentOrders = [
  { name: "淘宝订单", paid: 860, shipped: 712, pending: 148, timeout: 12, warehouse: "华东仓" },
  { name: "抖音订单", paid: 520, shipped: 390, pending: 130, timeout: 18, warehouse: "华南仓" },
  { name: "私域订单", paid: 180, shipped: 152, pending: 28, timeout: 2, warehouse: "华东仓" },
];

const logisticsIssues = [
  { name: "待揽收超时", target: 120, actual: 28, color: "#9c2f45" },
  { name: "派送异常", target: 80, actual: 16, color: "#0f766e" },
  { name: "拒收退回", target: 60, actual: 9, color: "#c47a1d" },
  { name: "预售临期", target: 100, actual: 34, color: "#6b5b95" },
];

const returnReasons = [
  { name: "尺码不合适", target: 100, actual: 32, color: "#9c2f45" },
  { name: "面料不符合预期", target: 100, actual: 24, color: "#0f766e" },
  { name: "色差", target: 100, actual: 18, color: "#c47a1d" },
  { name: "版型不显瘦", target: 100, actual: 16, color: "#6b5b95" },
  { name: "物流/包装", target: 100, actual: 10, color: "#4b5563" },
];

const productFeedback = [
  { title: "法式收腰碎花连衣裙", level: "尺码建议需强化", detail: "M/L 码咨询高，建议详情页加身高体重试穿表。" },
  { title: "轻薄防晒衬衫", level: "面料反馈好", detail: "用户认可轻薄，但担心透，建议强调内搭建议。" },
  { title: "通勤垂感西装裤", level: "版型反馈分化", detail: "梨形用户满意，苹果型用户反馈腰腹包容不足。" },
];

const competitors = [
  { title: "竞品 A：法式碎花裙", level: "热卖", detail: "售价 ¥279，主打显瘦腰线，抖音 3 条视频破 10 万播放。" },
  { title: "竞品 B：防晒衬衫", level: "快速上升", detail: "售价 ¥159，强调凉感面料，视频号成交增长明显。" },
  { title: "竞品 C：通勤西裤", level: "价格压力", detail: "售价 ¥199，使用买赠拉动转化，需关注利润空间。" },
];

const trendSignals = [
  { name: "低饱和花色", target: 100, actual: 86, color: "#9c2f45" },
  { name: "防晒轻外套", target: 100, actual: 78, color: "#0f766e" },
  { name: "松弛通勤", target: 100, actual: 72, color: "#c47a1d" },
  { name: "度假氛围感", target: 100, actual: 65, color: "#6b5b95" },
];

const collaborationTasks = [
  { stage: "商品", title: "确认 618 第一波商品结构", owner: "商品组", due: "05/02", risk: "正常" },
  { stage: "供应链", title: "跟进西装裤面料到厂", owner: "跟单", due: "04/30", risk: "逾期风险" },
  { stage: "内容", title: "碎花裙 3 条视频脚本定稿", owner: "内容组", due: "05/01", risk: "正常" },
  { stage: "运营", title: "五一活动库存分配", owner: "平台运营", due: "04/30", risk: "高优先级" },
  { stage: "客服", title: "更新尺码咨询话术", owner: "客服主管", due: "05/01", risk: "正常" },
  { stage: "数据", title: "补齐小红书采集登录", owner: "数据", due: "04/29", risk: "待处理" },
];

const sourceStatusText = {
  synced: "已更新",
  warning: "需确认",
  error: "待更新",
};

const statusText = {
  selling: "在售",
  soldout: "售罄",
  history: "历史款",
};

const formatCurrency = (value) =>
  new Intl.NumberFormat("zh-CN", {
    style: "currency",
    currency: "CNY",
    maximumFractionDigits: 0,
  }).format(value);

const sum = (items) => items.reduce((total, item) => total + item, 0);

const escapeHtml = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

let currentProductId = null;
let currentBusinessSection = "profile";
let currentLiveHost = "all";
let productFormState = { productId: null, colors: [] };
let productImportDraft = { rows: [], objects: [], products: [], summary: null };

const importAliases = {
  styleNo: ["款号", "SKU", "SKU码", "SQU编码", "商品编码", "货号", "款式编码"],
  productName: ["产品名称", "商品名称", "款名", "品名"],
  retailPrice: ["售价", "零售价", "销售价", "吊牌价"],
  liveDate: ["直播日期", "上新日期", "首播日期"],
  cost: ["成本", "成本价"],
  costGoodsValue: ["成本货值"],
  season: ["季节", "年份季节", "波段"],
  secondCategory: ["二级分类", "品类", "分类", "产品分类"],
  difficultyCategory: ["难易分类", "难度分类"],
  pending: ["待定"],
  styleGrade: ["产品款式划分", "爆款分类", "款式划分", "ABCD分类", "等级"],
  dataUpdatedAt: ["数据更新日期", "数据更新时间", "更新时间"],
  productImage: ["款式图", "产品图", "图片"],
  planProductionQty: ["计划生产件数", "做货件数", "生产件数", "生产数量"],
  firstOrderQty: ["首单数"],
  productionGoodsValue: ["生产货值"],
  arrivedQty: ["已到仓数", "到仓数"],
  arrivedGoodsValue: ["到仓货值"],
  arrivalStatus: ["到仓状态"],
  notArrivedQty: ["未到仓数"],
  notArrivedGoodsValue: ["未到仓货值"],
  warehouseStock: ["在仓库存", "剩余库存", "库存"],
  stockGoodsValue: ["库存货值", "在仓货值"],
  warehouseAndUnarrivedGoodsValue: ["在仓+未到仓货值", "在仓未到仓货值"],
  orderOccupiedQty: ["订单占有"],
  orderOccupiedGoodsValue: ["订单占有货值"],
  availableQty: ["共有可用数", "可用数"],
  twoDayReturnForecast: ["近两天发货后预估退货数", "预估退货数"],
  actualSalesAmount: ["实销金额"],
  totalSalesQty: ["总销量"],
  totalSalesAmount: ["总销售额"],
  totalReturnQty: ["总退货数"],
  totalReturnAmount: ["总退货额"],
  shippedQty: ["发货数"],
  shippedAmount: ["发货金额"],
  afterShippingReturnQty: ["发货后退货数"],
  returnAmount: ["退货金额"],
  afterShippingReturnRate: ["发货后退货率"],
  comprehensiveReturnRate: ["综合退货率"],
  expectedReceivedQty: ["预估实收件数"],
  expectedReceivedAmount: ["预估实收金额"],
  totalOrderQty: ["总下单数"],
  soldRealQty: ["已实销件数", "实销数", "实际销售数量"],
  targetSellThroughRate: ["需要完成目标售罄", "目标售罄率"],
  currentSellThroughRate: ["目前售罄率", "当前售罄率", "售罄率"],
  neededRealSalesQty: ["还需实销件数", "距离目标还需实销件数", "距目标还需实销"],
  neededRealSalesGoodsValue: ["还需实销货值"],
  targetGmvQty: ["完成对应目标所需gmv件数", "目标GMV件数"],
  targetGmvValue: ["完成对应目标所需gmv值", "目标GMV值"],
  colorName: ["颜色", "颜色名称", "色号", "色系"],
  sizeName: ["尺码", "码数", "尺寸", "size"],
  status: ["状态", "售卖状态", "产品状态"],
  platforms: ["平台", "售卖平台", "渠道"],
};

const operationImportFields = [
  ["dataUpdatedAt", "text"],
  ["styleNo", "text"],
  ["productImage", "text"],
  ["retailPrice", "number"],
  ["liveDate", "text"],
  ["cost", "number"],
  ["costGoodsValue", "number"],
  ["season", "text"],
  ["secondCategory", "text"],
  ["difficultyCategory", "text"],
  ["pending", "text"],
  ["styleGrade", "text"],
  ["planProductionQty", "number"],
  ["firstOrderQty", "number"],
  ["productionGoodsValue", "number"],
  ["arrivedQty", "number"],
  ["arrivedGoodsValue", "number"],
  ["arrivalStatus", "text"],
  ["notArrivedQty", "number"],
  ["notArrivedGoodsValue", "number"],
  ["warehouseStock", "number"],
  ["stockGoodsValue", "number"],
  ["warehouseAndUnarrivedGoodsValue", "number"],
  ["orderOccupiedQty", "number"],
  ["orderOccupiedGoodsValue", "number"],
  ["availableQty", "number"],
  ["twoDayReturnForecast", "number"],
  ["actualSalesAmount", "number"],
  ["totalSalesQty", "number"],
  ["totalSalesAmount", "number"],
  ["totalReturnQty", "number"],
  ["totalReturnAmount", "number"],
  ["shippedQty", "number"],
  ["shippedAmount", "number"],
  ["afterShippingReturnQty", "number"],
  ["returnAmount", "number"],
  ["afterShippingReturnRate", "percent"],
  ["comprehensiveReturnRate", "percent"],
  ["expectedReceivedQty", "number"],
  ["expectedReceivedAmount", "number"],
  ["totalOrderQty", "number"],
  ["soldRealQty", "number"],
  ["targetSellThroughRate", "percent"],
  ["currentSellThroughRate", "percent"],
  ["neededRealSalesQty", "number"],
  ["neededRealSalesGoodsValue", "number"],
  ["targetGmvQty", "number"],
  ["targetGmvValue", "number"],
];

const businessOpsEditorFields = [
  { key: "dataUpdatedAt", label: "数据更新日期", type: "text", group: "基础档案" },
  { key: "liveDate", label: "直播日期", type: "text", group: "基础档案" },
  { key: "season", label: "季节", type: "text", group: "基础档案" },
  { key: "secondCategory", label: "二级分类", type: "text", group: "基础档案" },
  { key: "difficultyCategory", label: "难易分类", type: "text", group: "基础档案" },
  { key: "pending", label: "待定备注", type: "text", group: "基础档案" },
  { key: "styleGrade", label: "爆款分类", type: "text", group: "基础档案" },
  { key: "cost", label: "成本", type: "number", group: "基础档案" },
  { key: "planProductionQty", label: "计划生产件数", type: "number", group: "生产到仓" },
  { key: "firstOrderQty", label: "首单数", type: "number", group: "生产到仓" },
  { key: "arrivedQty", label: "已到仓数", type: "number", group: "生产到仓" },
  { key: "arrivalStatus", label: "到仓状态", type: "text", group: "生产到仓" },
  { key: "warehouseStock", label: "在仓库存", type: "number", group: "库存占用" },
  { key: "orderOccupiedQty", label: "订单占有数", type: "number", group: "库存占用" },
  { key: "availableQty", label: "共有可用数", type: "number", group: "库存占用" },
  { key: "twoDayReturnForecast", label: "近两天预计退货", type: "number", group: "库存占用" },
  { key: "totalSalesQty", label: "总销量", type: "number", group: "销售退货" },
  { key: "totalReturnQty", label: "总退货数", type: "number", group: "销售退货" },
  { key: "shippedQty", label: "发货数", type: "number", group: "销售退货" },
  { key: "afterShippingReturnQty", label: "发货后退货数", type: "number", group: "销售退货" },
  { key: "afterShippingReturnRate", label: "发货后退货率", type: "percent", group: "销售退货" },
  { key: "comprehensiveReturnRate", label: "综合退货率", type: "percent", group: "销售退货" },
  { key: "expectedReceivedQty", label: "预计实收件数", type: "number", group: "目标测算" },
  { key: "totalOrderQty", label: "总下单数", type: "number", group: "目标测算" },
  { key: "soldRealQty", label: "实销件数", type: "number", group: "目标测算" },
  { key: "targetSellThroughRate", label: "目标售罄率", type: "percent", group: "目标测算" },
  { key: "currentSellThroughRate", label: "当前售罄率", type: "percent", group: "目标测算" },
  { key: "neededRealSalesQty", label: "距离目标还需实销", type: "number", group: "目标测算" },
  { key: "targetGmvQty", label: "完成目标所需 GMV 件数", type: "number", group: "目标测算" },
  { key: "targetGmvValue", label: "完成目标所需 GMV 值", type: "number", group: "目标测算" },
];

function productTotals(product) {
  const rows = product.colors.flatMap((color) => Object.values(color.sizes));
  const made = sum(rows.map((row) => row.made));
  const stock = sum(rows.map((row) => row.stock));
  const sold = made - stock;
  const sellRate = made ? sold / made : 0;
  const stockRate = made ? stock / made : 0;
  return { made, stock, sold, sellRate, stockRate };
}

function formatPercentValue(value) {
  return `${((Number(value) || 0) * 100).toFixed(1)}%`;
}

function getProductOperations(product) {
  const totals = productTotals(product);
  const raw = product.operations || {};
  const defaultSeasonByProduct = {
    P001: "26夏",
    P002: "26夏",
    P003: "26春",
    P004: "26夏",
    P005: "26春",
  };
  const numberField = (key, fallback) => {
    const value = Number(raw[key]);
    return Number.isFinite(value) ? value : fallback;
  };
  const textField = (key, fallback) => {
    const value = raw[key];
    return value === undefined || value === null || value === "" ? fallback : value;
  };

  const retailPrice = numberField("retailPrice", product.price || 0);
  const cost = numberField("cost", Math.round(retailPrice * 0.38));
  const planProductionQty = numberField("planProductionQty", totals.made);
  const firstOrderQty = numberField("firstOrderQty", planProductionQty);
  const productionGoodsValue = numberField("productionGoodsValue", planProductionQty * retailPrice);
  const arrivedQty = numberField("arrivedQty", Math.max(0, planProductionQty - Math.round(planProductionQty * 0.12)));
  const arrivedGoodsValue = numberField("arrivedGoodsValue", arrivedQty * retailPrice);
  const notArrivedQty = numberField("notArrivedQty", Math.max(0, planProductionQty - arrivedQty));
  const notArrivedGoodsValue = numberField("notArrivedGoodsValue", notArrivedQty * retailPrice);
  const warehouseStock = numberField("warehouseStock", totals.stock);
  const stockGoodsValue = numberField("stockGoodsValue", warehouseStock * retailPrice);
  const orderOccupiedQty = numberField("orderOccupiedQty", Math.round(warehouseStock * 0.04));
  const orderOccupiedGoodsValue = numberField("orderOccupiedGoodsValue", orderOccupiedQty * retailPrice);
  const availableQty = numberField("availableQty", Math.max(0, warehouseStock - orderOccupiedQty));
  const warehouseAndUnarrivedGoodsValue = numberField("warehouseAndUnarrivedGoodsValue", stockGoodsValue + notArrivedGoodsValue);
  const totalSalesQty = numberField("totalSalesQty", Math.max(totals.sold, Math.round(planProductionQty * 0.28)));
  const totalSalesAmount = numberField("totalSalesAmount", totalSalesQty * retailPrice);
  const totalReturnQty = numberField("totalReturnQty", Math.round(totalSalesQty * 0.18));
  const totalReturnAmount = numberField("totalReturnAmount", totalReturnQty * retailPrice);
  const shippedQty = numberField("shippedQty", Math.max(0, totalSalesQty - Math.round(totalReturnQty * 0.35)));
  const shippedAmount = numberField("shippedAmount", shippedQty * retailPrice);
  const afterShippingReturnQty = numberField("afterShippingReturnQty", Math.round(shippedQty * 0.12));
  const returnAmount = numberField("returnAmount", afterShippingReturnQty * retailPrice);
  const afterShippingReturnRate = numberField("afterShippingReturnRate", shippedQty ? afterShippingReturnQty / shippedQty : 0);
  const comprehensiveReturnRate = numberField("comprehensiveReturnRate", totalSalesQty ? totalReturnQty / totalSalesQty : 0);
  const expectedReceivedQty = numberField("expectedReceivedQty", Math.max(0, totalSalesQty - totalReturnQty));
  const expectedReceivedAmount = numberField("expectedReceivedAmount", expectedReceivedQty * retailPrice);
  const twoDayReturnForecast = numberField("twoDayReturnForecast", Math.round(afterShippingReturnQty / 6));
  const actualSalesAmount = numberField("actualSalesAmount", expectedReceivedAmount);
  const totalOrderQty = numberField("totalOrderQty", firstOrderQty);
  const soldRealQty = numberField("soldRealQty", expectedReceivedQty);
  const targetSellThroughRate = numberField("targetSellThroughRate", 0.75);
  const currentSellThroughRate = numberField("currentSellThroughRate", totalOrderQty ? soldRealQty / totalOrderQty : totals.sellRate);
  const targetRealQty = Math.ceil(totalOrderQty * targetSellThroughRate);
  const neededRealSalesQty = numberField("neededRealSalesQty", Math.max(0, targetRealQty - soldRealQty));
  const neededRealSalesGoodsValue = numberField("neededRealSalesGoodsValue", neededRealSalesQty * retailPrice);
  const targetGmvQty = numberField(
    "targetGmvQty",
    Math.ceil(neededRealSalesQty / Math.max(0.2, 1 - comprehensiveReturnRate)),
  );
  const targetGmvValue = numberField("targetGmvValue", targetGmvQty * retailPrice);
  const remainingRealSalesQty = numberField("remainingRealSalesQty", Math.max(0, totalOrderQty - soldRealQty));
  const remainingSellableValue = numberField("remainingSellableValue", remainingRealSalesQty * retailPrice);
  const arrivalStatus = textField("arrivalStatus", notArrivedQty > 0 ? "2部分到仓" : "1完全到仓");
  const styleGrade = textField(
    "styleGrade",
    currentSellThroughRate >= 0.65 && comprehensiveReturnRate <= 0.25 ? "A" : currentSellThroughRate >= 0.35 ? "B+" : "B",
  );

  return {
    dataUpdatedAt: textField("dataUpdatedAt", "2026/04/28"),
    styleNo: textField("styleNo", product.sku),
    productImage: textField("productImage", "款式图"),
    productName: product.name,
    retailPrice,
    liveDate: textField("liveDate", "待补充"),
    cost,
    costGoodsValue: numberField("costGoodsValue", cost * planProductionQty),
    season: textField("season", defaultSeasonByProduct[product.id] || "当季"),
    secondCategory: textField("secondCategory", product.category),
    difficultyCategory: textField("difficultyCategory", "待定"),
    pending: textField("pending", "待定"),
    styleGrade,
    planProductionQty,
    firstOrderQty,
    productionGoodsValue,
    arrivedQty,
    arrivedGoodsValue,
    arrivalStatus,
    notArrivedQty,
    notArrivedGoodsValue,
    warehouseStock,
    stockGoodsValue,
    warehouseAndUnarrivedGoodsValue,
    orderOccupiedQty,
    orderOccupiedGoodsValue,
    availableQty,
    twoDayReturnForecast,
    actualSalesAmount,
    totalSalesQty,
    totalSalesAmount,
    totalReturnQty,
    totalReturnAmount,
    shippedQty,
    shippedAmount,
    afterShippingReturnQty,
    returnAmount,
    afterShippingReturnRate,
    comprehensiveReturnRate,
    expectedReceivedQty,
    expectedReceivedAmount,
    totalOrderQty,
    soldRealQty,
    targetSellThroughRate,
    currentSellThroughRate,
    neededRealSalesQty,
    neededRealSalesGoodsValue,
    targetGmvQty,
    targetGmvValue,
    remainingRealSalesQty,
    remainingSellableValue,
  };
}

function businessFieldGroups(ops) {
  return [
    {
      id: "profile",
      title: "基础档案",
      meta: "产品身份、售价、季节、分类和款式判断",
      summary: `${ops.season} · ${ops.secondCategory} · ${ops.styleGrade}`,
      fields: [
        ["数据更新日期", ops.dataUpdatedAt],
        ["款号", ops.styleNo],
        ["款式图", ops.productImage],
        ["产品名称", ops.productName],
        ["售价", formatCurrency(ops.retailPrice)],
        ["直播日期", ops.liveDate],
        ["成本", formatCurrency(ops.cost)],
        ["成本货值", formatCurrency(ops.costGoodsValue)],
        ["季节", ops.season],
        ["二级分类", ops.secondCategory],
        ["难易分类", ops.difficultyCategory],
        ["待定", ops.pending],
        ["产品款式划分", ops.styleGrade],
      ],
    },
    {
      id: "production",
      title: "生产到仓",
      meta: "生产计划、首单、货值和到仓状态",
      summary: `${ops.arrivedQty} / ${ops.planProductionQty} 到仓`,
      fields: [
        ["计划生产件数", ops.planProductionQty.toLocaleString("zh-CN")],
        ["首单数", ops.firstOrderQty.toLocaleString("zh-CN")],
        ["生产货值", formatCurrency(ops.productionGoodsValue)],
        ["已到仓数", ops.arrivedQty.toLocaleString("zh-CN")],
        ["到仓货值", formatCurrency(ops.arrivedGoodsValue)],
        ["到仓状态", ops.arrivalStatus],
        ["未到仓数", ops.notArrivedQty.toLocaleString("zh-CN")],
        ["未到仓货值", formatCurrency(ops.notArrivedGoodsValue)],
      ],
    },
    {
      id: "stock",
      title: "库存数据",
      meta: "在仓、未到仓、订单占用和可售数量",
      summary: `${ops.availableQty} 件可用`,
      fields: [
        ["在仓库存", ops.warehouseStock.toLocaleString("zh-CN")],
        ["库存货值", formatCurrency(ops.stockGoodsValue)],
        ["在仓 + 未到仓货值", formatCurrency(ops.warehouseAndUnarrivedGoodsValue)],
        ["订单占有", ops.orderOccupiedQty.toLocaleString("zh-CN")],
        ["订单占有货值", formatCurrency(ops.orderOccupiedGoodsValue)],
        ["共有可用数", ops.availableQty.toLocaleString("zh-CN")],
        ["近两天发货后预估退货数", ops.twoDayReturnForecast.toLocaleString("zh-CN")],
        ["实销金额", formatCurrency(ops.actualSalesAmount)],
      ],
    },
    {
      id: "sales",
      title: "销售退货",
      meta: "销售、发货、退货和预计实收",
      summary: `${formatPercentValue(ops.comprehensiveReturnRate)} 综合退货率`,
      fields: [
        ["总销量", ops.totalSalesQty.toLocaleString("zh-CN")],
        ["总销售额", formatCurrency(ops.totalSalesAmount)],
        ["总退货数", ops.totalReturnQty.toLocaleString("zh-CN")],
        ["总退货额", formatCurrency(ops.totalReturnAmount)],
        ["发货数", ops.shippedQty.toLocaleString("zh-CN")],
        ["发货金额", formatCurrency(ops.shippedAmount)],
        ["发货后退货数", ops.afterShippingReturnQty.toLocaleString("zh-CN")],
        ["退货金额", formatCurrency(ops.returnAmount)],
        ["发货后退货率", formatPercentValue(ops.afterShippingReturnRate)],
        ["综合退货率", formatPercentValue(ops.comprehensiveReturnRate)],
        ["预计实收件数", ops.expectedReceivedQty.toLocaleString("zh-CN")],
        ["预计实收金额", formatCurrency(ops.expectedReceivedAmount)],
      ],
    },
    {
      id: "target",
      title: "目标测算",
      meta: "目标售罄、缺口件数和所需 GMV",
      summary: `还需 ${ops.neededRealSalesQty} 件`,
      fields: [
        ["总下单数", ops.totalOrderQty.toLocaleString("zh-CN")],
        ["已实销件数", ops.soldRealQty.toLocaleString("zh-CN")],
        ["目前售罄率", formatPercentValue(ops.currentSellThroughRate)],
        ["需完成目标售罄", formatPercentValue(ops.targetSellThroughRate)],
        ["还需实销件数", ops.neededRealSalesQty.toLocaleString("zh-CN")],
        ["还需实销货值", formatCurrency(ops.neededRealSalesGoodsValue)],
        ["完成对应目标所需 GMV 件数", ops.targetGmvQty.toLocaleString("zh-CN")],
        ["完成对应目标所需 GMV 值", formatCurrency(ops.targetGmvValue)],
        ["还可售件数", ops.remainingRealSalesQty.toLocaleString("zh-CN")],
        ["还可售货值", formatCurrency(ops.remainingSellableValue)],
      ],
    },
  ];
}

function selectedPlatform() {
  return document.querySelector("#platformFilter").value;
}

function filteredSalesRows() {
  const platform = selectedPlatform();
  return dailySales.map((row) => {
    if (platform === "all") return row;
    return { ...row, orders: Math.round(row.orders * (row[platform] / platformTotal(row))) };
  });
}

function platformTotal(row) {
  return sum(platforms.map((platform) => row[platform.id]));
}

function renderMetrics() {
  const rows = filteredSalesRows();
  const platform = selectedPlatform();
  const today = rows[rows.length - 1];
  const yesterday = rows[rows.length - 2];
  const todaySales = platform === "all" ? platformTotal(today) : today[platform];
  const yesterdaySales = platform === "all" ? platformTotal(yesterday) : yesterday[platform];
  const delta = yesterdaySales ? (todaySales - yesterdaySales) / yesterdaySales : 0;
  const totalStock = sum(products.map((product) => productTotals(product).stock));
  const totalMade = sum(products.map((product) => productTotals(product).made));
  const activeProducts = products.filter((product) => product.status === "selling").length;

  const metrics = [
    { label: "今日销售额", value: formatCurrency(todaySales), delta: `${(delta * 100).toFixed(1)}%`, sub: "较昨日", color: "#9c2f45" },
    { label: "今日订单量", value: today.orders.toLocaleString("zh-CN"), delta: "", sub: "全渠道成交订单", color: "#0f766e" },
    { label: "在售产品数", value: activeProducts.toString(), delta: "", sub: `产品库共 ${products.length} 款`, color: "#c47a1d" },
    { label: "总剩余库存", value: totalStock.toLocaleString("zh-CN"), delta: "", sub: `做货 ${totalMade.toLocaleString("zh-CN")} 件`, color: "#6b5b95" },
  ];

  document.querySelector("#metricGrid").innerHTML = metrics
    .map(
      (metric) => `
        <article class="metric-card" style="--metric-color:${metric.color}">
          <div class="metric-label">${metric.label}</div>
          <div class="metric-value">${metric.value}</div>
          <div class="metric-sub">${metric.delta ? `<span class="delta">${metric.delta}</span>` : ""}<span>${metric.sub}</span></div>
        </article>
      `,
    )
    .join("");
}

function renderTrendChart() {
  const rows = filteredSalesRows();
  const platform = selectedPlatform();
  const maxValue = Math.max(...rows.map((row) => (platform === "all" ? platformTotal(row) : row[platform])));

  document.querySelector("#trendChart").innerHTML = rows
    .map((row) => {
      if (platform !== "all") {
        const height = Math.max(6, (row[platform] / maxValue) * 218);
        return `
          <div class="trend-day" title="${row.date} ${formatCurrency(row[platform])}">
            <div class="bar-stack">
              <div class="bar ${platform}" style="height:${height}px"></div>
            </div>
            <div class="day-label">${row.date}</div>
          </div>
        `;
      }

      const total = platformTotal(row);
      return `
        <div class="trend-day" title="${row.date} ${formatCurrency(total)}">
          <div class="bar-stack">
            ${platforms
              .map((item) => {
                const height = Math.max(6, (row[item.id] / maxValue) * 218);
                return `<div class="bar ${item.id}" style="height:${height}px"></div>`;
              })
              .join("")}
          </div>
          <div class="day-label">${row.date}</div>
        </div>
      `;
    })
    .join("");
}

function renderPlatformBars() {
  const today = dailySales[dailySales.length - 1];
  const total = platformTotal(today);

  document.querySelector("#platformBars").innerHTML = platforms
    .map((platform) => {
      const value = today[platform.id];
      const percent = total ? (value / total) * 100 : 0;
      return `
        <div class="platform-row">
          <div class="platform-meta">
            <strong>${platform.name}</strong>
            <span>${formatCurrency(value)} · ${percent.toFixed(1)}%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width:${percent}%; --platform-color:${platform.color}"></div>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderContentMetrics() {
  const views = sum(contentPlatforms.map((item) => item.views));
  const interactions = sum(contentPlatforms.map((item) => item.interactions));
  const sales = sum(contentPlatforms.map((item) => item.sales));
  const avgConversion = contentPlatforms.length
    ? contentPlatforms.reduce((total, item) => total + item.conversion, 0) / contentPlatforms.length
    : 0;
  const publishing = contentTopics.filter((topic) => topic.stage !== "publish").length;

  const metrics = [
    { label: "本周播放量", value: views.toLocaleString("zh-CN"), sub: "短视频 / 种草内容", color: "#0f766e" },
    { label: "互动量", value: interactions.toLocaleString("zh-CN"), sub: "赞藏评转合计", color: "#c47a1d" },
    { label: "内容引导成交", value: formatCurrency(sales), sub: "样例归因口径", color: "#9c2f45" },
    { label: "制作中选题", value: publishing.toString(), sub: `共 ${contentTopics.length} 个选题`, color: "#6b5b95" },
    { label: "平均转化率", value: `${avgConversion.toFixed(1)}%`, sub: "成交 / 访问", color: "#4b5563" },
  ];

  document.querySelector("#contentMetricGrid").innerHTML = metrics
    .map(
      (metric) => `
        <article class="metric-card" style="--metric-color:${metric.color}">
          <div class="metric-label">${metric.label}</div>
          <div class="metric-value">${metric.value}</div>
          <div class="metric-sub"><span>${metric.sub}</span></div>
        </article>
      `,
    )
    .join("");
}

function renderContentBars() {
  const maxViews = Math.max(...contentPlatforms.map((item) => item.views));
  document.querySelector("#contentBars").innerHTML = contentPlatforms
    .map((item) => {
      const width = maxViews ? (item.views / maxViews) * 100 : 0;
      return `
        <div class="content-row">
          <div class="content-meta">
            <strong>${item.name}</strong>
            <span>${item.views.toLocaleString("zh-CN")} 播放</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width:${width}%; --platform-color:${item.color}"></div>
          </div>
          <div class="content-stats">
            <span>互动 ${item.interactions.toLocaleString("zh-CN")}</span>
            <span>转化 ${item.conversion}%</span>
            <span>成交 ${formatCurrency(item.sales)}</span>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderContentFunnel() {
  const maxCount = Math.max(...topicStages.map((stage) => contentTopics.filter((topic) => topic.stage === stage.id).length));
  document.querySelector("#contentFunnel").innerHTML = topicStages
    .map((stage) => {
      const count = contentTopics.filter((topic) => topic.stage === stage.id).length;
      const width = maxCount ? (count / maxCount) * 100 : 0;
      return `
        <div class="funnel-row">
          <div class="funnel-meta">
            <strong class="stage-label"><span class="stage-dot" style="--stage-color:${stage.color}"></span>${stage.name}</strong>
            <span>${count} 个</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width:${width}%; --platform-color:${stage.color}"></div>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderTopicBoard() {
  const stageFilter = document.querySelector("#topicStageFilter").value;
  document.querySelector("#topicBoard").innerHTML = topicStages
    .filter((stage) => stageFilter === "all" || stage.id === stageFilter)
    .map((stage) => {
      const topics = contentTopics.filter((topic) => topic.stage === stage.id);
      return `
        <section class="topic-column">
          <div class="topic-column-head">
            <span class="stage-label"><span class="stage-dot" style="--stage-color:${stage.color}"></span>${stage.name}</span>
            <span>${topics.length}</span>
          </div>
          ${topics
            .map(
              (topic) => `
                <article class="topic-card">
                  <strong>${topic.title}</strong>
                  <p>${topic.product}</p>
                  <div class="progress-track">
                    <div class="progress-fill" style="width:${topic.progress}%; --platform-color:${stage.color}"></div>
                  </div>
                  <div class="topic-footer">
                    <span>${topic.channel}</span>
                    <span>${topic.owner} · ${topic.due}</span>
                  </div>
                </article>
              `,
            )
            .join("")}
        </section>
      `;
    })
    .join("");
}

function renderContentStudio() {
  renderContentMetrics();
  renderContentBars();
  renderContentFunnel();
  renderTopicBoard();
}

function percent(actual, target) {
  return target ? Math.min((actual / target) * 100, 100) : 0;
}

function progressRow(item) {
  const complete = percent(item.actual, item.target);
  const gap = Math.max(item.target - item.actual, 0);
  return `
    <div class="progress-row">
      <div class="progress-meta">
        <strong>${item.name}</strong>
        <span>${formatCurrency(item.actual)} / ${formatCurrency(item.target)}</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width:${complete}%; --platform-color:${item.color || "#9c2f45"}"></div>
      </div>
      <div class="content-stats">
        <span>完成 ${complete.toFixed(1)}%</span>
        <span>缺口 ${formatCurrency(gap)}</span>
      </div>
    </div>
  `;
}

function renderSalesProgress() {
  const annualActual = sum(salesTargets.quarters.map((quarter) => quarter.actual));
  const annualRate = percent(annualActual, salesTargets.annualTarget);
  const annualGap = Math.max(salesTargets.annualTarget - annualActual, 0);
  const elapsedMonth = Number(salesTargets.currentMonth);
  const timeRate = (elapsedMonth / 12) * 100;

  document.querySelector("#annualProgress").innerHTML = `
    <section class="annual-main">
      <span>年度达成率</span>
      <div class="annual-number">${annualRate.toFixed(1)}%</div>
      <div class="progress-track">
        <div class="progress-fill" style="width:${annualRate}%; --platform-color:#9c2f45"></div>
      </div>
      <div class="annual-sub">
        <span>已完成 ${formatCurrency(annualActual)}</span>
        <span>年度目标 ${formatCurrency(salesTargets.annualTarget)}</span>
        <span>时间进度 ${timeRate.toFixed(1)}%</span>
      </div>
    </section>
    <section class="annual-card">
      <span>剩余目标</span>
      <strong>${formatCurrency(annualGap)}</strong>
    </section>
    <section class="annual-card">
      <span>本月完成</span>
      <strong>${formatCurrency(salesTargets.months.find((item) => item.month === salesTargets.currentMonth).actual)}</strong>
    </section>
    <section class="annual-card">
      <span>当前节奏</span>
      <strong>${annualRate >= timeRate ? "领先" : "偏慢"}</strong>
    </section>
  `;

  document.querySelector("#quarterProgress").innerHTML = salesTargets.quarters
    .map((quarter, index) => progressRow({ ...quarter, color: platforms[index]?.color || "#9c2f45" }))
    .join("");

  document.querySelector("#channelProgress").innerHTML = salesTargets.channels.map(progressRow).join("");

  document.querySelector("#monthGrid").innerHTML = salesTargets.months
    .map((month) => {
      const complete = percent(month.actual, month.target);
      return `
        <article class="month-card ${month.month === salesTargets.currentMonth ? "current" : ""}">
          <strong>${month.month} 月</strong>
          <span>目标 ${formatCurrency(month.target)}</span>
          <span>完成 ${formatCurrency(month.actual)}</span>
          <div class="mini-track">
            <div class="mini-fill" style="width:${complete}%"></div>
          </div>
          <span>${complete.toFixed(1)}%</span>
        </article>
      `;
    })
    .join("");
}

function renderDataSourceMetrics() {
  const synced = dataSources.filter((source) => source.status === "synced").length;
  const warning = dataSources.filter((source) => source.status === "warning").length;
  const error = dataSources.filter((source) => source.status === "error").length;
  const rows = sum(dataSources.map((source) => source.rows));
  const metrics = [
    { label: "数据源数量", value: dataSources.length.toString(), sub: "平台 / 库存 / 内容", color: "#9c2f45" },
    { label: "今日已更新", value: synced.toString(), sub: "自动或手动完成", color: "#0f766e" },
    { label: "需要确认", value: warning.toString(), sub: "登录 / 权限 / 页面变动", color: "#c47a1d" },
    { label: "待更新", value: error.toString(), sub: "库存或表格缺失", color: "#6b5b95" },
    { label: "数据行数", value: rows.toLocaleString("zh-CN"), sub: "样例累计", color: "#4b5563" },
  ];

  document.querySelector("#dataSourceMetricGrid").innerHTML = metrics
    .map(
      (metric) => `
        <article class="metric-card" style="--metric-color:${metric.color}">
          <div class="metric-label">${metric.label}</div>
          <div class="metric-value">${metric.value}</div>
          <div class="metric-sub"><span>${metric.sub}</span></div>
        </article>
      `,
    )
    .join("");
}

function renderDataSources() {
  document.querySelector("#sourceList").innerHTML = dataSources
    .map(
      (source) => `
        <article class="source-row">
          <div class="source-main">
            <div class="source-title">
              <span class="source-dot" style="--source-color:${source.color}"></span>
              ${source.name}
            </div>
            <span>${source.type} · ${source.mode} · ${source.lastSync} · ${source.rows.toLocaleString("zh-CN")} 行</span>
          </div>
          <span class="tag ${source.status === "synced" ? "selling" : source.status === "warning" ? "warning" : "error"}">${sourceStatusText[source.status]}</span>
        </article>
      `,
    )
    .join("");

  document.querySelector("#syncLog").innerHTML = syncLogs
    .map(
      (log) => `
        <article class="log-row">
          <div>
            <strong>${log.title}</strong>
            <span>${log.detail}</span>
          </div>
          <span>${log.time} · ${log.status}</span>
        </article>
      `,
    )
    .join("");
}

function normalizeImportHeader(value) {
  return String(value || "")
    .replace(/\s+/g, "")
    .replace(/[：:]/g, "")
    .replace(/[()（）]/g, "")
    .toLowerCase();
}

function normalizedAliases(key) {
  return (importAliases[key] || []).map(normalizeImportHeader);
}

function getImportValue(row, key) {
  const aliases = normalizedAliases(key);
  for (const alias of aliases) {
    const value = row[alias];
    if (value !== undefined && String(value).trim() !== "") return String(value).trim();
  }
  return "";
}

function parseImportNumber(value) {
  if (value === null || value === undefined) return null;
  const text = String(value).trim();
  if (!text || ["-", "--", "—"].includes(text)) return null;
  const normalized = text.replace(/[￥¥,\s，]/g, "").replace(/[件元%]/g, "");
  const match = normalized.match(/-?\d+(?:\.\d+)?/);
  return match ? Number(match[0]) : null;
}

function parseImportPercent(value) {
  const number = parseImportNumber(value);
  if (number === null) return null;
  return String(value).includes("%") || number > 1 ? number / 100 : number;
}

function detectImportDelimiter(text) {
  const sampleLine = String(text)
    .split(/\r?\n/)
    .find((line) => line.trim()) || "";
  const candidates = ["\t", ",", ";", "|"];
  return candidates
    .map((delimiter) => ({ delimiter, count: sampleLine.split(delimiter).length - 1 }))
    .sort((a, b) => b.count - a.count)[0].delimiter;
}

function parseDelimitedText(text) {
  const source = String(text || "").replace(/^\uFEFF/, "");
  const delimiter = detectImportDelimiter(source);
  const rows = [];
  let row = [];
  let cell = "";
  let inQuotes = false;

  for (let index = 0; index < source.length; index += 1) {
    const char = source[index];
    const next = source[index + 1];
    if (char === '"') {
      if (inQuotes && next === '"') {
        cell += '"';
        index += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }
    if (char === delimiter && !inQuotes) {
      row.push(cell.trim());
      cell = "";
      continue;
    }
    if ((char === "\n" || char === "\r") && !inQuotes) {
      if (char === "\r" && next === "\n") index += 1;
      row.push(cell.trim());
      if (row.some((item) => item !== "")) rows.push(row);
      row = [];
      cell = "";
      continue;
    }
    cell += char;
  }

  row.push(cell.trim());
  if (row.some((item) => item !== "")) rows.push(row);
  return rows;
}

function parseCsv(text) {
  return parseDelimitedText(text);
}

function rowLooksLikeProductHeader(row) {
  const headers = row.map(normalizeImportHeader);
  const hasIdentity = normalizedAliases("styleNo").some((alias) => headers.includes(alias)) ||
    normalizedAliases("productName").some((alias) => headers.includes(alias));
  const hasBusinessField = [
    "planProductionQty",
    "warehouseStock",
    "soldRealQty",
    "currentSellThroughRate",
    "styleGrade",
  ].some((key) => normalizedAliases(key).some((alias) => headers.includes(alias)));
  return hasIdentity && hasBusinessField;
}

function tableRowsToObjects(rows) {
  const cleanRows = rows.filter((row) => row.some((cell) => String(cell || "").trim() !== ""));
  if (!cleanRows.length) return { headers: [], objects: [], headerIndex: -1 };
  const headerIndex = cleanRows.findIndex(rowLooksLikeProductHeader);
  const safeHeaderIndex = headerIndex >= 0 ? headerIndex : 0;
  const headers = cleanRows[safeHeaderIndex].map((header, index) => normalizeImportHeader(header || `字段${index + 1}`));
  const objects = cleanRows
    .slice(safeHeaderIndex + 1)
    .map((row) =>
      headers.reduce((object, header, index) => {
        object[header] = String(row[index] || "").trim();
        return object;
      }, {}),
    )
    .filter((row) =>
      ["styleNo", "productName", "planProductionQty", "warehouseStock", "soldRealQty"].some((key) => getImportValue(row, key)),
    );
  return { headers: cleanRows[safeHeaderIndex], objects, headerIndex: safeHeaderIndex };
}

function buildImportedOperations(row) {
  return operationImportFields.reduce((operations, [key, type]) => {
    const rawValue = getImportValue(row, key);
    if (!rawValue) return operations;
    if (type === "number") {
      const value = parseImportNumber(rawValue);
      if (value !== null) operations[key] = value;
    } else if (type === "percent") {
      const value = parseImportPercent(rawValue);
      if (value !== null) operations[key] = value;
    } else {
      operations[key] = rawValue;
    }
    return operations;
  }, {});
}

function importKey(value) {
  return normalizeImportHeader(value).replace(/[^a-z0-9\u4e00-\u9fa5]/g, "");
}

function inferProductStatus(row) {
  const text = getImportValue(row, "status");
  if (/售罄|售完|sold/i.test(text)) return "soldout";
  if (/历史|下架|停卖|history/i.test(text)) return "history";
  return "selling";
}

function splitImportPlatforms(row) {
  const raw = getImportValue(row, "platforms");
  if (!raw) return ["淘宝", "抖音", "小红书", "视频号"];
  return raw
    .split(/[、,，/|;\s]+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function colorFromText(text, index) {
  const palette = ["#b93c56", "#f1e7da", "#2d3137", "#8b949e", "#5d9aa6", "#c47a1d", "#733b4a", "#0f766e"];
  if (!text) return palette[index % palette.length];
  const seed = Array.from(text).reduce((total, char) => total + char.charCodeAt(0), 0);
  return palette[seed % palette.length];
}

function addImportedSkuUnit(product, colorName, sizeName, made, stock) {
  const safeColor = colorName || "整款";
  const safeSize = sizeName || "合计";
  let color = product.colors.find((item) => item.name === safeColor);
  if (!color) {
    color = { name: safeColor, hex: colorFromText(safeColor, product.colors.length), sizes: {} };
    product.colors.push(color);
  }
  const existing = color.sizes[safeSize] || { made: 0, stock: 0 };
  color.sizes[safeSize] = {
    made: existing.made + Math.max(0, Math.round(made || 0)),
    stock: existing.stock + Math.max(0, Math.round(stock || 0)),
  };
}

function productsFromImportObjects(objects) {
  const grouped = new Map();
  objects.forEach((row, index) => {
    const styleNo = getImportValue(row, "styleNo") || `IMPORT-${index + 1}`;
    const key = importKey(styleNo);
    const operations = buildImportedOperations(row);
    const productName = getImportValue(row, "productName") || operations.productName || styleNo;
    const operationPrice = Number(operations.retailPrice);
    const price = parseImportNumber(getImportValue(row, "retailPrice")) ?? (Number.isFinite(operationPrice) ? operationPrice : 0);
    const category = getImportValue(row, "secondCategory") || operations.secondCategory || "未分类";

    if (!grouped.has(key)) {
      grouped.set(key, {
        id: "",
        name: productName,
        sku: styleNo,
        category,
        status: inferProductStatus(row),
        platforms: splitImportPlatforms(row),
        price,
        swatchA: "#9c2f45",
        swatchB: "#f1c2cc",
        colors: [],
        operations: {
          ...operations,
          styleNo,
          productName,
          secondCategory: category,
          retailPrice: price,
          importedAt: new Date().toLocaleString("zh-CN"),
        },
      });
    }

    const product = grouped.get(key);
    Object.entries(operations).forEach(([field, value]) => {
      if (value !== "" && value !== null && value !== undefined && product.operations[field] === undefined) {
        product.operations[field] = value;
      }
    });

    const made =
      parseImportNumber(getImportValue(row, "planProductionQty")) ??
      parseImportNumber(getImportValue(row, "totalOrderQty")) ??
      parseImportNumber(getImportValue(row, "firstOrderQty")) ??
      0;
    const stock =
      parseImportNumber(getImportValue(row, "warehouseStock")) ??
      parseImportNumber(getImportValue(row, "availableQty")) ??
      0;
    addImportedSkuUnit(product, getImportValue(row, "colorName"), getImportValue(row, "sizeName"), made, stock);
  });

  return [...grouped.values()].map((product) => {
    product.swatchA = product.colors[0]?.hex || product.swatchA;
    product.swatchB = product.colors[1]?.hex || product.colors[0]?.hex || product.swatchB;
    return normalizeProduct(product);
  });
}

function analyzeProductImport(rows) {
  const parsed = tableRowsToObjects(rows);
  const productsForImport = productsFromImportObjects(parsed.objects);
  const matchedFields = Object.keys(importAliases).filter((key) =>
    parsed.headers.map(normalizeImportHeader).some((header) => normalizedAliases(key).includes(header)),
  );
  const skuUnits = sum(productsForImport.map((product) => product.colors.reduce((total, color) => total + Object.keys(color.sizes).length, 0)));
  return {
    rows,
    headers: parsed.headers,
    objects: parsed.objects,
    products: productsForImport,
    summary: {
      headerIndex: parsed.headerIndex,
      sourceRows: parsed.objects.length,
      products: productsForImport.length,
      skuUnits,
      matchedFields,
    },
  };
}

function renderImportFieldHints(summary) {
  if (!summary) return "";
  const coreFields = [
    ["styleNo", "款号"],
    ["productName", "产品名称"],
    ["retailPrice", "售价"],
    ["planProductionQty", "做货件数"],
    ["warehouseStock", "库存"],
    ["soldRealQty", "实销数"],
    ["currentSellThroughRate", "售罄率"],
    ["styleGrade", "爆款分类"],
  ];
  const matched = new Set(summary.matchedFields);
  return `
    <div class="import-hint-title">字段识别</div>
    <div class="import-chip-row">
      ${coreFields
        .map(([key, label]) => `<span class="import-chip ${matched.has(key) ? "matched" : ""}">${matched.has(key) ? "已识别" : "可补充"} · ${label}</span>`)
        .join("")}
    </div>
  `;
}

function renderImportPreview(rows) {
  const preview = document.querySelector("#importPreview");
  const summaryBox = document.querySelector("#importSummary");
  const fieldHints = document.querySelector("#importFieldHints");
  const applyButton = document.querySelector("#applyProductImport");

  if (!rows.length) {
    productImportDraft = { rows: [], objects: [], products: [], summary: null };
    preview.innerHTML = "";
    summaryBox.innerHTML = `<p>没有读取到可导入的数据。</p>`;
    fieldHints.innerHTML = "";
    applyButton.disabled = true;
    return;
  }

  productImportDraft = analyzeProductImport(rows);
  const { products: importProducts, summary } = productImportDraft;
  applyButton.disabled = !importProducts.length;
  summaryBox.innerHTML = `
    <article class="import-summary-card">
      <span>识别产品</span>
      <strong>${summary.products} 款</strong>
    </article>
    <article class="import-summary-card">
      <span>数据行</span>
      <strong>${summary.sourceRows} 行</strong>
    </article>
    <article class="import-summary-card">
      <span>SKU 单元</span>
      <strong>${summary.skuUnits} 个</strong>
    </article>
    <article class="import-summary-card">
      <span>字段命中</span>
      <strong>${summary.matchedFields.length} 项</strong>
    </article>
  `;
  fieldHints.innerHTML = renderImportFieldHints(summary);

  if (!importProducts.length) {
    preview.innerHTML = `<div class="empty-state">没有识别到产品。请确认表头里至少有“款号 / 产品名称”，并包含库存、做货或实销字段。</div>`;
    return;
  }

  preview.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>款号</th>
          <th>产品名称</th>
          <th>分类</th>
          <th>售价</th>
          <th>做货件数</th>
          <th>库存</th>
          <th>实销数</th>
          <th>售罄率</th>
          <th>爆款分类</th>
        </tr>
      </thead>
      <tbody>
        ${importProducts
          .slice(0, 8)
          .map((product) => {
            const totals = productTotals(product);
            const ops = getProductOperations(product);
            return `
              <tr>
                <td>${escapeHtml(product.sku)}</td>
                <td>${escapeHtml(product.name)}</td>
                <td>${escapeHtml(product.category)}</td>
                <td>${formatCurrency(product.price)}</td>
                <td>${totals.made.toLocaleString("zh-CN")}</td>
                <td>${totals.stock.toLocaleString("zh-CN")}</td>
                <td>${ops.soldRealQty.toLocaleString("zh-CN")}</td>
                <td>${formatPercentValue(ops.currentSellThroughRate)}</td>
                <td>${escapeHtml(ops.styleGrade)}</td>
              </tr>
            `;
          })
          .join("")}
      </tbody>
    </table>
  `;
}

function uniqueImportedProductId(product, usedIds) {
  const skuPart = String(product.sku || "")
    .replace(/[^A-Za-z0-9]/g, "")
    .slice(0, 10)
    .toUpperCase();
  let seed = skuPart ? `P${skuPart}` : createProductId();
  let suffix = 1;
  while (products.some((item) => item.id === seed) || usedIds.has(seed)) {
    seed = `${skuPart ? `P${skuPart}` : "PIMPORT"}${suffix}`;
    suffix += 1;
  }
  usedIds.add(seed);
  return seed;
}

function applyProductImport() {
  const imported = productImportDraft.products || [];
  if (!imported.length) return;
  const usedIds = new Set();
  let created = 0;
  let updated = 0;

  imported.forEach((product) => {
    const key = importKey(product.sku);
    const existingIndex = products.findIndex((item) => importKey(item.sku) === key || importKey(item.operations?.styleNo) === key);
    if (existingIndex >= 0) {
      products[existingIndex] = normalizeProduct({
        ...products[existingIndex],
        ...product,
        id: products[existingIndex].id,
        operations: { ...products[existingIndex].operations, ...product.operations },
      });
      updated += 1;
    } else {
      products.unshift(normalizeProduct({ ...product, id: uniqueImportedProductId(product, usedIds) }));
      created += 1;
    }
  });

  saveProducts("product-import");
  const inventorySource = dataSources.find((source) => source.name.includes("SKU") || source.name.includes("库存"));
  if (inventorySource) {
    inventorySource.status = "synced";
    inventorySource.lastSync = "刚刚";
    inventorySource.rows = productImportDraft.summary?.sourceRows || imported.length;
  }
  syncLogs.unshift({
    title: "产品表导入完成",
    time: "刚刚",
    detail: `新增 ${created} 款，更新 ${updated} 款，写入 ${productImportDraft.summary?.skuUnits || 0} 个 SKU 单元`,
    status: "成功",
  });
  renderProducts();
  renderDataSourcePage();
  document.querySelector("#importSummary").insertAdjacentHTML(
    "beforeend",
    `<div class="import-success">已写入产品库：新增 ${created} 款，更新 ${updated} 款。</div>`,
  );
}

function generateProductTemplate() {
  const headers = [
    "数据更新日期",
    "款号",
    "产品名称",
    "售价",
    "直播日期",
    "成本",
    "季节",
    "二级分类",
    "难易分类",
    "计划生产件数",
    "首单数",
    "已到仓数",
    "到仓状态",
    "未到仓数",
    "在仓库存",
    "总销量",
    "总退货数",
    "发货后退货率",
    "综合退货率",
    "已实销件数",
    "目前售罄率",
    "产品款式划分",
    "还需实销件数",
    "颜色",
    "尺码",
  ];
  const sample = [
    "2026/04/29",
    "TG2626005",
    "减龄立裁弯刀牛仔裤",
    "680",
    "2026/03/28",
    "210",
    "26夏",
    "牛仔裤",
    "常规",
    "235",
    "235",
    "204",
    "2部分到仓",
    "31",
    "188",
    "86",
    "70",
    "64.4%",
    "81.4%",
    "15",
    "7%",
    "B+",
    "161",
    "牛仔蓝",
    "M",
  ];
  const text = `${headers.join("\t")}\n${sample.join("\t")}`;
  document.querySelector("#pasteImportText").value = text;
  renderImportPreview(parseDelimitedText(text));
}

function renderDataSourcePage() {
  renderDataSourceMetrics();
  renderDataSources();
}

function renderMetricCards(target, metrics) {
  document.querySelector(target).innerHTML = metrics
    .map(
      (metric) => `
        <article class="metric-card" style="--metric-color:${metric.color}">
          <div class="metric-label">${metric.label}</div>
          <div class="metric-value">${metric.value}</div>
          <div class="metric-sub"><span>${metric.sub}</span></div>
        </article>
      `,
    )
    .join("");
}

function productionStageIndex(stage) {
  return Math.max(productionStages.indexOf(stage), 0);
}

function renderProductionProgress() {
  const totalQty = sum(productionOrders.map((order) => order.quantity));
  const finishedQty = sum(productionOrders.map((order) => order.finished));
  const riskCount = productionOrders.filter((order) => order.risk !== "正常" && order.risk !== "即将到仓").length;
  const arrivingSoon = productionOrders.filter((order) => ["04/30", "05/03", "05/08"].includes(order.eta)).length;

  renderMetricCards("#productionMetricGrid", [
    { label: "在做款数", value: productionOrders.length.toString(), sub: "上游正在推进", color: "#9c2f45" },
    { label: "做货总量", value: totalQty.toLocaleString("zh-CN"), sub: `已完成 ${finishedQty.toLocaleString("zh-CN")}`, color: "#0f766e" },
    { label: "7 日内到仓", value: arrivingSoon.toString(), sub: "可安排上新/补货", color: "#c47a1d" },
    { label: "延期风险", value: riskCount.toString(), sub: "需采购/跟单介入", color: "#6b5b95" },
  ]);

  document.querySelector("#productionList").innerHTML = productionOrders
    .map((order) => {
      const complete = percent(order.finished, order.quantity);
      const stageIndex = productionStageIndex(order.stage);
      return `
        <article class="production-card">
          <div class="production-head">
            <div class="production-title">
              <strong>${order.product}</strong>
              <span>${order.sku} · ${order.supplier} · 预计到仓 ${order.eta}</span>
            </div>
            <span class="tag ${order.risk === "正常" || order.risk === "即将到仓" ? "selling" : "warning"}">${order.risk}</span>
          </div>
          <div class="stage-track">
            ${productionStages
              .map((stage, index) => `<div class="stage-step ${index < stageIndex ? "done" : index === stageIndex ? "current" : ""}">${stage}</div>`)
              .join("")}
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width:${complete}%; --platform-color:${order.color}"></div>
          </div>
          <div class="production-meta">
            <div><span>做货数量</span><strong>${order.quantity.toLocaleString("zh-CN")}</strong></div>
            <div><span>已完成</span><strong>${order.finished.toLocaleString("zh-CN")}</strong></div>
            <div><span>完成率</span><strong>${complete.toFixed(1)}%</strong></div>
            <div><span>准时概率</span><strong>${order.onTimeRate}%</strong></div>
          </div>
        </article>
      `;
    })
    .join("");

  const maxStageCount = Math.max(...productionStages.map((stage) => productionOrders.filter((order) => order.stage === stage).length));
  document.querySelector("#productionStageList").innerHTML = productionStages
    .map((stage, index) => {
      const count = productionOrders.filter((order) => order.stage === stage).length;
      const width = maxStageCount ? (count / maxStageCount) * 100 : 0;
      const color = platforms[index % platforms.length]?.color || "#9c2f45";
      return `
        <div class="funnel-row">
          <div class="funnel-meta">
            <strong class="stage-label"><span class="stage-dot" style="--stage-color:${color}"></span>${stage}</strong>
            <span>${count} 款</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width:${width}%; --platform-color:${color}"></div>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderSupplierProfiles() {
  const avgOnTime = suppliers.reduce((total, supplier) => total + supplier.onTimeRate, 0) / suppliers.length;
  const avgDefect = suppliers.reduce((total, supplier) => total + supplier.defectRate, 0) / suppliers.length;
  const producing = sum(suppliers.map((supplier) => supplier.producing));
  const styleCount = sum(suppliers.map((supplier) => supplier.styles.length));

  renderMetricCards("#supplierMetricGrid", [
    { label: "合作供应商", value: suppliers.length.toString(), sub: "当前档案数", color: "#9c2f45" },
    { label: "合作款式", value: styleCount.toString(), sub: "历史/在做款", color: "#0f766e" },
    { label: "准时履约率", value: `${avgOnTime.toFixed(1)}%`, sub: "供应商平均", color: "#c47a1d" },
    { label: "平均次品率", value: `${avgDefect.toFixed(1)}%`, sub: `在做 ${producing.toLocaleString("zh-CN")} 件`, color: "#6b5b95" },
  ]);

  document.querySelector("#supplierGrid").innerHTML = suppliers
    .map(
      (supplier) => `
        <article class="supplier-card">
          <div class="supplier-head">
            <div class="supplier-title">
              <strong>${supplier.name}</strong>
              <span>${supplier.city} · ${supplier.category}</span>
            </div>
            <span class="tag ${supplier.onTimeRate >= 88 ? "selling" : "warning"}">${supplier.score}</span>
          </div>
          <div class="supplier-kpis">
            <div class="supplier-kpi"><span>成品率</span><strong>${supplier.finishedRate}%</strong></div>
            <div class="supplier-kpi"><span>次品率</span><strong>${supplier.defectRate}%</strong></div>
            <div class="supplier-kpi"><span>准时率</span><strong>${supplier.onTimeRate}%</strong></div>
            <div class="supplier-kpi"><span>平均交期</span><strong>${supplier.leadTime} 天</strong></div>
          </div>
          ${supplier.styles.map((style) => `<div class="supplier-style"><span>${style}</span><span>${supplier.producing.toLocaleString("zh-CN")} 件在做</span></div>`).join("")}
        </article>
      `,
    )
    .join("");
}

function renderPrivateDomain() {
  renderMetricCards("#privateMetricGrid", [
    { label: "客户总数", value: privateDomain.totalCustomers.toLocaleString("zh-CN"), sub: "全平台沉淀", color: "#9c2f45" },
    { label: "今日新增", value: privateDomain.newToday.toLocaleString("zh-CN"), sub: "新客入池", color: "#0f766e" },
    { label: "今日活跃", value: privateDomain.activeToday.toLocaleString("zh-CN"), sub: "浏览/沟通/下单", color: "#c47a1d" },
    { label: "今日对话", value: privateDomain.conversations.toLocaleString("zh-CN"), sub: "企业微信为主", color: "#6b5b95" },
  ]);

  document.querySelector("#customerSegments").innerHTML = privateDomain.segments
    .map((segment) => {
      const share = (segment.count / privateDomain.totalCustomers) * 100;
      return `
        <article class="segment-card">
          <div class="segment-head">
            <div class="segment-title">
              <strong>${segment.name}</strong>
              <span>${segment.action}</span>
            </div>
            <span class="tag selling">${share.toFixed(1)}%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width:${share}%; --platform-color:${segment.color}"></div>
          </div>
          <div class="segment-kpis">
            <div class="segment-kpi"><span>客户数</span><strong>${segment.count.toLocaleString("zh-CN")}</strong></div>
            <div class="segment-kpi"><span>客单</span><strong>¥${segment.arpu}</strong></div>
            <div class="segment-kpi"><span>复购</span><strong>${segment.repurchase}%</strong></div>
          </div>
        </article>
      `;
    })
    .join("");

  document.querySelector("#privateChannels").innerHTML = privateDomain.channels.map(progressRow).join("");
  document.querySelector("#privateActions").innerHTML = privateDomain.actions
    .map(
      (action) => `
        <article class="operation-card">
          <strong>${action.title}</strong>
          <div class="metric-value">${action.value}</div>
          <span>${action.detail}</span>
        </article>
      `,
    )
    .join("");
}

function renderServiceExperience() {
  renderMetricCards("#serviceMetricGrid", [
    { label: "今日咨询量", value: serviceExperience.totalTickets.toLocaleString("zh-CN"), sub: "售前 + 售后", color: "#9c2f45" },
    { label: "平均响应", value: `${serviceExperience.responseMinutes} 分`, sub: "全平台均值", color: "#0f766e" },
    { label: "满意度", value: `${serviceExperience.satisfaction}%`, sub: "评价/回访", color: "#c47a1d" },
    { label: "退款率", value: `${serviceExperience.refundRate}%`, sub: "今日口径", color: "#6b5b95" },
  ]);

  document.querySelector("#serviceList").innerHTML = serviceExperience.platforms
    .map(
      (platform) => `
        <article class="service-card">
          <div class="service-head">
            <div class="service-title">
              <strong>${platform.name}</strong>
              <span>响应 ${platform.response} 分钟 · 售后 ${platform.afterSales} 单</span>
            </div>
            <span class="tag ${platform.satisfaction >= 95 ? "selling" : "warning"}">${platform.satisfaction}% 满意</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width:${Math.min(platform.inquiries / 900 * 100, 100)}%; --platform-color:${platform.color}"></div>
          </div>
          <div class="service-kpis">
            <div class="service-kpi"><span>咨询量</span><strong>${platform.inquiries}</strong></div>
            <div class="service-kpi"><span>响应</span><strong>${platform.response} 分</strong></div>
            <div class="service-kpi"><span>满意度</span><strong>${platform.satisfaction}%</strong></div>
            <div class="service-kpi"><span>售后量</span><strong>${platform.afterSales}</strong></div>
          </div>
        </article>
      `,
    )
    .join("");

  document.querySelector("#serviceIssueList").innerHTML = serviceExperience.issues.map(progressRow).join("");
}

function simpleBusinessCard(item) {
  return `
    <article class="business-card">
      <div class="business-card-head">
        <div class="business-card-title">
          <strong>${item.title || item.name}</strong>
          <span>${item.subtitle || ""}</span>
        </div>
        ${item.level || item.status || item.priority ? `<span class="tag ${item.level === "热卖" || item.status === "主推爆款" || item.priority === "高" ? "selling" : "warning"}">${item.level || item.status || item.priority}</span>` : ""}
      </div>
      ${item.detail || item.note || item.reason ? `<p>${item.detail || item.note || item.reason}</p>` : ""}
    </article>
  `;
}

function renderExecutiveDashboard() {
  renderMetricCards("#executiveMetricGrid", [
    { label: "今日销售额", value: formatCurrency(executiveMetrics.sales), sub: "全平台 GMV", color: "#9c2f45" },
    { label: "今日毛利", value: formatCurrency(executiveMetrics.grossProfit), sub: "未扣投放/佣金", color: "#0f766e" },
    { label: "净利率", value: `${executiveMetrics.netProfitRate}%`, sub: "经营口径", color: "#c47a1d" },
    { label: "现金缺口", value: formatCurrency(executiveMetrics.cashGap), sub: "货款/投放/库存占用", color: "#6b5b95" },
  ]);
  document.querySelector("#executiveAlerts").innerHTML = executiveMetrics.alerts.map(simpleBusinessCard).join("");
  document.querySelector("#businessHealth").innerHTML = executiveMetrics.health.map(progressRow).join("");
  document.querySelector("#productHealthGrid").innerHTML = productHealth
    .map(
      (item) => `
        <article class="business-card">
          <div class="business-card-head">
            <div class="business-card-title"><strong>${item.name}</strong><span>${item.status}</span></div>
            <span class="tag ${item.risk === "供应链" ? "warning" : "selling"}">${item.risk}</span>
          </div>
          <div class="business-kpis">
            <div class="business-kpi"><span>毛利率</span><strong>${item.profit}%</strong></div>
            <div class="business-kpi"><span>库存天数</span><strong>${item.stockDays} 天</strong></div>
            <div class="business-kpi"><span>内容</span><strong>${item.content} 条</strong></div>
          </div>
          <p>${item.note}</p>
        </article>
      `,
    )
    .join("");
}

function renderProfitFinance() {
  const sales = sum(platformProfit.map((item) => item.sales));
  const gross = sum(platformProfit.map((item) => item.gross));
  const ads = sum(platformProfit.map((item) => item.ads));
  const commission = sum(platformProfit.map((item) => item.commission));
  renderMetricCards("#profitMetricGrid", [
    { label: "销售额", value: formatCurrency(sales), sub: "今日经营口径", color: "#9c2f45" },
    { label: "毛利", value: formatCurrency(gross), sub: `${((gross / sales) * 100).toFixed(1)}% 毛利率`, color: "#0f766e" },
    { label: "投放消耗", value: formatCurrency(ads), sub: "广告/内容投流", color: "#c47a1d" },
    { label: "佣金费用", value: formatCurrency(commission), sub: "达人/平台佣金", color: "#6b5b95" },
  ]);
  document.querySelector("#platformProfitList").innerHTML = platformProfit
    .map(
      (item) => `
        <article class="business-card">
          <div class="business-card-head">
            <div class="business-card-title"><strong>${item.name}</strong><span>净利率 ${item.netRate}%</span></div>
            <span class="tag ${item.netRate >= 18 ? "selling" : "warning"}">${formatCurrency(item.sales)}</span>
          </div>
          <div class="business-kpis">
            <div class="business-kpi"><span>毛利</span><strong>${formatCurrency(item.gross)}</strong></div>
            <div class="business-kpi"><span>投放</span><strong>${formatCurrency(item.ads)}</strong></div>
            <div class="business-kpi"><span>佣金</span><strong>${formatCurrency(item.commission)}</strong></div>
          </div>
        </article>
      `,
    )
    .join("");
  document.querySelector("#costStructure").innerHTML = costStructure.map(progressRow).join("");
  document.querySelector("#productProfitGrid").innerHTML = productProfit
    .map((item) => simpleBusinessCard({ name: item.name, status: item.role, detail: `销售 ${formatCurrency(item.sales)}，净利 ${formatCurrency(item.net)}，毛利率 ${item.margin}%。` }))
    .join("");
}

function renderMerchPlanning() {
  const totalProducts = sum(launchWaves.map((wave) => wave.products));
  const totalTarget = sum(launchWaves.map((wave) => wave.target));
  renderMetricCards("#planningMetricGrid", [
    { label: "规划波段", value: launchWaves.length.toString(), sub: "未来 45 天", color: "#9c2f45" },
    { label: "规划款数", value: totalProducts.toString(), sub: "企划/开发/拍摄", color: "#0f766e" },
    { label: "目标销售", value: formatCurrency(totalTarget), sub: "波段目标", color: "#c47a1d" },
    { label: "开发中", value: developmentStyles.length.toString(), sub: "候选款式", color: "#6b5b95" },
  ]);
  document.querySelector("#launchWaveList").innerHTML = launchWaves
    .map((wave) => simpleBusinessCard({ name: wave.name, status: wave.status, detail: `${wave.date} · ${wave.products} 款 · 目标 ${formatCurrency(wave.target)} · 进度 ${wave.progress}%` }))
    .join("");
  document.querySelector("#categoryMix").innerHTML = categoryMix.map(progressRow).join("");
  document.querySelector("#developmentGrid").innerHTML = developmentStyles
    .map((style) => simpleBusinessCard({ name: style.name, status: style.stage, detail: `${style.role} · 目标价格 ${style.price} · 负责人 ${style.owner}` }))
    .join("");
}

function renderInventoryReplenishment() {
  renderMetricCards("#inventoryMetricGrid", [
    { label: "可售库存", value: "4,270", sub: "全渠道", color: "#9c2f45" },
    { label: "在途库存", value: "2,360", sub: "生产/入仓中", color: "#0f766e" },
    { label: "缺货风险", value: "2", sub: "SKU 需补货", color: "#c47a1d" },
    { label: "滞销风险", value: "1", sub: "需清仓/召回", color: "#6b5b95" },
  ]);
  document.querySelector("#stockAlertList").innerHTML = stockAlerts.map(simpleBusinessCard).join("");
  document.querySelector("#stockAllocation").innerHTML = stockAllocation.map(progressRow).join("");
  document.querySelector("#replenishmentGrid").innerHTML = replenishmentAdvice
    .map((item) => simpleBusinessCard({ name: item.name, priority: item.priority, detail: `${item.action} · ${item.reason}` }))
    .join("");
}

function renderMarketingLive() {
  const budget = sum(campaigns.map((item) => item.budget));
  const spent = sum(campaigns.map((item) => item.spent));
  const liveTarget = sum(liveSchedules.map((item) => item.target));
  renderMetricCards("#marketingMetricGrid", [
    { label: "活动预算", value: formatCurrency(budget), sub: `已消耗 ${formatCurrency(spent)}`, color: "#9c2f45" },
    { label: "平均 ROI", value: "3.3", sub: "投放/活动综合", color: "#0f766e" },
    { label: "直播场次", value: liveSchedules.length.toString(), sub: "今日排期", color: "#c47a1d" },
    { label: "直播目标", value: formatCurrency(liveTarget), sub: "今日 GMV", color: "#6b5b95" },
  ]);
  document.querySelector("#campaignList").innerHTML = campaigns
    .map((item) => simpleBusinessCard({ name: item.name, status: `ROI ${item.roi}`, detail: `${item.platform} · 预算 ${formatCurrency(item.budget)} · 已花 ${formatCurrency(item.spent)} · 主推 ${item.product}` }))
    .join("");
  document.querySelector("#liveScheduleList").innerHTML = liveSchedules
    .map((item) => simpleBusinessCard({ name: item.name, status: item.time, detail: `主播 ${item.host} · 主推 ${item.product} · 目标 ${formatCurrency(item.target)}` }))
    .join("");
}

function renderFulfillmentLogistics() {
  const paid = sum(fulfillmentOrders.map((item) => item.paid));
  const shipped = sum(fulfillmentOrders.map((item) => item.shipped));
  const pending = sum(fulfillmentOrders.map((item) => item.pending));
  const timeout = sum(fulfillmentOrders.map((item) => item.timeout));
  renderMetricCards("#fulfillmentMetricGrid", [
    { label: "已付款订单", value: paid.toLocaleString("zh-CN"), sub: "今日需履约", color: "#9c2f45" },
    { label: "已发货", value: shipped.toLocaleString("zh-CN"), sub: `${((shipped / paid) * 100).toFixed(1)}%`, color: "#0f766e" },
    { label: "待发货", value: pending.toLocaleString("zh-CN"), sub: "仓库处理中", color: "#c47a1d" },
    { label: "超时风险", value: timeout.toString(), sub: "需优先处理", color: "#6b5b95" },
  ]);
  document.querySelector("#fulfillmentList").innerHTML = fulfillmentOrders
    .map((item) => simpleBusinessCard({ name: item.name, status: item.warehouse, detail: `已付款 ${item.paid} · 已发货 ${item.shipped} · 待发 ${item.pending} · 超时风险 ${item.timeout}` }))
    .join("");
  document.querySelector("#logisticsIssueList").innerHTML = logisticsIssues.map(progressRow).join("");
}

function renderFeedbackReturns() {
  renderMetricCards("#feedbackMetricGrid", [
    { label: "今日退货率", value: "4.6%", sub: "全平台", color: "#9c2f45" },
    { label: "新增差评", value: "18", sub: "需客服回访", color: "#0f766e" },
    { label: "评价数", value: "642", sub: "今日新增", color: "#c47a1d" },
    { label: "产品问题", value: "3", sub: "需反推优化", color: "#6b5b95" },
  ]);
  document.querySelector("#returnReasonList").innerHTML = returnReasons.map(progressRow).join("");
  document.querySelector("#productFeedbackList").innerHTML = productFeedback.map(simpleBusinessCard).join("");
}

function renderMarketTrends() {
  renderMetricCards("#trendMetricGrid", [
    { label: "监控竞品", value: competitors.length.toString(), sub: "本周重点", color: "#9c2f45" },
    { label: "趋势信号", value: trendSignals.length.toString(), sub: "内容/商品方向", color: "#0f766e" },
    { label: "价格压力", value: "2", sub: "需关注毛利", color: "#c47a1d" },
    { label: "可开发机会", value: "4", sub: "下一波企划输入", color: "#6b5b95" },
  ]);
  document.querySelector("#competitorList").innerHTML = competitors.map(simpleBusinessCard).join("");
  document.querySelector("#trendSignalList").innerHTML = trendSignals.map(progressRow).join("");
}

function renderTaskCollaboration() {
  const overdue = collaborationTasks.filter((task) => task.risk !== "正常").length;
  renderMetricCards("#taskMetricGrid", [
    { label: "进行中任务", value: collaborationTasks.length.toString(), sub: "跨部门", color: "#9c2f45" },
    { label: "风险任务", value: overdue.toString(), sub: "需负责人确认", color: "#c47a1d" },
    { label: "今日截止", value: "3", sub: "需收口", color: "#0f766e" },
    { label: "关联产品", value: "5", sub: "围绕产品推进", color: "#6b5b95" },
  ]);
  const stages = ["商品", "供应链", "内容", "运营", "客服", "数据"];
  document.querySelector("#taskBoard").innerHTML = stages
    .map((stage) => {
      const tasks = collaborationTasks.filter((task) => task.stage === stage);
      return `
        <section class="task-column">
          <div class="task-column-head"><span>${stage}</span><span>${tasks.length}</span></div>
          ${tasks
            .map(
              (task) => `
                <article class="task-card">
                  <strong>${task.title}</strong>
                  <span>${task.owner} · ${task.due}</span>
                  <span class="tag ${task.risk === "正常" ? "selling" : "warning"}">${task.risk}</span>
                </article>
              `,
            )
            .join("")}
        </section>
      `;
    })
    .join("");
}

function filteredProductRows() {
  const keyword = document.querySelector("#productSearch").value.trim().toLowerCase();
  const status = document.querySelector("#statusFilter").value;
  return products.filter((product) => {
    const searchable = [
      product.name,
      product.sku,
      product.category,
      product.platforms.join(" "),
      product.colors.map((color) => color.name).join(" "),
    ]
      .join(" ")
      .toLowerCase();
    const matchesKeyword = !keyword || searchable.includes(keyword);
    const matchesStatus = status === "all" || product.status === status;
    return matchesKeyword && matchesStatus;
  });
}

function renderProductOverview(rows) {
  const signals = rows.map((product) => ({
    product,
    totals: productTotals(product),
    ops: getProductOperations(product),
  }));
  const totalMade = sum(signals.map((item) => item.totals.made));
  const totalStock = sum(signals.map((item) => item.totals.stock));
  const totalSold = sum(signals.map((item) => item.ops.soldRealQty));
  const totalAvailable = sum(signals.map((item) => item.ops.availableQty));
  const totalTargetGap = sum(signals.map((item) => item.ops.neededRealSalesQty));
  const totalTargetGmv = sum(signals.map((item) => item.ops.targetGmvValue));
  const arrivalRiskCount = signals.filter((item) => item.ops.notArrivedQty > 0).length;
  const returnRiskCount = signals.filter((item) => item.ops.comprehensiveReturnRate >= 0.25).length;
  const overallSellRate = totalMade ? totalSold / totalMade : 0;

  document.querySelector("#productOverviewGrid").innerHTML =
    [
      { label: "款数", value: `${rows.length} 款`, sub: `在售 ${rows.filter((item) => item.status === "selling").length} 款`, tone: "dark" },
      { label: "总做货", value: `${totalMade.toLocaleString("zh-CN")} 件`, sub: `已售 ${totalSold.toLocaleString("zh-CN")} 件`, tone: "red" },
      { label: "剩余库存", value: `${totalStock.toLocaleString("zh-CN")} 件`, sub: `可用 ${totalAvailable.toLocaleString("zh-CN")} 件`, tone: "teal" },
      { label: "整体售罄", value: formatPercentValue(overallSellRate), sub: "按做货与剩余库存测算", tone: "orange" },
      { label: "目标缺口", value: `${totalTargetGap.toLocaleString("zh-CN")} 件`, sub: `所需 GMV ${formatCurrency(totalTargetGmv)}`, tone: "purple" },
      { label: "风险提醒", value: `${arrivalRiskCount + returnRiskCount} 项`, sub: `${arrivalRiskCount} 到仓 / ${returnRiskCount} 退货`, tone: "gray" },
    ]
      .map(
        (item) => `
          <article class="product-overview-card ${item.tone}">
            <span>${item.label}</span>
            <strong>${item.value}</strong>
            <em>${item.sub}</em>
          </article>
        `,
      )
      .join("");

  document.querySelector("#productWatchGrid").innerHTML =
    signals
      .sort((a, b) => b.ops.neededRealSalesQty - a.ops.neededRealSalesQty)
      .slice(0, 3)
      .map(({ product, totals, ops }) => `
        <button class="product-watch-card" type="button" data-product-id="${product.id}">
          <div class="product-watch-head">
            <span class="thumb small" style="--swatch-a:${product.swatchA}; --swatch-b:${product.swatchB}"></span>
            <div>
              <strong>${escapeHtml(product.name)}</strong>
              <em>${escapeHtml(product.sku)} · ${escapeHtml(ops.styleGrade)}</em>
            </div>
          </div>
          <div class="watch-compact-row">
            <div><span>售罄</span><strong>${formatPercentValue(ops.currentSellThroughRate)}</strong></div>
            <div><span>缺口</span><strong>${ops.neededRealSalesQty}</strong></div>
            <div><span>退货</span><strong>${formatPercentValue(ops.comprehensiveReturnRate)}</strong></div>
          </div>
          <div class="mini-track">
            <div class="mini-fill" style="width:${Math.min(ops.currentSellThroughRate * 100, 100)}%"></div>
          </div>
          <div class="watch-foot">
            <span class="tag ${ops.notArrivedQty > 0 ? "warning" : "selling"}">${escapeHtml(ops.arrivalStatus)}</span>
            <span>库存 ${totals.stock} / 可用 ${ops.availableQty}</span>
          </div>
        </button>
      `)
      .join("") || `<div class="empty-state">没有匹配的产品</div>`;
}

function renderProducts() {
  const rows = filteredProductRows();
  renderProductOverview(rows);

  document.querySelector("#productTable").innerHTML =
    rows
      .map((product) => {
        const totals = productTotals(product);
        const ops = getProductOperations(product);
        return `
          <tr>
            <td>
              <div class="product-cell">
                <div class="thumb" style="--swatch-a:${product.swatchA}; --swatch-b:${product.swatchB}"></div>
                <div class="product-name">
                  <button type="button" data-product-id="${product.id}">${escapeHtml(product.name)}</button>
                  <span>${escapeHtml(product.sku)} · ${escapeHtml(product.category)} · ¥${product.price}</span>
                </div>
              </div>
            </td>
            <td>${totals.made.toLocaleString("zh-CN")}</td>
            <td>${ops.soldRealQty.toLocaleString("zh-CN")}</td>
            <td>${totals.stock.toLocaleString("zh-CN")}</td>
            <td>
              <div class="sell-rate">
                <strong>${formatPercentValue(ops.currentSellThroughRate)}</strong>
                <div class="mini-track">
                  <div class="mini-fill" style="width:${Math.min(ops.currentSellThroughRate * 100, 100)}%"></div>
                </div>
              </div>
            </td>
            <td>${ops.availableQty.toLocaleString("zh-CN")}</td>
            <td>${ops.neededRealSalesQty.toLocaleString("zh-CN")}</td>
            <td>${formatPercentValue(ops.comprehensiveReturnRate)}</td>
            <td><span class="tag ${ops.notArrivedQty > 0 ? "warning" : "selling"}">${escapeHtml(ops.arrivalStatus)}</span></td>
            <td><span class="grade-pill">${escapeHtml(ops.styleGrade)}</span></td>
            <td><span class="tag ${product.status}">${statusText[product.status]}</span></td>
            <td><button class="link-button" type="button" data-edit-product-id="${product.id}">编辑</button></td>
          </tr>
        `;
      })
      .join("") || `<tr><td colspan="12">没有匹配的产品</td></tr>`;
}

function seasonBucketName(season) {
  if (String(season).includes("春")) return "春季";
  if (String(season).includes("夏")) return "夏季";
  if (String(season).includes("秋")) return "秋季";
  if (String(season).includes("冬")) return "冬季";
  return "未分季";
}

function styleGradeWeight(grade) {
  return {
    "A+": 9,
    A: 8,
    "A-": 7,
    "B+": 6,
    B: 5,
    "B-": 4,
    C: 3,
    D: 2,
  }[grade] || 4;
}

function productAnalysisRows() {
  return products.map((product) => {
    const totals = productTotals(product);
    const ops = getProductOperations(product);
    const salesWeight = Math.max(
      0,
      Math.round(
        ops.soldRealQty * 0.35 +
          ops.availableQty * 0.18 +
          ops.neededRealSalesQty * 0.28 +
          styleGradeWeight(ops.styleGrade) * 18 -
          ops.comprehensiveReturnRate * 80,
      ),
    );
    return {
      product,
      totals,
      ops,
      sellThroughRate: ops.currentSellThroughRate,
      season: seasonBucketName(ops.season),
      salesWeight,
      riskScore: Math.round(ops.comprehensiveReturnRate * 100 + totals.stock * 0.05 + ops.neededRealSalesQty * 0.08),
    };
  });
}

function analysisThreshold(prompt) {
  const text = prompt.replace(/\s/g, "");
  const match = text.match(/(低于|小于|少于|<|高于|大于|超过|>)(\d+(?:\.\d+)?)%?/);
  if (!match) return null;
  return {
    direction: ["高于", "大于", "超过", ">"].includes(match[1]) ? "above" : "below",
    value: Number(match[2]) / 100,
    label: `${match[1]}${match[2]}%`,
  };
}

function renderAnalysisProductCard(row, reason) {
  return `
    <button class="ai-product-result" type="button" data-product-id="${row.product.id}">
      <span>${escapeHtml(row.product.sku)} · ${escapeHtml(row.season)} · ${escapeHtml(row.ops.styleGrade)}</span>
      <strong>${escapeHtml(row.product.name)}</strong>
      <em>售罄 ${formatPercentValue(row.sellThroughRate)} · 实销 ${row.ops.soldRealQty} · 库存 ${row.totals.stock} · 缺口 ${row.ops.neededRealSalesQty} · 权重 ${row.salesWeight}</em>
      ${reason ? `<em>${escapeHtml(reason)}</em>` : ""}
    </button>
  `;
}

function groupedAnalysisSections(rows) {
  const grouped = rows.reduce((groups, row) => {
    groups[row.season] = groups[row.season] || [];
    groups[row.season].push(row);
    return groups;
  }, {});
  return Object.entries(grouped)
    .map(
      ([season, groupRows]) => `
        <section class="ai-report-section">
          <h4>${escapeHtml(season)} · ${groupRows.length} 款</h4>
          <div class="ai-product-grid">
            ${groupRows.map((row, index) => renderAnalysisProductCard(row, `本组第 ${index + 1} 优先`)).join("")}
          </div>
        </section>
      `,
    )
    .join("");
}

function renderProductAnalysis() {
  const prompt = document.querySelector("#aiProductPrompt").value.trim();
  const resultBox = document.querySelector("#aiAnalysisResult");
  if (!prompt) {
    resultBox.innerHTML = `<p>先输入一个分析需求，例如“找出售罄率低于50%的产品，按季节分类，并按售卖权重排序”。</p>`;
    return;
  }

  const rows = productAnalysisRows();
  const threshold = analysisThreshold(prompt);
  const asksSellThrough = /售罄|收罄|售卖率/.test(prompt);
  const asksSeason = /季节|春|夏|秋|冬/.test(prompt);
  const asksTarget = /目标|缺口|还需|实销/.test(prompt);
  const asksRisk = /退货|风险|库存/.test(prompt);

  let title = "产品经营分析报告";
  let subtitle = "基于当前产品库的做货、库存、售罄、退货、目标缺口和款式分类字段生成。";
  let selected = rows;
  let note = "当前是本地规则分析 Demo。后续接入大模型后，可以把这份结构化产品数据作为上下文，让模型理解更复杂的问题。";

  if (asksSellThrough) {
    const rule = threshold || { direction: "below", value: 0.5, label: "低于50%" };
    title = `售罄率${rule.label}产品分析`;
    selected = rows.filter((row) => (rule.direction === "above" ? row.sellThroughRate > rule.value : row.sellThroughRate < rule.value));
    selected.sort((a, b) => b.salesWeight - a.salesWeight);
    if (!selected.length) {
      const nearest = [...rows].sort((a, b) => a.sellThroughRate - b.sellThroughRate).slice(0, 5);
      resultBox.innerHTML = `
        <div class="ai-report">
          <div class="ai-report-head">
            <div>
              <h4>${escapeHtml(title)}</h4>
              <p>当前没有命中“${escapeHtml(rule.label)}”的产品。下面列出售罄率最低的款，方便你判断是否放宽阈值。</p>
            </div>
            <span class="tag selling">0 款命中</span>
          </div>
          <div class="ai-report-kpis">
            <article class="ai-report-kpi"><span>分析产品</span><strong>${rows.length} 款</strong></article>
            <article class="ai-report-kpi"><span>最低售罄</span><strong>${formatPercentValue(nearest[0]?.sellThroughRate || 0)}</strong></article>
            <article class="ai-report-kpi"><span>建议阈值</span><strong>80%</strong></article>
            <article class="ai-report-kpi"><span>分类方式</span><strong>${asksSeason ? "季节" : "综合"}</strong></article>
          </div>
          <section class="ai-report-section">
            <h4>最接近低售罄的款</h4>
            <div class="ai-product-grid">${nearest.map((row) => renderAnalysisProductCard(row, "售罄率最低候选")).join("")}</div>
          </section>
          <div class="ai-report-note">${note}</div>
        </div>
      `;
      return;
    }
  } else if (asksRisk) {
    title = "退货与库存风险款分析";
    selected = rows
      .filter((row) => row.ops.comprehensiveReturnRate >= 0.18 || row.totals.stock >= 100)
      .sort((a, b) => b.riskScore - a.riskScore)
      .slice(0, 8);
    subtitle = "优先找出退货率高、库存仍高、目标缺口未消化的产品。";
  } else if (asksTarget) {
    title = "目标缺口优先级分析";
    selected = [...rows].sort((a, b) => b.ops.neededRealSalesQty - a.ops.neededRealSalesQty).slice(0, 8);
    subtitle = "按照距目标还需实销件数排序，适合安排内容、直播和补投优先级。";
  } else {
    selected = [...rows].sort((a, b) => b.salesWeight - a.salesWeight).slice(0, 8);
  }

  const avgSellRate = rows.length ? sum(rows.map((row) => row.sellThroughRate)) / rows.length : 0;
  const selectedStock = sum(selected.map((row) => row.totals.stock));
  const selectedTargetGap = sum(selected.map((row) => row.ops.neededRealSalesQty));
  const body = asksSeason ? groupedAnalysisSections(selected) : `
    <section class="ai-report-section">
      <h4>优先级结果</h4>
      <div class="ai-product-grid">${selected.map((row, index) => renderAnalysisProductCard(row, `总排序第 ${index + 1}`)).join("")}</div>
    </section>
  `;

  resultBox.innerHTML = `
    <div class="ai-report">
      <div class="ai-report-head">
        <div>
          <h4>${escapeHtml(title)}</h4>
          <p>${escapeHtml(subtitle)}</p>
        </div>
        <span class="tag selling">${selected.length} 款命中</span>
      </div>
      <div class="ai-report-kpis">
        <article class="ai-report-kpi"><span>分析产品</span><strong>${rows.length} 款</strong></article>
        <article class="ai-report-kpi"><span>平均售罄</span><strong>${formatPercentValue(avgSellRate)}</strong></article>
        <article class="ai-report-kpi"><span>命中库存</span><strong>${selectedStock.toLocaleString("zh-CN")} 件</strong></article>
        <article class="ai-report-kpi"><span>命中缺口</span><strong>${selectedTargetGap.toLocaleString("zh-CN")} 件</strong></article>
      </div>
      ${body}
      <div class="ai-report-note">${note}</div>
    </div>
  `;
}

function unitLabels(product) {
  return product.colors.flatMap((color) => Object.keys(color.sizes).map((size) => `${color.name}-${size}`));
}

function getProductKnowledge(product) {
  const totals = productTotals(product);
  const ops = getProductOperations(product);
  const fallbackElements = {
    色彩元素: product.colors.map((color) => color.name),
    款式元素: [product.category, "女装基础款"],
    材质元素: ["待补充"],
    场景元素: product.platforms,
    内容关键词: ["新品分析", "商品卖点", "待提炼"],
  };
  const fallbackVideos = contentTopics
    .filter((topic) => topic.product === product.name)
    .map((topic) => ({
      title: topic.title,
      platform: topic.channel,
      status: topicStages.find((stage) => stage.id === topic.stage)?.name || "制作中",
      views: Math.round(topic.progress * 1200),
      interactions: Math.round(topic.progress * 95),
      sales: Math.round(topic.progress * product.price * 8),
      conversion: 1.8,
      linkedUnits: unitLabels(product).slice(0, 2),
    }));

  return {
    videos: fallbackVideos,
    paidCampaigns: [
      {
        name: `${product.name} 内容加热`,
        platform: product.platforms[0] || "淘宝",
        content: `${product.name} 主推素材`,
        spend: Math.max(1800, Math.round(product.price * 18)),
        paidUnits: Math.max(8, Math.round(totals.sold * 0.08)),
        paidGmv: Math.max(product.price * 8, Math.round(product.price * Math.max(8, totals.sold * 0.08))),
        refundUnits: Math.max(1, Math.round(totals.sold * 0.012)),
        refundAmount: Math.max(product.price, Math.round(product.price * Math.max(1, totals.sold * 0.012))),
        exposure: Math.max(12000, totals.made * 90),
        clicks: Math.max(500, totals.made * 4),
        verdict: "待验证",
        note: "示例投流记录，后续可接入巨量、淘宝、聚光等投放明细。",
      },
    ],
    liveSessions: [
      {
        title: `${product.name} 日常店播讲解`,
        hostGroup: "店铺主播1",
        host: "店铺主播1-待记录",
        date: "待补充",
        scene: "日常店播",
        clip: "待上传录屏",
        units: Math.max(5, Math.round(ops.soldRealQty * 0.06)),
        gmv: Math.max(product.price * 5, Math.round(product.price * Math.max(5, ops.soldRealQty * 0.06))),
        conversion: 3.6,
        tryOn: "待补充主播身高/尺码",
        visual: "待补充画面呈现",
        verdict: "待验证",
        script: "这里记录主播对这个产品的原始讲解文案，后续可以从录屏自动转写。",
        analysis: ["待沉淀开场钩子", "待记录尺码解释", "待对比不同主播成交"],
        signals: [{ time: "待记录", event: "讲解片段", units: Math.max(1, Math.round(ops.soldRealQty * 0.02)) }],
      },
    ],
    assets: [
      { type: "主图", title: `${product.name} 主图`, note: "待上传正式商品图", a: product.swatchA, b: product.swatchB },
      { type: "详情图", title: `${product.category} 卖点图`, note: "待补充详情页素材", a: product.swatchB, b: product.swatchA },
    ],
    detailBlocks: [{ title: "详情页内容", copy: "这里记录商品详情页首屏文案、卖点、尺码建议和搭配建议。" }],
    elements: fallbackElements,
    ...(productKnowledge[product.id] || {}),
  };
}

function activateProductTab(tabId) {
  document.querySelectorAll(".detail-tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.productTab === tabId);
  });
  document.querySelectorAll(".detail-panel").forEach((panel) => {
    panel.classList.toggle("active-detail-panel", panel.id === `tab-${tabId}`);
  });
}

function renderSkuMatrix(product) {
  document.querySelector("#skuMatrix").innerHTML = product.colors
    .map((color) => {
      const colorRows = Object.entries(color.sizes);
      const made = sum(colorRows.map(([, row]) => row.made));
      const stock = sum(colorRows.map(([, row]) => row.stock));
      const stockRate = made ? stock / made : 0;
      return `
        <section class="color-block">
          <div class="color-head">
            <div class="color-title">
              <span class="swatch" style="--swatch:${color.hex}"></span>
              ${escapeHtml(color.name)}
            </div>
            <span class="sku-ratio-summary">${stock.toLocaleString("zh-CN")} / ${made.toLocaleString("zh-CN")}<em>剩余 / 做货 · ${formatPercentValue(stockRate)}</em></span>
          </div>
          <div class="size-grid">
            ${colorRows
              .map(
                ([size, row]) => `
                  <div class="size-cell">
                    <span>${escapeHtml(size)}</span>
                    <strong>${row.stock.toLocaleString("zh-CN")} / ${row.made.toLocaleString("zh-CN")}</strong>
                    <span>剩余 / 做货</span>
                    <div class="unit-code">${escapeHtml(product.sku)}-${escapeHtml(color.name)}-${escapeHtml(size)}</div>
                  </div>
                `,
              )
              .join("")}
          </div>
        </section>
      `;
    })
    .join("");
}

function renderRelatedContent(knowledge) {
  document.querySelector("#relatedContentList").innerHTML =
    knowledge.videos
      .map(
        (video) => `
          <article class="content-card">
            <div class="content-card-head">
              <div class="content-card-title">
                <strong>${escapeHtml(video.title)}</strong>
                <span class="muted">${escapeHtml(video.platform)} · ${escapeHtml(video.status)}</span>
              </div>
              <span class="tag selling">${video.conversion}% 转化</span>
            </div>
            <div class="content-metrics">
              <div class="content-mini-metric"><span>播放</span><strong>${video.views.toLocaleString("zh-CN")}</strong></div>
              <div class="content-mini-metric"><span>互动</span><strong>${video.interactions.toLocaleString("zh-CN")}</strong></div>
              <div class="content-mini-metric"><span>引导成交</span><strong>${formatCurrency(video.sales)}</strong></div>
              <div class="content-mini-metric"><span>关联单元</span><strong>${video.linkedUnits.length}</strong></div>
            </div>
            <div class="unit-tags">
              ${video.linkedUnits.map((unit) => `<span class="unit-tag">${escapeHtml(unit)}</span>`).join("")}
            </div>
          </article>
        `,
      )
      .join("") || `<div class="detail-copy-block"><p>还没有关联内容。后续可以把选题、短视频、直播切片绑定到这件产品。</p></div>`;
}

function renderPaidPromotion(knowledge) {
  const campaigns = knowledge.paidCampaigns || [];
  const totalSpend = sum(campaigns.map((item) => item.spend || 0));
  const paidUnits = sum(campaigns.map((item) => item.paidUnits || 0));
  const paidGmv = sum(campaigns.map((item) => item.paidGmv || 0));
  const refundAmount = sum(campaigns.map((item) => item.refundAmount || 0));
  const netGmv = paidGmv - refundAmount;
  const paymentRoi = totalSpend ? paidGmv / totalSpend : 0;
  const netRoi = totalSpend ? netGmv / totalSpend : 0;

  document.querySelector("#paidSummaryGrid").innerHTML = [
    ["付费花费", formatCurrency(totalSpend), `${campaigns.length} 条投放记录`],
    ["带动成交", `${paidUnits.toLocaleString("zh-CN")} 件`, formatCurrency(paidGmv)],
    ["支付 ROI", paymentRoi.toFixed(2), "未扣退款"],
    ["净 ROI", netRoi.toFixed(2), `扣退款 ${formatCurrency(refundAmount)}`],
  ]
    .map(
      ([label, value, sub]) => `
        <article class="paid-summary-card">
          <span>${label}</span>
          <strong>${value}</strong>
          <em>${sub}</em>
        </article>
      `,
    )
    .join("");

  document.querySelector("#paidCampaignList").innerHTML =
    campaigns
      .map((campaign) => {
        const paymentRoiValue = campaign.spend ? campaign.paidGmv / campaign.spend : 0;
        const netGmvValue = campaign.paidGmv - campaign.refundAmount;
        const netRoiValue = campaign.spend ? netGmvValue / campaign.spend : 0;
        return `
          <article class="paid-campaign-card">
            <div class="paid-campaign-head">
              <div>
                <strong>${escapeHtml(campaign.name)}</strong>
                <span>${escapeHtml(campaign.platform)} · ${escapeHtml(campaign.content)}</span>
              </div>
              <span class="tag ${netRoiValue >= 1.4 ? "selling" : netRoiValue >= 1 ? "warning" : "error"}">${escapeHtml(campaign.verdict)}</span>
            </div>
            <div class="paid-metric-grid">
              <div><span>花费</span><strong>${formatCurrency(campaign.spend)}</strong></div>
              <div><span>成交件数</span><strong>${campaign.paidUnits}</strong></div>
              <div><span>支付 GMV</span><strong>${formatCurrency(campaign.paidGmv)}</strong></div>
              <div><span>支付 ROI</span><strong>${paymentRoiValue.toFixed(2)}</strong></div>
              <div><span>退款金额</span><strong>${formatCurrency(campaign.refundAmount)}</strong></div>
              <div><span>净 ROI</span><strong>${netRoiValue.toFixed(2)}</strong></div>
              <div><span>曝光</span><strong>${campaign.exposure.toLocaleString("zh-CN")}</strong></div>
              <div><span>点击</span><strong>${campaign.clicks.toLocaleString("zh-CN")}</strong></div>
            </div>
            <p>${escapeHtml(campaign.note)}</p>
          </article>
        `;
      })
      .join("") || `<div class="detail-copy-block"><p>还没有付费投流记录。后续可从广告平台导入花费、成交、退款和 ROI。</p></div>`;
}

function liveHostKey(session) {
  return session.hostGroup || session.host || "未分主播";
}

function liveHostSummaries(sessions) {
  const grouped = sessions.reduce((groups, session) => {
    const key = liveHostKey(session);
    groups[key] = groups[key] || [];
    groups[key].push(session);
    return groups;
  }, {});

  return Object.entries(grouped).map(([key, group]) => {
    const units = sum(group.map((session) => session.units || 0));
    const gmv = sum(group.map((session) => session.gmv || 0));
    const conversion = group.length ? sum(group.map((session) => session.conversion || 0)) / group.length : 0;
    const best = [...group].sort((a, b) => (b.units || 0) - (a.units || 0))[0];
    return { key, label: key, sessions: group.length, units, gmv, conversion, best };
  });
}

function renderLiveSelling(knowledge) {
  const sessions = knowledge.liveSessions || [];
  const hostSummaries = liveHostSummaries(sessions);
  if (currentLiveHost !== "all" && !hostSummaries.some((host) => host.key === currentLiveHost)) {
    currentLiveHost = "all";
  }
  const activeSessions = currentLiveHost === "all" ? sessions : sessions.filter((session) => liveHostKey(session) === currentLiveHost);
  const totalUnits = sum(activeSessions.map((session) => session.units || 0));
  const totalGmv = sum(activeSessions.map((session) => session.gmv || 0));
  const bestSession = [...activeSessions].sort((a, b) => (b.units || 0) - (a.units || 0))[0];
  const bestSignal = activeSessions
    .flatMap((session) => (session.signals || []).map((signal) => ({ ...signal, host: session.host, title: session.title })))
    .sort((a, b) => (b.units || 0) - (a.units || 0))[0];
  const topHost = [...hostSummaries].sort((a, b) => b.units - a.units)[0];

  document.querySelector("#liveInsightGrid").innerHTML = [
    ["当前筛选", currentLiveHost === "all" ? "全部主播" : currentLiveHost, `${activeSessions.length} 段录屏`],
    ["直播成交", `${totalUnits.toLocaleString("zh-CN")} 件`, formatCurrency(totalGmv)],
    ["最佳讲解人", bestSession?.host || "待补充", bestSession ? `${bestSession.units} 件 · ${bestSession.verdict || bestSession.scene}` : "暂无"],
    ["最强主播组", topHost?.label || "暂无", topHost ? `${topHost.units} 件 · ${topHost.conversion.toFixed(1)}% 转化` : "暂无"],
  ]
    .map(
      ([label, value, sub]) => `
        <article class="live-insight-card">
          <span>${label}</span>
          <strong>${escapeHtml(value)}</strong>
          <em>${escapeHtml(sub)}</em>
        </article>
      `,
    )
    .join("");

  const allUnits = sum(sessions.map((session) => session.units || 0));
  const allGmv = sum(sessions.map((session) => session.gmv || 0));
  const hostCards = [
    { key: "all", label: "全部主播", sessions: sessions.length, units: allUnits, gmv: allGmv, conversion: sessions.length ? sum(sessions.map((session) => session.conversion || 0)) / sessions.length : 0, best: { verdict: "整体对比" } },
    ...hostSummaries,
  ];

  document.querySelector("#liveHostGrid").innerHTML = hostCards
    .map(
      (host) => `
        <button class="live-host-card ${host.key === currentLiveHost ? "active" : ""}" type="button" data-live-host="${escapeHtml(host.key)}">
          <span>主播分类</span>
          <strong>${escapeHtml(host.label)}</strong>
          <em>${host.sessions} 段 · ${host.units} 件 · ${formatCurrency(host.gmv)}</em>
          <div class="host-mini-kpis">
            <div><span>转化</span><strong>${host.conversion.toFixed(1)}%</strong></div>
            <div><span>判断</span><strong>${escapeHtml(host.best?.verdict || "待判断")}</strong></div>
          </div>
        </button>
      `,
    )
    .join("");

  document.querySelector("#liveSessionList").innerHTML =
    activeSessions
      .map(
        (session) => `
          <article class="live-session-card">
            <div class="live-session-head">
              <div>
                <strong>${escapeHtml(session.title)}</strong>
                <span>${escapeHtml(liveHostKey(session))} · ${escapeHtml(session.host)} · ${escapeHtml(session.date)} · ${escapeHtml(session.scene)} · ${escapeHtml(session.clip)}</span>
              </div>
              <span class="tag ${session.verdict === "不建议主讲" ? "warning" : "selling"}">${escapeHtml(session.verdict || `${session.units} 件`)}</span>
            </div>
            <div class="live-layout">
              <div class="live-recording">
                <div class="recording-screen">
                  <span>录屏片段</span>
                  <strong>${escapeHtml(session.clip)}</strong>
                </div>
                <div class="paid-metric-grid">
                  <div><span>成交</span><strong>${session.units} 件</strong></div>
                  <div><span>GMV</span><strong>${formatCurrency(session.gmv)}</strong></div>
                  <div><span>转化</span><strong>${session.conversion}%</strong></div>
                  <div><span>试穿</span><strong>${escapeHtml(session.tryOn)}</strong></div>
                </div>
              </div>
              <div class="live-copy-card">
                <strong>讲解文案转写</strong>
                <p>${escapeHtml(session.script)}</p>
                <strong>文案/画面分析</strong>
                <div class="chip-row">${session.analysis.map((item) => `<span class="element-chip">${escapeHtml(item)}</span>`).join("")}</div>
              </div>
            </div>
            <div class="live-signal-list">
              ${(session.signals || [])
                .map(
                  (signal) => `
                    <div class="live-signal">
                      <span>${escapeHtml(signal.time)}</span>
                      <strong>${escapeHtml(signal.event)}</strong>
                      <em>${signal.units} 件</em>
                    </div>
                  `,
                )
                .join("")}
            </div>
            <p class="live-note">这个模块后续可以接录屏文件、语音转文字和分钟级成交数据，用来反推“哪个主播、哪种话术、哪个画面”最能卖这个款。</p>
          </article>
        `,
      )
      .join("") || `<div class="detail-copy-block"><p>这个主播分类下还没有直播讲解记录。</p></div>`;
}

function renderAssets(knowledge) {
  document.querySelector("#assetGrid").innerHTML = knowledge.assets
    .map(
      (asset) => `
        <article class="asset-card">
          <div class="asset-thumb" data-label="${escapeHtml(asset.type)}" style="--asset-a:${asset.a}; --asset-b:${asset.b}"></div>
          <strong>${escapeHtml(asset.title)}</strong>
          <span>${escapeHtml(asset.note)}</span>
        </article>
      `,
    )
    .join("");

  document.querySelector("#detailPageBlocks").innerHTML = knowledge.detailBlocks
    .map(
      (block) => `
        <section class="detail-copy-block">
          <strong>${escapeHtml(block.title)}</strong>
          <p>${escapeHtml(block.copy)}</p>
        </section>
      `,
    )
    .join("");
}

function renderElements(knowledge) {
  document.querySelector("#elementGroups").innerHTML = Object.entries(knowledge.elements)
    .map(
      ([group, values]) => `
        <section class="element-group">
          <strong>${escapeHtml(group)}</strong>
          <div class="chip-row">
            ${values.map((value) => `<span class="element-chip">${escapeHtml(value)}</span>`).join("")}
          </div>
        </section>
      `,
    )
    .join("");
}

function renderRelationGraph(product, knowledge) {
  const units = unitLabels(product);
  const elementCount = sum(Object.values(knowledge.elements).map((values) => values.length));
  document.querySelector("#relationGraph").innerHTML = `
    <div class="graph-center">${escapeHtml(product.name)}<br><span>${escapeHtml(product.sku)}</span></div>
    <div class="graph-grid">
      <div class="graph-node"><strong>SKU 单元</strong><span>${units.length} 个颜色尺码单元，例如 ${units.slice(0, 3).join("、")}</span></div>
      <div class="graph-node"><strong>关联内容</strong><span>${knowledge.videos.length} 条视频/选题，连接销售表现与内容表现</span></div>
      <div class="graph-node"><strong>付费投流</strong><span>${(knowledge.paidCampaigns || []).length} 条投放记录，追踪花费、成交、退款后净 ROI</span></div>
      <div class="graph-node"><strong>直播讲解</strong><span>${(knowledge.liveSessions || []).length} 段录屏文案，关联主播、画面与分钟级成交</span></div>
      <div class="graph-node"><strong>素材详情</strong><span>${knowledge.assets.length} 组图片素材，${knowledge.detailBlocks.length} 段详情页内容</span></div>
      <div class="graph-node"><strong>元素标签</strong><span>${elementCount} 个色彩、款式、材质、场景和关键词标签</span></div>
    </div>
  `;
}

function renderBusinessSection(group) {
  document.querySelector("#businessDetailTitle").textContent = group.title;
  document.querySelector("#businessDetailMeta").textContent = group.meta;
  document.querySelector("#businessFieldGrid").innerHTML = group.fields
    .map(
      ([label, value]) => `
        <article class="business-field">
          <span>${escapeHtml(label)}</span>
          <strong>${escapeHtml(value)}</strong>
        </article>
      `,
    )
    .join("");
}

function businessOpsEditorValue(ops, field) {
  const value = ops[field.key];
  if (field.type === "percent") {
    const percent = Number(value);
    return Number.isFinite(percent) ? Number((percent * 100).toFixed(1)) : "";
  }
  if (field.type === "number") {
    const number = Number(value);
    return Number.isFinite(number) ? Math.round(number) : "";
  }
  return value ?? "";
}

function renderBusinessOpsEditor(product, ops) {
  const editor = document.querySelector("#businessOpsEditor");
  if (!editor) return;

  let currentGroup = "";
  editor.innerHTML = businessOpsEditorFields
    .map((field) => {
      const groupTitle =
        field.group !== currentGroup ? `<div class="business-edit-group">${escapeHtml(field.group)}</div>` : "";
      currentGroup = field.group;
      const inputType = field.type === "text" ? "text" : "number";
      const step = field.type === "percent" ? "0.1" : "1";
      const suffix = field.type === "percent" ? "<em>%</em>" : "";
      const value = businessOpsEditorValue(ops, field);

      return `
        ${groupTitle}
        <label>
          <span>${escapeHtml(field.label)}</span>
          <div class="business-edit-input">
            <input
              type="${inputType}"
              name="${escapeHtml(field.key)}"
              value="${escapeHtml(value)}"
              ${inputType === "number" ? `min="0" step="${step}"` : ""}
              data-business-field="${escapeHtml(field.key)}"
            />
            ${suffix}
          </div>
        </label>
      `;
    })
    .join("");

  const status = document.querySelector("#businessOpsStatus");
  if (status) {
    status.textContent = `当前维护款号：${product.sku}`;
    status.classList.remove("error");
  }
}

function parseBusinessOpsValue(input, field) {
  const rawValue = input.value.trim();
  if (field.type === "text") return rawValue;

  if (rawValue === "") return 0;
  const value = Number(rawValue);
  if (!Number.isFinite(value)) return null;
  return field.type === "percent" ? Math.max(0, value) / 100 : Math.max(0, value);
}

function handleBusinessOpsSubmit(event) {
  event.preventDefault();
  const status = document.querySelector("#businessOpsStatus");
  const product = products.find((item) => item.id === currentProductId);
  if (!product) return;

  const nextOperations = { ...(product.operations || {}) };
  for (const field of businessOpsEditorFields) {
    const input = event.currentTarget.querySelector(`[name="${field.key}"]`);
    if (!input) continue;
    const value = parseBusinessOpsValue(input, field);
    if (value === null) {
      status.textContent = `${field.label} 不是有效数字，请调整后再保存。`;
      status.classList.add("error");
      return;
    }
    nextOperations[field.key] = value;
  }

  product.operations = nextOperations;
  if (nextOperations.secondCategory) product.category = nextOperations.secondCategory;

  saveProducts("business-ops-editor");
  renderAll();
  openProduct(product.id);
  activateProductTab("business");

  const nextStatus = document.querySelector("#businessOpsStatus");
  if (nextStatus) {
    nextStatus.textContent = `已保存 ${businessOpsEditorFields.length} 个经营字段，并同步到本地产品数据库。`;
    nextStatus.classList.remove("error");
  }
}

function renderBusinessData(product) {
  const ops = getProductOperations(product);
  const groups = businessFieldGroups(ops);
  const activeGroup = groups.find((group) => group.id === currentBusinessSection) || groups[0];
  currentBusinessSection = activeGroup.id;

  document.querySelector("#businessKpiGrid").innerHTML = [
    ["计划生产", `${ops.planProductionQty.toLocaleString("zh-CN")} 件`, `首单 ${ops.firstOrderQty.toLocaleString("zh-CN")} 件`],
    ["到仓进度", `${ops.arrivedQty.toLocaleString("zh-CN")} / ${ops.planProductionQty.toLocaleString("zh-CN")}`, ops.arrivalStatus],
    ["在仓库存", `${ops.warehouseStock.toLocaleString("zh-CN")} 件`, `可用 ${ops.availableQty.toLocaleString("zh-CN")} 件`],
    ["目前售罄率", formatPercentValue(ops.currentSellThroughRate), `目标 ${formatPercentValue(ops.targetSellThroughRate)}`],
    ["综合退货率", formatPercentValue(ops.comprehensiveReturnRate), `发货后 ${formatPercentValue(ops.afterShippingReturnRate)}`],
    ["目标缺口", `${ops.neededRealSalesQty.toLocaleString("zh-CN")} 件`, `所需 GMV ${formatCurrency(ops.targetGmvValue)}`],
  ]
    .map(
      ([label, value, sub]) => `
        <article class="business-kpi-card">
          <span>${label}</span>
          <strong>${value}</strong>
          <em>${sub}</em>
        </article>
      `,
    )
    .join("");

  document.querySelector("#businessSectionGrid").innerHTML = groups
    .map(
      (group) => `
        <button class="business-section-card ${group.id === activeGroup.id ? "active" : ""}" type="button" data-business-section="${group.id}">
          <span>${group.title}</span>
          <strong>${group.summary}</strong>
          <em>${group.fields.length} 个字段</em>
        </button>
      `,
    )
    .join("");

  renderBusinessSection(activeGroup);
  renderBusinessOpsEditor(product, ops);
  document.querySelector("#businessFieldLedger").innerHTML = groups
    .map(
      (group) => `
        <section class="ledger-group">
          <h4>${group.title}</h4>
          <div class="ledger-grid">
            ${group.fields
              .map(
                ([label, value]) => `
                  <div class="ledger-row">
                    <span>${escapeHtml(label)}</span>
                    <strong>${escapeHtml(value)}</strong>
                  </div>
                `,
              )
              .join("")}
          </div>
        </section>
      `,
    )
    .join("");
}

function createProductId() {
  const nextNumber =
    Math.max(
      0,
      ...products
        .map((product) => Number.parseInt(String(product.id).replace(/^P/i, ""), 10))
        .filter(Number.isFinite),
    ) + 1;
  return `P${String(nextNumber).padStart(3, "0")}`;
}

function defaultSkuRows() {
  return [
    { size: "S", made: 0, stock: 0 },
    { size: "M", made: 0, stock: 0 },
    { size: "L", made: 0, stock: 0 },
  ];
}

function productToFormState(product) {
  return {
    productId: product?.id || null,
    colors: (product?.colors?.length ? product.colors : [{ name: "默认色", hex: "#9c2f45", sizes: {} }]).map((color) => ({
      name: color.name || "默认色",
      hex: color.hex || "#9c2f45",
      sizes: Object.entries(color.sizes || {}).map(([size, row]) => ({
        size,
        made: Number(row.made) || 0,
        stock: Number(row.stock) || 0,
      })),
    })),
  };
}

function renderProductSkuEditor() {
  document.querySelector("#productSkuEditor").innerHTML = productFormState.colors
    .map(
      (color, colorIndex) => `
        <article class="sku-editor-card" data-color-index="${colorIndex}">
          <div class="sku-editor-head">
            <label>
              颜色名称
              <input type="text" data-color-field="name" value="${escapeHtml(color.name)}" placeholder="例如 莓果红" />
            </label>
            <label>
              色值
              <input type="color" data-color-field="hex" value="${escapeHtml(color.hex || "#9c2f45")}" />
            </label>
            <button class="secondary-button" type="button" data-remove-color ${productFormState.colors.length <= 1 ? "disabled" : ""}>移除颜色</button>
          </div>
          ${(color.sizes.length ? color.sizes : defaultSkuRows())
            .map(
              (row, sizeIndex) => `
                <div class="sku-row" data-size-index="${sizeIndex}">
                  <label>
                    尺码
                    <input type="text" data-size-field="size" value="${escapeHtml(row.size)}" placeholder="S" />
                  </label>
                  <label>
                    做货件数
                    <input type="number" min="0" step="1" data-size-field="made" value="${Number(row.made) || 0}" />
                  </label>
                  <label>
                    剩余库存
                    <input type="number" min="0" step="1" data-size-field="stock" value="${Number(row.stock) || 0}" />
                  </label>
                  <button class="link-button" type="button" data-remove-size>移除尺码</button>
                </div>
              `,
            )
            .join("")}
          <button class="link-button" type="button" data-add-size>增加尺码</button>
        </article>
      `,
    )
    .join("");
}

function readSkuEditorState() {
  return [...document.querySelectorAll("#productSkuEditor .sku-editor-card")].map((card) => ({
    name: card.querySelector('[data-color-field="name"]').value.trim(),
    hex: card.querySelector('[data-color-field="hex"]').value || "#9c2f45",
    sizes: [...card.querySelectorAll(".sku-row")].map((row) => ({
      size: row.querySelector('[data-size-field="size"]').value.trim(),
      made: Math.max(0, Number(row.querySelector('[data-size-field="made"]').value) || 0),
      stock: Math.max(0, Number(row.querySelector('[data-size-field="stock"]').value) || 0),
    })),
  }));
}

function setProductFormError(message = "") {
  document.querySelector("#productFormError").textContent = message;
}

function setPlatformChecks(platformsForProduct) {
  document.querySelectorAll('[name="productPlatforms"]').forEach((checkbox) => {
    checkbox.checked = platformsForProduct.includes(checkbox.value);
  });
}

function openProductForm(productId = null) {
  const product = productId ? products.find((item) => item.id === productId) : null;
  const draft = product || {
    id: null,
    name: "",
    sku: "",
    category: "",
    status: "selling",
    platforms: ["淘宝"],
    price: 0,
    swatchA: "#9c2f45",
    swatchB: "#f1c2cc",
    colors: [{ name: "默认色", hex: "#9c2f45", sizes: { S: { made: 0, stock: 0 }, M: { made: 0, stock: 0 }, L: { made: 0, stock: 0 } } }],
  };

  productFormState = productToFormState(draft);
  document.querySelector("#productFormTitle").textContent = product ? "编辑产品" : "新增产品";
  document.querySelector("#productFormId").value = product?.id || "";
  document.querySelector("#productFormName").value = product?.name || "";
  document.querySelector("#productFormSku").value = product?.sku || "";
  document.querySelector("#productFormCategory").value = product?.category || "";
  document.querySelector("#productFormPrice").value = product?.price || 0;
  document.querySelector("#productFormStatus").value = product?.status || "selling";
  document.querySelector("#productFormSwatchA").value = product?.swatchA || productFormState.colors[0]?.hex || "#9c2f45";
  document.querySelector("#productFormSwatchB").value = product?.swatchB || productFormState.colors[1]?.hex || "#f1c2cc";
  setPlatformChecks(product?.platforms || ["淘宝"]);
  setProductFormError();
  renderProductSkuEditor();
  document.querySelector("#productFormBackdrop").classList.add("show");
  document.querySelector("#productFormBackdrop").setAttribute("aria-hidden", "false");
  document.querySelector("#productFormName").focus();
}

function closeProductForm() {
  document.querySelector("#productFormBackdrop").classList.remove("show");
  document.querySelector("#productFormBackdrop").setAttribute("aria-hidden", "true");
}

function collectProductFormData() {
  const productId = document.querySelector("#productFormId").value || createProductId();
  const existingProduct = products.find((item) => item.id === productId);
  const name = document.querySelector("#productFormName").value.trim();
  const sku = document.querySelector("#productFormSku").value.trim();
  const category = document.querySelector("#productFormCategory").value.trim();
  const price = Math.max(0, Number(document.querySelector("#productFormPrice").value) || 0);
  const status = document.querySelector("#productFormStatus").value;
  const platformsForProduct = [...document.querySelectorAll('[name="productPlatforms"]:checked')].map((item) => item.value);
  const swatchA = document.querySelector("#productFormSwatchA").value || "#9c2f45";
  const swatchB = document.querySelector("#productFormSwatchB").value || "#f1c2cc";
  const editorColors = readSkuEditorState();

  if (!name || !sku || !category) return setProductFormError("产品名称、SKU 款号和品类都需要填写。");
  if (!platformsForProduct.length) return setProductFormError("至少选择一个销售平台。");

  const colors = [];
  for (const color of editorColors) {
    if (!color.name) return setProductFormError("每个颜色都需要填写颜色名称。");
    const sizeMap = {};
    for (const row of color.sizes) {
      if (!row.size) return setProductFormError(`颜色「${color.name}」里有尺码没有填写。`);
      if (sizeMap[row.size]) return setProductFormError(`颜色「${color.name}」里的尺码「${row.size}」重复了。`);
      if (row.stock > row.made) return setProductFormError(`颜色「${color.name}」尺码「${row.size}」的库存不能大于做货件数。`);
      sizeMap[row.size] = { made: row.made, stock: row.stock };
    }
    if (!Object.keys(sizeMap).length) return setProductFormError(`颜色「${color.name}」至少需要一个尺码。`);
    colors.push({ name: color.name, hex: color.hex, sizes: sizeMap });
  }

  return normalizeProduct({
    id: productId,
    name,
    sku,
    category,
    status,
    platforms: platformsForProduct,
    price,
    swatchA,
    swatchB,
    operations: existingProduct?.operations || {},
    colors,
  });
}

function handleProductFormSubmit(event) {
  event.preventDefault();
  const product = collectProductFormData();
  if (!product) return;

  const shouldRefreshOpenProduct = document.querySelector("#modalBackdrop").classList.contains("show") && currentProductId === product.id;
  const existingIndex = products.findIndex((item) => item.id === product.id);
  if (existingIndex >= 0) {
    products[existingIndex] = product;
  } else {
    products.unshift(product);
  }
  saveProducts("product-form");
  renderAll();
  closeProductForm();
  if (shouldRefreshOpenProduct) openProduct(product.id);
}

function openProduct(productId) {
  const product = products.find((item) => item.id === productId);
  if (!product) return;
  currentProductId = product.id;
  currentBusinessSection = "profile";
  currentLiveHost = "all";
  const totals = productTotals(product);
  const ops = getProductOperations(product);
  const knowledge = getProductKnowledge(product);
  const units = unitLabels(product);
  const elementCount = sum(Object.values(knowledge.elements).map((values) => values.length));

  document.querySelector("#modalSku").textContent = product.sku;
  document.querySelector("#modalTitle").textContent = product.name;
  document.querySelector("#modalMeta").textContent = `${product.category} · ${product.platforms.join(" / ")} · 零售价 ¥${product.price}`;
  document.querySelector("#modalVisual").style.setProperty("--swatch-a", product.swatchA);
  document.querySelector("#modalVisual").style.setProperty("--swatch-b", product.swatchB);
  document.querySelector("#detailMetrics").innerHTML = [
    ["做货件数", totals.made.toLocaleString("zh-CN")],
    ["剩余库存", totals.stock.toLocaleString("zh-CN")],
    ["售罄率", formatPercentValue(ops.currentSellThroughRate)],
    ["剩余占比", `${(totals.stockRate * 100).toFixed(1)}%`],
  ]
    .map(
      ([label, value]) => `
        <div class="detail-metric">
          <span>${label}</span>
          <strong>${value}</strong>
        </div>
      `,
    )
    .join("");

  document.querySelector("#relationSummary").innerHTML = [
    ["最小 SKU 单元", `${units.length} 个`],
    ["关联视频/选题", `${knowledge.videos.length} 条`],
    ["图片素材", `${knowledge.assets.length} 组`],
    ["元素标签", `${elementCount} 个`],
  ]
    .map(
      ([label, value]) => `
        <div class="summary-pill">
          <span>${label}</span>
          <strong>${value}</strong>
        </div>
      `,
    )
    .join("");

  renderBusinessData(product);
  renderSkuMatrix(product);
  renderRelatedContent(knowledge);
  renderPaidPromotion(knowledge);
  renderLiveSelling(knowledge);
  renderAssets(knowledge);
  renderElements(knowledge);
  renderRelationGraph(product, knowledge);
  activateProductTab("business");

  document.querySelector("#modalBackdrop").classList.add("show");
  document.querySelector("#modalBackdrop").setAttribute("aria-hidden", "false");
}

function closeModal() {
  document.querySelector("#modalBackdrop").classList.remove("show");
  document.querySelector("#modalBackdrop").setAttribute("aria-hidden", "true");
}

function renderProductPersistenceBadge() {
  const badge = document.querySelector("#productPersistenceBadge");
  if (!badge) return;
  badge.classList.remove("local", "error");
  if (productSyncState.lastError) {
    badge.textContent = "本地缓存";
    badge.classList.add("error");
    return;
  }
  if (productSyncState.mode === "server") {
    badge.textContent = "本地数据库";
    return;
  }
  badge.textContent = "本地缓存";
  badge.classList.add("local");
}

function renderAll() {
  renderProductPersistenceBadge();
  renderMetrics();
  renderTrendChart();
  renderPlatformBars();
  renderProducts();
  renderContentStudio();
  renderSalesProgress();
  renderDataSourcePage();
  renderProductionProgress();
  renderSupplierProfiles();
  renderPrivateDomain();
  renderServiceExperience();
  renderExecutiveDashboard();
  renderProfitFinance();
  renderMerchPlanning();
  renderInventoryReplenishment();
  renderMarketingLive();
  renderFulfillmentLogistics();
  renderFeedbackReturns();
  renderMarketTrends();
  renderTaskCollaboration();
}

function activateSection(sectionId) {
  const targetButton = document.querySelector(`.nav-item[data-section="${sectionId}"]`);
  const targetView = document.querySelector(`#${sectionId}`);
  if (!targetButton || !targetView) return;
  document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
  document.querySelectorAll(".view").forEach((view) => view.classList.remove("active-view"));
  targetButton.classList.add("active");
  targetView.classList.add("active-view");
}

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => {
    activateSection(button.dataset.section);
    history.replaceState(null, "", `#${button.dataset.section}`);
  });
});

document.querySelector("#platformFilter").addEventListener("change", () => {
  renderMetrics();
  renderTrendChart();
});

document.querySelector("#productSearch").addEventListener("input", renderProducts);
document.querySelector("#statusFilter").addEventListener("change", renderProducts);
document.querySelector("#openProductImport").addEventListener("click", () => {
  activateSection("dataSources");
  history.replaceState(null, "", "#dataSources");
  document.querySelector("#pasteImportText").focus();
});
document.querySelector("#openProductForm").addEventListener("click", () => openProductForm());
document.querySelector("#runProductAnalysis").addEventListener("click", renderProductAnalysis);
document.querySelector(".ai-prompt-examples").addEventListener("click", (event) => {
  const button = event.target.closest("[data-analysis-prompt]");
  if (!button) return;
  document.querySelector("#aiProductPrompt").value = button.dataset.analysisPrompt;
  renderProductAnalysis();
});
document.querySelector("#aiAnalysisResult").addEventListener("click", (event) => {
  const button = event.target.closest("[data-product-id]");
  if (button) openProduct(button.dataset.productId);
});
document.querySelector("#topicStageFilter").addEventListener("change", renderTopicBoard);
document.querySelector("#csvImport").addEventListener("change", (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.addEventListener("load", () => renderImportPreview(parseCsv(String(reader.result || ""))));
  reader.readAsText(file, "utf-8");
});
document.querySelector("#parsePastedTable").addEventListener("click", () => {
  renderImportPreview(parseDelimitedText(document.querySelector("#pasteImportText").value));
});
document.querySelector("#applyProductImport").addEventListener("click", applyProductImport);
document.querySelector("#downloadProductTemplate").addEventListener("click", generateProductTemplate);

document.querySelector("#productTable").addEventListener("click", (event) => {
  const editButton = event.target.closest("[data-edit-product-id]");
  if (editButton) {
    openProductForm(editButton.dataset.editProductId);
    return;
  }
  const button = event.target.closest("[data-product-id]");
  if (button) openProduct(button.dataset.productId);
});
document.querySelector("#productWatchGrid").addEventListener("click", (event) => {
  const button = event.target.closest("[data-product-id]");
  if (button) openProduct(button.dataset.productId);
});

document.querySelector("#closeModal").addEventListener("click", closeModal);
document.querySelector("#editCurrentProduct").addEventListener("click", () => {
  if (currentProductId) openProductForm(currentProductId);
});
document.querySelector("#productForm").addEventListener("submit", handleProductFormSubmit);
document.querySelector("#businessOpsForm").addEventListener("submit", handleBusinessOpsSubmit);
document.querySelector("#closeProductForm").addEventListener("click", closeProductForm);
document.querySelector("#cancelProductForm").addEventListener("click", closeProductForm);
document.querySelector("#addColorRow").addEventListener("click", () => {
  productFormState.colors = readSkuEditorState();
  productFormState.colors.push({ name: "新颜色", hex: "#9c2f45", sizes: defaultSkuRows() });
  renderProductSkuEditor();
});
document.querySelector("#productSkuEditor").addEventListener("click", (event) => {
  const colorCard = event.target.closest("[data-color-index]");
  if (!colorCard) return;
  const colorIndex = Number(colorCard.dataset.colorIndex);
  productFormState.colors = readSkuEditorState();

  if (event.target.closest("[data-add-size]")) {
    productFormState.colors[colorIndex].sizes.push({ size: "XL", made: 0, stock: 0 });
    renderProductSkuEditor();
    return;
  }

  const removeSizeButton = event.target.closest("[data-remove-size]");
  if (removeSizeButton) {
    const sizeRow = removeSizeButton.closest("[data-size-index]");
    const sizeIndex = Number(sizeRow.dataset.sizeIndex);
    if (productFormState.colors[colorIndex].sizes.length > 1) {
      productFormState.colors[colorIndex].sizes.splice(sizeIndex, 1);
      renderProductSkuEditor();
    }
    return;
  }

  if (event.target.closest("[data-remove-color]") && productFormState.colors.length > 1) {
    productFormState.colors.splice(colorIndex, 1);
    renderProductSkuEditor();
  }
});
document.querySelector(".detail-tabs").addEventListener("click", (event) => {
  const tab = event.target.closest("[data-product-tab]");
  if (tab) activateProductTab(tab.dataset.productTab);
});
document.querySelector("#businessSectionGrid").addEventListener("click", (event) => {
  const sectionButton = event.target.closest("[data-business-section]");
  if (!sectionButton || !currentProductId) return;
  const product = products.find((item) => item.id === currentProductId);
  if (!product) return;
  currentBusinessSection = sectionButton.dataset.businessSection;
  renderBusinessData(product);
});
document.querySelector("#liveHostGrid").addEventListener("click", (event) => {
  const hostButton = event.target.closest("[data-live-host]");
  if (!hostButton || !currentProductId) return;
  const product = products.find((item) => item.id === currentProductId);
  if (!product) return;
  currentLiveHost = hostButton.dataset.liveHost;
  renderLiveSelling(getProductKnowledge(product));
});
document.querySelector("#modalBackdrop").addEventListener("click", (event) => {
  if (event.target.id === "modalBackdrop") closeModal();
});
document.querySelector("#productFormBackdrop").addEventListener("click", (event) => {
  if (event.target.id === "productFormBackdrop") closeProductForm();
});
document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  if (document.querySelector("#productFormBackdrop").classList.contains("show")) {
    closeProductForm();
  } else {
    closeModal();
  }
});

renderAll();
const productHash = location.hash.match(/^#product-([A-Za-z0-9]+)(?:-(business|sku|content|paid|live|assets|elements|graph))?$/);
if (productHash) {
  activateSection("products");
  openProduct(productHash[1]);
  if (productHash[2]) activateProductTab(productHash[2]);
} else {
  const sectionFromHash = location.hash.replace("#", "");
  activateSection(
    [
      "products",
      "contentStudio",
      "salesProgress",
      "dataSources",
      "productionProgress",
      "supplierProfiles",
      "privateDomain",
      "serviceExperience",
      "executiveDashboard",
      "profitFinance",
      "merchPlanning",
      "inventoryReplenishment",
      "marketingLive",
      "fulfillmentLogistics",
      "feedbackReturns",
      "marketTrends",
      "taskCollaboration",
    ].includes(sectionFromHash)
      ? sectionFromHash
      : "executiveDashboard",
  );
}

hydrateProductsFromServer();

requestAnimationFrame(() => window.scrollTo(0, 0));
window.addEventListener("load", () => {
  setTimeout(() => window.scrollTo(0, 0), 0);
  setTimeout(() => window.scrollTo(0, 0), 120);
});
