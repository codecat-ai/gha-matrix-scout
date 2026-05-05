# gha-matrix-scout

[English](README.md) | [中文](README-zh.md) | [日本語](README-ja.md)


`gha-matrix-scout` は、ローカルのワークフローファイルから静的な GitHub Actions matrix ジョブの組み合わせをプレビューします。メンテナーがワークフロー変更を push する前に matrix の展開結果を確認するためのツールです。

## 機能

- ローカルクローン内の 1 つのワークフロー YAML ファイルを読み込みます。
- `strategy.matrix` マッピングを持つジョブを探します。
- 静的なリスト値の matrix 軸を直積に展開します。
- 完全なキー/値一致で静的な `exclude` エントリを適用します。
- 一致する組み合わせへのマージ、または新しい組み合わせの追加として静的な `include` エントリを適用します。
- 繰り返し指定できる `--job` オプションで、1 つ以上の完全一致したジョブ名にレポートを絞り込みます。
- `--max-combinations N` で CI 用のガードレールを設定し、報告対象の matrix ジョブが正の上限を超えて展開された場合に失敗します。
- 読みやすいテキスト、CI ログ向けの簡潔なサマリーテキスト、または警告付きの決定的な JSON を出力します。
- 未対応の動的 matrix 値には警告を出し、GitHub には接続しません。

## インストール

このリポジトリをクローンし、リポジトリのルートで使用します。

```bash
git clone https://github.com/codecat-ai/gha-matrix-scout.git
cd gha-matrix-scout
```

このプロジェクトはパッケージレジストリには公開されていません。ローカルクローンから使用してください。

## クイックスタート

ワークフローファイルに対して CLI モジュールを実行します。

```bash
PYTHONPATH=src python -m gha_matrix_scout .github/workflows/ci.yml
```

自動化向けに JSON を出力します。

```bash
PYTHONPATH=src python -m gha_matrix_scout .github/workflows/ci.yml --json
```

CI ログ向けに、ジョブごとに 1 行の簡潔な出力を表示します。

```bash
PYTHONPATH=src python -m gha_matrix_scout .github/workflows/ci.yml --summary
```

完全一致のジョブ名で、選択した matrix ジョブだけをプレビューします。

```bash
PYTHONPATH=src python -m gha_matrix_scout .github/workflows/ci.yml --job test --job build
```

報告対象の matrix ジョブが指定した上限を超えて展開された場合にコマンドを失敗させます。

```bash
PYTHONPATH=src python -m gha_matrix_scout .github/workflows/ci.yml --max-combinations 20
```

## 例

2 つの OS と 2 つの Python バージョンを持ち、そのうち 1 組を除外する matrix の場合、テキストレポートにはワークフローパス、各 matrix ジョブ、最終的な組み合わせ数、生成された各組み合わせが表示されます。

```text
Workflow: .github/workflows/ci.yml

Job: test
Combinations: 3
1. os=ubuntu-latest, python=3.11
2. os=ubuntu-latest, python=3.12
3. os=windows-latest, python=3.12
```

`--summary` を使うと、同じ報告対象ジョブは組み合わせ数に圧縮されます。

```text
test: 3 combinations
```

## 設定

ネットワークアクセス、GitHub 認証情報、ワークフロー実行は不要です。この scout は静的な YAML 値のみをサポートします。

- Matrix 軸はリストである必要があります。
- `exclude` と `include` はマッピングのリストである必要があります。
- 動的式はスキップされ、警告が出ます。
- `--job NAME` はワークフローのジョブ名を完全一致で絞り込み、繰り返し指定できます。
- `--summary` は、報告対象の matrix ジョブごとに `<job-name>: <count> combination(s)` 形式で 1 行を出力します。数がちょうど 1 の場合は `combination` を使います。
- `--max-combinations N` は正の整数を受け取ります。通常の分析と `--job` フィルターの適用後、報告対象の matrix ジョブの展開組み合わせ数が `N` を超えている場合、CLI はステータス 1 で終了します。
- テキストモードとサマリーモードでは警告が見える状態に保たれます。JSON モードでは有効な JSON を保ち、警告メッセージをトップレベルの `warnings` リストに追加します。
- `--json` を使う場合、`--summary` は無視され、JSON の形は変わりません。
- `--job` フィルターが matrix ジョブに一致しない場合、CLI は非ゼロで終了します。テキストモードではエラーを出力し、JSON モードではその警告を含む有効なレポートを出力します。

## 開発

ソースパッケージは `src/gha_matrix_scout/` にあります。振る舞いのテストは `tests/` にあります。

リポジトリのルートで振る舞いのテストを実行します。

```bash
PYTHONPATH=src python -m pytest -q
```

フォーマットと lint のチェックを実行します。

```bash
ruff check .
ruff format --check .
```

## テスト

テストは観測可能な振る舞いに集中しています。matrix 展開、include/exclude 処理、未対応値、ジョブの絞り込み、最大組み合わせ数のガードレール、テキスト出力、サマリー出力、JSON 出力、CLI エラーを扱います。

## ロードマップ

- 不正なワークフローに対する YAML 診断を増やす。
- レビューコメント向けのより豊富なサマリー形式。
- matrix 定義に対する追加の静的互換性チェック。

## コントリビュート

`CONTRIBUTING.md` を参照してください。振る舞いの変更にはテストを追加し、英語、中国語、日本語の README の意味を同期してください。

## AI 支援メンテナンス

AI ツールはコード、テスト、ドキュメントの下書きを支援できますが、メンテナーはマージ前にすべての変更の正確性、独自性、ライセンス、安全性を確認する必要があります。

## ライセンス

MIT。`LICENSE` を参照してください。
