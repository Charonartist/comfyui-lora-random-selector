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

### Setting up your LoRAs (v2.0 Multi-File Structure)

**New in v2.0**: Configuration is now split into multiple files for better organization!

1. **Global Settings**: Edit `config/global_settings.json` for general settings
2. **Category Files**: Create individual JSON files in `config/lora_style/` directory
3. **Auto-Detection**: Each JSON file name becomes a category (e.g., `fantasy.json` → "fantasy" category)
4. **Save and restart**: Save files and restart ComfyUI to apply changes

### New File Structure

```
comfyui-lora-random-selector/
├── config/
│   ├── global_settings.json        # Global settings
│   └── lora_style/                  # Category files directory
│       ├── character.json           # Character LoRAs
│       ├── style.json               # Style LoRAs
│       ├── environment.json         # Environment LoRAs
│       └── concept.json             # Concept LoRAs
```

### Category File Structure

Each category file in `config/lora_style/` follows this structure:

```json
{
  "category_info": {
    "name": "character",
    "description": "Character LoRAs"
  },
  "loras": {
    "anime_girl_v1": {
      "file_path": "anime_girl_v1.safetensors",
      "strength_default": 0.8,
      "trigger_words": ["anime girl", "cute girl", "kawaii"],
      "tags": ["anime", "character", "girl"]
    }
  }
}
```

### Global Settings File

`config/global_settings.json`:
```json
{
  "global_settings": {
    "max_trigger_words": 3,
    "default_strength": 0.7,
    "random_seed": null,
    "debug_mode": false,
    "file_validation": true
  }
}
```

### Adding New Categories

Simply create a new JSON file in `config/lora_style/` directory:

1. Create `config/lora_style/my_category.json`
2. Follow the category file structure above
3. Restart ComfyUI
4. "my_category" will appear in the category dropdown

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
3. Set trigger_word_count to 2
4. Connect the "combined_prompt" output to your text encoder
5. Connect the "lora_path" and "lora_strength" to a LoRA loader node

## Advanced Configuration

### Migration from v1.0

If you have an existing `config/lora_config.json` file, the tool will automatically migrate it to the new structure:

1. **Automatic Migration**: On first run, the old file will be split into multiple files
2. **Backup Created**: Your original file is saved as `lora_config_backup.json`
3. **New Structure**: Categories are separated into individual files in `config/lora_style/`

### Legacy Support

The tool automatically handles:
- Migration from single JSON file to multi-file structure
- Backup of original configuration
- Seamless transition without data loss

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

- **v2.0.0**: 
  - **Multi-file configuration**: Split single JSON into multiple category files
  - **Auto-category detection**: JSON file names automatically become categories
  - **Improved LoRA path handling**: Better ComfyUI loader compatibility
  - **Automatic migration**: Seamless upgrade from v1.0 configuration
  - **Enhanced scalability**: Support for large LoRA collections
- **v1.0.0**: Initial release with basic LoRA selection and trigger word functionality