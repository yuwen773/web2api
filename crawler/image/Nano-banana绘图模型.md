## Nano-banana 2 绘图 API

                "label": "Nano-banana绘图模型",
                "value": "gemini-2.5-flash-image",

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
  --data-raw ^"^{^\^"text^\^":^\^"^ ^ ^ ^  ^ ^ ^ ^\^\^\^"^ ^ AI^ ^ ^\^\^\^"^ ^ ^ ^ ^\^",^\^"sessionId^\^":563021,^\^"files^\^":^[^]^}^"
```


整个响应
response:
```json
data: {"id":"2036758982604886016","type":"string","data":"当然，这是一个","code":0}

data: {"id":"2036758982604886016","type":"string","data":"“","code":0}

data: {"id":"2036758982604886016","type":"string","data":"每日AI资讯”","code":0}

data: {"id":"2036758982604886016","type":"string","data":"的封面图：","code":0}

data: {"id":"2036758982604886016","type":"string","data":"\n","code":0}

data: {"id":"2036758982604886016","type":"string","data":"![image](https://googlecdn.datas.systems/storage/response_images/831/2026/03/25/1774436166416765852_5573.png)","code":0}

data: {"id":"2036758982604886016","type":"object","data":{"id":4363459,"created":"2026-03-25 18:55:57","updated":"2026-03-25 18:56:06","sessionId":563021,"userText":"帮我生成 标题为\"每日AI资讯\"的封面图","aiText":"当然，这是一个“每日AI资讯”的封面图：\n![image](https://googlecdn.datas.systems/storage/response_images/831/2026/03/25/1774436166416765852_5573.png)","uid":18605,"ip":"222.247.225.33","taskId":"2036758982604886016","model":"Nano-banana绘图模型","deductCount":100000,"refundCount":0,"promptTokens":223,"completionTokens":54,"contextTokens":195,"useTokens":277,"useImages":null,"useFiles":null,"useAppId":0,"appendDeductCount":0,"userStop":false},"code":0}

data: [DONE]

```