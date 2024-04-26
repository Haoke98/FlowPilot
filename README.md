# FlowPilot

A net flow pilot in order to handle some proxy configuration automatically.

### Usage

```shell
python FlowPilot-cli.py 
```

![](assets/截屏2024-04-26%2012.59.44.png)

```shell
python proxy-cli.py -h 10.2.1.0 -p 7890 -bypass-domains *.baidu.com,*.gitee.com
```

### TODO

* [ ] Make this way automatic by using the applescript.
    * [x] MacOS
    * [ ] Windows
    * [ ] Linux
* [ ] 实现从数据中心拉下来当前地址里位置对应的忽略列表, 以此实现根据地理位置确定忽略哪些地址走代理.
* [ ] 利用ClashWindows的源码实现自动配置系统代理设置.π