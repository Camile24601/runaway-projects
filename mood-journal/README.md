# 心情手账

## 本地测试地址

电脑本机：

```text
http://localhost:8000
```

同一个 Wi-Fi 下的手机：

```text
http://你的电脑局域网 IP:8000
```

## Supabase 建表

1. 打开 Supabase 项目。
2. 进入 SQL Editor。
3. 新建 Query。
4. 粘贴并运行 `supabase-setup.sql` 里的全部 SQL。
5. 根据 `config.example.js` 新建本地 `config.js`，填入自己的 Supabase URL 和 publishable key。
6. 回到网页，输入一个“同步暗号”，点击“同步”。
7. 手机和电脑输入同一个同步暗号，就会读取同一份云端记录。

## 当前隐私说明

这个版本适合个人测试和轻量使用。同步暗号会在浏览器里转成哈希值再保存到云端，但目前还没有正式登录系统。后续如果要更私密，可以升级成 Supabase Auth 登录版。
