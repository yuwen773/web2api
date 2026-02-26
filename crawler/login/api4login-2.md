疑似为获取模型列表 的接口

## tmpl 可用模型列表（我自己判断的）


```bash
curl ^"https://ai.aurod.cn/api/chat/tmpl^" ^
  -H ^"accept: application/json, text/plain, */*^" ^
  -H ^"accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6^" ^
  -H ^"authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjE4NjA1LCJzaWduIjoiNTU0MDhlMTdkNzIzNTIxNWNhODhkYWE2Mzg2MmY2NGEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc3NDc3ODUwMywibmJmIjoxNzcyMTAwMTAzLCJpYXQiOjE3NzIxMDAxMDN9.qJbvq0YFSUzdzaSK0iDgPv7nohNpTLwB7kV-vDsg6qY^" ^
  -b ^"server_name_session=5521b2b0d0c90d6ccce57cc1912bef3c^" ^
  -H ^"priority: u=1, i^" ^
  -H ^"referer: https://ai.aurod.cn/chat^" ^
  -H ^"sec-ch-ua: ^\^"Not:A-Brand^\^";v=^\^"99^\^", ^\^"Microsoft Edge^\^";v=^\^"145^\^", ^\^"Chromium^\^";v=^\^"145^\^"^" ^
  -H ^"sec-ch-ua-mobile: ?0^" ^
  -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^" ^
  -H ^"sec-fetch-dest: empty^" ^
  -H ^"sec-fetch-mode: cors^" ^
  -H ^"sec-fetch-site: same-origin^" ^
  -H ^"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0^" ^
  -H ^"x-app-version: 2.14.0^"
```



```json
{
    "code": 0,
    "data": {
        "cm": true,
        "defModel": "gpt-4.1-mini",
        "defaultChat": "\u003cp\u003e您好，有什么可以帮助您的吗？\u003c/p\u003e",
        "genLine": 2,
        "genTitle": false,
        "mFileCount": 5,
        "mFileSize": 5,
        "mcp": null,
        "models": [
            {
                "label": "GT-5-Chat【流式/长上下文】",
                "value": "gpt-5-chat",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/f19627a7d38ae8bb2635b32bf7553965.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5-Chat-Latest【流式/长上下文】",
                "value": "gpt-5-chat-latest",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/f19627a7d38ae8bb2635b32bf7553965.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5.1-Chat【流式】",
                "value": "gpt-5.1-chat",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/f19627a7d38ae8bb2635b32bf7553965.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5.1-Chat-Latest【流式】",
                "value": "gpt-5.1-chat-latest",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/f19627a7d38ae8bb2635b32bf7553965.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5-nano【无限上下文】",
                "value": "gpt-5-nano",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/f19627a7d38ae8bb2635b32bf7553965.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5-nano-2025-08-07【无限上下文】",
                "value": "gpt-5-nano-2025-08-07",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/f19627a7d38ae8bb2635b32bf7553965.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5-mini",
                "value": "gpt-5-mini",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/f19627a7d38ae8bb2635b32bf7553965.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "GPT-5 mini 是一个小巧、快速且经济实惠的模型，在许多智能和视觉相关任务中可以媲美或超越 GPT-4.1。支持400k个令牌的上下文\n要指示机器人使用更多的推理努力，请在消息末尾添加 --reasoning_effort，可选值为\"minimal\"、\"low\"、\"medium\"或\"high\"",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5-mini-2025-08-07",
                "value": "gpt-5-mini-2025-08-07",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/f19627a7d38ae8bb2635b32bf7553965.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5",
                "value": "gpt-5",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/f19627a7d38ae8bb2635b32bf7553965.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5-2025-08-07",
                "value": "gpt-5-2025-08-07",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/f19627a7d38ae8bb2635b32bf7553965.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5.1",
                "value": "gpt-5.1",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/10/14/68ed5e4493a22.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5.1-2025-11-13",
                "value": "gpt-5.1-2025-11-13",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/10/14/68ed5e4493a22.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5.2",
                "value": "gpt-5.2",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/10/14/68ed5e4493a22.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5.1-codex",
                "value": "gpt-5.1-codex",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/10/09/68e7504bdcc4a.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5.1-codex-max",
                "value": "gpt-5.1-codex-max",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/10/09/68e7504bdcc4a.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5-codex",
                "value": "gpt-5-codex",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/10/09/68e7504bdcc4a.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5-codex-low",
                "value": "gpt-5-codex-low",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/10/09/68e7504bdcc4a.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5-codex-medium",
                "value": "gpt-5-codex-medium",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/10/09/68e7504bdcc4a.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5.3-codex",
                "value": "gpt-5.3-codex",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/10/09/68e7504bdcc4a.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5.3-codex-xhigh",
                "value": "gpt-5.3-codex-xhigh",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/10/09/68e7504bdcc4a.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5-thinking-all",
                "value": "gpt-5-thinking-all",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250815/93f8745fda701d766bbcfbed7bdd8c62.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "GPT官方200美元/月才能享用的模型，这里给大家安排上了！非必要情况尽量要用！价格昂贵，请合理使用，滥用随时下架！",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-oss-120b",
                "value": "gpt-oss-120b",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/21/68a6441554eed.jpeg",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "ChatGPT最新的开源模型，拥有1200亿参数，采用八张H100显卡本地部署给大家使用",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-4.1-nano【无限上下文】",
                "value": "gpt-4.1-nano",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "快、稳定、聪明、首选！",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "gt-4.1-nano-2025-04-14【无限上下文】",
                "value": "gpt-4.1-nano-2025-04-14",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-3.5-turbo",
                "value": "gpt-3.5-turbo",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-3.5-turbo-16k",
                "value": "gpt-3.5-turbo-16k",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-3.5-turbo-16k-0613",
                "value": "gpt-3.5-turbo-16k-0613",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "o1-mini",
                "value": "o1-mini",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "o3-mini-high",
                "value": "o3-mini-high",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "o4-mini",
                "value": "o4-mini",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-4o-mini",
                "value": "gpt-4o-mini",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-4o-mini-2024-07-18",
                "value": "gpt-4o-mini-2024-07-18",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-4o",
                "value": "gpt-4o",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-4o-2024-08-06",
                "value": "gpt-4o-2024-08-06",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-4o-2024-11-20",
                "value": "gpt-4o-2024-11-20",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-4o-image-vip（绘图模型）",
                "value": "gpt-4o-image-vip",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/41dbd630e21e1f4763bacb2ca6da20d0.jpeg",
                    "integral": "300000积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-4o-2024-05-13",
                "value": "gpt-4o-2024-05-13",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5-all",
                "value": "gpt-5-all",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": false,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5.1-all",
                "value": "gpt-5.1-all",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": false,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-4.1-mini",
                "value": "gpt-4.1-mini",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-4.1-mini-2025-04-14",
                "value": "gpt-4.1-mini-2025-04-14",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-4.1",
                "value": "gpt-4.1",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-4.5-preview-2025-02-27",
                "value": "gpt-4.1-2025-04-14",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "GT-5-thinking",
                "value": "gpt-5-thinking",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "ChatGPT"
                }
            },
            {
                "label": "claude-3-haiku-20240307",
                "value": "claude-3-haiku-20240307",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-3-sonnet-20240229",
                "value": "claude-3-sonnet-20240229",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-3-5-haiku-20241022",
                "value": "claude-3-5-haiku-20241022",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-3-5-sonnet-20240620",
                "value": "claude-3-5-sonnet-20240620",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-3-5-sonnet-20241022",
                "value": "claude-3-5-sonnet-20241022",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-3-7-sonnet-20250219",
                "value": "claude-3-7-sonnet-20250219",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-3-7-sonnet-20250219-thinking",
                "value": "claude-3-7-sonnet-20250219-thinking",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "Claude-opus-4-1-20250805",
                "value": "claude-sonnet-4-20250514-coder",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "世界最贵模型，75美元/百万，请勿滥用！",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-haiku-4-5-20251001",
                "value": "claude-haiku-4-5-20251001",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-sonnet-4-20250514",
                "value": "claude-sonnet-4-20250514",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-sonnet-4-20250514-thinking",
                "value": "claude-sonnet-4-20250514-thinking",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-sonnet-4-5-20250929",
                "value": "claude-sonnet-4-5-20250929",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-sonnet-4-5-20250929-thinking",
                "value": "claude-sonnet-4-5-20250929-thinking",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-opus-4-6（消耗较大，请合理安排使用）",
                "value": "claude-opus-4-6",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1000000积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-opus-4-6-thinking（消耗较大，请合理安排使用）",
                "value": "claude-opus-4-6-thinking",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1000000积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-sonnet-4-6",
                "value": "claude-sonnet-4-6",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "claude-sonnet-4-6-thinking",
                "value": "claude-sonnet-4-6-thinking",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/2242652396d51d76665ad8983c368b12.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Claude"
                }
            },
            {
                "label": "gemini-2.0-flash",
                "value": "gemini-2.0-flash",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.0-flash-lite-preview-02-05",
                "value": "gemini-2.0-flash-lite-preview-02-05",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-flash-lite",
                "value": "gemini-2.5-flash-lite",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-flash-preview-05-20",
                "value": "gemini-2.5-flash-preview-05-20",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-flash-lite-preview-06-17",
                "value": "gemini-2.5-flash-lite-preview-06-17",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-flash-lite-preview-06-17-thinking",
                "value": "gemini-2.5-flash-lite-preview-06-17-thinking",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-flash-lite-preview-09-2025",
                "value": "gemini-2.5-flash-lite-preview-09-2025",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-flash-preview-09-2025",
                "value": "gemini-2.5-flash-preview-09-2025",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-flash-nothinking",
                "value": "gemini-2.5-flash-nothinking",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-flash",
                "value": "gemini-2.5-flash",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-flash-thinking",
                "value": "gemini-2.5-flash-thinking",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-pro-preview-03-25",
                "value": "gemini-2.5-pro-preview-03-25",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-pro-preview-05-06",
                "value": "gemini-2.5-pro-preview-05-06",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "Nano-banana绘图模型",
                "value": "gemini-2.5-flash-image",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/27/68af18ec5af7e.jpeg",
                    "integral": "100000积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-pro-preview-06-05",
                "value": "gemini-2.5-pro-preview-06-05",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-pro",
                "value": "gemini-2.5-pro",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-2.5-pro-thinking",
                "value": "gemini-2.5-pro-thinking",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-3-pro-preview",
                "value": "gemini-3-pro-preview",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "100000积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-3-pro-preview-thinking",
                "value": "gemini-3-pro-preview-thinking",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "100000积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-3.1-pro",
                "value": "gemini-3.1-pro",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "100000积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-3.1-pro-preview",
                "value": "gemini-3.1-pro-preview",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "100000积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-3-flash-preview(快、质量高、超高上下文)",
                "value": "gemini-3-flash-preview",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "gemini-3-flash-preview-thinking",
                "value": "gemini-3-flash-preview-thinking",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/08/18/68a2928eea3f0.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Gemini"
                }
            },
            {
                "label": "grok-3-mini",
                "value": "grok-3-mini",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/ca84cfe6d72c55d7b4d50daf553b83ef.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Grok马斯克"
                }
            },
            {
                "label": "grok-3",
                "value": "grok-3",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/ca84cfe6d72c55d7b4d50daf553b83ef.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Grok马斯克"
                }
            },
            {
                "label": "grok-4",
                "value": "grok-4",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/ca84cfe6d72c55d7b4d50daf553b83ef.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Grok马斯克"
                }
            },
            {
                "label": "grok-4-1-thinking-1129（维护中）",
                "value": "grok-4-1-thinking-1129",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/ca84cfe6d72c55d7b4d50daf553b83ef.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Grok马斯克"
                }
            },
            {
                "label": "grok-4-1-thinking-1129【联网】",
                "value": "grok-4-1-thinking-1129",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/ca84cfe6d72c55d7b4d50daf553b83ef.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "联网模型"
                }
            },
            {
                "label": "gpt-5-all-联网版",
                "value": "gpt-5-all",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": false,
                    "plugin": false,
                    "tag": "联网模型"
                }
            },
            {
                "label": "gpt-5.1-all【联网版】",
                "value": "gpt-5.1-all",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": false,
                    "plugin": false,
                    "tag": "联网模型"
                }
            },
            {
                "label": "gpt-5-thinking-all-联网版",
                "value": "gpt-5-thinking-all",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250815/93f8745fda701d766bbcfbed7bdd8c62.jpeg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "联网模型"
                }
            },
            {
                "label": "gpt-5-all【文件识别+联网】【Plus账号逆向不保稳定】",
                "value": "gpt-5-all",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": false,
                    "plugin": false,
                    "tag": "文件多模态"
                }
            },
            {
                "label": "gpt-5.1-all【文件识别+联网】【Plus账号逆向不保稳定】",
                "value": "gpt-5.1-all",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/510a7ca739d50f2e6d2cf3758444e596.png",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": false,
                    "plugin": false,
                    "tag": "文件多模态"
                }
            },
            {
                "label": "DeepSeek-V3.2-Exp",
                "value": "deepseek-chat",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/0ea1afb683b563019812e0688ba4921d.jpg",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "DeepSeek"
                }
            },
            {
                "label": "Deepseek-R1-671B满血版-V3.2-Exp",
                "value": "deepseek-reasoner",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/0ea1afb683b563019812e0688ba4921d.jpg",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "DeepSeek"
                }
            },
            {
                "label": "glm-4-flashx",
                "value": "glm-4-flashx",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "GLM-4-Flash-250414",
                "value": "GLM-4-Flash-250414",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "GLM-4-FlashX-250414",
                "value": "GLM-4-FlashX-250414",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "GLM-Z1-FlashX",
                "value": "GLM-Z1-FlashX",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "glm-4-flash",
                "value": "glm-4-flash",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "glm-4-airx",
                "value": "glm-4-airx",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "glm-4-air",
                "value": "glm-4-air",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "glm-4-long",
                "value": "glm-4-long",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "GLM-Z1-Flash",
                "value": "GLM-Z1-Flash",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "GLM-Z1-Air",
                "value": "GLM-Z1-Air",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "GLM-Z1-AirX",
                "value": "GLM-Z1-AirX",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "推理模型",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "glm-4-0520",
                "value": "glm-4-0520",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "glm-4-plus",
                "value": "glm-4-plus",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "GLM-4.5-X",
                "value": "GLM-4.5-X",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "Glm-4.5",
                "value": "glm-4.5",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "GLM-4.5-Flash",
                "value": "GLM-4.5-Flash",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "GLM-4.6",
                "value": "GLM-4.6",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "GLM-4.7",
                "value": "GLM-4.7",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/ad20e6b84a8be06a9112e7122a6ba880.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "清华智谱"
                }
            },
            {
                "label": "qwen-plus",
                "value": "qwen-plus",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen-plus-latest",
                "value": "qwen-plus-latest",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen-turbo",
                "value": "qwen-turbo",
                "attr": {
                    "icon": "http://tu.feixuekeji.com/uploads/20250814/6f675ce311b7d7bd3742f2d5c8c77b6f.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen-turbo-latest",
                "value": "qwen-turbo-latest",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/6f675ce311b7d7bd3742f2d5c8c77b6f.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen-turbo-2025-04-28",
                "value": "qwen-turbo-2025-04-28",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/6f675ce311b7d7bd3742f2d5c8c77b6f.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen-turbo-2025-07-15",
                "value": "qwen-turbo-2025-07-15",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/6f675ce311b7d7bd3742f2d5c8c77b6f.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen-plus-2025-04-28",
                "value": "qwen-plus-2025-04-28",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/6f675ce311b7d7bd3742f2d5c8c77b6f.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen-plus-2025-07-14",
                "value": "qwen-plus-2025-07-14",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/6f675ce311b7d7bd3742f2d5c8c77b6f.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-30b-a3b-instruct-2507",
                "value": "qwen3-30b-a3b-instruct-2507",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/6f675ce311b7d7bd3742f2d5c8c77b6f.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "基于Qwen3的非思考模式开源模型，相较上一版本（通义千问3-30B-A3B）中英文和多语言整体通用能力有大幅提升。主观开放类任务专项优化，显著更加符合用户偏好，能够提供更有帮助性的回复。",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-30b-a3b-thinking-2507",
                "value": "qwen3-30b-a3b-thinking-2507",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/6f675ce311b7d7bd3742f2d5c8c77b6f.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "基于Qwen3的思考模式开源模型，相较上一版本（通义千问3-30B-A3B）复杂推理类任务性能优秀，包括逻辑推理、数学、科学、代码类等具有一定难度的任务场景，指令遵循、文本理解、多语言翻译等能力显著提高。",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen-flash",
                "value": "qwen-flash",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen-flash-2025-07-28",
                "value": "qwen-flash-2025-07-28",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-max",
                "value": "qwen3-max",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-max-preview",
                "value": "qwen3-max-preview",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-vl-30b-a3b-instruct",
                "value": "qwen3-vl-30b-a3b-instruct",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-vl-30b-a3b-thinking",
                "value": "qwen3-vl-30b-a3b-thinking",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-vl-8b-instruct",
                "value": "qwen3-vl-8b-instruct",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-vl-235b-a22b-instruct",
                "value": "qwen3-vl-235b-a22b-instruct",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-vl-235b-a22b-thinking",
                "value": "qwen3-vl-235b-a22b-thinking",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "Qwen3-235B-A22B-Instruct-2507-FP8",
                "value": "Qwen3-235B-A22B-Instruct-2507-FP8",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/6f675ce311b7d7bd3742f2d5c8c77b6f.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-next-80b-a3b-instruct",
                "value": "qwen3-next-80b-a3b-instruct",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-next-80b-a3b-thinking",
                "value": "qwen3-next-80b-a3b-thinking",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-30b-a3b-instruct-2507",
                "value": "qwen3-30b-a3b-instruct-2507",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-30b-a3b-thinking-2507",
                "value": "qwen3-30b-a3b-thinking-2507",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-235b-a22b-thinking-2507",
                "value": "qwen3-235b-a22b-thinking-2507",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-vl-32b-instruct",
                "value": "qwen3-vl-32b-instruct",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-vl-32b-thinking",
                "value": "qwen3-vl-32b-thinking",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen-max",
                "value": "qwen-max",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen-max-latest",
                "value": "qwen-max-latest",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-coder-plus",
                "value": "qwen3-coder-plus",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-coder-plus-2025-07-22",
                "value": "qwen3-coder-plus-2025-07-22",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-coder-plus-2025-09-23",
                "value": "qwen3-coder-plus-2025-09-23",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-coder-flash",
                "value": "qwen3-coder-flash",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-coder-flash-2025-07-28",
                "value": "qwen3-coder-flash-2025-07-28",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-coder-480b-a35b-instruct",
                "value": "qwen3-coder-480b-a35b-instruct",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "qwen3-coder-30b-a3b-instruct",
                "value": "qwen3-coder-30b-a3b-instruct",
                "attr": {
                    "icon": "https://img.feixuekeji.com/i/2025/12/21/6947193cdb0a0.png",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "阿里通义千问"
                }
            },
            {
                "label": "moonshot-v1-8k",
                "value": "moonshot-v1-8k",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/723c09bdb057c7410d79945af57131fa.jpg",
                    "integral": "1积分",
                    "multimodal": true,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Kimi月之暗面"
                }
            },
            {
                "label": "moonshot-v1-32k",
                "value": "moonshot-v1-32k",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/723c09bdb057c7410d79945af57131fa.jpg",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Kimi月之暗面"
                }
            },
            {
                "label": "moonshot-v1-128k",
                "value": "moonshot-v1-128k",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/723c09bdb057c7410d79945af57131fa.jpg",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Kimi月之暗面"
                }
            },
            {
                "label": "kimi-latest",
                "value": "kimi-latest",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/723c09bdb057c7410d79945af57131fa.jpg",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Kimi月之暗面"
                }
            },
            {
                "label": "kimi-k2-0711-preview",
                "value": "kimi-k2-0711-preview",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/723c09bdb057c7410d79945af57131fa.jpg",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": true,
                    "plugin": false,
                    "tag": "Kimi月之暗面"
                }
            },
            {
                "label": "kimi-k2-0905-preview",
                "value": "kimi-k2-0905-preview",
                "attr": {
                    "icon": "https://tu.feixuekeji.com/uploads/20250814/723c09bdb057c7410d79945af57131fa.jpg",
                    "integral": "1积分",
                    "multimodal": false,
                    "note": "",
                    "onlyImg": false,
                    "plugin": false,
                    "tag": "Kimi月之暗面"
                }
            }
        ],
        "notice": "",
        "ocp": true,
        "p": true,
        "plugins": null,
        "rm": false,
        "sessionHoverSetting": true,
        "showTokens": false,
        "thinkModel": "deepseek-reasoner",
        "toggleTipTime": 3,
        "tooltipsText": "\u003cp\u003e\u003cspan style=\"font-size: 12px;\"\u003e以上内容为AI生成，切勿用于违法用途\u003c/span\u003e\u003c/p\u003e",
        "voice": true
    },
    "msg": ""
}
```