"""Function Calling 工具定义（供 Planner 节点使用）"""

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "respond",
            "description": "信息足够，生成最终回复。或用于拒绝/追问/闲聊。",
            "parameters": {
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": "做出此决策的简短理由",
                    }
                },
                "required": ["reasoning"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_memory",
            "description": "检索用户记忆（全量偏好/约束 + 语义检索相关事实）。生成或恢复场景必须先调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用于语义检索的查询文本",
                    }
                },
                "required": ["query"],
            },
        },
    },
    # --- 强度评估 ---
    {
        "type": "function",
        "function": {
            "name": "zxcvbn_check",
            "description": "评估口令熵值、评分(0-4)、破解时间。强度评估通常第一个调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待评估的口令"}
                },
                "required": ["password"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "charset_analyze",
            "description": "分析口令字符组成：长度、大小写、数字、特殊字符、唯一字符比例。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待分析的口令"}
                },
                "required": ["password"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "keyboard_pattern_check",
            "description": "检测口令中的键盘连续模式（如 qwerty, asdf）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待检测的口令"}
                },
                "required": ["password"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "weak_list_match",
            "description": "检查口令是否在弱口令库中（top100/top1000/rockyou）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待检查的口令"}
                },
                "required": ["password"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "repetition_check",
            "description": "检测口令中的重复字符和序列。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待检测的口令"}
                },
                "required": ["password"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pcfg_analyze",
            "description": "分析口令的 PCFG 结构模式，判断是否为常见结构。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待分析的口令"}
                },
                "required": ["password"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "passgpt_prob",
            "description": "使用微调模型评估口令被猜中的概率。需要 GPU。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待评估的口令"}
                },
                "required": ["password"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pass2rule",
            "description": "分析口令容易发生的 hashcat 规则变化。需要 GPU。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待分析的口令"}
                },
                "required": ["password"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pinyin_check",
            "description": "检测口令中的拼音组合。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待检测的口令"}
                },
                "required": ["password"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "date_pattern_check",
            "description": "检测口令中的日期模式。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待检测的口令"}
                },
                "required": ["password"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "personal_info_check",
            "description": "结合用户记忆检测口令中是否包含个人信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待检测的口令"},
                    "memories": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "用户记忆列表",
                    },
                },
                "required": ["password"],
            },
        },
    },
    # --- 口令生成 ---
    {
        "type": "function",
        "function": {
            "name": "multimodal_parse",
            "description": "将上传的图片/音频文件转为文本关键词。仅在有上传文件时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "文件路径"},
                    "file_type": {"type": "string", "description": "MIME 类型"},
                },
                "required": ["file_path", "file_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_password",
            "description": "基于种子词和约束条件变换生成口令候选。",
            "parameters": {
                "type": "object",
                "properties": {
                    "seeds": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "种子词列表",
                    },
                    "constraints": {
                        "type": "object",
                        "description": "约束条件（min_length, max_length, preferred_specials 等）",
                    },
                },
                "required": ["seeds"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "passphrase_generate",
            "description": "生成助记短语型口令。",
            "parameters": {
                "type": "object",
                "properties": {
                    "word_count": {
                        "type": "integer",
                        "description": "词数，默认 4",
                    },
                    "separator": {
                        "type": "string",
                        "description": "分隔符，默认 -",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pronounceable_generate",
            "description": "生成可发音的随机口令。",
            "parameters": {
                "type": "object",
                "properties": {
                    "length": {
                        "type": "integer",
                        "description": "口令长度，默认 12",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_site_policy",
            "description": "获取指定网站的密码策略要求。",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_name": {
                        "type": "string",
                        "description": "网站名称（如 GitHub, 微信, Steam）",
                    }
                },
                "required": ["site_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "strength_verify",
            "description": "对生成的口令进行反向强度验证。生成口令后应调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待验证的口令"}
                },
                "required": ["password"],
            },
        },
    },
    # --- 记忆恢复 ---
    {
        "type": "function",
        "function": {
            "name": "fragment_combine",
            "description": "将记忆片段进行排列组合，生成候选口令。",
            "parameters": {
                "type": "object",
                "properties": {
                    "fragments": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "记忆片段列表",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "可选的组合模式提示",
                    },
                },
                "required": ["fragments"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "common_variant_expand",
            "description": "对候选口令列表进行常见变体扩展（大小写、leet speak 等）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_list": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "基础候选列表",
                    }
                },
                "required": ["base_list"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rule_generate",
            "description": "使用微调模型生成 hashcat 规则进行变体扩展。需要 GPU。",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "源口令"},
                    "target_hint": {
                        "type": "string",
                        "description": "目标口令的提示信息",
                    },
                },
                "required": ["source"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "date_expand",
            "description": "将年份扩展为各种日期格式变体。",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {
                        "type": "string",
                        "description": "年份（如 2019）",
                    }
                },
                "required": ["year"],
            },
        },
    },
    # --- 泄露检查 ---
    {
        "type": "function",
        "function": {
            "name": "hibp_password_check",
            "description": "通过 k-Anonymity 查询密码是否在泄露数据库中。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待查询的密码"}
                },
                "required": ["password"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hibp_email_check",
            "description": "查询邮箱是否关联泄露事件。",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "待查询的邮箱"}
                },
                "required": ["email"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "breach_detail",
            "description": "获取指定泄露事件的详细信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "breach_name": {
                        "type": "string",
                        "description": "泄露事件名称（如 LinkedIn, Adobe）",
                    }
                },
                "required": ["breach_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "similar_leak_check",
            "description": "对口令的常见变体进行批量泄露检查。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "基础口令"}
                },
                "required": ["password"],
            },
        },
    },
    # --- 图形口令 ---
    {
        "type": "function",
        "function": {
            "name": "graphical_mode",
            "description": "唤起前端图形口令组件（图片选点或地图选点）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["image", "map"],
                        "description": "图形口令模式",
                    }
                },
                "required": ["mode"],
            },
        },
    },
]
