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
    
    BUILTIN_ZTE_TEMPLATES = {
        "接入交换机标准配置": {
            "description": "中兴 ZXR10 接入交换机示例（经典 ZXROS，接口名为 gei_1/x）",
            "config": {
                "basic": {
                    "hostname": "ZTE-Access-01",
                    "password": {"value": "Admin@123", "encrypted": False},
                    "mgmt_interface": {
                        "interface": "vlan 1",
                        "ip_address": "192.168.1.1",
                        "mask": "255.255.255.0",
                        "gateway": "192.168.1.254"
                    },
                    "enable_ssh": True,
                    "user": {"username": "admin", "password": "Admin@123", "level": 15}
                },
                "vlan": {
                    "vlans": [
                        {"id": 10, "name": "Office"},
                        {"id": 20, "name": "Server"}
                    ],
                    "interfaces": [
                        {"interface": "gei_1/1", "type": "access", "vlan_id": 10},
                        {
                            "interface": "gei_1/24",
                            "type": "trunk",
                            "trunk_vlans": [10, 20],
                            "pvid": 1
                        }
                    ],
                    "vlanifs": [
                        {
                            "vlan_id": 10,
                            "ip_address": "192.168.10.1",
                            "mask": "255.255.255.0",
                            "description": "Office-GW"
                        }
                    ]
                }
            }
        },
        "核心交换机配置": {
            "description": "中兴 ZXR10 核心交换机示例，含 OSPF 与静态默认路由所需的基础项",
            "config": {
                "basic": {
                    "hostname": "ZTE-Core-01",
                    "password": {"value": "CoreAdmin@123", "encrypted": False},
                    "mgmt_interface": {
                        "interface": "vlan 1",
                        "ip_address": "10.0.0.1",
                        "mask": "255.255.255.0"
                    },
                    "enable_ssh": True,
                    "user": {"username": "admin", "password": "CoreAdmin@123", "level": 15},
                    "ntp": {
                        "servers": [{"ip": "10.0.0.100", "prefer": True}],
                        "timezone": "UTC+8"
                    }
                }
            }
        }
    }

    BUILTIN_ZTE_ROSNG_TEMPLATES = {
        "接入交换机基础配置": {
            "description": "中兴 ZXR10 ROSNG 接入示例（5960/9900）。口令 Placeholder1 是占位符，下发前请修改。接口名为 gei-0/1/1/x",
            "config": {
                "basic": {
                    "hostname": "ZTE-ROSNG-01",
                    "user": {"username": "netops", "password": "Placeholder1", "level": 15},
                    "mgmt_interface": {
                        "interface": "vlan1",
                        "ip_address": "192.168.1.1",
                        "mask": "255.255.255.0",
                        "gateway": "192.168.1.254"
                    },
                    "enable_ssh": True
                },
                "vlan": {
                    "vlans": [{"id": 10, "name": "Office"}],
                    "interfaces": [
                        {"interface": "gei-0/1/1/1", "type": "access", "vlan_id": 10},
                        {
                            "interface": "gei-0/1/1/24",
                            "type": "trunk",
                            "trunk_vlans": [10, 20],
                            "pvid": 1
                        }
                    ],
                    "vlanifs": [{
                        "vlan_id": 10,
                        "ip_address": "192.168.10.1",
                        "mask": "255.255.255.0",
                        "description": "Office-GW"
                    }]
                }
            }
        },
        "上联聚合与静态路由": {
            "description": "中兴 ZXR10 ROSNG 上联：smartgroup 按 802.3ad 写出，并带一条文档地址段的静态路由。口令 Placeholder1 是占位符",
            "config": {
                "basic": {
                    "hostname": "ZTE-ROSNG-Agg",
                    "user": {"username": "netops", "password": "Placeholder1", "level": 15},
                    "enable_ssh": True
                },
                "vlan": {
                    "vlans": [{"id": 10, "name": "Office"}, {"id": 20, "name": "Server"}]
                },
                "routing": {
                    "static_routes": [{
                        "dest_network": "198.51.100.0",
                        "mask": "255.255.255.0",
                        "next_hop": "192.0.2.1"
                    }]
                },
                "interface": {
                    "eth_trunks": [{
                        "trunk_id": 1,
                        "mode": "lacp-static",
                        "description": "uplink",
                        "member_ports": ["gei-0/1/1/23", "gei-0/1/1/24"],
                        "port_link_type": "trunk",
                        "trunk_vlans": [10, 20]
                    }]
                }
            }
        }
    }

    BUILTIN_DPTECH_TEMPLATES = {
        "三层防火墙基础配置": {
            "description": "迪普 FW1000 带外管理示例：meth0_0、SSH、管理员和默认路由",
            "config": {
                "basic": {
                    "hostname": "DP-FW-01",
                    "password": {"value": "Admin@123", "encrypted": False},
                    "mgmt_interface": {
                        "interface": "meth0_0",
                        "ip_address": "192.168.0.1",
                        "mask": "255.255.255.0",
                        "gateway": "192.168.0.254"
                    },
                    "enable_ssh": True,
                    "user": {"username": "admin", "password": "Admin@123", "level": 15},
                    "ntp": {
                        "servers": [{"ip": "10.0.0.100", "prefer": True}],
                        "timezone": "UTC+8"
                    },
                    "dns": {"servers": ["223.5.5.5"]}
                }
            }
        },
        "安全域与包过滤": {
            "description": "迪普 FW1000 业务口、VLAN 接口和一条放通 Web 的安全策略",
            "config": {
                "basic": {
                    "hostname": "DP-FW-Edge",
                    "user": {"username": "netops", "password": "Netops1", "level": 15},
                    "mgmt_interface": {
                        "interface": "gige0_0",
                        "ip_address": "10.1.1.1",
                        "mask": "255.255.255.0"
                    },
                    "enable_ssh": True
                },
                "vlan": {
                    "vlans": [{"id": 10, "name": "Office"}],
                    "interfaces": [
                        {"interface": "gige0_1", "type": "access", "vlan_id": 10}
                    ],
                    "vlanifs": [{
                        "vlan_id": 10,
                        "ip_address": "192.168.10.1",
                        "mask": "255.255.255.0",
                        "description": "Office-GW"
                    }]
                },
                "security": {
                    "acls": [{
                        "number": 100,
                        "type": "extended",
                        "description": "web",
                        "rules": [{
                            "id": 10,
                            "action": "permit",
                            "protocol": "tcp",
                            "source": "any",
                            "destination": "192.168.10.10",
                            "dest_port": "80"
                        }]
                    }]
                }
            }
        }
    }

    BUILTIN_DPTECH_LSW_TEMPLATES = {
        "接入交换机基础配置": {
            "description": "迪普 LSW 接入示例：vlan-if 管理地址、SSH、Access 口和三层 VLAN",
            "config": {
                "basic": {
                    "hostname": "DP-LSW-01",
                    "user": {"username": "admin", "password": "Admin@123", "level": 15},
                    "mgmt_interface": {
                        "interface": "vlan-if 1",
                        "ip_address": "192.168.1.1",
                        "mask": "255.255.255.0",
                        "gateway": "192.168.1.254"
                    },
                    "enable_ssh": True
                },
                "vlan": {
                    "vlans": [{"id": 10, "name": "Office"}],
                    "interfaces": [
                        {"interface": "gige0_1", "type": "access", "vlan_id": 10}
                    ],
                    "vlanifs": [{
                        "vlan_id": 10,
                        "ip_address": "192.168.10.1",
                        "mask": "255.255.255.0",
                        "description": "Office-GW"
                    }]
                }
            }
        },
        "汇聚链路聚合": {
            "description": "迪普 LSW 上联：bond 动态聚合，Trunk 放行两个 VLAN",
            "config": {
                "basic": {
                    "hostname": "DP-LSW-Agg",
                    "user": {"username": "netops", "password": "Netops1", "level": 15},
                    "enable_ssh": True
                },
                "vlan": {
                    "vlans": [{"id": 10, "name": "Office"}, {"id": 20, "name": "Server"}],
                    "interfaces": [
                        {"interface": "gige0_1", "type": "access", "vlan_id": 10},
                        {
                            "interface": "gige0_2",
                            "type": "trunk",
                            "trunk_vlans": [10, 20],
                            "pvid": 1
                        }
                    ]
                },
                "interface": {
                    "eth_trunks": [{
                        "trunk_id": 1,
                        "mode": "lacp-dynamic",
                        "description": "uplink",
                        "member_ports": ["gige0_23", "gige0_24"],
                        "port_link_type": "trunk",
                        "trunk_vlans": [10, 20]
                    }]
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

        for name, data in self.BUILTIN_ZTE_TEMPLATES.items():
            template = Template(
                name=name,
                device_type="zte",
                description=data["description"],
                config=data["config"],
                tags=["内置", "中兴"]
            )
            template.is_builtin = True
            self.templates[f"zte_{name}"] = template

        for name, data in self.BUILTIN_ZTE_ROSNG_TEMPLATES.items():
            template = Template(
                name=name,
                device_type="zte-rosng",
                description=data["description"],
                config=data["config"],
                tags=["内置", "中兴", "ROSNG"]
            )
            template.is_builtin = True
            self.templates[f"zte-rosng_{name}"] = template

        for name, data in self.BUILTIN_DPTECH_TEMPLATES.items():
            template = Template(
                name=name,
                device_type="dptech",
                description=data["description"],
                config=data["config"],
                tags=["内置", "迪普"]
            )
            template.is_builtin = True
            self.templates[f"dptech_{name}"] = template

        for name, data in self.BUILTIN_DPTECH_LSW_TEMPLATES.items():
            template = Template(
                name=name,
                device_type="dptech-lsw",
                description=data["description"],
                config=data["config"],
                tags=["内置", "迪普", "LSW"]
            )
            template.is_builtin = True
            self.templates[f"dptech-lsw_{name}"] = template
    
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
