# backend/app/services/password_service.py
import re
import math
import string
from typing import Dict, List, Any
import zxcvbn

class PasswordService:
    """密码分析服务"""
    
    def __init__(self):
        self.common_passwords = {
            "123456", "password", "123456789", "12345678", "12345",
            "qwerty", "abc123", "password123", "admin", "root"
        }
        
        self.common_patterns = [
            r"(.)\1{2,}",  # 重复字符
            r"(012|123|234|345|456|567|678|789|890)",  # 连续数字
            r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)",  # 连续字母
            r"(qwer|asdf|zxcv|hjkl)",  # 键盘模式
        ]
    
    def analyze_strength(self, password: str, include_suggestions: bool = True) -> Dict[str, Any]:
        """分析密码强度"""
        try:
            # 基础检查
            length = len(password)
            has_uppercase = bool(re.search(r'[A-Z]', password))
            has_lowercase = bool(re.search(r'[a-z]', password))
            has_numbers = bool(re.search(r'\d', password))
            has_symbols = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
            
            # 使用zxcvbn进行高级分析
            zxcvbn_result = zxcvbn.zxcvbn(password)
            
            # 计算字符集大小
            charset_size = 0
            if has_lowercase:
                charset_size += 26
            if has_uppercase:
                charset_size += 26
            if has_numbers:
                charset_size += 10
            if has_symbols:
                charset_size += 32
            
            # 计算熵值
            entropy = length * math.log2(charset_size) if charset_size > 0 else 0
            
            # 检查常见模式
            found_patterns = []
            for pattern in self.common_patterns:
                if re.search(pattern, password.lower()):
                    found_patterns.append(pattern)
            
            # 检查是否为常见密码
            is_common = password.lower() in self.common_passwords
            
            # 计算综合得分 (0-100)
            score = self._calculate_score(
                length, has_uppercase, has_lowercase, has_numbers, 
                has_symbols, entropy, found_patterns, is_common, zxcvbn_result
            )
            
            # 确定强度等级
            if score >= 80:
                level = "very_strong"
            elif score >= 60:
                level = "strong"
            elif score >= 40:
                level = "medium"
            elif score >= 20:
                level = "weak"
            else:
                level = "very_weak"
            
            result = {
                "score": score,
                "level": level,
                "has_uppercase": has_uppercase,
                "has_lowercase": has_lowercase,
                "has_numbers": has_numbers,
                "has_symbols": has_symbols,
                "entropy": round(entropy, 2),
                "common_patterns": found_patterns,
                "is_common_password": is_common,
                "estimated_crack_time": zxcvbn_result['crack_times_display']['offline_slow_hashing_1e4_per_second']
            }
            
            if include_suggestions:
                result["suggestions"] = self._generate_suggestions(
                    password, has_uppercase, has_lowercase, has_numbers, 
                    has_symbols, found_patterns, is_common, length
                )
            
            return result
            
        except Exception as e:
            # 降级处理
            return {
                "score": 0,
                "level": "unknown",
                "has_uppercase": False,
                "has_lowercase": False,
                "has_numbers": False,
                "has_symbols": False,
                "entropy": 0,
                "common_patterns": [],
                "is_common_password": False,
                "estimated_crack_time": "unknown",
                "error": str(e)
            }
    
    def _calculate_score(self, length, has_upper, has_lower, has_numbers, 
                        has_symbols, entropy, patterns, is_common, zxcvbn_result):
        """计算密码强度得分"""
        score = 0
        
        # 长度得分 (0-30分)
        if length >= 12:
            score += 30
        elif length >= 8:
            score += 20
        elif length >= 6:
            score += 10
        
        # 字符种类得分 (0-30分)
        char_types = sum([has_upper, has_lower, has_numbers, has_symbols])
        score += char_types * 7.5
        
        # 熵值得分 (0-25分)
        if entropy >= 60:
            score += 25
        elif entropy >= 40:
            score += 15
        elif entropy >= 20:
            score += 10
        
        # zxcvbn得分 (0-15分)
        score += zxcvbn_result['score'] * 3
        
        # 扣分项
        if is_common:
            score -= 30
        score -= len(patterns) * 5  # 每个模式扣5分
        
        return max(0, min(100, int(score)))
    
    def _generate_suggestions(self, password, has_upper, has_lower, has_numbers, 
                            has_symbols, patterns, is_common, length):
        """生成密码改进建议"""
        suggestions = []
        
        if length < 8:
            suggestions.append("密码长度至少应为8位字符")
        elif length < 12:
            suggestions.append("建议密码长度达到12位或更长")
        
        if not has_upper:
            suggestions.append("添加大写字母 (A-Z)")
        if not has_lower:
            suggestions.append("添加小写字母 (a-z)")
        if not has_numbers:
            suggestions.append("添加数字 (0-9)")
        if not has_symbols:
            suggestions.append("添加特殊符号 (!@#$%^&*)")
        
        if is_common:
            suggestions.append("避免使用常见密码")
        
        if patterns:
            suggestions.append("避免使用重复字符、连续数字或键盘模式")
        
        if not suggestions:
            suggestions.append("密码强度良好！建议定期更换")
        
        return suggestions