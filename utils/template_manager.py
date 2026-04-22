#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模板管理器
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import shutil


class Template:
    """模板类"""
    
    def __init__(self, name: str, device_type: str = "huawei", 
                 description: str = "", config: Dict = None,
                 created_time: str = None, modified_time: str = None,
                 tags: List[str] = None, author: str = ""):
        self.name = name
        self.device_type = device_type
        self.description = description
        self.config = config or {}
        self.created_time = created_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.modified_time = modified_time or self.created_time
        self.tags = tags or []
        self.author = author
        self.is_builtin = False
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "device_type": self.device_type,
            "description": self.description,
            "config": self.config,
            "created_time": self.created_time,
            "modified_time": self.modified_time,
            "tags": self.tags,
            "author": self.author,
            "is_builtin": self.is_builtin
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Template':
        return cls(
            name=data.get("name", ""),
            device_type=data.get("device_type", "huawei"),
            description=data.get("description", ""),
            config=data.get("config", {}),
            created_time=data.get("created_time"),
            modified_time=data.get("modified_time"),
            tags=data.get("tags", []),
            author=data.get("author", ""),
            is_builtin=data.get("is_builtin", False)
        )


class TemplateManager:
    """模板管理器"""
    
    BUILTIN_HUAWEI_TEMPLATES = {
        "接入交换机标准配置": {
            "description": "华为接入层交换机标准配置模板",
            "config": {
                "basic": {
                    "hostname": "Access-SW-01",
                    "password": {"value": "Admin@123", "encrypted": True},
                    "mgmt_interface": {
                        "interface": "Vlanif1",
                        "ip_address": "192.168.1.1",
                        "mask": "255.255.255.0",
                        "gateway": "192.168.1.254"
                    },
                    "enable_ssh": True,
                    "user": {"username": "admin", "password": "Admin@123", "level": 15}
                },
                "vlan": {
                    "vlans": [{"id": 1, "name": "Management"}, {"id": 10, "name": "Sales"}]
                }
            }
        },
        "核心交换机配置": {
            "description": "华为核心层交换机配置模板",
            "config": {
                "basic": {
                    "hostname": "Core-SW-01",
                    "password": {"value": "CoreAdmin@123", "encrypted": True},
                    "mgmt_interface": {
                        "interface": "Vlanif1",
                        "ip_address": "10.0.0.1",
                        "mask": "255.255.255.0"
                    },
                    "enable_ssh": True,
                    "user": {"username": "admin", "password": "CoreAdmin@123", "level": 15}
                }
            }
        },
        "汇聚交换机配置": {
            "description": "华为汇聚层交换机配置模板",
            "config": {
                "basic": {
                    "hostname": "Agg-SW-01",
                    "password": {"value": "AggAdmin@123", "encrypted": True},
                    "enable_ssh": True,
                    "user": {"username": "admin", "password": "AggAdmin@123", "level": 15}
                }
            }
        }
    }
    
    BUILTIN_H3C_TEMPLATES = {
        "接入交换机标准配置": {
            "description": "H3C接入层交换机标准配置模板",
            "config": {
                "basic": {
                    "hostname": "Access-SW-01",
                    "password": {"value": "Admin@123", "encrypted": True},
                    "mgmt_interface": {
                        "interface": "Vlan-interface1",
                        "ip_address": "192.168.1.1",
                        "mask": "255.255.255.0",
                        "gateway": "192.168.1.254"
                    },
                    "enable_ssh": True,
                    "user": {"username": "admin", "password": "Admin@123", "level": 3}
                }
            }
        },
        "核心交换机配置": {
            "description": "H3C核心层交换机配置模板",
            "config": {
                "basic": {
                    "hostname": "Core-SW-01",
                    "password": {"value": "CoreAdmin@123", "encrypted": True},
                    "mgmt_interface": {
                        "interface": "Vlan-interface1",
                        "ip_address": "10.0.0.1",
                        "mask": "255.255.255.0"
                    },
                    "enable_ssh": True,
                    "user": {"username": "admin", "password": "CoreAdmin@123", "level": 3}
                }
            }
        }
    }
    
    BUILTIN_RUIJIE_TEMPLATES = {
        "接入交换机标准配置": {
            "description": "锐捷接入层交换机标准配置模板",
            "config": {
                "basic": {
                    "hostname": "Ruijie-Access-SW-01",
                    "password": {"value": "Admin@123", "encrypted": False},
                    "mgmt_interface": {
                        "interface": "vlan 1",
                        "ip_address": "192.168.1.1",
                        "mask": "255.255.255.0",
                        "gateway": "192.168.1.254"
                    },
                    "enable_ssh": True,
                    "user": {"username": "admin", "password": "Admin@123", "level": 15}
                }
            }
        },
        "核心交换机配置": {
            "description": "锐捷核心层交换机配置模板",
            "config": {
                "basic": {
                    "hostname": "Ruijie-Core-SW-01",
                    "password": {"value": "CoreAdmin@123", "encrypted": False},
                    "enable_ssh": True,
                    "user": {"username": "admin", "password": "CoreAdmin@123", "level": 15}
                }
            }
        }
    }
    
    BUILTIN_MAIPU_TEMPLATES = {
        "接入交换机标准配置": {
            "description": "迈普接入层交换机标准配置模板",
            "config": {
                "basic": {
                    "hostname": "Maipu-Access-SW-01",
                    "password": {"value": "Admin@123", "encrypted": False},
                    "mgmt_interface": {
                        "interface": "vlan 1",
                        "ip_address": "192.168.1.1",
                        "mask": "255.255.255.0",
                        "gateway": "192.168.1.254"
                    },
                    "enable_ssh": True,
                    "user": {"username": "admin", "password": "Admin@123", "level": 15}
                }
            }
        },
        "核心交换机配置": {
            "description": "迈普核心层交换机配置模板",
            "config": {
                "basic": {
                    "hostname": "Maipu-Core-SW-01",
                    "password": {"value": "CoreAdmin@123", "encrypted": False},
                    "enable_ssh": True,
                    "user": {"username": "admin", "password": "CoreAdmin@123", "level": 15}
                }
            }
        }
    }
    
    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        
        self.templates_dir = os.path.abspath(templates_dir)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        self.custom_templates_file = os.path.join(self.templates_dir, "custom_templates.json")
        
        self.templates: Dict[str, Template] = {}
        self._load_builtin_templates()
        self._load_custom_templates()
    
    def _load_builtin_templates(self):
        for name, data in self.BUILTIN_HUAWEI_TEMPLATES.items():
            template = Template(
                name=name,
                device_type="huawei",
                description=data["description"],
                config=data["config"],
                tags=["内置", "华为"]
            )
            template.is_builtin = True
            self.templates[f"huawei_{name}"] = template
        
        for name, data in self.BUILTIN_H3C_TEMPLATES.items():
            template = Template(
                name=name,
                device_type="h3c",
                description=data["description"],
                config=data["config"],
                tags=["内置", "H3C"]
            )
            template.is_builtin = True
            self.templates[f"h3c_{name}"] = template
        
        for name, data in self.BUILTIN_RUIJIE_TEMPLATES.items():
            template = Template(
                name=name,
                device_type="ruijie",
                description=data["description"],
                config=data["config"],
                tags=["内置", "锐捷"]
            )
            template.is_builtin = True
            self.templates[f"ruijie_{name}"] = template
        
        for name, data in self.BUILTIN_MAIPU_TEMPLATES.items():
            template = Template(
                name=name,
                device_type="maipu",
                description=data["description"],
                config=data["config"],
                tags=["内置", "迈普"]
            )
            template.is_builtin = True
            self.templates[f"maipu_{name}"] = template
    
    def _load_custom_templates(self):
        if os.path.exists(self.custom_templates_file):
            try:
                with open(self.custom_templates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, template_data in data.items():
                        self.templates[key] = Template.from_dict(template_data)
            except Exception as e:
                print(f"加载自定义模板失败: {e}")
    
    def _save_custom_templates(self):
        custom_data = {}
        for key, template in self.templates.items():
            if not template.is_builtin:
                custom_data[key] = template.to_dict()
        
        try:
            with open(self.custom_templates_file, 'w', encoding='utf-8') as f:
                json.dump(custom_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存自定义模板失败: {e}")
    
    def get_templates(self, device_type: str = None) -> List[Template]:
        templates = list(self.templates.values())
        if device_type:
            templates = [t for t in templates if t.device_type == device_type]
        return templates
    
    def get_template(self, name: str, device_type: str) -> Optional[Template]:
        key = f"{device_type}_{name}"
        return self.templates.get(key)
    
    def save_template(self, template: Template) -> bool:
        if template.is_builtin:
            return False
        
        key = f"{template.device_type}_{template.name}"
        if key in self.templates and self.templates[key].is_builtin:
            return False
        
        template.modified_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.templates[key] = template
        self._save_custom_templates()
        return True
    
    def delete_template(self, name: str, device_type: str) -> bool:
        key = f"{device_type}_{name}"
        if key not in self.templates:
            return False
        if self.templates[key].is_builtin:
            return False
        
        del self.templates[key]
        self._save_custom_templates()
        return True
    
    def rename_template(self, old_name: str, new_name: str, device_type: str) -> bool:
        old_key = f"{device_type}_{old_name}"
        if old_key not in self.templates:
            return False
        if self.templates[old_key].is_builtin:
            return False
        
        template = self.templates[old_key]
        template.name = new_name
        new_key = f"{device_type}_{new_name}"
        
        del self.templates[old_key]
        self.templates[new_key] = template
        self._save_custom_templates()
        return True
    
    def duplicate_template(self, name: str, device_type: str, new_name: str) -> bool:
        key = f"{device_type}_{name}"
        if key not in self.templates:
            return False
        
        original = self.templates[key]
        new_template = Template(
            name=new_name,
            device_type=device_type,
            description=f"复制自 {original.name}",
            config=original.config.copy(),
            tags=original.tags.copy(),
            author=original.author
        )
        return self.save_template(new_template)
    
    def export_template(self, name: str, device_type: str, export_path: str) -> bool:
        key = f"{device_type}_{name}"
        if key not in self.templates:
            return False
        
        template = self.templates[key]
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(template.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出模板失败: {e}")
            return False
    
    def import_template(self, import_path: str) -> bool:
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            template = Template.from_dict(data)
            template.is_builtin = False
            return self.save_template(template)
        except Exception as e:
            print(f"导入模板失败: {e}")
            return False
    
    def search_templates(self, keyword: str, device_type: str = None) -> List[Template]:
        results = []
        keyword = keyword.lower()
        
        for template in self.templates.values():
            if device_type and template.device_type != device_type:
                continue
            
            if (keyword in template.name.lower() or 
                keyword in template.description.lower() or
                keyword in ' '.join(template.tags)):
                results.append(template)
        
        return results
