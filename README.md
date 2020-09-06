# ID Card

本服务用于提取身份证号中的相关信息。

## API

```
GET /search?id={identity}
identity: 15位或18位的身份证号
```

获取成功：

property    |type   |NN |description
------------|-------|---|-------------
id          |string |T  |身份证号
id2         |string |   |修正校验码后的身份证号
birthday    |date   |T  |生日
gender      |char   |T  |性别
province    |string |T  |省份
city        |string |T  |市
district    |string |T  |区县
region_code |string |T  |行政区号

## 启动服务

```bash
gunicorn -w 4 -b 0.0.0.0:8000 idcard:app
```
