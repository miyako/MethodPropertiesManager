# 用語集 / Glossary

Keep terminology consistent across `src/<target>.md` and `figures/*.<target>.txt`.
Change an entry here first, then search and replace in both places.

Style (ja): です・ます調. Half-width alphanumerics, no space between Japanese and Latin text (e.g. `4D.Vector型`).
Full-width `（）` and `：` in prose. Do not append English equivalents unless needed to disambiguate;
preserve code identifiers and quoted labels that must match the current UI.
Cover (editor-approved): Japanese title, then `Elliott Jensen（4D Inc. テクニカルサービスエンジニア）`;
omit the technical-note number from the Japanese cover only.

## 4D terms (from the official 4D Japanese documentation)

| English | 日本語 | Notes |
|---|---|---|
| entity / entity selection | エンティティ / エンティティセレクション | |
| datastore | データストア | |
| dataclass | データクラス | |
| attribute | 属性 | |
| computed attribute | 計算属性 | |
| collection | コレクション | |
| object | オブジェクト | |
| method | メソッド | |
| project method | プロジェクトメソッド | |
| function | 関数 | |
| class | クラス | |
| parameter | 引数 | |
| form | フォーム | |
| form object | フォームオブジェクト | |
| list box | リストボックス | |
| web area | Webエリア | |
| 4D Web Server | 4D Webサーバー | |
| worker | ワーカー | |
| process | プロセス | |
| query | クエリ | |
| formula | フォーミュラ | |
| component | コンポーネント | |

## Document-specific terms

| English | 日本語 | Notes |
|---|---|---|
| method property | メソッドプロパティ | 4DのUI表記に合わせ、一般的なpropertyは「プロパティ」とします。 |
| property / attribute | プロパティ / 属性 | 本文のpropertyとattributeを区別します。コマンド名や属性値は変更しません。 |
| Explorer | エクスプローラー | 4D 20.8：`ExplorerJA.xlf`、`Explorer`（ID 1）。 |
| Code Editor | メソッドエディター | 編集者指定の用語。本文全体で統一します。 |
| Method Properties | メソッドプロパティ | 4D 20.8：`ExplorerJA.xlf`、`Exp_MethodProperties`。原文の末尾の三点リーダーは画面に従います。 |
| Edit Properties... | プロパティを編集... | 4D 20.8：`ExplorerMenusJA.xlf`、`exploProperties`（ID 56、5、93、112）。本文では操作名として「プロパティを編集」と表記します。 |
| batch setting of attributes | 属性の一括設定 | 4D 20.8：`ExplorerMenusJA.xlf`、`exploBatch`（ID 57、94）の「属性の一括設定...」。ネイティブダイアログのタイトルはスクリーンショットの確認時に別途照合します。 |
| preemptive | プリエンプティブ | 4D公式用語。属性値`capable`、`incapable`、`indifferent`は変更しません。 |
| interpreted mode | インタープリターモード | 4D 20.8：`BuildAppJA.xlf`、`Build_App_Log_Interpreted`。コンパイル済みの実行モードと区別します。 |
| standalone | シングルユーザー版 | 編集者指定の用語。ローカルの4Dでの実行。 |
| Boolean | ブール型 | `True`と`False`は値として原文の表記を維持します。 |
| filter | フィルター | メソッド一覧の絞り込み条件。 |
| naming convention | 命名規則 | `Web`、`Web@`は例示文字列として変更しません。 |
| Execute / Execute Method | 実行 / メソッドを実行 | 4D 20.8：`ToolBarJA.xlf`の`TB_Execute`、`4DClientJA.xlf`の`common_STR#1029:1`と`:2`。 |
| Apply / Remove | 適用 / 解除 | 承認済みのデモUIローカライズで使用するボタン名。英語の元スクリーンショットは、日本語版の確認が終わるまで変更しません。 |
| capable / incapable / indifferent | capable / incapable / indifferent | プリエンプティブ属性の値。識別子として原文を維持します。 |
| Capable / Incapable / Indifferent | 実行可 / 実行不可 / 指定なし | デモのプリエンプティブ属性を設定するボタン。保存する属性値は`capable`、`incapable`、`indifferent`のままです。 |
| Any / Methods / Count | すべて / メソッド / メソッド数 | デモの一覧・フィルター用。内部の選択キーやメソッド名は翻訳しません。 |
| Invisible / Shared | 非表示 / 共有 | デモのプロパティ選択肢。4D本体のダイアログは、対応するリソースを別途確認します。 |
| Published Web / SOAP / WSDL / SQL | Web公開 / SOAP公開 / WSDL公開 / SQL公開 | デモのプロパティ選択肢。保存する属性名は変更しません。 |
| Executed on Server | サーバー上で実行 | デモのプロパティ選択肢。 |
| write-protected host database | 書き込み禁止のホストデータベース | `MPM_HostProtectedError`の警告で使用します。 |

## Proper nouns in examples

| English | 日本語 | Notes |
|---|---|---|
| Method Properties Manager | メソッドプロパティマネージャー | 編集者指定の邦題。タイトルと本文で統一します。原文のProperties Manager Component、Method Property Manager Componentもこの名前に統一します。コード識別子や未確認のUI文字列は変更しません。 |
| 4D / 4D Inc. | 4D / 4D Inc. | 製品名・会社名を維持します。 |
| Elliott Jensen | Elliott Jensen | 表紙の著者表記は「Elliott Jensen（4D Inc. テクニカルサービスエンジニア）」とします。 |
| Technical Note 24-12 | 表紙では省略 | 編集者の承認により日本語の表紙から省略します。英語原文と元のPDFは変更しません。 |
| Visual Studio Code | Visual Studio Code | 製品名を維持します。 |
| Components / .4dbase / .4dm | Components / .4dbase / .4dm | フォルダー名・拡張子を維持します。 |
| open_property_manager | open_property_manager | 実行するメソッドの識別子を維持します。 |
| METHOD GET ATTRIBUTE / METHOD SET ATTRIBUTE | METHOD GET ATTRIBUTE / METHOD SET ATTRIBUTE | コマンド表記は原文どおり。参照先は確認済みの現行日本語版`https://developer.4d.com/docs/ja/commands/method-get-attribute`と`https://developer.4d.com/docs/ja/commands/method-set-attribute`を使用します。 |
| Web / Web@ | Web / Web@ | 命名規則と検索条件の例を維持します。 |
