"""
ComfyUI LoRA Random Selector Custom Node
カテゴリベースでLoRAをランダム選択し、トリガーワードを自動適用するカスタムノード
"""

from .lora_random_selector import LoRARandomSelector

# ComfyUIにノードを登録
NODE_CLASS_MAPPINGS = {
    "LoRARandomSelector": LoRARandomSelector
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoRARandomSelector": "LoRA Random Selector"
}

__version__ = "1.0.0"
__author__ = "Claude Code Assistant"
__description__ = "ComfyUI custom node for randomly selecting LoRA files by category with automatic trigger word application"