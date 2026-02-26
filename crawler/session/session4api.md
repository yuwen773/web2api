## 删除会话

```bash
curl ^"https://ai.aurod.cn/api/chat/session/493590^" ^
  -X ^"DELETE^" ^
  -H ^"accept: application/json, text/plain, */*^" ^
  -H ^"accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6^" ^
  -H ^"authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjE4NjA1LCJzaWduIjoiNTU0MDhlMTdkNzIzNTIxNWNhODhkYWE2Mzg2MmY2NGEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc3NDc3ODUwMywibmJmIjoxNzcyMTAwMTAzLCJpYXQiOjE3NzIxMDAxMDN9.qJbvq0YFSUzdzaSK0iDgPv7nohNpTLwB7kV-vDsg6qY^" ^
  -b ^"server_name_session=5521b2b0d0c90d6ccce57cc1912bef3c^" ^
  -H ^"origin: https://ai.aurod.cn^" ^
  -H ^"priority: u=1, i^" ^
  -H ^"referer: https://ai.aurod.cn/chat?_userMenuKey=chat^" ^
  -H ^"sec-ch-ua: ^\^"Not:A-Brand^\^";v=^\^"99^\^", ^\^"Microsoft Edge^\^";v=^\^"145^\^", ^\^"Chromium^\^";v=^\^"145^\^"^" ^
  -H ^"sec-ch-ua-mobile: ?0^" ^
  -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^" ^
  -H ^"sec-fetch-dest: empty^" ^
  -H ^"sec-fetch-mode: cors^" ^
  -H ^"sec-fetch-site: same-origin^" ^
  -H ^"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0^" ^
  -H ^"x-app-version: 2.14.0^"
```

response
```json
{"code":0,"data":null,"msg":""}
```