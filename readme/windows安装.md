在开始采集POI之前，请根据自己的情况安装合适的客户端。

目前仅支持windows环境，mac环境在打包时一直遇到问题未能成功打包，考虑到使用macOs的同学毕竟比较少，所以先不封装了。

有需要的同学可以通过公众号或者知乎给我私信，我会尽快将相应的客户端上线。

本文仅讲解Windows客户端安装方法与常见的问题汇总。

 

**一、下载EasyPoi Windows客户端**

下载地址：

* 天翼云盘：
* 百度网盘：

如果发现下载地址失效，请在微信搜索**人文互联网** 公众号，关注后回复"poi"获取最新的下载链接；

 

**1、系统要求**

 

Win7/Win10（x64位）

XP系统和32位系统未测试，不保证可以使用。

 

特别说明：

a. windows如何查看自己电脑是什么系统？

win10 找到【此电脑】，右键，选择【属性】即可查看。

![win10_version](C:\Users\soari\OneDrive\myGitHubProjects\easypoi\readme\win10_version.png)

 win7 找到【计算机】，右键，选择【属性】即可查看

![](C:\Users\soari\OneDrive\myGitHubProjects\easypoi\readme\win7_version.png)

**2、下载安装**

①下载EasyPoi安装文件（.exe）

② 关闭所有杀毒软件,如果是win10 可能会被windows defender拦截，请将其设置为允许。

③ 双击.exe文件，开始安装

![setup](C:\Users\soari\OneDrive\myGitHubProjects\easypoi\readme\setup.png)

④ 安装完成后，在开始菜单或桌面上找到EasyPoi的快捷方式

⑤ 启动EasyPoi

如果提示无写入权限，请在EasyPoi的快捷方式上右键，选择”管理员身份运行“







 

**二、安装过程中常见问题**

 

按照以上常规操作，无法安装八爪鱼Windows客户端？您可能遇到以下问题：

 

**1、安装过程中提示【安装已终止，安装程序并未成功地运行完成】**

 

**![img](https://www.bazhuayu.com/media/119506/%E5%BE%AE%E4%BF%A1%E6%88%AA%E5%9B%BE_20200318104911.png)**

 

出现原因：之前安装过老版本，没有卸载干净，有残留。

 

解决方法① ：删除八爪鱼8缓存文件夹。找到\AppData\Roaming\Octopus8 文件夹，将Octopus8 文件夹删除。

 

![img](https://www.bazhuayu.com/media/119507/%E5%BE%AE%E4%BF%A1%E6%88%AA%E5%9B%BE_20200318111246.png)

 

解决方法②：打开【控制面板】-【程序】，将之前安装过的版本卸载干净。

 

![img](https://www.bazhuayu.com/media/119508/%E5%BE%AE%E4%BF%A1%E6%88%AA%E5%9B%BE_20200318111421.png)

 

 

**二、安装成功进入客户端，几分钟后自动退出。再次进入提示【找不到路径，没有权限】**

 

出现原因：电脑上安装了杀毒软件，将八爪鱼的部分程序删掉了。

 

解决方法：将电脑上的杀毒软件关掉。