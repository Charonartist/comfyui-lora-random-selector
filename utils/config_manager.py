"""
設定ファイル管理クラス
LoRA設定の読み込み、検証、管理を行う
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

class ConfigManager:
    """LoRA設定ファイルの管理クラス"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初期化
        
        Args:
            config_path: 設定ディレクトリのパス（指定がない場合はデフォルトパスを使用）
        """
        if config_path is None:
            # デフォルトの設定ディレクトリパス
            current_dir = Path(__file__).parent.parent
            config_path = current_dir / "config"
        
        self.config_dir = Path(config_path)
        self.lora_style_dir = self.config_dir / "lora_style"
        self.global_settings_path = self.config_dir / "global_settings.json"
        self.legacy_config_path = self.config_dir / "lora_config.json"  # 旧形式用
        
        self.global_settings: Dict[str, Any] = {}
        self.categories: List[str] = []
        self.category_cache: Dict[str, Dict[str, Any]] = {}
        
        # ログ設定
        self.logger = logging.getLogger(__name__)
        
        # 設定ファイルの読み込み
        self.reload_config()
    
    def reload_config(self) -> bool:
        """
        設定ファイルを再読み込みする
        
        Returns:
            bool: 読み込み成功時True
        """
        try:
            # マイグレーション処理（旧形式から新形式への移行）
            if self.legacy_config_path.exists() and not self.lora_style_dir.exists():
                self._migrate_legacy_config()
            
            # グローバル設定の読み込み
            if not self._load_global_settings():
                return False
            
            # カテゴリファイルの読み込み
            if not self._load_category_files():
                return False
            
            self.logger.info(f"設定ファイルを読み込みました: {len(self.categories)}個のカテゴリ")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON形式エラー: {e}")
            return False
        except Exception as e:
            self.logger.error(f"設定ファイル読み込みエラー: {e}")
            return False
    
    def _load_global_settings(self) -> bool:
        """
        グローバル設定ファイルを読み込む
        
        Returns:
            bool: 読み込み成功時True
        """
        if not self.global_settings_path.exists():
            self.logger.warning(f"グローバル設定ファイルが見つかりません: {self.global_settings_path}")
            self._create_default_global_settings()
            return True
        
        try:
            with open(self.global_settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.global_settings = data.get('global_settings', {})
            return True
        except Exception as e:
            self.logger.error(f"グローバル設定読み込みエラー: {e}")
            return False
    
    def _load_category_files(self) -> bool:
        """
        カテゴリファイルを読み込む
        
        Returns:
            bool: 読み込み成功時True
        """
        if not self.lora_style_dir.exists():
            self.logger.warning(f"lora_styleディレクトリが見つかりません: {self.lora_style_dir}")
            self._create_default_category_files()
            return True
        
        self.categories = []
        self.category_cache = {}
        
        # JSONファイルを検索してカテゴリとして登録
        for json_file in self.lora_style_dir.glob("*.json"):
            category_name = json_file.stem  # 拡張子を除いたファイル名
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    category_data = json.load(f)
                    
                # データ検証
                if self._validate_category_data(category_name, category_data):
                    self.categories.append(category_name)
                    self.category_cache[category_name] = category_data
                    self.logger.debug(f"カテゴリ '{category_name}' を読み込みました")
                else:
                    self.logger.warning(f"カテゴリ '{category_name}' のデータが無効です")
                    
            except Exception as e:
                self.logger.error(f"カテゴリファイル '{json_file}' の読み込みエラー: {e}")
        
        return len(self.categories) > 0
    
    def _validate_category_data(self, category_name: str, category_data: Dict[str, Any]) -> bool:
        """
        カテゴリデータの形式を検証する
        
        Args:
            category_name: カテゴリ名
            category_data: カテゴリデータ
            
        Returns:
            bool: 検証成功時True
        """
        if not isinstance(category_data, dict):
            self.logger.error(f"カテゴリ '{category_name}' のデータが辞書型ではありません")
            return False
        
        # 必須キーの確認
        if 'loras' not in category_data:
            self.logger.error(f"カテゴリ '{category_name}' に 'loras' キーが見つかりません")
            return False
        
        # LoRAデータの検証
        loras = category_data['loras']
        if not isinstance(loras, dict):
            self.logger.error(f"カテゴリ '{category_name}' の 'loras' が辞書型ではありません")
            return False
        
        for lora_name, lora_data in loras.items():
            if not self._validate_lora_data(lora_name, lora_data):
                return False
        
        return True
    
    def _validate_lora_data(self, lora_name: str, lora_data: Dict[str, Any]) -> bool:
        """
        個別のLoRAデータを検証する
        
        Args:
            lora_name: LoRA名
            lora_data: LoRAデータ
            
        Returns:
            bool: 検証成功時True
        """
        required_keys = ['file_path', 'strength_default', 'trigger_words']
        
        for key in required_keys:
            if key not in lora_data:
                self.logger.error(f"LoRA '{lora_name}' に必須キー '{key}' が見つかりません")
                return False
        
        # trigger_wordsがリスト型かチェック
        if not isinstance(lora_data['trigger_words'], list):
            self.logger.error(f"LoRA '{lora_name}' の trigger_words はリスト型である必要があります")
            return False
        
        # strength_defaultが数値かチェック
        if not isinstance(lora_data['strength_default'], (int, float)):
            self.logger.error(f"LoRA '{lora_name}' の strength_default は数値である必要があります")
            return False
        
        return True
    
    def _create_default_config(self):
        """デフォルト設定ファイルを作成する"""
        default_config = {
            "categories": {
                "character": {
                    "description": "キャラクター系LoRA",
                    "loras": {
                        "sample_character": {
                            "file_path": "models/loras/sample_character.safetensors",
                            "strength_default": 0.8,
                            "trigger_words": ["sample character", "anime girl"],
                            "tags": ["anime", "character", "girl"]
                        }
                    }
                },
                "style": {
                    "description": "スタイル系LoRA",
                    "loras": {
                        "sample_style": {
                            "file_path": "models/loras/sample_style.safetensors",
                            "strength_default": 0.6,
                            "trigger_words": ["artistic style", "painting"],
                            "tags": ["style", "art"]
                        }
                    }
                }
            },
            "global_settings": {
                "max_trigger_words": 3,
                "default_strength": 0.7,
                "random_seed": None
            }
        }
        
        try:
            # 設定ディレクトリを作成
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # デフォルト設定を保存
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"デフォルト設定ファイルを作成しました: {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"デフォルト設定ファイルの作成に失敗: {e}")
    
    def get_categories(self) -> List[str]:
        """
        利用可能なカテゴリリストを取得
        
        Returns:
            List[str]: カテゴリ名のリスト
        """
        return self.categories.copy()
    
    def get_category_loras(self, category: str) -> Dict[str, Dict[str, Any]]:
        """
        指定されたカテゴリのLoRA一覧を取得
        
        Args:
            category: カテゴリ名
            
        Returns:
            Dict: LoRA情報の辞書
        """
        if category not in self.category_cache:
            self.logger.warning(f"存在しないカテゴリ: {category}")
            return {}
        
        return self.category_cache[category].get('loras', {})
    
    def get_lora_info(self, category: str, lora_name: str) -> Optional[Dict[str, Any]]:
        """
        特定のLoRA情報を取得
        
        Args:
            category: カテゴリ名
            lora_name: LoRA名
            
        Returns:
            Optional[Dict]: LoRA情報、見つからない場合None
        """
        loras = self.get_category_loras(category)
        return loras.get(lora_name)
    
    def get_global_settings(self) -> Dict[str, Any]:
        """
        グローバル設定を取得
        
        Returns:
            Dict: グローバル設定
        """
        return self.global_settings
    
    def validate_file_exists(self, file_path: str) -> bool:
        """
        LoRAファイルの存在を確認
        
        Args:
            file_path: ファイルパス
            
        Returns:
            bool: ファイルが存在する場合True
        """
        # 相対パスの場合は絶対パスに変換
        if not os.path.isabs(file_path):
            # ComfyUIのmodelsディレクトリを想定
            comfyui_models_path = Path("models") / "loras"
            file_path = comfyui_models_path / file_path
        
        return Path(file_path).exists()
    
    def _create_default_global_settings(self):
        """デフォルトのグローバル設定ファイルを作成する"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # global_settings.jsonが既に存在する場合はスキップ
            if self.global_settings_path.exists():
                return
                
            default_global = {
                "global_settings": {
                    "max_trigger_words": 3,
                    "default_strength": 0.7,
                    "random_seed": None,
                    "debug_mode": False,
                    "file_validation": True
                }
            }
            
            with open(self.global_settings_path, 'w', encoding='utf-8') as f:
                json.dump(default_global, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"デフォルトグローバル設定を作成しました: {self.global_settings_path}")
            
        except Exception as e:
            self.logger.error(f"デフォルトグローバル設定の作成に失敗: {e}")
    
    def _create_default_category_files(self):
        """デフォルトのカテゴリファイルを作成する"""
        try:
            self.lora_style_dir.mkdir(parents=True, exist_ok=True)
            
            # character.json が既に存在する場合はスキップ
            character_path = self.lora_style_dir / "character.json"
            if character_path.exists():
                return
                
            default_character = {
                "category_info": {
                    "name": "character",
                    "description": "キャラクター系LoRA"
                },
                "loras": {
                    "sample_character": {
                        "file_path": "sample_character.safetensors",
                        "strength_default": 0.8,
                        "trigger_words": ["sample character", "anime girl"],
                        "tags": ["character", "sample"]
                    }
                }
            }
            
            with open(character_path, 'w', encoding='utf-8') as f:
                json.dump(default_character, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"デフォルトカテゴリファイルを作成しました: {character_path}")
            
        except Exception as e:
            self.logger.error(f"デフォルトカテゴリファイルの作成に失敗: {e}")
    
    def _migrate_legacy_config(self):
        """旧形式の設定ファイルを新形式に移行する"""
        try:
            if not self.legacy_config_path.exists():
                return
            
            self.logger.info("旧形式設定ファイルから新形式への移行を開始します")
            
            # 旧設定ファイルの読み込み
            with open(self.legacy_config_path, 'r', encoding='utf-8') as f:
                legacy_data = json.load(f)
            
            # ディレクトリ作成
            self.lora_style_dir.mkdir(parents=True, exist_ok=True)
            
            # グローバル設定を分離
            global_settings = legacy_data.get('global_settings', {})
            global_data = {"global_settings": global_settings}
            
            with open(self.global_settings_path, 'w', encoding='utf-8') as f:
                json.dump(global_data, f, ensure_ascii=False, indent=2)
            
            # カテゴリごとのファイルを作成
            categories = legacy_data.get('categories', {})
            for category_name, category_data in categories.items():
                category_file = self.lora_style_dir / f"{category_name}.json"
                
                new_category_data = {
                    "category_info": {
                        "name": category_name,
                        "description": category_data.get('description', f'{category_name}系LoRA')
                    },
                    "loras": category_data.get('loras', {})
                }
                
                with open(category_file, 'w', encoding='utf-8') as f:
                    json.dump(new_category_data, f, ensure_ascii=False, indent=2)
            
            # 旧ファイルをバックアップ用にリネーム
            backup_path = self.config_dir / "lora_config_backup.json"
            self.legacy_config_path.rename(backup_path)
            
            self.logger.info(f"移行完了: {len(categories)}個のカテゴリを移行しました")
            self.logger.info(f"旧設定ファイルは {backup_path} にバックアップされました")
            
        except Exception as e:
            self.logger.error(f"設定ファイルの移行に失敗: {e}")