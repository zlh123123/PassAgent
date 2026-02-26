# models_deploy 使用说明

## 1 start.sh 启动方式

在 `models_deploy` 目录下执行：

```bash
cd /models_deploy
chmod +x start.sh
./start.sh
```


---

## 2 AutoDL 穿透使用 TTS 服务（端口映射）

### 2.1 启动 start.sh

见上

### 2.2 在本地主机建立 SSH 端口转发

假设 AutoDL 服务器 SSH 登录指令为：

```bash
ssh -p 16845 root@connect.cqa1.seetacloud.com
```

则在**本地主机**终端执行：

```bash
ssh -CNg -L 6006:127.0.0.1:6006 -p 16845 root@connect.cqa1.seetacloud.com
```

输入密码后，终端会“卡住”且无输出，这是正常现象。请保持该终端运行，不要关闭。

