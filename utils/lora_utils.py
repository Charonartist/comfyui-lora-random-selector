"""
LoRA関連のユーティリティ関数
ランダム選択、トリガーワード処理など
"""

import random
from typing import Dict, List, Any, Tuple, Optional
import logging

class LoRASelector:
    """LoRAの選択とトリガーワード処理を行うクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def select_random_lora(
        self, 
        loras: Dict[str, Dict[str, Any]], 
        count: int = 1,
        seed: Optional[int] = None
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        LoRAをランダムに選択する
        
        Args:
            loras: LoRA情報の辞書
            count: 選択するLoRAの数
            seed: ランダムシード
            
        Returns:
            List[Tuple[str, Dict]]: (LoRA名, LoRA情報)のタプルのリスト
        """
        if not loras:
            self.logger.warning("選択可能なLoRAがありません")
            return []
        
        # シード設定
        if seed is not None and seed >= 0:
            random.seed(seed)
        
        # 利用可能なLoRAリスト
        available_loras = list(loras.items())
        
        # 選択数を調整
        actual_count = min(count, len(available_loras))
        
        if actual_count == 0:
            return []
        
        # ランダム選択
        if actual_count == len(available_loras):
            selected = available_loras
        else:
            selected = random.sample(available_loras, actual_count)
        
        self.logger.info(f"{len(selected)}個のLoRAを選択しました")
        return selected
    
    def select_trigger_words(
        self, 
        lora_info: Dict[str, Any], 
        count: int = 1,
        seed: Optional[int] = None
    ) -> List[str]:
        """
        LoRAからトリガーワードをランダムに選択する
        
        Args:
            lora_info: LoRA情報
            count: 選択するトリガーワード数
            seed: ランダムシード
            
        Returns:
            List[str]: 選択されたトリガーワードのリスト
        """
        trigger_words = lora_info.get('trigger_words', [])
        
        if not trigger_words:
            self.logger.warning("トリガーワードが設定されていません")
            return []
        
        # シード設定
        if seed is not None and seed >= 0:
            random.seed(seed)
        
        # 選択数を調整
        actual_count = min(count, len(trigger_words))
        
        if actual_count == 0:
            return []
        
        # ランダム選択
        if actual_count == len(trigger_words):
            selected = trigger_words.copy()
        else:
            selected = random.sample(trigger_words, actual_count)
        
        return selected
    
    def combine_trigger_words(self, words_list: List[List[str]]) -> str:
        """
        複数のLoRAのトリガーワードを結合する
        
        Args:
            words_list: LoRAごとのトリガーワードリストのリスト
            
        Returns:
            str: カンマ区切りで結合されたトリガーワード
        """
        all_words = []
        for words in words_list:
            all_words.extend(words)
        
        # 重複を削除しつつ順序を保持
        unique_words = list(dict.fromkeys(all_words))
        
        return ", ".join(unique_words)
    
    def calculate_weighted_strength(
        self, 
        selected_loras: List[Tuple[str, Dict[str, Any]]], 
        strength_override: Optional[float] = None
    ) -> List[float]:
        """
        選択されたLoRAの強度を計算する
        
        Args:
            selected_loras: 選択されたLoRAのリスト
            strength_override: 強度の上書き値
            
        Returns:
            List[float]: 各LoRAの強度リスト
        """
        strengths = []
        
        for lora_name, lora_info in selected_loras:
            if strength_override is not None and strength_override > 0:
                # 上書き値を使用
                strength = strength_override
            else:
                # デフォルト値を使用
                strength = lora_info.get('strength_default', 0.7)
            
            # 強度の範囲チェック（0.1～2.0）
            strength = max(0.1, min(2.0, strength))
            strengths.append(strength)
        
        return strengths
    
    def format_lora_info(
        self, 
        selected_loras: List[Tuple[str, Dict[str, Any]]], 
        strengths: List[float],
        trigger_words_list: List[List[str]]
    ) -> Dict[str, Any]:
        """
        選択されたLoRA情報をフォーマットする
        
        Args:
            selected_loras: 選択されたLoRAのリスト
            strengths: 各LoRAの強度リスト
            trigger_words_list: 各LoRAのトリガーワードリスト
            
        Returns:
            Dict: フォーマットされたLoRA情報
        """
        formatted_info = {
            "selected_count": len(selected_loras),
            "loras": [],
            "combined_strength": 0.0,
            "all_trigger_words": self.combine_trigger_words(trigger_words_list)
        }
        
        total_strength = 0.0
        
        for i, ((lora_name, lora_info), strength) in enumerate(zip(selected_loras, strengths)):
            lora_detail = {
                "name": lora_name,
                "file_path": lora_info.get('file_path', ''),
                "strength": strength,
                "trigger_words": trigger_words_list[i] if i < len(trigger_words_list) else [],
                "tags": lora_info.get('tags', [])
            }
            
            formatted_info["loras"].append(lora_detail)
            total_strength += strength
        
        # 平均強度を計算
        if len(selected_loras) > 0:
            formatted_info["combined_strength"] = total_strength / len(selected_loras)
        
        return formatted_info
    
    def validate_lora_paths(self, selected_loras: List[Tuple[str, Dict[str, Any]]]) -> List[bool]:
        """
        選択されたLoRAファイルのパスを検証する
        
        Args:
            selected_loras: 選択されたLoRAのリスト
            
        Returns:
            List[bool]: 各LoRAファイルの存在チェック結果
        """
        from pathlib import Path
        import os
        
        validation_results = []
        
        for lora_name, lora_info in selected_loras:
            file_path = lora_info.get('file_path', '')
            
            # 相対パスの場合は絶対パスに変換
            if not os.path.isabs(file_path):
                # ComfyUIのmodelsディレクトリを想定
                comfyui_models_path = Path("models") / "loras"
                full_path = comfyui_models_path / file_path
            else:
                full_path = Path(file_path)
            
            exists = full_path.exists()
            validation_results.append(exists)
            
            if not exists:
                self.logger.warning(f"LoRAファイルが見つかりません: {full_path}")
            else:
                self.logger.debug(f"LoRAファイル確認OK: {full_path}")
        
        return validation_results

class PromptBuilder:
    """プロンプト構築用ユーティリティクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def build_combined_prompt(
        self, 
        base_prompt: str, 
        trigger_words: str, 
        position: str = "beginning"
    ) -> str:
        """
        ベースプロンプトにトリガーワードを組み合わせる
        
        Args:
            base_prompt: ベースとなるプロンプト
            trigger_words: トリガーワード（カンマ区切り）
            position: トリガーワードの位置（"beginning", "end", "both"）
            
        Returns:
            str: 結合されたプロンプト
        """
        if not trigger_words.strip():
            return base_prompt
        
        base_prompt = base_prompt.strip()
        trigger_words = trigger_words.strip()
        
        if position == "beginning":
            if base_prompt:
                return f"{trigger_words}, {base_prompt}"
            else:
                return trigger_words
        elif position == "end":
            if base_prompt:
                return f"{base_prompt}, {trigger_words}"
            else:
                return trigger_words
        elif position == "both":
            if base_prompt:
                return f"{trigger_words}, {base_prompt}, {trigger_words}"
            else:
                return trigger_words
        else:
            # デフォルトは先頭
            if base_prompt:
                return f"{trigger_words}, {base_prompt}"
            else:
                return trigger_words
    
    def clean_prompt(self, prompt: str) -> str:
        """
        プロンプトをクリーンアップする
        
        Args:
            prompt: クリーンアップ対象のプロンプト
            
        Returns:
            str: クリーンアップされたプロンプト
        """
        if not prompt:
            return ""
        
        # 余分なスペースとカンマを整理
        cleaned = ", ".join([part.strip() for part in prompt.split(",") if part.strip()])
        
        return cleaned