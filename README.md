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

* [ ] Make system proxy setting configuration automatic.
    * [x] MacOS
    * [ ] Windows
    * [ ] Linux
* [ ] Make the command line setting configuration automatic.
    * [ ] MacOS
        * [x] .zshrc
        * [ ] auto detect the env file.
    * [ ] Windows
    * [ ] Linux
* [ ] 实现从数据中心拉下来当前地址里位置对应的忽略列表, 以此实现根据地理位置确定忽略哪些地址走代理.
* [ ] Combine with the [zerotier-cli](https://github.com/zerotier/ZeroTierOne).
* [ ] Implementing upstream-configurable clash / agent.
* [ ] Publish as python site-packages.
* [ ] Release the pre-built packages for all the platform:
    * [ ] MacOSX
    * [ ] Windows
    * [ ] Linux
