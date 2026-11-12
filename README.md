# 苏运算 · 广告标识外贸报价与运费核算

广告标识（发光字、千层镜等）出口业务的一体化报价工具：产品计价 → 国际运费核算 → 汇总报价单，三页打通。

## 下载

Windows 10/11 免安装单文件，双击即用（依赖系统自带 WebView2 内核）。

| 线路 | 链接 |
|---|---|
| 线路 1（推荐） | https://ghfast.top/https://github.com/xyxyyx933-coder/suyun-quote/releases/download/v1.22.2/SuyunQuote.exe |
| 线路 2 | https://gh-proxy.com/https://github.com/xyxyyx933-coder/suyun-quote/releases/download/v1.22.2/SuyunQuote.exe |
| 线路 3 | https://ghproxy.net/https://github.com/xyxyyx933-coder/suyun-quote/releases/download/v1.22.2/SuyunQuote.exe |
| GitHub 原生 | https://github.com/xyxyyx933-coder/suyun-quote/releases/download/v1.22.2/SuyunQuote.exe |

国内网络访问 github.com 常被阻断，因此推荐前三条镜像线路。仓库内 `dist/SuyunQuote.exe` 是同一份程序的备份副本。

升级方式：下载新 exe，替换掉旧 exe 即可。业务数据存在 exe 同目录的 JSON 文件里，不受影响。

## 功能

1. **产品报价**：按字 / 按米 / 按路径 / 按㎡ 计价；客户档案与标签；SVG/PDF 稿件自动量字；智能排箱估算包装尺寸重量；报价单出图、打印 PDF、导出 Excel。
2. **国际运费报价**：快递 / 空运 / 海运拼箱 / 整柜 / 专线 DDP 五路比价，含体积重、最低计费方、按票固定费、目的港杂费提示。
3. **汇总报价单**：产品成本 + 运费 = 对外总价，多币种，支持汇总记录与再次编辑。

## 自动更新

程序启动时读取本仓库根目录的 `version.json`：

```json
{
  "version": "1.22.2",
  "url": "主下载地址",
  "mirrors": ["备用地址1", "备用地址2"],
  "notes": "更新说明"
}
```

版本源按三路镜像自动回退读取：jsDelivr 主节点 → jsDelivr 备用节点 → GitHub 原生，任意一路可达即可。发现新版本时顶部弹出提示条，「下载更新」走主地址，下载不动可点「备用线路」依次切换。

发新版本流程：
1. 把 `data-version` 改成新版本号，重新打包；
2. 新建 Release 并上传 exe（文件名建议保持 `SuyunQuote.exe`）；
3. 更新 `version.json` 的 `version` / `url` / `mirrors`；
4. 到 <https://purge.jsdelivr.net/gh/xyxyyx933-coder/suyun-quote@main/version.json> 刷新镜像缓存（约 1 分钟生效）。

## 目录

```
version.json          版本信息（自动更新用）
dist/SuyunQuote.exe   主程序备份副本
source/main.html      主程序界面（导航 / 运费 / 汇总）
source/quote.html     报价计算器界面（内嵌 iframe）
source/app.py         桌面宿主（pywebview + 本地数据读写 + 汇率）
```

## 说明

- 运价基准为 2026 年 11 月货代实单校准值，实际报价请以当期货代报价为准。
- 所有业务数据仅保存在本机 exe 同目录的 JSON 文件中，不上传任何服务器。
