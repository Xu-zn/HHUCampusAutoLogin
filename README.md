# HHUCampusAutoLogin
基于playwright实现的自动登录河海校园网

**安装依赖**

```bat
pip install -r requirements.txt
```

如果不想用到`loguru`、`toml`也可以自己手动安装一下`requests`和`playwright`

**修改config.toml**

配置自己的学号、密码、登录服务

**修改浏览器**

如果没有基于chromium的Edge浏览器，那就把`connect.py`第55行的`executable_path`的路径改为chrome的绝对路径。

也可以使用Firefox，需要将`playwright.chromium`改成`playwright.firefox`，`executable_path`改为firefox的绝对路径。

**打包（如果需要）** 

```bat
pyinstaller -Fw connect.py
``` 

`-F` 打包成单文件

`-w` 隐藏黑黑的控制台

将`dist/connect.exe`文件复制到想要放的地方，别忘了`config.toml`也要复制过去

**配置任务计划（如果需要）**

1. `win + r` 输入`taskschd.msc`回车
2. 右侧`操作` -> `创建基本任务`
3. 自己填写任务名、下一步
4. 触发器选择`计算机启动时`、下一步、下一步
5. 程序或脚本路径选择、下一步
6. 完成

> 程序中探测网络与win10的探测方式一致；
> 
> 如果使用`-w`打包，停止程序的时候需要在任务管理器中停止（占用较大的那个）;
> 
> 另外，也可以在存放exe目录下使用powershell，输入
> ```ps
Stop-Process -Id (Get-Content pid)
```
