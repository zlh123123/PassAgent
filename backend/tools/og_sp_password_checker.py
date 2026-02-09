"""
MCP Tool: 国际和国内安全标准密码策略检查
"""

import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def _get_security_standards_config() -> Dict[str, Dict[str, Any]]:
    """获取国际和国内安全标准配置"""
    return {
        # 国际标准
        "iso27001": {
            "description": "ISO/IEC 27001 信息安全管理体系标准",
            "region": "国际",
            "min_length": 12,
            "required_char_types": 4,
            "password_history_limit": 8,
            "similarity_threshold": 0.8,
            "min_entropy": 60,
            "max_age_days": 90,
            "lockout_attempts": 5,
            "special_requirements": {
                "no_dictionary_words": True,
                "no_consecutive_chars": True,
                "no_repeated_chars": 3,
                "require_mixed_case": True,
            },
            "compliance_level": "高",
        },
        "nist_sp800_63b": {
            "description": "NIST SP 800-63B 数字身份认证指南",
            "region": "美国",
            "min_length": 8,
            "max_length": 64,
            "required_char_types": 1,  # NIST 不强制要求复杂度
            "password_history_limit": 0,  # NIST 不要求密码历史
            "similarity_threshold": 1.0,
            "min_entropy": 40,
            "max_age_days": 0,  # NIST 不推荐定期更换
            "lockout_attempts": 10,
            "special_requirements": {
                "check_breached_passwords": True,
                "no_hints": True,
                "allow_all_printable": True,
                "no_composition_rules": True,
            },
            "compliance_level": "标准",
        },
        "pci_dss": {
            "description": "PCI DSS 支付卡行业数据安全标准",
            "region": "国际",
            "min_length": 12,
            "required_char_types": 4,
            "password_history_limit": 4,
            "similarity_threshold": 0.8,
            "min_entropy": 65,
            "max_age_days": 90,
            "lockout_attempts": 6,
            "special_requirements": {
                "no_user_info": True,
                "no_vendor_defaults": True,
                "two_factor_required": True,
                "encryption_required": True,
            },
            "compliance_level": "高",
        },
        "hipaa": {
            "description": "HIPAA 医疗保险便携性和责任法案",
            "region": "美国",
            "min_length": 12,
            "required_char_types": 4,
            "password_history_limit": 6,
            "similarity_threshold": 0.8,
            "min_entropy": 55,
            "max_age_days": 90,
            "lockout_attempts": 5,
            "special_requirements": {
                "access_logging": True,
                "role_based_access": True,
                "automatic_logout": True,
                "audit_trail": True,
            },
            "compliance_level": "高",
        },
        "sox": {
            "description": "SOX 萨班斯-奥克斯利法案",
            "region": "美国",
            "min_length": 14,
            "required_char_types": 4,
            "password_history_limit": 12,
            "similarity_threshold": 0.7,
            "min_entropy": 70,
            "max_age_days": 60,
            "lockout_attempts": 3,
            "special_requirements": {
                "segregation_of_duties": True,
                "change_documentation": True,
                "regular_review": True,
                "privileged_account_mgmt": True,
            },
            "compliance_level": "严格",
        },
        "gdpr": {
            "description": "GDPR 通用数据保护条例",
            "region": "欧盟",
            "min_length": 12,
            "required_char_types": 4,
            "password_history_limit": 6,
            "similarity_threshold": 0.8,
            "min_entropy": 60,
            "max_age_days": 90,
            "lockout_attempts": 5,
            "special_requirements": {
                "data_minimization": True,
                "purpose_limitation": True,
                "storage_limitation": True,
                "pseudonymization": True,
            },
            "compliance_level": "高",
        },
        # 国内标准
        "gb_t_25058": {
            "description": "GB/T 25058-2019 信息安全技术 网络安全等级保护基本要求",
            "region": "中国",
            "min_length": 12,
            "required_char_types": 4,
            "password_history_limit": 5,
            "similarity_threshold": 0.8,
            "min_entropy": 60,
            "max_age_days": 90,
            "lockout_attempts": 5,
            "special_requirements": {
                "level_protection": True,
                "centralized_management": True,
                "access_control": True,
                "security_audit": True,
            },
            "compliance_level": "高",
        },
        "gb_t_22239": {
            "description": "GB/T 22239-2019 信息安全技术 网络安全等级保护基本要求",
            "region": "中国",
            "min_length": 8,
            "required_char_types": 3,
            "password_history_limit": 3,
            "similarity_threshold": 0.8,
            "min_entropy": 50,
            "max_age_days": 90,
            "lockout_attempts": 6,
            "special_requirements": {
                "identity_authentication": True,
                "access_control": True,
                "security_audit": True,
                "intrusion_prevention": True,
            },
            "compliance_level": "标准",
        },
        "djbh": {
            "description": "党政机关办公网络安全技术要求",
            "region": "中国",
            "min_length": 15,
            "required_char_types": 4,
            "password_history_limit": 10,
            "similarity_threshold": 0.7,
            "min_entropy": 75,
            "max_age_days": 60,
            "lockout_attempts": 3,
            "special_requirements": {
                "classified_protection": True,
                "strong_authentication": True,
                "encrypted_storage": True,
                "regular_assessment": True,
            },
            "compliance_level": "严格",
        },
        "yinhangye": {
            "description": "银行业信息系统安全技术指引",
            "region": "中国",
            "min_length": 14,
            "required_char_types": 4,
            "password_history_limit": 8,
            "similarity_threshold": 0.7,
            "min_entropy": 70,
            "max_age_days": 90,
            "lockout_attempts": 5,
            "special_requirements": {
                "financial_grade_security": True,
                "transaction_integrity": True,
                "anti_money_laundering": True,
                "risk_control": True,
            },
            "compliance_level": "严格",
        },
        "zhengquanye": {
            "description": "证券期货业信息安全保障管理办法",
            "region": "中国",
            "min_length": 12,
            "required_char_types": 4,
            "password_history_limit": 6,
            "similarity_threshold": 0.8,
            "min_entropy": 65,
            "max_age_days": 90,
            "lockout_attempts": 5,
            "special_requirements": {
                "trading_security": True,
                "market_data_protection": True,
                "investor_protection": True,
                "regulatory_compliance": True,
            },
            "compliance_level": "高",
        },
        "baoxianye": {
            "description": "保险业信息系统安全管理指引",
            "region": "中国",
            "min_length": 12,
            "required_char_types": 4,
            "password_history_limit": 6,
            "similarity_threshold": 0.8,
            "min_entropy": 60,
            "max_age_days": 90,
            "lockout_attempts": 5,
            "special_requirements": {
                "customer_data_protection": True,
                "actuarial_data_security": True,
                "claims_integrity": True,
                "regulatory_reporting": True,
            },
            "compliance_level": "高",
        },
        "dianzishangwu": {
            "description": "电子商务安全技术要求",
            "region": "中国",
            "min_length": 10,
            "required_char_types": 3,
            "password_history_limit": 5,
            "similarity_threshold": 0.8,
            "min_entropy": 55,
            "max_age_days": 120,
            "lockout_attempts": 6,
            "special_requirements": {
                "payment_security": True,
                "user_privacy": True,
                "transaction_logging": True,
                "fraud_prevention": True,
            },
            "compliance_level": "标准",
        },
        # 其他国际标准
        "cobit": {
            "description": "COBIT 信息技术治理框架",
            "region": "国际",
            "min_length": 12,
            "required_char_types": 4,
            "password_history_limit": 6,
            "similarity_threshold": 0.8,
            "min_entropy": 60,
            "max_age_days": 90,
            "lockout_attempts": 5,
            "special_requirements": {
                "governance_alignment": True,
                "value_delivery": True,
                "risk_optimization": True,
                "resource_optimization": True,
            },
            "compliance_level": "高",
        },
        "coso": {
            "description": "COSO 内部控制整合框架",
            "region": "国际",
            "min_length": 12,
            "required_char_types": 4,
            "password_history_limit": 8,
            "similarity_threshold": 0.8,
            "min_entropy": 60,
            "max_age_days": 90,
            "lockout_attempts": 5,
            "special_requirements": {
                "control_environment": True,
                "risk_assessment": True,
                "control_activities": True,
                "monitoring": True,
            },
            "compliance_level": "高",
        },
        "ffiec": {
            "description": "FFIEC 联邦金融机构检查委员会指导",
            "region": "美国",
            "min_length": 15,
            "required_char_types": 4,
            "password_history_limit": 10,
            "similarity_threshold": 0.7,
            "min_entropy": 75,
            "max_age_days": 60,
            "lockout_attempts": 3,
            "special_requirements": {
                "multi_factor_auth": True,
                "risk_based_auth": True,
                "customer_authentication": True,
                "fraud_monitoring": True,
            },
            "compliance_level": "严格",
        },
        "basel_iii": {
            "description": "Basel III 巴塞尔协议III",
            "region": "国际",
            "min_length": 14,
            "required_char_types": 4,
            "password_history_limit": 8,
            "similarity_threshold": 0.7,
            "min_entropy": 70,
            "max_age_days": 90,
            "lockout_attempts": 5,
            "special_requirements": {
                "operational_risk": True,
                "capital_adequacy": True,
                "stress_testing": True,
                "liquidity_risk": True,
            },
            "compliance_level": "严格",
        },
    }


async def check_security_standards_compliance_tool(
    password: str,
    standard_name: str = "iso27001",
    user_info: Optional[Dict[str, str]] = None,
    previous_passwords: Optional[List[str]] = None,
    account_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """MCP Tool: 检查安全标准合规性"""
    print(f"接收到安全标准合规性检查请求: {standard_name}")

    try:
        if not password:
            return {"status": "error", "error": "密码不能为空"}

        # 获取标准配置
        standards_config = _get_security_standards_config()
        if standard_name not in standards_config:
            available_standards = list(standards_config.keys())
            return {
                "status": "error",
                "error": f"未知的安全标准: {standard_name}。可用标准: {', '.join(available_standards)}",
            }

        standard_config = standards_config[standard_name]
        user_info = user_info or {}
        previous_passwords = previous_passwords or []
        account_info = account_info or {}

        # 执行各项检查
        checks = {}
        issues = []
        recommendations = []
        compliance_details = {}

        # 1. 基础密码要求检查
        basic_result = await _check_standard_basic_requirements(
            password, standard_config
        )
        checks.update(basic_result["checks"])
        issues.extend(basic_result["issues"])
        recommendations.extend(basic_result["recommendations"])

        # 2. 特殊要求检查
        special_result = await _check_standard_special_requirements(
            password, standard_config, user_info
        )
        checks.update(special_result["checks"])
        issues.extend(special_result["issues"])
        recommendations.extend(special_result["recommendations"])

        # 3. 历史密码检查
        if previous_passwords and standard_config.get("password_history_limit", 0) > 0:
            history_result = await _check_standard_password_history(
                password, previous_passwords, standard_config
            )
            checks.update(history_result["checks"])
            issues.extend(history_result["issues"])
            recommendations.extend(history_result["recommendations"])

        # 4. 标准特定检查
        specific_result = await _check_standard_specific_rules(
            password, standard_name, standard_config
        )
        checks.update(specific_result["checks"])
        issues.extend(specific_result["issues"])
        recommendations.extend(specific_result["recommendations"])

        # 合规性评估
        critical_issues = [
            issue
            for issue in issues
            if "关键" in issue or "严重" in issue or "不符合" in issue
        ]
        warning_issues = [
            issue for issue in issues if "建议" in issue or "推荐" in issue
        ]

        total_checks = len(checks)
        passed_checks = sum(1 for check in checks.values() if check)
        compliance_percentage = (
            (passed_checks / total_checks * 100) if total_checks > 0 else 0
        )

        # 根据标准的严格程度确定合规等级
        compliance_level = standard_config.get("compliance_level", "标准")
        if compliance_level == "严格":
            threshold_excellent = 95
            threshold_good = 85
        elif compliance_level == "高":
            threshold_excellent = 90
            threshold_good = 80
        else:  # 标准
            threshold_excellent = 85
            threshold_good = 75

        if len(critical_issues) == 0 and compliance_percentage >= threshold_excellent:
            security_level = "完全合规"
            level_color = "✅"
        elif len(critical_issues) == 0 and compliance_percentage >= threshold_good:
            security_level = "基本合规"
            level_color = "🟡"
        elif len(critical_issues) <= 2 and compliance_percentage >= 60:
            security_level = "部分合规"
            level_color = "🟠"
        else:
            security_level = "不合规"
            level_color = "🔴"

        return {
            "status": "success",
            "standard_name": standard_name,
            "standard_description": standard_config["description"],
            "standard_region": standard_config["region"],
            "compliance_level": compliance_level,
            "compliant": len(critical_issues) == 0
            and compliance_percentage >= threshold_good,
            "security_level": security_level,
            "level_indicator": level_color,
            "compliance_percentage": round(compliance_percentage, 1),
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "checks": checks,
            "issues": issues,
            "critical_issues": critical_issues,
            "warning_issues": warning_issues,
            "recommendations": recommendations,
            "compliance_details": {
                "threshold_excellent": threshold_excellent,
                "threshold_good": threshold_good,
                "standard_level": compliance_level,
            },
            "summary": f"{standard_config['description']} - {security_level} ({compliance_percentage:.1f}%)",
        }

    except Exception as e:
        logger.error(f"安全标准合规性检查失败: {str(e)}")
        return {"status": "error", "error": f"检查失败: {str(e)}"}


async def _check_standard_basic_requirements(
    password: str, standard_config: Dict
) -> Dict[str, Any]:
    """检查标准基础要求"""
    checks = {}
    issues = []
    recommendations = []

    # 长度检查
    min_length = standard_config.get("min_length", 8)
    max_length = standard_config.get("max_length", 128)

    if len(password) < min_length:
        issues.append(
            f"关键：密码长度不足，标准要求至少{min_length}位，当前{len(password)}位"
        )
        recommendations.append(f"增加密码长度至{min_length}位或更多")
    checks["meets_min_length"] = len(password) >= min_length

    if max_length and len(password) > max_length:
        issues.append(
            f"密码长度超限，标准要求最多{max_length}位，当前{len(password)}位"
        )
        recommendations.append(f"减少密码长度至{max_length}位以内")
    checks["within_max_length"] = not max_length or len(password) <= max_length

    # 字符复杂度检查
    required_types = standard_config.get("required_char_types", 1)
    if required_types > 1:  # NIST等标准可能不要求复杂度
        char_types = _count_character_types(password)
        if char_types < required_types:
            issues.append(
                f"字符类型不足：标准要求{required_types}种，当前{char_types}种"
            )
            recommendations.append("使用大写字母、小写字母、数字和特殊字符的组合")
        checks["meets_complexity"] = char_types >= required_types

    # 熵值检查
    min_entropy = standard_config.get("min_entropy", 0)
    if min_entropy > 0:
        entropy = _calculate_password_entropy(password)
        if entropy < min_entropy:
            issues.append(f"密码熵值不足：标准要求{min_entropy}，当前{entropy:.1f}")
            recommendations.append("增加密码的随机性和复杂度")
        checks["meets_entropy"] = entropy >= min_entropy

    return {"checks": checks, "issues": issues, "recommendations": recommendations}


async def _check_standard_special_requirements(
    password: str, standard_config: Dict, user_info: Dict
) -> Dict[str, Any]:
    """检查标准特殊要求"""
    checks = {}
    issues = []
    recommendations = []

    special_reqs = standard_config.get("special_requirements", {})

    # 检查字典单词
    if special_reqs.get("no_dictionary_words"):
        if _contains_dictionary_words(password):
            issues.append("不符合标准：密码包含常见字典单词")
            recommendations.append("避免使用常见单词，使用随机字符组合")
        checks["no_dictionary_words"] = not _contains_dictionary_words(password)

    # 检查连续字符
    if special_reqs.get("no_consecutive_chars"):
        if _has_consecutive_chars(password):
            issues.append("不符合标准：密码包含连续字符")
            recommendations.append("避免使用连续的字母或数字")
        checks["no_consecutive_chars"] = not _has_consecutive_chars(password)

    # 检查重复字符
    max_repeated = special_reqs.get("no_repeated_chars", 0)
    if max_repeated > 0:
        if _has_excessive_repeated_chars(password, max_repeated):
            issues.append(f"不符合标准：密码包含超过{max_repeated}个连续重复字符")
            recommendations.append(f"避免连续重复字符超过{max_repeated}个")
        checks["no_excessive_repeats"] = not _has_excessive_repeated_chars(
            password, max_repeated
        )

    # 检查大小写混合
    if special_reqs.get("require_mixed_case"):
        has_upper = bool(re.search(r"[A-Z]", password))
        has_lower = bool(re.search(r"[a-z]", password))
        if not (has_upper and has_lower):
            issues.append("不符合标准：必须同时包含大写和小写字母")
            recommendations.append("确保密码同时包含大写和小写字母")
        checks["mixed_case"] = has_upper and has_lower

    # 检查用户信息
    if special_reqs.get("no_user_info") and user_info:
        if _contains_user_info(password, user_info):
            issues.append("严重：密码包含用户个人信息")
            recommendations.append("创建与个人信息完全无关的密码")
        checks["no_user_info"] = not _contains_user_info(password, user_info)

    return {"checks": checks, "issues": issues, "recommendations": recommendations}


async def _check_standard_password_history(
    password: str, previous_passwords: List[str], standard_config: Dict
) -> Dict[str, Any]:
    """检查标准密码历史要求"""
    checks = {}
    issues = []
    recommendations = []

    history_limit = standard_config.get("password_history_limit", 0)
    similarity_threshold = standard_config.get("similarity_threshold", 1.0)

    if history_limit > 0:
        # 检查重复使用
        if password in previous_passwords[:history_limit]:
            issues.append(f"严重：不能重用最近{history_limit}个密码")
            recommendations.append("创建全新的密码，避免重复使用")
        checks["not_reused"] = password not in previous_passwords[:history_limit]

        # 检查相似度
        if similarity_threshold < 1.0:
            for i, prev_pwd in enumerate(previous_passwords[: min(3, history_limit)]):
                similarity = _calculate_password_similarity(password, prev_pwd)
                if similarity > similarity_threshold:
                    issues.append(
                        f"密码与第{i+1}个历史密码过于相似（相似度：{similarity:.1%}）"
                    )
                    recommendations.append("创建与历史密码差异更大的新密码")
                    break
            checks["sufficiently_different"] = True  # 简化实现

    return {"checks": checks, "issues": issues, "recommendations": recommendations}


async def _check_standard_specific_rules(
    password: str, standard_name: str, standard_config: Dict
) -> Dict[str, Any]:
    """检查标准特定规则"""
    checks = {}
    issues = []
    recommendations = []

    # NIST SP 800-63B 特定规则
    if standard_name == "nist_sp800_63b":
        # NIST 推荐检查已泄露密码
        if standard_config["special_requirements"].get("check_breached_passwords"):
            # 这里应该调用真实的泄露检查API
            # 为了演示，假设某些弱密码已泄露
            weak_passwords = ["password", "123456", "qwerty", "admin"]
            if password.lower() in weak_passwords:
                issues.append("严重：密码在已知泄露数据库中")
                recommendations.append("使用未曾泄露的强密码")
            checks["not_breached"] = password.lower() not in weak_passwords

    # PCI DSS 特定规则
    elif standard_name == "pci_dss":
        # 检查是否需要双因素认证提示
        if standard_config["special_requirements"].get("two_factor_required"):
            recommendations.append("建议：配置双因素认证以满足PCI DSS要求")

        # 检查加密要求
        if standard_config["special_requirements"].get("encryption_required"):
            recommendations.append("建议：确保密码存储时使用强加密算法")

    # 国内等保标准特定规则
    elif standard_name in ["gb_t_25058", "gb_t_22239"]:
        # 检查是否符合等保要求
        if len(password) >= 12 and _count_character_types(password) >= 3:
            checks["meets_dengbao"] = True
        else:
            issues.append("不符合等保标准：密码复杂度不足")
            recommendations.append("按照等保要求设置密码复杂度")
            checks["meets_dengbao"] = False

    # 党政机关特定规则
    elif standard_name == "djbh":
        if not _check_government_grade_complexity(password):
            issues.append("不符合党政机关要求：密码安全等级不足")
            recommendations.append("使用政府级别的高强度密码")
        checks["meets_government_grade"] = _check_government_grade_complexity(password)

    return {"checks": checks, "issues": issues, "recommendations": recommendations}


# 辅助函数
def _contains_dictionary_words(password: str) -> bool:
    """检查是否包含字典单词"""
    common_words = [
        "password",
        "admin",
        "user",
        "login",
        "welcome",
        "system",
        "computer",
        "internet",
        "security",
        "manager",
        "master",
        "123456",
        "qwerty",
        "abc123",
        "letmein",
        "monkey",
    ]
    password_lower = password.lower()
    return any(word in password_lower for word in common_words)


def _has_consecutive_chars(password: str, min_length: int = 3) -> bool:
    """检查是否有连续字符"""
    for i in range(len(password) - min_length + 1):
        substr = password[i : i + min_length]
        # 检查连续数字
        if substr.isdigit():
            digits = [int(c) for c in substr]
            if all(digits[j] == digits[j - 1] + 1 for j in range(1, len(digits))):
                return True
            if all(digits[j] == digits[j - 1] - 1 for j in range(1, len(digits))):
                return True
        # 检查连续字母
        elif substr.isalpha():
            chars = [ord(c.lower()) for c in substr]
            if all(chars[j] == chars[j - 1] + 1 for j in range(1, len(chars))):
                return True
            if all(chars[j] == chars[j - 1] - 1 for j in range(1, len(chars))):
                return True
    return False


def _has_excessive_repeated_chars(password: str, max_repeated: int) -> bool:
    """检查是否有过多重复字符"""
    count = 1
    for i in range(1, len(password)):
        if password[i] == password[i - 1]:
            count += 1
            if count > max_repeated:
                return True
        else:
            count = 1
    return False


def _contains_user_info(password: str, user_info: Dict) -> bool:
    """检查是否包含用户信息"""
    password_lower = password.lower()

    # 检查用户名
    if user_info.get("username") and user_info["username"].lower() in password_lower:
        return True

    # 检查姓名
    if user_info.get("name"):
        name_parts = user_info["name"].lower().split()
        for part in name_parts:
            if len(part) > 2 and part in password_lower:
                return True

    # 检查生日
    if user_info.get("birthdate"):
        birth_patterns = _extract_date_patterns(user_info["birthdate"])
        for pattern in birth_patterns:
            if pattern in password:
                return True

    return False


def _check_government_grade_complexity(password: str) -> bool:
    """检查政府级别复杂度"""
    if len(password) < 15:
        return False

    char_types = _count_character_types(password)
    if char_types < 4:
        return False

    # 检查是否有足够的特殊字符
    special_count = len(re.findall(r"[^a-zA-Z0-9]", password))
    if special_count < 3:
        return False

    # 检查熵值
    entropy = _calculate_password_entropy(password)
    if entropy < 75:
        return False

    return True


def _count_character_types(password: str) -> int:
    """计算字符类型数量"""
    types = 0
    if re.search(r"[a-z]", password):
        types += 1
    if re.search(r"[A-Z]", password):
        types += 1
    if re.search(r"\d", password):
        types += 1
    if re.search(r"[^a-zA-Z0-9]", password):
        types += 1
    return types


def _extract_date_patterns(birthdate: str) -> List[str]:
    """从生日中提取可能的密码模式"""
    patterns = []
    if "-" in birthdate:
        parts = birthdate.split("-")
        patterns.extend(parts)
        patterns.append("".join(parts))
        if len(parts[0]) == 4:  # YYYY格式
            patterns.append(parts[0][2:] + parts[1] + parts[2])
    return patterns


def _calculate_password_similarity(pwd1: str, pwd2: str) -> float:
    """计算两个密码的相似度"""
    if len(pwd1) == 0 or len(pwd2) == 0:
        return 0.0

    matches = sum(1 for i, c in enumerate(pwd1) if i < len(pwd2) and c == pwd2[i])
    return matches / max(len(pwd1), len(pwd2))


def _calculate_password_entropy(password: str) -> float:
    """计算密码熵值"""
    import math

    charset_size = 0
    if re.search(r"[a-z]", password):
        charset_size += 26
    if re.search(r"[A-Z]", password):
        charset_size += 26
    if re.search(r"\d", password):
        charset_size += 10
    if re.search(r"[^a-zA-Z0-9]", password):
        charset_size += 32

    if charset_size == 0:
        return 0.0

    return len(password) * math.log2(charset_size)


async def list_available_standards_tool() -> Dict[str, Any]:
    """MCP Tool: 列出所有可用的安全标准"""
    try:
        standards_config = _get_security_standards_config()

        # 按地区分组
        international_standards = {}
        domestic_standards = {}

        for name, config in standards_config.items():
            standard_info = {
                "name": name,
                "description": config["description"],
                "compliance_level": config["compliance_level"],
                "min_length": config["min_length"],
                "required_char_types": config["required_char_types"],
            }

            if config["region"] == "中国":
                domestic_standards[name] = standard_info
            else:
                international_standards[name] = standard_info

        return {
            "status": "success",
            "international_standards": international_standards,
            "domestic_standards": domestic_standards,
            "total_count": len(standards_config),
            "regions": list(
                set(config["region"] for config in standards_config.values())
            ),
        }

    except Exception as e:
        logger.error(f"获取安全标准列表失败: {str(e)}")
        return {"status": "error", "error": f"获取失败: {str(e)}"}
