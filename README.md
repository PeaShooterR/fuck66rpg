### 使用方法

```
pip install urllib3

python 66rpgProjectDropper.py
```

根据提示输入游戏链接以及版本号即可，文件会下载到同目录下

-----
### 工作原理
以下接口通过截包网页、手机app以及制作工具获得
- 通过gindex获取guid

    参考https://github.com/ssz66666/66rpg-spoofer
- 通过guid获取 gindex ver name uid create_time

    http://www.66rpg.com/api/common/versions?guid=$guid$
- 通过guid+ver获取资源文件Map.bin

    http://wcdn1.cgyouxi.com/web/$guid$/$ver$/Map.bin
- 通过guid+ver获取资源文件（网页客户端）

    https://cgv2.66rpg.com/api/oapi_map.php?action=create_bin&guid=$guid$&version=$ver$&quality=32
- 资源文件

    http://wcdn1.cgyouxi.com/shareres/$md5前两位$/$md5$
- 资源文件（网页客户端的CDN）

    https://dlcdn1.cgyouxi.com/shareres/$md5前两位$/$md5$


-----

### 运行游戏
v1工具制作的游戏可以将制作工具中的.swf文件拷至游戏文件夹后直接运行

v2工具制作的游戏可以参考https://github.com/MXWXZ/AVGMakerStarter


##### 制作工具下载（官方）：

- v1制作工具32位

    https://cg.66rpg.com/redirect.php?t=1

- v1制作工具64位

    http://cg.66rpg.com/redirect.php?t=33

- v2制作工具

    https://cg.66rpg.com/redirect.php?t=301

-----
### 关于工程文件
橙光游戏的工程文件保存在阿里云oss内

由于制作工具内以**明码**储存了RAM账号的AccessKey和AccessKeySecret，且**多年未曾更改**，才得以使下载成为可能

本程序仅内置了阿里云oss的SDK，**未提供**工程文件实质下载

部分v1游戏的工程文件也可以通过逆向Game.bin获得