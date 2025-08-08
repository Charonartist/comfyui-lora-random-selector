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
            config_path: 設定ファイルのパス（指定がない場合はデフォルトパスを使用）
        """
        if config_path is None:
            # デフォルトの設定ファイルパス
            current_dir = Path(__file__).parent.parent
            config_path = current_dir / "config" / "lora_config.json"
        
        self.config_path = Path(config_path)
        self.config_data: Dict[str, Any] = {}
        self.categories: List[str] = []
        
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
            if not self.config_path.exists():
                self.logger.warning(f"設定ファイルが見つかりません: {self.config_path}")
                self._create_default_config()
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            
            # カテゴリリストを更新
            self.categories = list(self.config_data.get('categories', {}).keys())
            
            # 設定ファイルの検証
            if not self._validate_config():
                self.logger.error("設定ファイルの形式が正しくありません")
                return False
            
            self.logger.info(f"設定ファイルを読み込みました: {len(self.categories)}個のカテゴリ")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON形式エラー: {e}")
            return False
        except Exception as e:
            self.logger.error(f"設定ファイル読み込みエラー: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """
        設定ファイルの形式を検証する
        
        Returns:
            bool: 検証成功時True
        """
        required_keys = ['categories', 'global_settings']
        
        for key in required_keys:
            if key not in self.config_data:
                self.logger.error(f"必須キーが見つかりません: {key}")
                return False
        
        # カテゴリの検証
        categories = self.config_data['categories']
        if not isinstance(categories, dict):
            self.logger.error("categories は辞書型である必要があります")
            return False
        
        for cat_name, cat_data in categories.items():
            if not isinstance(cat_data, dict) or 'loras' not in cat_data:
                self.logger.error(f"カテゴリ '{cat_name}' の形式が正しくありません")
                return False
            
            # LoRAデータの検証
            loras = cat_data['loras']
            if not isinstance(loras, dict):
                self.logger.error(f"カテゴリ '{cat_name}' の loras は辞書型である必要があります")
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
        if category not in self.config_data.get('categories', {}):
            self.logger.warning(f"存在しないカテゴリ: {category}")
            return {}
        
        return self.config_data['categories'][category]['loras']
    
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
        return self.config_data.get('global_settings', {})
    
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