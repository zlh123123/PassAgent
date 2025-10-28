"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Shield, Zap, Code2, ArrowRight } from "lucide-react";

export default function WelcomePage(): React.ReactNode {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  return (
    <div className="min-h-screen bg-white text-slate-900 overflow-hidden flex flex-col">
      {/* 极简背景 */}
      <div className="fixed inset-0 pointer-events-none opacity-40">
        <div 
          className="w-full h-full"
          style={{
            backgroundImage: "radial-gradient(circle at 1px 1px, rgba(0,0,0,0.05) 1px, transparent 1px)",
            backgroundSize: "40px 40px",
          }}
        />
      </div>

      {/* 内容容器 */}
      <div className="relative z-10 flex-1 flex flex-col">
        {/* 导航栏 */}
        <nav className="flex items-center justify-between px-8 py-6 border-b border-slate-200">
          <div className={`flex items-center gap-3 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-10"}`}>
            <div className="relative w-10 h-10">
              <Image
                src="/favicon.ico"
                alt="PassAgent Logo"
                width={40}
                height={40}
                className="rounded-lg"
              />
            </div>
            <div>
              <h1 className="text-2xl font-black text-slate-900">
                PassAgent
              </h1>
              <p className="text-xs text-slate-500">基于LLM的口令安全智能助手</p>
            </div>
          </div>

          <div className={`flex gap-3 transition-all duration-1000 delay-200 ${isLoaded ? "opacity-100 translate-x-0" : "opacity-0 translate-x-10"}`}>
            <Link href="/auth/login">
              <Button 
                variant="outline"
                className="text-slate-900 border-slate-300 hover:bg-slate-50 rounded-lg font-medium"
              >
                登录
              </Button>
            </Link>
            <Link href="/auth/register">
              <Button className="bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-medium">
                开始使用
              </Button>
            </Link>
          </div>
        </nav>

        {/* 主要内容 */}
        <div className="flex-1 flex flex-col items-center justify-center px-6 py-20">

          {/* 标题部分 */}
          <div className={`text-center mb-16 max-w-4xl transition-all duration-1000 delay-300 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}>
            <h2 className="text-6xl md:text-7xl font-black mb-6 leading-tight text-slate-900">
              守护你的数字身份
            </h2>
            <p className="text-lg md:text-xl text-slate-600 mb-10 font-light leading-relaxed">
              智能分析口令强度、检测口令泄露、获取专业建议
            </p>
            <div className="flex gap-4 justify-center flex-wrap">
              <Link href="/auth/register">
                <Button 
                  size="lg" 
                  className="bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-lg px-8 group font-medium"
                >
                  立即开始
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <Link href="/auth/login">
                <Button 
                  size="lg" 
                  variant="outline"
                  className="border-slate-300 text-slate-900 hover:bg-slate-50 rounded-lg text-lg px-8 font-medium"
                >
                  已有账户登录
                </Button>
              </Link>
            </div>
          </div>

          {/* 功能卡片网格 */}
          <div className={`grid md:grid-cols-3 gap-6 max-w-5xl transition-all duration-1000 delay-500 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}>
            {[
              {
                icon: Shield,
                title: "口令强度评分",
                desc: "实时分析口令强度，多维度安全评估",
              },
              {
                icon: Zap,
                title: "智能改进建议",
                desc: "个性化优化方案，让口令更安全",
              },
              {
                icon: Code2,
                title: "泄露检测",
                desc: "检查口令是否在数据泄露中出现",
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="group relative bg-white border border-slate-200 rounded-2xl p-8 hover:border-slate-300 hover:shadow-md transition-all duration-300"
              >
                <div className="relative">
                  <div className="w-12 h-12 bg-slate-100 rounded-xl mb-6 flex items-center justify-center group-hover:bg-slate-200 transition-colors">
                    <feature.icon className="w-6 h-6 text-slate-900" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-slate-600 text-sm leading-relaxed font-light">
                    {feature.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 页脚 */}
        <footer className={`border-t border-slate-200 py-8 px-6 bg-slate-50 transition-all duration-1000 delay-700 ${isLoaded ? "opacity-100" : "opacity-0"}`}>
          <div className="max-w-6xl mx-auto text-center">
            <p className="text-slate-600 text-sm font-light mb-2">
              &copy; 2025 PassAgent. 智能守护您的口令安全。
            </p>
            <p className="text-slate-500 text-xs font-light">
              本产品用于教育和研究目的。请合理使用。
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}