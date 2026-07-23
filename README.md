# Adobe Full Rules

自动从 `ignaciocastro/a-dove-is-dumb` 拉取完整 Adobe 域名列表，并生成：

- `adobe-block.json`：Karing 使用的 sing-box JSON Rule Set
- `adobe-block.yaml`：Mihomo / OpenClash 使用的 classical YAML Rule Provider
- `adobe-block.txt`：Mihomo / OpenClash 可选 text Rule Provider
- `metadata.json`：生成时间、来源和域名数量

## 第一次使用

1. 本仓库已就绪：`asrtroh-netizen/OneBlock`（公开）。
2. 仓库根目录需包含本目录全部内容，含隐藏目录 `.github`。
3. 打开仓库的 **Actions** 页面。
4. 选择 **Update Adobe rules**，点击 **Run workflow**。
5. 等待运行完成，仓库根目录会自动出现四个生成文件。

## Karing 来源地址

仓库为 `asrtroh-netizen/OneBlock`：

```text
https://raw.githubusercontent.com/asrtroh-netizen/OneBlock/main/adobe-block.json
```

Karing 中给该自定义分流组选择 **拦截**。

## Mihomo / OpenClash

主 YAML 中加入：

```yaml
rule-providers:
  Adobe-Block:
    type: http
    behavior: classical
    format: yaml
    url: "https://raw.githubusercontent.com/asrtroh-netizen/OneBlock/main/adobe-block.yaml"
    path: ./rule_provider/adobe-block.yaml
    interval: 86400

rules:
  - RULE-SET,Adobe-Block,REJECT
```

`RULE-SET` 规则要放在 `MATCH` 等兜底规则前面。

## 自动更新

GitHub Actions 每天自动检查一次。只有上游域名列表发生变化时才会提交新文件。
