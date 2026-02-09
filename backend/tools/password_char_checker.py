"""
MCP Tool: 密码字符组成规则检查
"""

import re
import logging
from typing import Dict, Any, List, Set

logger = logging.getLogger(__name__)


async def check_password_composition_rules_tool(
    password: str,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digits: bool = True,
    require_special: bool = True,
    min_char_types: int = 3,
    allowed_special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?",
    forbidden_chars: str = "",
    require_non_sequential: bool = True,
) -> Dict[str, Any]:
    """MCP Tool: 检查密码字符组成规则"""
    print(f"接收到密码字符组成规则检查请求")

    try:
        if not password:
            return {"status": "error", "error": "密码不能为空"}

        # 字符类型分析
        has_uppercase = bool(re.search(r"[A-Z]", password))
        has_lowercase = bool(re.search(r"[a-z]", password))
        has_digits = bool(re.search(r"\d", password))
        has_special = bool(re.search(r"[^a-zA-Z0-9]", password))

        # 特殊字符详细分析
        special_chars_found = set(re.findall(r"[^a-zA-Z0-9]", password))
        allowed_special_set = set(allowed_special_chars)
        forbidden_special_set = set(forbidden_chars)

        invalid_special_chars = special_chars_found - allowed_special_set
        forbidden_chars_found = special_chars_found & forbidden_special_set

        # 字符类型计数
        char_types_count = sum([has_uppercase, has_lowercase, has_digits, has_special])

        # 规则检查
        checks = {
            "has_uppercase": has_uppercase,
            "has_lowercase": has_lowercase,
            "has_digits": has_digits,
            "has_special": has_special,
            "char_types_count": char_types_count,
            "meets_min_types": char_types_count >= min_char_types,
            "valid_special_chars": len(invalid_special_chars) == 0,
            "no_forbidden_chars": len(forbidden_chars_found) == 0,
            "non_sequential": True,  # 将在下面详细检查
        }

        # 连续字符检查
        if require_non_sequential:
            checks["non_sequential"] = not _has_sequential_chars(password)

        # 生成问题和建议
        issues = []
        recommendations = []

        if require_uppercase and not has_uppercase:
            issues.append("缺少大写字母")
            recommendations.append("添加至少一个大写字母 (A-Z)")

        if require_lowercase and not has_lowercase:
            issues.append("缺少小写字母")
            recommendations.append("添加至少一个小写字母 (a-z)")

        if require_digits and not has_digits:
            issues.append("缺少数字")
            recommendations.append("添加至少一个数字 (0-9)")

        if require_special and not has_special:
            issues.append("缺少特殊字符")
            recommendations.append(
                f"添加至少一个特殊字符 ({allowed_special_chars[:10]}...)"
            )

        if char_types_count < min_char_types:
            issues.append(
                f"字符类型不足：当前{char_types_count}种，需要至少{min_char_types}种"
            )
            recommendations.append(f"增加更多字符类型以达到{min_char_types}种要求")

        if invalid_special_chars:
            issues.append(f"包含不允许的特殊字符：{''.join(invalid_special_chars)}")
            recommendations.append(f"只使用允许的特殊字符：{allowed_special_chars}")

        if forbidden_chars_found:
            issues.append(f"包含禁止的字符：{''.join(forbidden_chars_found)}")
            recommendations.append("移除所有禁止使用的字符")

        if require_non_sequential and not checks["non_sequential"]:
            issues.append("包含连续字符序列")
            recommendations.append("避免使用连续的字母或数字序列")

        # 合规性评估
        compliant = len(issues) == 0
        if compliant:
            security_level = "完全合规"
            level_color = "✅"
        elif len(issues) <= 2:
            security_level = "基本合规"
            level_color = "🟡"
        else:
            security_level = "不合规"
            level_color = "🔴"

        return {
            "status": "success",
            "compliant": compliant,
            "security_level": security_level,
            "level_indicator": level_color,
            "checks": checks,
            "character_analysis": {
                "uppercase_count": len(re.findall(r"[A-Z]", password)),
                "lowercase_count": len(re.findall(r"[a-z]", password)),
                "digit_count": len(re.findall(r"\d", password)),
                "special_count": len(special_chars_found),
                "special_chars_found": list(special_chars_found),
                "invalid_special_chars": list(invalid_special_chars),
                "forbidden_chars_found": list(forbidden_chars_found),
            },
            "issues": issues,
            "recommendations": recommendations,
            "summary": f"字符组成检查 - {security_level}",
        }

    except Exception as e:
        logger.error(f"密码字符组成规则检查失败: {str(e)}")
        return {"status": "error", "error": f"检查失败: {str(e)}"}


def _has_sequential_chars(password: str, min_sequence_length: int = 3) -> bool:
    """检查是否包含连续字符"""
    # 检查连续数字
    for i in range(len(password) - min_sequence_length + 1):
        substr = password[i : i + min_sequence_length]
        if substr.isdigit():
            digits = [int(c) for c in substr]
            if all(digits[j] == digits[j - 1] + 1 for j in range(1, len(digits))):
                return True
            if all(digits[j] == digits[j - 1] - 1 for j in range(1, len(digits))):
                return True

    # 检查连续字母
    for i in range(len(password) - min_sequence_length + 1):
        substr = password[i : i + min_sequence_length].lower()
        if substr.isalpha():
            chars = [ord(c) for c in substr]
            if all(chars[j] == chars[j - 1] + 1 for j in range(1, len(chars))):
                return True
            if all(chars[j] == chars[j - 1] - 1 for j in range(1, len(chars))):
                return True

    return False


def get_composition_rule_presets() -> Dict[str, Dict[str, Any]]:
    """获取常见字符组成规则预设"""
    return {
        "basic": {
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digits": True,
            "require_special": False,
            "min_char_types": 3,
        },
        "standard": {
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digits": True,
            "require_special": True,
            "min_char_types": 4,
        },
        "enterprise": {
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digits": True,
            "require_special": True,
            "min_char_types": 4,
            "require_non_sequential": True,
        },
        "high_security": {
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digits": True,
            "require_special": True,
            "min_char_types": 4,
            "allowed_special_chars": "!@#$%^&*",
            "require_non_sequential": True,
        },
    }
