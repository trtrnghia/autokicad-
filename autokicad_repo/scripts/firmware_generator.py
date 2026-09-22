"""
firmware_generator.py - Phase 2 Opt-in Module
Generates compilable firmware boilerplate (PlatformIO/Zephyr).
"""

import os
from typing import Dict, Any

class FirmwareGenerator:
    def __init__(self, project_dir: str, platform: str):
        self.project_dir = project_dir
        self.platform = platform

    def generate_project(self, project_name: str, pinmap: Dict[str, Any]):
        fw_dir = os.path.join(self.project_dir, "DOCUMENTATION", "FIRMWARE", "project")
        os.makedirs(fw_dir, exist_ok=True)
        
        print(f"[*] Scaffolding {self.platform} firmware project...")
        
        if self.platform == "platformio":
            ini_path = os.path.join(fw_dir, "platformio.ini")
            with open(ini_path, "w") as f:
                f.write("[env:generic]\nplatform = ststm32\nboard = genericSTM32F407VGT6\nframework = arduino\n")
            
            src_dir = os.path.join(fw_dir, "src")
            os.makedirs(src_dir, exist_ok=True)
            main_path = os.path.join(src_dir, "main.cpp")
            with open(main_path, "w") as f:
                f.write("#include <Arduino.h>\n\nvoid setup() {\n  // AutoKiCad Auto-Init\n}\n\nvoid loop() {\n}\n")
                
        return fw_dir
