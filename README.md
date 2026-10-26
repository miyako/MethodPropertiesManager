# メソッドプロパティマネージャー

**Method Properties Manager**の日本語版です。

メソッドプロパティマネージャーは、4Dのメソッドをプロパティで絞り込み、選択した複数のメソッドの属性をまとめて変更するコンポーネントです。このテクニカルノートでは、4D標準のプロパティ編集機能と属性の一括設定の制約を説明し、コンポーネントの導入方法と使い方を紹介します。付属の4Dプロジェクトには、日本語・英語の画面リソースを収録しています。

## ダウンロード

| 内容 | ファイル |
|---|---|
| 日本語PDF | [24-12_MethodPropertiesManager_ja.pdf](https://github.com/miyako/MethodPropertiesManager/releases/latest/download/24-12_MethodPropertiesManager_ja.pdf) |
| 4Dデモプロジェクト | [MethodPropertiesManager.zip](https://github.com/miyako/MethodPropertiesManager/releases/latest/download/MethodPropertiesManager.zip) |
| 英語原文 | [24-12_MethodPropertiesManager.pdf](document/24-12_MethodPropertiesManager.pdf) |

公開済みのバージョンは[Releases](https://github.com/miyako/MethodPropertiesManager/releases)から確認できます。

## デモ

プロジェクトの互換バージョンは4D 20.3（`2003`）です。書き込み可能なホストプロジェクトを、シングルユーザー版4Dのインタープリターモードで開いて使用します。

ZIPを展開し、`MethodPropertiesManager/Project/MethodPropertiesManager.4DProject`を開きます。リポジトリ内のプロジェクトは`demo/MethodPropertiesManager/`にあります。

メソッド実行ダイアログから`open_property_manager`を実行すると、メソッドプロパティマネージャーが開きます。自動起動は行いません。再実行すると既存のウィンドウを前面に表示します。「閉じる」はウィンドウを閉じる操作であり、4D自体は終了しません。

コンポーネントとして使用する場合は、展開したフォルダーを`MethodPropertiesManager.4dbase`に変更して、ホストプロジェクトの`Components/`フォルダーに配置します。ホストから同じ公開メソッド`open_property_manager`を呼び出してください。ホストのメニューバーは変更しません。

画面の言語は4Dのローカライズ設定に従います。英語・日本語のリソースは`Resources/en.lproj/`と`Resources/ja.lproj/`にあります。開発時に日本語を明示的に選択する場合は、次のコードを実行します。

```4d
SET DATABASE LOCALIZATION("ja"; *)
open_property_manager
```

詳しくは[ローカライズと開発時の確認](demo/MethodPropertiesManager/Documentation/localisation.md)を参照してください。この説明はZIP内の`Documentation/localisation.md`にも収録しています。

## 原文との主な違い

- 本文と画面ラベルを日本語化しています。図版の一部には、日本語版4Dの実際の画面キャプチャを使用しています。
- デモの画面と警告メッセージを英語・日本語のXLIFFリソースに分離しています。
- 起動メソッドは処理をブロックしないウィンドウを開き、再実行時に同じウィンドウを再利用します。
- メソッド名、プロパティの内部キー・属性値は翻訳していません。デモデータの日本向け置き換えも行っていません。

## 編集と再ビルド

PDFは原文PDFを直接変更せず、Markdownと図版から生成します。

| ファイル | 内容 |
|---|---|
| `src/en.md` | 抽出・確認済みの英語本文 |
| `src/ja.md` | 日本語本文。プログラムコードは英語版と一致させます。 |
| `figures/fig-NN-ja.png` | 確認済みの日本語図版 |
| `figures/fig-NN.ja.txt` | 対応ファイルがある図のラベル。英語ラベルと行を対応させます。 |
| `figures/layout/fig-NN.json` | 図の配置と置き換え画像の指定 |
| `figures/localisation/` | スクリーンショットのリソース対応、フォント、マスク、ネイティブキャプチャの記録 |
| `glossary.md` | 用語集 |

```sh
git submodule update --init .agents
make setup
make                 # 本文・図版を確認し、日本語PDFを生成
make check           # コードと図の参照を照合
make review          # 原図と日本語図版のコンタクトシートを生成
make release-assets  # PDFとコミット済みデモのZIPを生成
```

出力先は`build/`です。`make release-assets`のZIPには、`demo/MethodPropertiesManager/`の**コミット済みファイルだけ**が入ります。

スクリーンショットは汎用のラベル描画ではなく、`"replace"`で確認済み画像を使用しています。ラベルファイルの変更だけでは置き換え画像は再生成されません。再現・照合の手順は[パイプラインの説明](.github/instructions/technote-translation.instructions.md#screenshots)を参照してください。

ビルドにはPython 3.10以降、Google ChromeまたはChromium、日本語フォントが必要です。Tesseractは原文の再抽出時のみ使用します。macOSではヒラギノ、LinuxではNoto CJKを使用するため、PDF本文の組版には差が出る場合があります。詳細なワークフローは[ローカライズ用テンプレート](https://github.com/miyako/4d-technote-localisation-template)を参照してください。

## 原文

**Method Properties Manager** — Elliott Jensen（4D Inc. テクニカルサービスエンジニア）
