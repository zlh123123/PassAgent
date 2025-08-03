"""
MCP Tool: 密码长度规则检查
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


async def check_password_length_rules_tool(
    password: str,
    min_length: int = 8,
    max_length: int = 128,
    recommended_length: int = 12,
) -> Dict[str, Any]:
    """MCP Tool: 检查密码长度规则"""
    print(f"接收到密码长度规则检查请求")

    try:
        if not password:
            return {"status": "error", "error": "密码不能为空"}

        password_length = len(password)

        # 基本规则检查
        checks = {
            "meets_minimum": password_length >= min_length,
            "within_maximum": password_length <= max_length,
            "meets_recommended": password_length >= recommended_length,
            "current_length": password_length,
            "min_required": min_length,
            "max_allowed": max_length,
            "recommended": recommended_length,
        }

        # 生成详细报告
        issues = []
        recommendations = []

        if not checks["meets_minimum"]:
            issues.append(
                f"密码长度不足：当前{password_length}位，最少需要{min_length}位"
            )
            recommendations.append(
                f"增加密码长度至少{min_length - password_length}位字符"
            )

        if not checks["within_maximum"]:
            issues.append(f"密码过长：当前{password_length}位，最多允许{max_length}位")
            recommendations.append(f"减少密码长度{password_length - max_length}位字符")

        if checks["meets_minimum"] and checks["within_maximum"]:
            if not checks["meets_recommended"]:
                recommendations.append(
                    f"建议使用{recommended_length}位或更长的密码以提高安全性"
                )

        # 安全等级评估
        if password_length < min_length:
            security_level = "不合规"
            level_color = "🔴"
        elif password_length < recommended_length:
            security_level = "基本合规"
            level_color = "🟡"
        elif password_length >= recommended_length:
            security_level = "推荐长度"
            level_color = "🟢"
        else:
            security_level = "优秀"
            level_color = "✅"

        return {
            "status": "success",
            "compliant": len(issues) == 0,
            "security_level": security_level,
            "level_indicator": level_color,
            "checks": checks,
            "issues": issues,
            "recommendations": recommendations,
            "summary": f"密码长度{password_length}位 - {security_level}",
        }

    except Exception as e:
        logger.error(f"密码长度规则检查失败: {str(e)}")
        return {"status": "error", "error": f"检查失败: {str(e)}"}


def get_length_rule_presets() -> Dict[str, Dict[str, int]]:
    """获取常见长度规则预设"""
    return {
        "basic": {"min_length": 8, "max_length": 128, "recommended_length": 12},
        "enterprise": {"min_length": 12, "max_length": 64, "recommended_length": 16},
        "high_security": {"min_length": 16, "max_length": 32, "recommended_length": 20},
        "financial": {"min_length": 12, "max_length": 128, "recommended_length": 14},
        "government": {"min_length": 15, "max_length": 128, "recommended_length": 18},
    }
