"""Function Calling 工具定义（供 Planner 节点使用）

工具清单（共 20 个）：

通用：respond, retrieve_memory
强度评估（8）：zxcvbn_check, basic_analysis, pattern_detect, pcfg_analyze,
               weak_list_match, personal_info_check, passtsl_prob, pass2rule
口令生成（5）：generate_password, passphrase_generate, pronounceable_generate,
               fetch_site_policy, multimodal_parse
泄露检查（3）：hibp_password_check, hibp_email_check, breach_detail
口令恢复（2）：fragment_combine, common_variant_expand
图形口令（2）：graphical_mode, passinfinity_artifact
"""

TOOL_DEFINITIONS = [
    # ================================================================
    #  通用
    # ================================================================
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
    # ================================================================
    #  强度评估
    # ================================================================
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
            "name": "basic_analysis",
            "description": "分析口令字符组成（长度、大小写、数字、特殊字符、唯一字符比例）及重复模式（连续字符、重复子串、顺序/逆序序列）。",
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
            "name": "pattern_detect",
            "description": "统一检测口令中的键盘模式（如 qwerty, 1qaz2wsx）、拼音组合和日期模式。",
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
            "name": "personal_info_check",
            "description": "结合用户记忆检测口令中是否包含个人信息（姓名、生日、手机号等）。",
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
    {
        "type": "function",
        "function": {
            "name": "passtsl_prob",
            "description": "使用 PassTSL ONNX 模型评估口令被猜中的概率，可在后端 CPU 上运行。",
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
            "description": "使用 Pass2Rule / PTN Transformer 预测旧口令可能演化出的变换规则和候选口令。",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "待分析的旧口令或基础口令"},
                    "top_k": {
                        "type": "integer",
                        "description": "返回候选数量，默认 20，最大 50",
                    },
                    "include_input": {
                        "type": "boolean",
                        "description": "是否把原口令作为候选返回，默认 true",
                    },
                },
                "required": ["password"],
            },
        },
    },
    # ================================================================
    #  口令生成
    # ================================================================
    {
        "type": "function",
        "function": {
            "name": "generate_password",
            "description": "基于种子词和约束条件生成口令候选。无种子词时生成纯随机安全口令。",
            "parameters": {
                "type": "object",
                "properties": {
                    "seeds": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "种子词列表（可选，留空则纯随机生成）",
                    },
                    "constraints": {
                        "type": "object",
                        "description": "约束条件（min_length, max_length, require_upper, require_digit, require_special, preferred_specials 等）",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "passphrase_generate",
            "description": "基于 xkcdpass/diceware 方法生成助记短语型口令，由多个随机英文单词组成。",
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
            "description": "生成可发音的随机口令（辅音-元音音节组合），易读且安全。",
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
            "description": "获取指定网站的密码策略要求（最小/最大长度、字符类别要求等）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_name": {
                        "type": "string",
                        "description": "网站名称（如 GitHub, 微信, Steam, 支付宝）",
                    }
                },
                "required": ["site_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "multimodal_parse",
            "description": "调用 Qwen3-Omni 将上传的图片/音频文件转为文本关键词，作为口令生成素材。仅在有上传文件时调用。解析结果会自动回写到 UploadedFile.extracted_text。",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "文件 ID（从 uploaded_files 中获取）"},
                    "file_path": {"type": "string", "description": "文件路径（从 uploaded_files 中获取）"},
                    "file_type": {"type": "string", "description": "MIME 类型（从 uploaded_files 中获取）"},
                },
                "required": ["file_id", "file_path", "file_type"],
            },
        },
    },
    # ================================================================
    #  泄露检查
    # ================================================================
    {
        "type": "function",
        "function": {
            "name": "hibp_password_check",
            "description": "通过 HIBP k-Anonymity API 查询密码是否在泄露数据库中。",
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
            "description": "通过 Hunter.io API 验证邮箱有效性并获取关联的个人/公司信息，评估邮箱暴露风险。",
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
            "description": "查询 HIBP 泄露事件。提供 breach_name 时返回单个事件详情，不提供时列出全部已知泄露事件。",
            "parameters": {
                "type": "object",
                "properties": {
                    "breach_name": {
                        "type": "string",
                        "description": "泄露事件名称（如 LinkedIn, Adobe），留空则列出全部",
                    },
                    "domain": {
                        "type": "string",
                        "description": "按域名筛选泄露事件列表（可选）",
                    },
                },
                "required": [],
            },
        },
    },
    # ================================================================
    #  口令恢复
    # ================================================================
    {
        "type": "function",
        "function": {
            "name": "fragment_combine",
            "description": "将记忆片段排列组合生成候选口令。自动检测年份片段并展开为多种日期格式。",
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
            "description": "对候选口令进行 hashcat 规则子集变体扩展（大小写、leet speak、追加数字/符号、反转等）。",
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
    # ================================================================
    #  图形口令
    # ================================================================
    {
        "type": "function",
        "function": {
            "name": "graphical_mode",
            "description": "打开 PassInfinity 独立体验页。Agent 可直接打开图片、地图、富文本界面，或先打开模式选择页。",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["select", "image", "map", "richtext"],
                        "description": "PassInfinity 模式：select（选择入口）、image（图片选点）、map（地图选点）、richtext（富文本标记）",
                    }
                },
                "required": ["mode"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "passinfinity_artifact",
            "description": "读取当前用户已保存的 PassInfinity 体验结果，可读最近一条，也可按 artifact_id 精确读取，供后续解释和建议。",
            "parameters": {
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "体验结果 ID。留空时默认读取最近一条。",
                    },
                    "latest": {
                        "type": "boolean",
                        "description": "是否读取最近一条体验结果，默认 true。",
                    },
                },
                "required": [],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# 按工具名索引，供 skill 动态过滤使用
# ---------------------------------------------------------------------------
TOOL_DEFINITIONS_MAP: dict[str, dict] = {
    tool["function"]["name"]: tool for tool in TOOL_DEFINITIONS
}


def get_tools_for_skill(skill_name: str) -> list[dict]:
    """返回指定 skill 对应的工具定义列表（skill 专属工具 + 通用工具）。"""
    from agent.skills import SKILL_REGISTRY, UTILITY_TOOLS

    if skill_name not in SKILL_REGISTRY:
        # 未知 skill，仅返回通用工具
        return [TOOL_DEFINITIONS_MAP[n] for n in UTILITY_TOOLS if n in TOOL_DEFINITIONS_MAP]

    names = SKILL_REGISTRY[skill_name]["tools"] + UTILITY_TOOLS
    return [TOOL_DEFINITIONS_MAP[n] for n in names if n in TOOL_DEFINITIONS_MAP]
