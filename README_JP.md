# ComfyUI LoRA Random Selector

カテゴリごとに登録されたLoRAファイルをランダムで選択し、対応するトリガーワードを自動で適用するComfyUIカスタムノードです。

## 機能

- **カテゴリベースLoRA管理**: LoRAファイルをカスタマイズ可能なカテゴリで整理
- **ランダム選択**: 指定されたカテゴリからLoRAファイルをランダムで選択
- **自動トリガーワード**: 選択されたLoRAに対応するトリガーワードを自動適用
- **ユーザー設定可能**: JSON設定でカテゴリ、LoRA、トリガーワードを簡単に編集
- **複数選択**: 一度に複数のLoRAを選択可能
- **柔軟な強度制御**: LoRA強度の上書きまたはデフォルト値使用
- **プロンプト統合**: トリガーワードをプロンプトにシームレスに統合

## インストール方法

1. **リポジトリをクローンまたはダウンロード**: ComfyUIのcustom nodesディレクトリに配置
   ```bash
   cd ComfyUI/custom_nodes/
   git clone https://github.com/your-username/comfyui-lora-random-selector.git
   ```

2. **ComfyUIを再起動**: 新しいカスタムノードを読み込み

3. **LoRAを設定**: 設定ファイルを編集（下記の設定セクションを参照）

## 設定方法

### LoRAの設定

1. **設定ファイルを編集**: `config/lora_config.json`をテキストエディタで開く
2. **カテゴリを追加**: LoRAコレクションに適したカテゴリを作成
3. **LoRAを追加**: 各LoRAについて、ファイルパス、デフォルト強度、トリガーワードを指定
4. **保存して再起動**: ファイルを保存し、ComfyUIを再起動して変更を適用

### 設定ファイルの構造

```json
{
  "categories": {
    "character": {
      "description": "キャラクター系LoRA",
      "loras": {
        "anime_girl_v1": {
          "file_path": "anime_girl_v1.safetensors",
          "strength_default": 0.8,
          "trigger_words": ["anime girl", "cute girl", "kawaii"],
          "tags": ["anime", "character", "girl"]
        }
      }
    }
  },
  "global_settings": {
    "max_trigger_words": 3,
    "default_strength": 0.7,
    "random_seed": null
  }
}
```

### ファイルパスの指定方法

- `ComfyUI/models/loras/`ディレクトリからの相対パスを使用
- 例: LoRAが`ComfyUI/models/loras/characters/my_character.safetensors`にある場合、`characters/my_character.safetensors`と指定
- 対応形式: `.safetensors`, `.ckpt`, `.pt`

## 使用方法

### 基本的な使い方

1. **ノードを追加**: ComfyUIで「LoRA Random Selector」ノードをワークフローに追加
2. **カテゴリを選択**: 使用したいLoRAが含まれるカテゴリを選択
3. **設定を調整**: LoRAの数、トリガーワード数、その他のパラメータを調整
4. **出力を接続**: ノードの出力を必要に応じてワークフローに接続

### ノードパラメータ

#### 必須入力
- **category**: 選択するLoRAカテゴリ
- **num_loras**: 選択するLoRAの数（1-5）
- **trigger_word_count**: LoRAあたりのトリガーワード数（0-5）
- **seed**: 再現可能な結果のためのランダムシード（-1でランダム）
- **enable_trigger_words**: 自動トリガーワード適用の有効/無効

#### オプション入力
- **strength_override**: デフォルトLoRA強度の上書き（-1でデフォルト値使用）
- **base_prompt**: トリガーワードと組み合わせるベースプロンプト

#### 出力
- **selected_lora_info**: 選択されたLoRAのJSON情報
- **lora_path**: 最初に選択されたLoRAのパス
- **lora_strength**: 最初のLoRAの強度値
- **trigger_words**: 結合されたトリガーワード（カンマ区切り）
- **combined_prompt**: ベースプロンプトとトリガーワードの結合
- **debug_info**: トラブルシューティング用デバッグ情報

### ワークフローの例

1. 「LoRA Random Selector」ノードを接続
2. カテゴリを「character」に設定
3. num_lorasを1に設定
4. trigger_word_countを2に設定
5. 「combined_prompt」出力をテキストエンコーダーに接続
6. 「lora_path」と「lora_strength」をLoRAローダーノードに接続

## 高度な設定

### 新しいカテゴリの追加

1. `config/lora_config.json`を開く
2. 「categories」セクションに新しいカテゴリを追加:
   ```json
   "my_category": {
     "description": "カスタムLoRAカテゴリ",
     "loras": {
       "my_lora": {
         "file_path": "path/to/my_lora.safetensors",
         "strength_default": 0.75,
         "trigger_words": ["マイトリガー", "カスタムスタイル"],
         "tags": ["カスタム", "スタイル"]
       }
     }
   }
   ```
3. ComfyUIを再起動

### グローバル設定

- **max_trigger_words**: 一度に選択する最大トリガーワード数
- **default_strength**: 指定がない場合のデフォルトLoRA強度
- **random_seed**: 一貫した結果のための固定シード（nullでランダム）
- **debug_mode**: トラブルシューティング用の追加ログを有効化
- **file_validation**: ファイル存在確認を有効化

## トラブルシューティング

### よくある問題

1. **ノードが表示されない**: インストール後にComfyUIを再起動
2. **LoRAが見つからない**: 設定ファイルのファイルパスを確認
3. **ファイルが見つからないエラー**: 指定されたパスにLoRAファイルが存在するかを確認
4. **JSONエラー**: 設定ファイルのJSON構文を検証

### デバッグ情報

ノードは「debug_info」出力を通じて詳細なデバッグ情報を提供します:
- 実行詳細（使用されたシード、選択されたLoRA数）
- ファイル検証結果
- 選択されたLoRAの詳細

### ログ出力

以下の詳細なログメッセージについて、ComfyUIコンソールを確認してください:
- 設定の読み込み
- LoRA選択プロセス
- ファイル検証結果
- エラーメッセージ

## ファイル構造

```
comfyui-lora-random-selector/
├── __init__.py                     # ノード登録
├── lora_random_selector.py         # メインノードクラス
├── config/
│   ├── lora_config.json           # メイン設定ファイル
│   └── config_template.json       # 設定テンプレート
├── utils/
│   ├── __init__.py
│   ├── config_manager.py          # 設定管理
│   └── lora_utils.py              # LoRAユーティリティ関数
├── examples/
│   └── sample_workflow.json       # サンプルワークフロー
├── README.md                       # 英語ドキュメント
└── README_JP.md                    # このファイル
```

## 設定例

### キャラクター系LoRAの設定例

```json
"character": {
  "description": "キャラクター系LoRA",
  "loras": {
    "sakura_character": {
      "file_path": "characters/sakura_v2.safetensors",
      "strength_default": 0.8,
      "trigger_words": [
        "sakura",
        "pink hair",
        "school uniform",
        "anime girl"
      ],
      "tags": ["character", "anime", "school"]
    }
  }
}
```

### スタイル系LoRAの設定例

```json
"style": {
  "description": "アートスタイル系LoRA",
  "loras": {
    "watercolor_style": {
      "file_path": "styles/watercolor.safetensors",
      "strength_default": 0.6,
      "trigger_words": [
        "水彩画",
        "watercolor",
        "淡い色調",
        "アート風"
      ],
      "tags": ["style", "watercolor", "art"]
    }
  }
}
```

## 貢献

貢献を歓迎します！問題報告、機能要求、プルリクエストをお気軽に送信してください。

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細はLICENSEファイルを参照してください。

## バージョン履歴

- **v1.0.0**: 基本的なLoRA選択とトリガーワード機能を含む初期リリース