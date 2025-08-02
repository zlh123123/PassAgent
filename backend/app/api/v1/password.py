# backend/app/api/v1/password.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import asyncio

from app.models.api_models import (
    PasswordAnalysisRequest,
    PasswordAnalysisResponse,
    PasswordBatchRequest,
    PasswordStrengthResult
)
from app.tools.leak_checker import PasswordLeakChecker
from app.services.password_service import PasswordService

router = APIRouter()

@router.post("/analyze", response_model=PasswordAnalysisResponse)
async def analyze_password(request: PasswordAnalysisRequest):
    """分析单个密码"""
    try:
        async with PasswordLeakChecker() as leak_checker:
            # 检查密码泄露
            leak_result = await leak_checker.check_password_leak(request.password)
            
            # 获取密码强度分析服务
            password_service = PasswordService()
            
            # 分析密码强度
            strength_result = password_service.analyze_strength(
                request.password,
                include_suggestions=request.include_suggestions
            )
            
            # 合并结果
            response = PasswordAnalysisResponse(
                password_length=len(request.password),
                strength_score=strength_result["score"],
                strength_level=strength_result["level"],
                is_leaked=leak_result["is_leaked"],
                leak_count=leak_result["leak_count"],
                risk_level=leak_result["risk_level"],
                suggestions=strength_result.get("suggestions", []) if request.include_suggestions else [],
                analysis_details={
                    "has_uppercase": strength_result["has_uppercase"],
                    "has_lowercase": strength_result["has_lowercase"], 
                    "has_numbers": strength_result["has_numbers"],
                    "has_symbols": strength_result["has_symbols"],
                    "entropy": strength_result["entropy"],
                    "common_patterns": strength_result["common_patterns"]
                },
                breach_sources=leak_result["breach_sources"]
            )
            
            return response
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"密码分析失败: {str(e)}")

@router.post("/batch-analyze")
async def batch_analyze_passwords(request: PasswordBatchRequest):
    """批量分析密码"""
    try:
        async with PasswordLeakChecker() as leak_checker:
            # 批量检查泄露
            leak_results = await leak_checker.batch_check_passwords(request.passwords)
            
            password_service = PasswordService()
            results = []
            
            for password in request.passwords:
                # 分析强度
                strength_result = password_service.analyze_strength(password)
                leak_result = leak_results.get(password, {
                    "is_leaked": None,
                    "leak_count": 0,
                    "risk_level": "unknown",
                    "breach_sources": []
                })
                
                result = PasswordStrengthResult(
                    password=password[:3] + "*" * (len(password) - 3),  # 脱敏显示
                    strength_score=strength_result["score"],
                    strength_level=strength_result["level"],
                    is_leaked=leak_result["is_leaked"],
                    leak_count=leak_result["leak_count"],
                    risk_level=leak_result["risk_level"]
                )
                results.append(result)
            
            return {"results": results, "total_count": len(request.passwords)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量分析失败: {str(e)}")

@router.get("/check-leak/{password}")
async def check_password_leak(password: str):
    """检查单个密码泄露情况"""
    try:
        async with PasswordLeakChecker() as checker:
            result = await checker.check_password_leak(password)
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"泄露检查失败: {str(e)}")