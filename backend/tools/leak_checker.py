"""
MCP Tool: 密码泄露检测
使用 HaveIBeenPwned API 检查密码是否已泄露
"""

import hashlib
import logging
from typing import Dict, Any
import httpx

logger = logging.getLogger(__name__)


async def check_password_leak_tool(password: str) -> Dict[str, Any]:
    """MCP Tool: 检测密码是否泄露"""
    print(f"接收到密码泄露检测请求")  # 调试信息

    try:
        if not password:
            return {"status": "error", "error": "密码不能为空"}

        # 使用 SHA-1 哈希
        sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        # 调用 HaveIBeenPwned API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.pwnedpasswords.com/range/{prefix}", timeout=10.0
            )

            if response.status_code != 200:
                return {
                    "status": "error",
                    "error": f"API调用失败: {response.status_code}",
                }

            # 解析响应
            leaked_count = 0
            for line in response.text.splitlines():
                if line.startswith(suffix):
                    leaked_count = int(line.split(":")[1])
                    break

            if leaked_count > 0:
                return {
                    "status": "success",
                    "is_leaked": True,
                    "leak_count": leaked_count,
                    "message": f"⚠️ 密码已泄露！在数据泄露中出现了 {leaked_count:,} 次",
                    "recommendation": "强烈建议立即更换此密码，并检查使用相同密码的其他账户",
                }
            else:
                return {
                    "status": "success",
                    "is_leaked": False,
                    "leak_count": 0,
                    "message": "✅ 密码未在已知泄露数据库中发现",
                    "recommendation": "密码相对安全，但仍建议使用强密码",
                }

    except httpx.TimeoutException:
        logger.error("密码泄露检测超时")
        return {"status": "error", "error": "网络请求超时，请稍后重试"}
    except Exception as e:
        logger.error(f"密码泄露检测失败: {str(e)}")
        return {"status": "error", "error": f"检测失败: {str(e)}"}


async def batch_check_password_leak_tool(passwords: list) -> Dict[str, Any]:
    """MCP Tool: 批量检测密码泄露"""
    print(f"接收到批量密码泄露检测请求，数量: {len(passwords)}")

    try:
        if not passwords:
            return {"status": "error", "error": "密码列表不能为空"}

        if len(passwords) > 50:  # 限制批量数量
            return {"status": "error", "error": "批量检测密码数量不能超过50个"}

        results = []
        for i, password in enumerate(passwords):
            if not password:
                results.append(
                    {
                        "index": i,
                        "password": "***",
                        "status": "error",
                        "error": "密码为空",
                    }
                )
                continue

            result = await check_password_leak_tool(password)
            results.append(
                {
                    "index": i,
                    "password": "***",  # 不返回明文密码
                    "status": result["status"],
                    "is_leaked": result.get("is_leaked", False),
                    "leak_count": result.get("leak_count", 0),
                    "message": result.get("message", ""),
                    "error": result.get("error"),
                }
            )

        # 统计信息
        leaked_count = sum(1 for r in results if r.get("is_leaked"))
        safe_count = len(results) - leaked_count

        return {
            "status": "success",
            "total_checked": len(passwords),
            "leaked_passwords": leaked_count,
            "safe_passwords": safe_count,
            "results": results,
            "summary": f"检测完成：{leaked_count} 个密码已泄露，{safe_count} 个密码相对安全",
        }

    except Exception as e:
        logger.error(f"批量密码泄露检测失败: {str(e)}")
        return {"status": "error", "error": f"批量检测失败: {str(e)}"}
