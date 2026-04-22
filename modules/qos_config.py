#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NetOps Toolkit - QoS配置模块
"""


class QoSConfigGenerator:
    """QoS配置生成器"""
    
    @staticmethod
    def generate_traffic_classifier(name: str,
                                    rules: list,
                                    operator: str = "or") -> str:
        """生成流分类配置"""
        config_lines = []
        config_lines.append(f"traffic classifier {name}")
        if operator == "and":
            config_lines.append(" operator and")
        config_lines.append("\n")
        
        for rule in rules:
            rule_type = rule.get("type")
            value = rule.get("value")
            
            if rule_type == "acl":
                config_lines.append(f" if-match acl {value}\n")
            elif rule_type == "protocol":
                config_lines.append(f" if-match protocol {value}\n")
            elif rule_type == "dscp":
                config_lines.append(f" if-match dscp {value}\n")
            elif rule_type == "vlan":
                config_lines.append(f" if-match vlan-id {value}\n")
            elif rule_type == "source_mac":
                config_lines.append(f" if-match source-mac {value}\n")
            elif rule_type == "destination_mac":
                config_lines.append(f" if-match destination-mac {value}\n")
            elif rule_type == "source_ip":
                config_lines.append(f" if-match source-ip {value}\n")
            elif rule_type == "destination_ip":
                config_lines.append(f" if-match destination-ip {value}\n")
            elif rule_type == "tcp_flag":
                config_lines.append(f" if-match tcp-flag {value}\n")
            elif rule_type == "destination_port":
                config_lines.append(f" if-match tcp-port {value}\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_traffic_behavior(name: str,
                                  actions: list) -> str:
        """生成流行为配置"""
        config_lines = []
        config_lines.append(f"traffic behavior {name}\n")
        
        for action in actions:
            action_type = action.get("type")
            value = action.get("value")
            
            if action_type == "permit":
                config_lines.append(" permit\n")
            elif action_type == "deny":
                config_lines.append(" deny\n")
            
            elif action_type == "remark_dscp":
                config_lines.append(f" remark dscp {value}\n")
            elif action_type == "remark_8021p":
                config_lines.append(f" remark 8021p {value}\n")
            elif action_type == "remark_vlan":
                config_lines.append(f" remark vlan-id {value}\n")
            elif action_type == "remark_local_priority":
                config_lines.append(f" remark local-precedence {value}\n")
            elif action_type == "remark_ip_precedence":
                config_lines.append(f" remark ip-precedence {value}\n")
            
            elif action_type == "car":
                cir = action.get("cir", 1000)
                pir = action.get("pir", cir)
                cbs = action.get("cbs", cir * 125)
                pbs = action.get("pbs", pir * 125)
                green = action.get("green_action", "pass")
                red = action.get("red_action", "discard")
                config_lines.append(f" car cir {cir} pir {pir} cbs {cbs} pbs {pbs} green {green} red {red}\n")
            
            elif action_type == "redirect":
                config_lines.append(f" redirect interface {value}\n")
            elif action_type == "redirect_next_hop":
                config_lines.append(f" redirect ip-nexthop {value}\n")
            
            elif action_type == "mirroring":
                config_lines.append(f" mirroring to observe-port {value}\n")
            
            elif action_type == "statistic":
                config_lines.append(" statistic enable\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_traffic_policy(name: str,
                               classifier_behavior_pairs: list,
                               share_mode: bool = False) -> str:
        """生成流策略配置"""
        config_lines = []
        config_lines.append(f"traffic policy {name}")
        if share_mode:
            config_lines.append(" share-mode")
        config_lines.append("\n")
        
        for idx, pair in enumerate(classifier_behavior_pairs, 1):
            classifier = pair.get("classifier")
            behavior = pair.get("behavior")
            config_lines.append(f" classifier {classifier} behavior {behavior}\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_qos_interface_policy(interface: str,
                                     policy_name: str,
                                     direction: str = "inbound") -> str:
        """生成接口QoS策略应用配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        config_lines.append(f" traffic-policy {policy_name} {direction}\n")
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_qos_vlan_policy(vlan_id: int,
                                policy_name: str,
                                direction: str = "inbound") -> str:
        """生成VLAN QoS策略应用配置"""
        config_lines = []
        config_lines.append(f"vlan {vlan_id}\n")
        config_lines.append(f" traffic-policy {policy_name} {direction}\n")
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_queue_scheduler(mode: str = "wfq",
                                 weights: dict = None,
                                 wred_enable: bool = False) -> str:
        """生成队列调度配置"""
        config_lines = []
        config_lines.append(f"qos queue scheduler {mode}\n")
        
        if mode == "wfq" and weights:
            for queue_id, weight in weights.items():
                config_lines.append(f"qos queue {queue_id} weight {weight}\n")
        
        if wred_enable:
            config_lines.append("qos queue wred enable\n")
        
        return "".join(config_lines)
    
    @staticmethod
    def generate_port_queue(interface: str,
                           queue_id: int,
                           scheduler: str = "wfq",
                           weight: int = 10,
                           shaping: int = None) -> str:
        """生成端口队列配置"""
        config_lines = []
        config_lines.append(f"interface {interface}\n")
        config_lines.append(f" qos queue {queue_id} scheduler {scheduler}\n")
        config_lines.append(f" qos queue {queue_id} weight {weight}\n")
        
        if shaping:
            config_lines.append(f" qos queue {queue_id} shaping {shaping}\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_bandwidth_policy(policy_name: str,
                                 bandwidth_percent: int = None,
                                 bandwidth_kbps: int = None) -> str:
        """生成带宽策略配置"""
        config_lines = []
        config_lines.append(f"qos bandwidth {policy_name}\n")
        
        if bandwidth_percent:
            config_lines.append(f" bandwidth percent {bandwidth_percent}\n")
        elif bandwidth_kbps:
            config_lines.append(f" bandwidth {bandwidth_kbps} kbps\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_acl_qos(name: str,
                        rules: list) -> str:
        """生成扩展ACL用于QoS"""
        config_lines = []
        config_lines.append(f"acl number {name}\n")
        
        for rule in rules:
            rule_id = rule.get("id", 5)
            protocol = rule.get("protocol", "ip")
            source = rule.get("source", "any")
            dest = rule.get("destination", "any")
            src_port = rule.get("source_port")
            dst_port = rule.get("dest_port")
            dscp = rule.get("dscp")
            
            rule_str = f" rule {rule_id} permit {protocol}"
            if source != "any":
                src_wildcard = rule.get("source_wildcard", "0.0.0.0")
                rule_str += f" source {source} {src_wildcard}"
            if dest != "any":
                dst_wildcard = rule.get("destination_wildcard", "0.0.0.0")
                rule_str += f" destination {dest} {dst_wildcard}"
            if dst_port and protocol in ["tcp", "udp"]:
                rule_str += f" destination-port eq {dst_port}"
            if dscp:
                rule_str += f" dscp {dscp}"
            
            config_lines.append(rule_str + "\n")
        
        config_lines.append("#\n")
        return "".join(config_lines)
    
    @staticmethod
    def generate_qos_all(config: dict) -> str:
        """生成完整QoS配置"""
        config_lines = ["#\n", "# QoS配置\n", "#\n"]
        
        has_traffic_config = False
        
        if "classifiers" in config:
            config_lines.append("\n#\n# 流分类配置\n#\n")
            for classifier in config["classifiers"]:
                config_lines.append(QoSConfigGenerator.generate_traffic_classifier(
                    classifier["name"],
                    classifier["rules"],
                    classifier.get("operator", "or")
                ))
            has_traffic_config = True
        
        if "behaviors" in config:
            config_lines.append("\n#\n# 流行为配置\n#\n")
            for behavior in config["behaviors"]:
                config_lines.append(QoSConfigGenerator.generate_traffic_behavior(
                    behavior["name"],
                    behavior["actions"]
                ))
            has_traffic_config = True
        
        if "policies" in config:
            config_lines.append("\n#\n# 流策略配置\n#\n")
            for policy in config["policies"]:
                config_lines.append(QoSConfigGenerator.generate_traffic_policy(
                    policy["name"],
                    policy["classifier_behavior_pairs"],
                    policy.get("share_mode", False)
                ))
            has_traffic_config = True
        
        if has_traffic_config and "interface_policies" in config:
            config_lines.append("\n#\n# 接口QoS策略应用\n#\n")
            for iface_policy in config["interface_policies"]:
                config_lines.append(QoSConfigGenerator.generate_qos_interface_policy(
                    iface_policy["interface"],
                    iface_policy["policy_name"],
                    iface_policy.get("direction", "inbound")
                ))
        
        if "queue_scheduler" in config:
            config_lines.append("\n#\n# 队列调度配置\n#\n")
            config_lines.append(QoSConfigGenerator.generate_queue_scheduler(
                config["queue_scheduler"].get("mode", "wfq"),
                config["queue_scheduler"].get("weights"),
                config["queue_scheduler"].get("wred_enable", False)
            ))
        
        if "port_queue" in config:
            config_lines.append("\n#\n# 端口队列配置\n#\n")
            for port_queue in config["port_queue"]:
                config_lines.append(QoSConfigGenerator.generate_port_queue(
                    port_queue["interface"],
                    port_queue["queue_id"],
                    port_queue.get("scheduler", "wfq"),
                    port_queue.get("weight", 10),
                    port_queue.get("shaping")
                ))
        
        return "".join(config_lines)
