# 前端界面

## 登录注册界面
- [ ] 这个还是要尽快做一下，用交大邮箱注册，验证码、忘记密码等

## 侧边栏

收起状态下，
- [ ] Logo放最左上角
- [ ] Logo下方是新建对话、查看上传过的文件、询问记录三个按钮（仅icon）
- [ ] 最下方为用户头像，用户头像下方为侧边栏缩回伸出按钮
- [ ] 点击用户头像，出现设置、帮助、退出登录这些功能
- [ ] 设置包括头像、外观、模型API
- [ ] 设置这里还要考虑修改密码

伸出状态下，
- [ ] Logo放最左上角，如果左边有空位的话加上PassAgent的名字
- [ ] Logo下方是新建对话、查看上传过的文件、询问记录三个按钮（icon+文字说明）
- [ ] 历史记录项展示所有的历史记录
- [ ] 历史记录按时间排序（时间可展示）
- [ ] 历史记录提供模糊搜索功能
- [ ] 最下方是用户头像，用户头像的右侧为侧边栏缩回伸出按钮

## 主界面
- [ ] 欢迎使用 PassAgent🤗改成Logo+名称
- [ ] 上传文件功能在输入聊天框时要显示
- [ ] 右上角添加私密模式选项，该选项进入后界面颜色改变，并使用本地模型

## 对话界面
- [ ] 主要是要展示运行顺序
- [ ] 每一个回复添加重新生成、复制、点赞、点踩以及导出到PDF的按钮

# 数据库设计

1. users（用户表）
- user_id (主键)
- email (唯一，交大邮箱)
- password_hash (加密密码)
- avatar_url (头像URL)
- theme (外观设置：light/dark)
- created_at (注册时间)
2. user_api_configs（用户API配置表）
- config_id (主键)
- user_id (外键 → users)
- model_type (qwen/deepseek/local)
- api_key (加密存储)
- model_name (具体模型名称)
- is_default (是否默认使用)
- created_at
3. sessions（会话表）
- session_id (主键)
- user_id (外键 → users)
- title (会话标题)，这一步可以通过LLM做
- is_private (是否私密模式)
- created_at
- updated_at
4. messages（消息表）
- message_id (主键)
- session_id (外键 → sessions)
- user_id (外键 → users)
- content (消息内容)
- message_type (user/assistant)
- created_at
5. feedback（用户反馈表）
- feedback_id (主键)
- message_id (外键 → messages，唯一)
- user_id (外键 → users)
- feedback_type (like/dislike/null)
- created_at
6. uploaded_files（上传文件表）
- file_id (主键)
- user_id (外键 → users)
- session_id (外键 → sessions，可选关联)
- filename (原文件名)
- file_path (存储路径)
- file_size (文件大小)
- file_type (MIME类型)
- uploaded_at
7. password_analysis（密码分析记录表）
- analysis_id (主键)
- session_id (外键 → sessions)
- user_id (外键 → users)
- original_password_hash (原密码哈希)
- target_password_hash (目标密码哈希)
- hashcat_rule (生成的规则)
- strength_score (强度评分 0-100)
- is_leaked (是否泄露)
- analysis_type (transformation/strength/recommendation)
- created_at


