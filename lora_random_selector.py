"""
ComfyUI LoRA Random Selector Custom Node
カテゴリベースでLoRAをランダム選択し、トリガーワードを自動適用する
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from .utils.config_manager import ConfigManager
    from .utils.lora_utils import LoRASelector, PromptBuilder
except ImportError:
    # スタンドアローン実行時
    from utils.config_manager import ConfigManager
    from utils.lora_utils import LoRASelector, PromptBuilder

class LoRARandomSelector:
    """ComfyUI用LoRAランダム選択カスタムノード"""
    
    def __init__(self):
        """初期化"""
        self.config_manager = ConfigManager()
        self.lora_selector = LoRASelector()
        self.prompt_builder = PromptBuilder()
        
        # ログ設定
        self.logger = logging.getLogger(__name__)
        
    @classmethod
    def INPUT_TYPES(cls):
        """入力パラメータの定義"""
        # 設定ファイルからカテゴリリストを動的に取得
        try:
            temp_config = ConfigManager()
            categories = temp_config.get_categories()
            if not categories:
                categories = ["default"]
        except Exception as e:
            categories = ["default"]
            print(f"カテゴリ読み込みエラー: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"[LoRARandomSelector] 検出されたカテゴリ: {categories}")
        
        return {
            "required": {
                "category": (categories, {
                    "default": categories[0] if categories else "default"
                }),
                "num_loras": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 5,
                    "step": 1,
                    "display": "number"
                }),
                "trigger_word_count": ("INT", {
                    "default": 100,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "display": "number"
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2**32 - 1,
                    "step": 1,
                    "display": "number"
                }),
                "enable_trigger_words": ("BOOLEAN", {
                    "default": True
                }),
            },
            "optional": {
                "strength_override": ("FLOAT", {
                    "default": -1.0,
                    "min": -1.0,
                    "max": 2.0,
                    "step": 0.1,
                    "display": "number"
                }),
                "base_prompt": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "FLOAT", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "selected_lora_info", 
        "lora_path", 
        "lora_strength", 
        "trigger_words", 
        "combined_prompt",
        "debug_info"
    )
    
    FUNCTION = "select_random_lora"
    CATEGORY = "LoRA"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """設定ファイルの変更を検出してUIを更新"""
        try:
            config = ConfigManager()
            # カテゴリファイルの最終更新時刻をチェック
            if config.lora_style_dir.exists():
                import os
                max_mtime = 0
                for json_file in config.lora_style_dir.glob("*.json"):
                    mtime = os.path.getmtime(json_file)
                    max_mtime = max(max_mtime, mtime)
                return str(max_mtime)
        except Exception:
            pass
        return "0"
    
    def select_random_lora(
        self, 
        category: str,
        num_loras: int = 1,
        trigger_word_count: int = 1,
        seed: int = -1,
        enable_trigger_words: bool = True,
        strength_override: float = -1.0,
        base_prompt: str = ""
    ) -> Tuple[str, str, float, str, str, str]:
        """
        LoRAをランダムに選択し、トリガーワードを適用する
        
        Args:
            category: 選択するカテゴリ
            num_loras: 選択するLoRAの数
            trigger_word_count: 適用するトリガーワード数
            seed: ランダムシード（-1の場合はランダム）
            enable_trigger_words: トリガーワード適用の有効/無効
            strength_override: LoRA強度の上書き値（-1の場合はデフォルト値を使用）
            base_prompt: ベースプロンプト
            
        Returns:
            Tuple: (選択されたLoRA情報, LoRAパス, LoRA強度, トリガーワード, 結合プロンプト, デバッグ情報)
        """
        try:
            # 設定ファイルの再読み込み
            self.config_manager.reload_config()
            
            # カテゴリのLoRA一覧を取得
            loras = self.config_manager.get_category_loras(category)
            if not loras:
                error_msg = f"カテゴリ '{category}' にLoRAが見つかりません"
                self.logger.error(error_msg)
                return self._create_error_response(error_msg)
            
            # シード値の処理
            actual_seed = None if seed < 0 else seed
            
            # LoRAをランダム選択
            selected_loras = self.lora_selector.select_random_lora(
                loras, 
                count=num_loras, 
                seed=actual_seed
            )
            
            if not selected_loras:
                error_msg = "LoRAの選択に失敗しました"
                self.logger.error(error_msg)
                return self._create_error_response(error_msg)
            
            # LoRA強度の計算
            strength_override_value = strength_override if strength_override > 0 else None
            strengths = self.lora_selector.calculate_weighted_strength(
                selected_loras, 
                strength_override_value
            )
            
            # トリガーワードの選択
            trigger_words_list = []
            if enable_trigger_words and trigger_word_count > 0:
                for lora_name, lora_info in selected_loras:
                    words = self.lora_selector.select_trigger_words(
                        lora_info, 
                        count=trigger_word_count,
                        seed=actual_seed
                    )
                    trigger_words_list.append(words)
            else:
                trigger_words_list = [[] for _ in selected_loras]
            
            # LoRA情報のフォーマット
            formatted_info = self.lora_selector.format_lora_info(
                selected_loras, 
                strengths, 
                trigger_words_list
            )
            
            # ファイルパスの検証
            validation_results = self.lora_selector.validate_lora_paths(selected_loras)
            
            # 出力値の準備
            selected_lora_info = json.dumps(formatted_info, ensure_ascii=False, indent=2)
            # LoRAファイル名のみを取得（ComfyUIローダー用）
            lora_path = self._get_lora_name_for_loader(selected_loras[0]) if selected_loras else ''
            lora_strength = strengths[0] if strengths else 0.7
            trigger_words = formatted_info.get('all_trigger_words', '')
            
            # 結合プロンプトの作成
            combined_prompt = self.prompt_builder.build_combined_prompt(
                base_prompt, 
                trigger_words, 
                position="beginning"
            )
            combined_prompt = self.prompt_builder.clean_prompt(combined_prompt)
            
            # デバッグ情報の作成
            debug_info = self._create_debug_info(
                selected_loras, 
                strengths, 
                trigger_words_list, 
                validation_results,
                actual_seed
            )
            
            self.logger.info(f"LoRA選択完了: {len(selected_loras)}個のLoRAを選択")
            
            return (
                selected_lora_info,
                lora_path,
                lora_strength,
                trigger_words,
                combined_prompt,
                debug_info
            )
            
        except Exception as e:
            error_msg = f"LoRA選択中にエラーが発生: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return self._create_error_response(error_msg)
    
    def _get_lora_name_for_loader(self, selected_lora: Tuple[str, Dict[str, Any]]) -> str:
        """
        ComfyUIローダー用のLoRAパスを取得
        ファイルパスをそのまま返す（拡張子あり）
        
        Args:
            selected_lora: (LoRA名, LoRA情報)のタプル
            
        Returns:
            str: ComfyUIローダー用のLoRAパス
        """
        lora_name, lora_info = selected_lora
        file_path = lora_info.get('file_path', '')
        
        # ファイルパスがある場合はそのまま返す、なければLoRA名を返す
        return file_path if file_path else lora_name
    
    def _create_error_response(self, error_msg: str) -> Tuple[str, str, float, str, str, str]:
        """
        エラー時のレスポンスを作成
        
        Args:
            error_msg: エラーメッセージ
            
        Returns:
            Tuple: エラー情報を含むレスポンス
        """
        error_info = {
            "error": True,
            "message": error_msg,
            "selected_count": 0,
            "loras": []
        }
        
        return (
            json.dumps(error_info, ensure_ascii=False, indent=2),  # selected_lora_info
            "",           # lora_path
            0.7,          # lora_strength
            "",           # trigger_words
            error_msg,    # combined_prompt
            error_msg     # debug_info
        )
    
    def _create_debug_info(
        self, 
        selected_loras: List[Tuple[str, Dict[str, Any]]], 
        strengths: List[float],
        trigger_words_list: List[List[str]],
        validation_results: List[bool],
        seed: int
    ) -> str:
        """
        デバッグ情報を作成
        
        Args:
            selected_loras: 選択されたLoRAのリスト
            strengths: 各LoRAの強度リスト
            trigger_words_list: 各LoRAのトリガーワードリスト
            validation_results: ファイル存在確認結果
            seed: 使用されたシード値
            
        Returns:
            str: デバッグ情報（JSON文字列）
        """
        debug_data = {
            "execution_info": {
                "seed_used": seed,
                "loras_selected": len(selected_loras),
                "timestamp": str(Path(__file__).stat().st_mtime)
            },
            "file_validation": {},
            "details": []
        }
        
        for i, ((lora_name, lora_info), strength, words, is_valid) in enumerate(
            zip(selected_loras, strengths, trigger_words_list, validation_results)
        ):
            file_path = lora_info.get('file_path', '')
            debug_data["file_validation"][lora_name] = {
                "path": file_path,
                "exists": is_valid
            }
            
            debug_data["details"].append({
                "index": i,
                "name": lora_name,
                "strength": strength,
                "trigger_words": words,
                "file_exists": is_valid
            })
        
        return json.dumps(debug_data, ensure_ascii=False, indent=2)

# ノードクラスマッピング用の辞書
NODE_CLASS_MAPPINGS = {
    "LoRARandomSelector": LoRARandomSelector
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoRARandomSelector": "LoRA Random Selector"
}