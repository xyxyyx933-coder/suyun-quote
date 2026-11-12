# 苏运算 · 广告标识外贸报价与运费核算

广告标识（发光字、千层镜等）出口业务的一体化报价工具：产品计价 → 国际运费核算 → 汇总报价单，三页打通。

## 下载

- **程序（免安装单文件）**：`dist/SuyunQuote.exe`
- 高速镜像：<https://cdn.jsdelivr.net/gh/xyxyyx933-coder/suyun-quote@main/dist/SuyunQuote.exe>
- GitHub 直链：<https://github.com/xyxyyx933-coder/suyun-quote/raw/main/dist/SuyunQuote.exe>

Windows 10/11，双击即用（依赖系统自带 WebView2 内核）。数据保存在 exe 同目录，升级时把旧 exe 换掉即可，数据文件不受影响。

## 功能

1. **产品报价**：按字 / 按米 / 按路径 / 按㎡ 计价；客户档案与标签；SVG/PDF 稿件自动量字；智能排箱估算包装尺寸重量；报价单出图、打印 PDF、导出 Excel。
2. **国际运费报价**：快递 / 空运 / 海运拼箱 / 整柜 / 专线 DDP 五路比价，含体积重、最低计费方、按票固定费、目的港杂费提示。
3. **汇总报价单**：产品成本 + 运费 = 对外总价，多币种，支持汇总记录与再次编辑。

## 自动更新

程序启动时会读取本仓库根目录的 `version.json`：

```json
{ "version": "1.22.2", "url": "下载地址", "notes": "更新说明" }
```

读取顺序为三路镜像自动回退（jsDelivr 主节点 → jsDelivr 备用 → GitHub 原生），任意一路可达即可。
发新版本只需：替换 `dist/SuyunQuote.exe`、把 `version.json` 里的 `version` 调高，再把程序内的 `data-version` 改成同一版本号重新打包。

## 目录

```
version.json          版本信息（自动更新用）
dist/SuyunQuote.exe   主程序
source/main.html      主程序界面（导航/运费/汇总）
source/quote.html     报价计算器界面（内嵌 iframe）
source/app.py         桌面宿主（pywebview + 本地数据读写 + 汇率）
```

## 说明

- 运价基准为 2026 年 11 月货代实单校准值，实际报价请以当期货代报价为准。
- 所有业务数据仅保存在本机 exe 同目录的 JSON 文件中，不上传任何服务器。
