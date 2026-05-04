# gha-matrix-scout

`gha-matrix-scout` 可以从本地工作流文件预览静态 GitHub Actions matrix 作业组合。它帮助维护者在推送工作流变更前检查 matrix 展开结果。

## 功能

- 从本地克隆读取一个工作流 YAML 文件。
- 查找包含 `strategy.matrix` 映射的作业。
- 将静态列表形式的 matrix 轴展开为笛卡尔积。
- 通过精确的键值匹配应用静态 `exclude` 条目。
- 通过合并到匹配组合或添加新组合来应用静态 `include` 条目。
- 通过可重复使用的 `--job` 选项，将报告过滤到一个或多个精确作业名称。
- 输出可读文本，或输出带警告的确定性 JSON。
- 对不支持的动态 matrix 值给出警告，且不会连接 GitHub。

## 安装

克隆此仓库，并在仓库根目录中使用：

```bash
git clone https://github.com/codecat-ai/gha-matrix-scout.git
cd gha-matrix-scout
```

本项目不会发布到包注册表。请从本地克隆使用。

## 快速开始

对工作流文件运行 CLI 模块：

```bash
PYTHONPATH=src python -m gha_matrix_scout .github/workflows/ci.yml
```

输出适合自动化处理的 JSON：

```bash
PYTHONPATH=src python -m gha_matrix_scout .github/workflows/ci.yml --json
```

按精确作业名称只预览选定的 matrix 作业：

```bash
PYTHONPATH=src python -m gha_matrix_scout .github/workflows/ci.yml --job test --job build
```

## 示例

如果一个 matrix 包含两个操作系统、两个 Python 版本，并排除了其中一组组合，文本报告会列出工作流路径、每个 matrix 作业、最终组合数量以及每个生成的组合。

```text
Workflow: .github/workflows/ci.yml

Job: test
Combinations: 3
1. os=ubuntu-latest, python=3.11
2. os=ubuntu-latest, python=3.12
3. os=windows-latest, python=3.12
```

## 配置

不需要网络访问、GitHub 凭据，也不会执行工作流。此工具只支持静态 YAML 值：

- Matrix 轴必须是列表。
- `exclude` 和 `include` 必须是映射列表。
- 动态表达式会被跳过，并产生警告。
- `--job NAME` 会按工作流作业名称进行精确过滤，并且可以重复使用。
- 如果 `--job` 过滤器没有匹配到 matrix 作业，CLI 会以非零状态退出。文本模式输出错误；JSON 模式输出包含该警告的有效报告。

## 开发

源码包位于 `src/gha_matrix_scout/`。行为测试位于 `tests/`。

在仓库根目录运行行为测试：

```bash
PYTHONPATH=src python -m pytest -q
```

运行格式和 lint 检查：

```bash
ruff check .
ruff format --check .
```

## 测试

测试关注可观察行为：matrix 展开、include/exclude 处理、不支持的值、作业过滤、文本输出、JSON 输出以及 CLI 错误。

## 路线图

- 为格式错误的工作流提供更多 YAML 诊断。
- 为评审评论提供更丰富的摘要格式。
- 增加 matrix 定义的静态兼容性检查。

## 贡献

请参阅 `CONTRIBUTING.md`。行为变更需要测试覆盖，并保持英文、中文和日文 README 的含义同步。

## AI 辅助维护

AI 工具可以协助起草代码、测试和文档，但维护者必须在合并前审查所有变更的正确性、原创性、许可和安全性。

## 许可证

MIT。见 `LICENSE`。
