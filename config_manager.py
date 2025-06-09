import json
import os
from typing import Dict, Any


class ConfigManager:
    def __init__(self, config_file="soroban_config.json"):
        self.config_file = config_file
        self.default_config = {
            'ocr_threshold': 100,
            'min_numbers_required': 2,
            'high_confidence_mode': False,
            'capture_timeout': 5,
            'solve_interval_ms': 1000,
            'window_geometry': "700x720",
            'auto_save_history': True,
            'max_history_entries': 1000
        }
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to handle missing keys
                    config = self.default_config.copy()
                    config.update(loaded_config)
                    return config
            except Exception as e:
                print(f"Failed to load config: {e}, using defaults")
                
        return self.default_config.copy()

    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False

    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value

    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        self.config.update(updates)

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()

    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate numeric ranges
        if not (50 <= self.config.get('ocr_threshold', 100) <= 200):
            issues.append("OCR threshold must be between 50 and 200")
            
        if not (1 <= self.config.get('min_numbers_required', 2) <= 10):
            issues.append("Min numbers required must be between 1 and 10")
            
        if not (1 <= self.config.get('capture_timeout', 5) <= 30):
            issues.append("Capture timeout must be between 1 and 30 seconds")
            
        if not (100 <= self.config.get('solve_interval_ms', 1000) <= 10000):
            issues.append("Solve interval must be between 100 and 10000 milliseconds")
            
        return issues
