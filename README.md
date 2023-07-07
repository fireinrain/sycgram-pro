

## 配置

- 需要两个参数：`api_id`、`api_hash`
- 如果没有，点击这个[电报链接](https://my.telegram.org/apps)申请


## 安装与更新

```shell
# 脚本的【安装】都是前台运行，完成安装后如无报错可先后使用Ctrl+P、Ctrl+Q挂到后台运行
bash <(curl -fsL "https://raw.githubusercontent.com/h88782481/sycgram/main/install.sh")
```

## 更新存在的问题

> 指令更新是通过拉取一次`watchower`来更新。

watchower存在的问题：有一定的概率拉取最新镜像后移除容器后没法再次创建容器，sycgram就会失联。


## 指令说明

- 使用`-help`查看指令列表


## 迁移备份

1. 停止容器
2. 打包`/opt/sycgram`文件夹到新环境相同位置
3. 在新环境运行sycgram管理脚本


## 自定义指令前缀及指令别名

- 脚本更新：都会覆盖本地的`command.yml`，原文件会备份到`command目录`。
- 指令更新：本地的`command.yml`不会被覆盖
- 可以通过指令修改前缀和别名
- 指令别名只支持单别名和源名（不再支持多别名）


## 注意事项

- 脚本仅适用于Ubuntu/Debian，其它系统自行解决~
- 按个人需求随缘更，仅用于学习用途
- 如果号码等输入错误了，重新安装即可
- 如果偷贴纸没有反应，先给贴纸Bot `@Stickers` 随便发点消息
