# backend/app/services/ai_service.py
import asyncio
from typing import List, Dict, Any, Optional
import json
import base64
import io
from PIL import Image

class AIService:
    """AI服务 - 模拟实现，后续可接入真实AI API"""
    
    def __init__(self):
        self.model_name = "simulated-ai-model"
    
    async def generate_text_response(self, message: str, context: List[Dict] = None) -> str:
        """生成文本回复"""
        # 模拟AI思考时间
        await asyncio.sleep(1)
        
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ['密码', 'password', '口令']):
            if '分析' in message_lower or '检测' in message_lower:
                return self._generate_password_analysis_response(message)
            elif '生成' in message_lower or '推荐' in message_lower:
                return self._generate_password_recommendation_response(message)
            else:
                return self._generate_password_general_response()
        
        elif '你好' in message_lower or 'hello' in message_lower:
            return "你好！我是PassAgent，一个专业的密码安全分析助手。我可以帮您分析密码强度、检测安全风险、生成安全密码建议等。请告诉我您需要什么帮助？"
        
        else:
            return f"我理解您想了解关于'{message}'的信息。作为密码安全专家，我建议我们专注于密码相关的安全话题。您可以询问密码强度分析、安全建议或密码生成等问题。"
    
    async def analyze_password_with_ai(self, password: str, analysis_context: Dict = None) -> str:
        """使用AI深度分析密码"""
        await asyncio.sleep(1.5)
        
        # 简单的模式识别
        analysis = []
        
        if len(password) < 8:
            analysis.append("⚠️ 密码长度不足，建议至少8位字符")
        
        if password.isdigit():
            analysis.append("🔢 纯数字密码容易被破解，建议添加字母和符号")
        
        if password.isalpha():
            analysis.append("🔤 纯字母密码安全性较低，建议添加数字和符号")
        
        if password == password.lower():
            analysis.append("📝 建议添加大写字母增强复杂度")
        
        # 检查常见模式
        if '123' in password or 'abc' in password.lower():
            analysis.append("🔄 检测到连续字符模式，建议使用更随机的组合")
        
        if not analysis:
            analysis.append("✅ 密码结构良好，建议定期更换保持安全")
        
        return "**AI密码深度分析结果：**\n\n" + "\n".join(analysis) + "\n\n💡 **建议：** 使用密码管理器生成和存储强密码，开启两步验证增强账户安全。"
    
    async def analyze_image_for_password(self, image_data: str, prompt: str = None) -> str:
        """分析图片生成密码建议"""
        await asyncio.sleep(2)
        
        try:
            # 解析base64图片数据
            if image_data.startswith('data:image'):
                base64_data = image_data.split(',')[1]
            else:
                base64_data = image_data
            
            # 这里实际应该调用图像识别API
            # 模拟图像分析结果
            simulated_objects = ["cat", "coffee", "book", "tree", "sky"]
            colors = ["blue", "green", "brown", "white"]
            
            suggestions = []
            suggestions.append(f"🖼️ **图片密码生成建议：**\n")
            suggestions.append(f"根据图片内容，我为您推荐以下密码组合策略：\n")
            
            # 生成基于图片的密码建议
            for i, obj in enumerate(simulated_objects[:3]):
                password_example = f"{obj.capitalize()}{2024}{['!', '@', '#'][i]}"
                suggestions.append(f"{i+1}. `{password_example}` - 基于图片主要元素")
            
            suggestions.append(f"\n💡 **个性化建议：**")
            suggestions.append(f"- 选择图片中最有意义的元素作为密码基础")
            suggestions.append(f"- 添加个人重要数字（非生日）")
            suggestions.append(f"- 用特殊符号连接不同元素")
            suggestions.append(f"- 避免使用过于明显的图片信息")
            
            return "\n".join(suggestions)
            
        except Exception as e:
            return f"图片分析遇到问题：{str(e)}。请尝试上传清晰的图片文件。"
    
    async def generate_location_based_password(self, locations: List[Dict], prompt: str = None) -> str:
        """基于位置生成密码建议"""
        await asyncio.sleep(1.5)
        
        if not locations:
            return "未检测到位置信息，请先选择地图位置。"
        
        suggestions = []
        suggestions.append(f"📍 **位置密码生成建议：**\n")
        suggestions.append(f"基于您选择的 {len(locations)} 个位置，推荐以下密码策略：\n")
        
        for i, location in enumerate(locations[:3]):
            lat = location.get('lat', 0)
            lng = location.get('lng', 0)
            
            # 基于坐标生成密码示例
            lat_str = str(abs(int(lat * 100)))[:3]
            lng_str = str(abs(int(lng * 100)))[:3]
            password_example = f"Loc{lat_str}{lng_str}@{2024+i}"
            
            suggestions.append(f"{i+1}. `{password_example}` - 基于坐标 ({lat:.4f}, {lng:.4f})")
        
        suggestions.append(f"\n🗺️ **位置密码安全提示：**")
        suggestions.append(f"- 避免使用家庭或工作地址")
        suggestions.append(f"- 可以使用旅行纪念地点")
        suggestions.append(f"- 结合坐标数字和个人符号")
        suggestions.append(f"- 定期更换避免地理位置泄露")
        
        return "\n".join(suggestions)
    
    def get_follow_up_suggestions(self, user_message: str) -> List[str]:
        """获取跟进建议"""
        suggestions = [
            "检测我的密码是否被泄露",
            "生成一个强密码",
            "密码安全最佳实践",
            "如何保护账户安全"
        ]
        
        if '密码' in user_message:
            suggestions.extend([
                "批量检测多个密码",
                "密码管理器推荐"
            ])
        
        return suggestions[:4]  # 返回前4个建议
    
    def _generate_password_analysis_response(self, message: str) -> str:
        """生成密码分析相关回复"""
        return """**密码安全分析服务** 🔐

我可以为您提供全面的密码安全分析：

🔍 **分析功能：**
• 密码强度评估 (长度、复杂度、熵值)
• 泄露数据库检测 (基于HaveIBeenPwned)
• 常见模式识别 (重复、连续、键盘模式)
• 个性化改进建议

📊 **评分维度：**
• 字符种类多样性
• 长度充足性  
• 随机性程度
• 已知泄露风险

请直接发送您要分析的密码，我会为您提供详细的安全评估报告。"""
    
    def _generate_password_recommendation_response(self, message: str) -> str:
        """生成密码推荐相关回复"""
        return """**智能密码生成建议** 💡

我可以基于不同方式为您生成安全密码：

🎯 **生成方式：**
• 文本描述 → 个性化密码
• 图片内容 → 视觉记忆密码  
• 地理位置 → 位置相关密码
• 随机生成 → 高强度密码

🔒 **安全原则：**
• 12位以上长度
• 包含大小写、数字、符号
• 避免个人信息泄露
• 独一无二不重复

您可以描述密码用途或上传图片，我会为您生成既安全又好记的密码建议！"""
    
    def _generate_password_general_response(self) -> str:
        """生成密码通用回复"""
        return """**PassAgent 密码安全助手** 🛡️

我是您的专业密码安全顾问，可以帮助您：

✅ **核心功能：**
• 密码强度分析与评分
• 数据泄露检测查询
• 个性化密码生成
• 安全策略建议

🔧 **使用方式：**
• 直接发送密码进行分析
• 上传图片生成记忆密码
• 选择地图位置创建位置密码
• 描述需求获取定制建议

请告诉我您希望分析密码还是生成新密码？"""