# ComfyUI LoRA Random Selector

A ComfyUI custom node that randomly selects LoRA files by category and automatically applies corresponding trigger words.

## Features

- **Category-based LoRA Management**: Organize your LoRA files into customizable categories
- **Random Selection**: Randomly select LoRA files from specified categories
- **Automatic Trigger Words**: Automatically apply trigger words associated with selected LoRAs
- **User Configurable**: Easily edit categories, LoRAs, and trigger words via JSON configuration
- **Multiple Selection**: Select multiple LoRAs at once
- **Flexible Strength Control**: Override or use default LoRA strengths
- **Prompt Integration**: Seamlessly integrate trigger words with your prompts

## Installation

1. **Clone or download** this repository to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   git clone https://github.com/your-username/comfyui-lora-random-selector.git
   ```

2. **Restart ComfyUI** to load the new custom node

3. **Configure your LoRAs** by editing the configuration file (see Configuration section below)

## Configuration

### Setting up your LoRAs

1. **Edit the configuration file**: Open `config/lora_config.json` in a text editor
2. **Add your categories**: Create categories that make sense for your LoRA collection
3. **Add your LoRAs**: For each LoRA, specify the file path, default strength, and trigger words
4. **Save and restart**: Save the file and restart ComfyUI to apply changes

### Configuration File Structure

```json
{
  "categories": {
    "character": {
      "description": "Character LoRAs",
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

### File Path Specification

- Use relative paths from the `ComfyUI/models/loras/` directory
- Example: If your LoRA is at `ComfyUI/models/loras/characters/my_character.safetensors`, use `characters/my_character.safetensors`
- Supported formats: `.safetensors`, `.ckpt`, `.pt`

## Usage

### Basic Usage

1. **Add the node**: In ComfyUI, add the "LoRA Random Selector" node to your workflow
2. **Select category**: Choose the category containing the LoRAs you want to use
3. **Configure settings**: Adjust the number of LoRAs, trigger word count, and other parameters
4. **Connect outputs**: Connect the node outputs to your workflow as needed

### Node Parameters

#### Required Inputs
- **category**: Select the LoRA category to choose from
- **num_loras**: Number of LoRAs to select (1-5)
- **trigger_word_count**: Number of trigger words to apply per LoRA (0-5)
- **seed**: Random seed for reproducible results (-1 for random)
- **enable_trigger_words**: Enable/disable automatic trigger word application

#### Optional Inputs
- **strength_override**: Override the default LoRA strength (-1 to use default)
- **base_prompt**: Base prompt to combine with trigger words

#### Outputs
- **selected_lora_info**: JSON information about selected LoRAs
- **lora_path**: Path to the first selected LoRA
- **lora_strength**: Strength value for the first LoRA
- **trigger_words**: Combined trigger words (comma-separated)
- **combined_prompt**: Base prompt combined with trigger words
- **debug_info**: Debug information for troubleshooting

### Example Workflow

1. Connect a "LoRA Random Selector" node
2. Set category to "character"
3. Set num_loras to 1
4. Set trigger_word_count to 2
5. Connect the "combined_prompt" output to your text encoder
6. Connect the "lora_path" and "lora_strength" to a LoRA loader node

## Advanced Configuration

### Adding New Categories

1. Open `config/lora_config.json`
2. Add a new category under the "categories" section:
   ```json
   "my_category": {
     "description": "My custom LoRA category",
     "loras": {
       "my_lora": {
         "file_path": "path/to/my_lora.safetensors",
         "strength_default": 0.75,
         "trigger_words": ["my trigger", "custom style"],
         "tags": ["custom", "style"]
       }
     }
   }
   ```
3. Restart ComfyUI

### Global Settings

- **max_trigger_words**: Maximum number of trigger words to select at once
- **default_strength**: Default LoRA strength when not specified
- **random_seed**: Fixed seed for consistent results (null for random)
- **debug_mode**: Enable additional logging for troubleshooting
- **file_validation**: Enable file existence checking

## Troubleshooting

### Common Issues

1. **Node not appearing**: Restart ComfyUI after installation
2. **No LoRAs found**: Check file paths in configuration file
3. **File not found errors**: Verify LoRA files exist at specified paths
4. **JSON errors**: Validate JSON syntax in configuration file

### Debug Information

The node provides detailed debug information through the "debug_info" output, including:
- Execution details (seed used, number of LoRAs selected)
- File validation results
- Selected LoRA details

### Log Output

Check the ComfyUI console for detailed log messages about:
- Configuration loading
- LoRA selection process
- File validation results
- Error messages

## File Structure

```
comfyui-lora-random-selector/
├── __init__.py                     # Node registration
├── lora_random_selector.py         # Main node class
├── config/
│   ├── lora_config.json           # Main configuration file
│   └── config_template.json       # Configuration template
├── utils/
│   ├── __init__.py
│   ├── config_manager.py          # Configuration management
│   └── lora_utils.py              # LoRA utility functions
├── examples/
│   └── sample_workflow.json       # Sample workflow
└── README.md                       # This file
```

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Version History

- **v1.0.0**: Initial release with basic LoRA selection and trigger word functionality