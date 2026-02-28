"use client";

import { useState } from "react";
import { useAuth } from "@/providers/Auth";
import { apiPut, apiDelete, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PasswordInput } from "@/components/ui/password-input";
import { Lock } from "lucide-react";

export function AccountPage() {
  const { user, updateUser, logout } = useAuth();
  const [nickname, setNickname] = useState(user?.nickname || "");
  const [saving, setSaving] = useState(false);

  const [oldPwd, setOldPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [pwdMsg, setPwdMsg] = useState("");
  const [pwdSaving, setPwdSaving] = useState(false);

  const [confirmDelete, setConfirmDelete] = useState(false);

  const handleSaveNickname = async () => {
    setSaving(true);
    try {
      await apiPut("/api/user/profile", { nickname });
      updateUser({ nickname });
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (!oldPwd || !newPwd || !confirmPwd) return;
    if (newPwd !== confirmPwd) {
      setPwdMsg("两次输入的新密码不一致");
      return;
    }
    if (newPwd.length < 6) {
      setPwdMsg("新密码长度至少6位");
      return;
    }
    setPwdSaving(true);
    setPwdMsg("");
    try {
      await apiPut<{ message: string }>("/api/user/password", {
        old_password: oldPwd,
        new_password: newPwd,
      });
      setPwdMsg("密码修改成功");
      setOldPwd("");
      setNewPwd("");
      setConfirmPwd("");
    } catch (e) {
      setPwdMsg(e instanceof ApiError ? e.message : "修改失败");
    } finally {
      setPwdSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    try {
      await apiDelete("/api/user/account");
      logout();
    } catch {
      // ignore
    }
  };

  return (
    <div className="space-y-6">
      <h3 className="text-base font-medium text-slate-900 dark:text-slate-100">账户设置</h3>

      <div className="space-y-3">
        <div>
          <label className="text-sm text-slate-600 dark:text-slate-400 mb-1.5 block">邮箱</label>
          <div className="relative">
            <Input value={user?.email || ""} disabled className="bg-slate-50 dark:bg-slate-900 pr-10" />
            <Lock className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          </div>
        </div>
        <div>
          <label className="text-sm text-slate-600 dark:text-slate-400 mb-1.5 block">昵称</label>
          <Input
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            placeholder="输入昵称"
          />
        </div>
        <Button
          onClick={handleSaveNickname}
          disabled={saving || nickname === (user?.nickname || "")}
          className="w-full"
          size="sm"
        >
          {saving ? "保存中..." : "保存"}
        </Button>
      </div>

      {/* 修改密码 */}
      <div className="border-t border-dashed border-slate-200 dark:border-slate-700 pt-5">
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-3 text-center">修改密码</p>
        <div className="space-y-3">
          <div>
            <label className="text-sm text-slate-600 dark:text-slate-400 mb-1.5 block">当前密码</label>
            <PasswordInput
              value={oldPwd}
              onChange={(e) => setOldPwd(e.target.value)}
              placeholder="输入当前密码"
            />
          </div>
          <div>
            <label className="text-sm text-slate-600 dark:text-slate-400 mb-1.5 block">新密码</label>
            <PasswordInput
              value={newPwd}
              onChange={(e) => setNewPwd(e.target.value)}
              placeholder="输入新密码"
            />
          </div>
          <div>
            <label className="text-sm text-slate-600 dark:text-slate-400 mb-1.5 block">确认新密码</label>
            <PasswordInput
              value={confirmPwd}
              onChange={(e) => setConfirmPwd(e.target.value)}
              placeholder="再次输入新密码"
            />
          </div>
          {pwdMsg && (
            <p className={`text-xs ${pwdMsg.includes("成功") ? "text-green-600" : "text-red-500"}`}>
              {pwdMsg}
            </p>
          )}
          <Button
            onClick={handleChangePassword}
            disabled={pwdSaving || !oldPwd || !newPwd || !confirmPwd}
            variant="outline"
            className="w-full"
            size="sm"
          >
            {pwdSaving ? "修改中..." : "修改密码"}
          </Button>
        </div>
      </div>

      {/* 删除账户 */}
      <div className="border-t border-dashed border-slate-200 dark:border-slate-700 pt-5">
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
          删除账户后所有数据将永久丢失，包括对话记录、记忆和上传文件。
        </p>
        {!confirmDelete ? (
          <Button
            variant="outline"
            className="w-full text-red-600 border-red-200 hover:bg-red-50 dark:text-red-400 dark:border-red-800 dark:hover:bg-red-950"
            size="sm"
            onClick={() => setConfirmDelete(true)}
          >
            删除账户
          </Button>
        ) : (
          <div className="space-y-2">
            <p className="text-xs text-red-500">此操作不可撤销，确定要删除账户吗？</p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="flex-1"
                onClick={() => setConfirmDelete(false)}
              >
                取消
              </Button>
              <Button
                size="sm"
                className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                onClick={handleDeleteAccount}
              >
                确认删除
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
