## Nano-banana 2 绘图 API

                "label": "Nano-banana 2 绘图",
                "value": "gemini-3.1-flash-image-preview",

```bash
curl ^"https://ai.aurod.cn/api/chat/completions^" ^
  -H ^"accept: text/event-stream^" ^
  -H ^"accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6^" ^
  -H ^"authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjE4NjA1LCJzaWduIjoiNTU0MDhlMTdkNzIzNTIxNWNhODhkYWE2Mzg2MmY2NGEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc3NTczMDAzNCwibmJmIjoxNzc0NDM0MDM0LCJpYXQiOjE3NzQ0MzQwMzR9.vnvQje0L2CHZ7QwBOxF3Qq8OhrHTijadfxL_akltJ9Y^" ^
  -H ^"cache-control: no-cache^" ^
  -H ^"content-type: application/json^" ^
  -b ^"server_name_session=3cbc176e0f2260d6e1517874502f4f1a^" ^
  -H ^"origin: https://ai.aurod.cn^" ^
  -H ^"pragma: no-cache^" ^
  -H ^"priority: u=1, i^" ^
  -H ^"referer: https://ai.aurod.cn/chat?_userMenuKey=chat^" ^
  -H ^"sec-ch-ua: ^\^"Chromium^\^";v=^\^"146^\^", ^\^"Not-A.Brand^\^";v=^\^"24^\^", ^\^"Microsoft Edge^\^";v=^\^"146^\^"^" ^
  -H ^"sec-ch-ua-mobile: ?0^" ^
  -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^" ^
  -H ^"sec-fetch-dest: empty^" ^
  -H ^"sec-fetch-mode: cors^" ^
  -H ^"sec-fetch-site: same-origin^" ^
  -H ^"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0^" ^
  -H ^"x-app-version: 2.16.0^" ^
  --data-raw ^"^{^\^"text^\^":^\^"^ ^ ^ ^  ^ ^ ^ ^\^\^\^"^ ^ AI^ ^ ^\^\^\^"^ ^ ^ ^ ^\^",^\^"sessionId^\^":496862,^\^"files^\^":^[^]^}^"
```


整个响应
response:
```json
data: {"id":"2036750722346782720","type":"string","data":"\n\n![image](https://cn-nb1.rains3.com/jay/1774434209943376277-dd69151f1d5c.jpg)\n","code":0}

data: {"id":"2036750722346782720","type":"string","data":"\n\n![image](https://cn-nb1.rains3.com/jay/1774434236312566151-24571fc4b044.jpg)\n","code":0}

data: {"id":"2036750722346782720","type":"string","data":"\n\n![image](https://cn-nb1.rains3.com/jay/1774434264441457321-5af3daee77df.jpg)\n","code":0}

data: {"id":"2036750722346782720","type":"object","data":{"id":4363044,"created":"2026-03-25 18:23:07","updated":"2026-03-25 18:25:20","sessionId":496862,"userText":"帮我生成 标题为\"每日AI资讯\"的封面图","aiText":"\n\n![image](https://cn-nb1.rains3.com/jay/1774434209943376277-dd69151f1d5c.jpg)\n\n\n![image](https://cn-nb1.rains3.com/jay/1774434236312566151-24571fc4b044.jpg)\n\n\n![image](https://cn-nb1.rains3.com/jay/1774434264441457321-5af3daee77df.jpg)\n","uid":18605,"ip":"222.247.225.33","taskId":"2036750722346782720","model":"Nano-banana 2 绘图","deductCount":880000,"refundCount":0,"promptTokens":271,"completionTokens":99,"contextTokens":243,"useTokens":370,"useImages":null,"useFiles":null,"useAppId":0,"appendDeductCount":0,"userStop":false},"code":0}

data: [DONE]


```