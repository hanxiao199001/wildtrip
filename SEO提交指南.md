# SEO提交指南 - 百度和Google

## 📍 Sitemap地址

**你的sitemap地址:**
```
https://wildtrip.vip/sitemap.xml
https://api.wildtrip.com.cn/sitemap.xml (如果有)
```

**验证访问:**
```bash
curl https://wildtrip.vip/sitemap.xml
# 应该返回XML格式的URL列表
```

---

## 🔵 百度站长平台

### 步骤1: 注册/登录

访问: https://ziyuan.baidu.com/site/index

### 步骤2: 添加网站

1. 点击"用户中心" → "站点管理" → "添加网站"
2. 输入: `https://wildtrip.vip`
3. 选择站点类型: HTTPS

### 步骤3: 验证网站所有权（3选1）

**方法A: 文件验证（推荐）**
```bash
# 1. 下载验证文件（百度会给你一个HTML文件）
# 2. 上传到服务器
scp baidu_verify_xxx.html root@47.82.159.93:/root/clawd/web/

# 3. 确认可访问
curl https://wildtrip.vip/baidu_verify_xxx.html
```

**方法B: HTML标签验证**
```html
<!-- 在 web/index.html 的 <head> 中添加 -->
<meta name="baidu-site-verification" content="你的验证码" />
```

**方法C: CNAME验证**
```bash
# 在DNS添加记录
类型: CNAME
主机记录: xxx (百度提供)
记录值: ziyuan.baidu.com
```

### 步骤4: 提交Sitemap

1. 验证成功后，进入"数据引入" → "链接提交"
2. 选择"sitemap"
3. 输入: `https://wildtrip.vip/sitemap.xml`
4. 点击"提交"

### 步骤5: 提交新增URL（可选，自动化）

**手动提交:**
```bash
# 每次生成新攻略后，主动推送给百度
curl -H 'Content-Type:text/plain' \
  --data-binary @urls.txt \
  "http://data.zz.baidu.com/urls?site=https://wildtrip.vip&token=你的token"
```

**自动化（推荐）:**
在 `backend/services/seo_service.py` 中添加百度推送

---

## 🔴 Google Search Console

### 步骤1: 注册/登录

访问: https://search.google.com/search-console

### 步骤2: 添加资源

1. 点击"添加资源" → "网址前缀"
2. 输入: `https://wildtrip.vip`

### 步骤3: 验证网站所有权（4选1）

**方法A: HTML文件验证（推荐）**
```bash
# 1. 下载验证文件
# 2. 上传到服务器
scp google-site-verification_xxx.html root@47.82.159.93:/root/clawd/web/

# 3. 确认可访问
curl https://wildtrip.vip/google-site-verification_xxx.html
```

**方法B: HTML标签验证**
```html
<!-- 在 web/index.html 的 <head> 中添加 -->
<meta name="google-site-verification" content="你的验证码" />
```

**方法C: Google Analytics**
```
如果已配置GA，可直接验证
```

**方法D: DNS验证**
```bash
# 在DNS添加TXT记录
类型: TXT
主机记录: @
记录值: google-site-verification=xxx
```

### 步骤4: 提交Sitemap

1. 验证成功后，左侧菜单 → "站点地图"
2. 输入: `sitemap.xml`
3. 点击"提交"

### 步骤5: 查看收录情况

```
概览 → 覆盖率 → 查看已收录页面数
一般需要1-2周开始收录
```

---

## 📊 验证提交成功

### 百度验证

```bash
# 方法1: site命令（需要等1-2周）
在百度搜索: site:wildtrip.vip

# 方法2: 站长平台查看
百度站长平台 → 数据监控 → 索引量
```

### Google验证

```bash
# 方法1: site命令
在Google搜索: site:wildtrip.vip

# 方法2: Search Console查看
覆盖率 → 有效页面数
```

---

## 🤖 自动化推送（可选）

### 百度主动推送

在 `backend/services/seo_service.py` 添加：

```python
def push_to_baidu(self, url: str):
    """主动推送URL到百度"""
    import requests
    
    api = "http://data.zz.baidu.com/urls"
    token = os.getenv('BAIDU_PUSH_TOKEN', '')
    
    if not token:
        return
    
    params = {
        'site': 'https://wildtrip.vip',
        'token': token
    }
    
    try:
        response = requests.post(
            api, 
            params=params,
            data=url,
            headers={'Content-Type': 'text/plain'}
        )
        logger.info(f"百度推送成功: {response.json()}")
    except Exception as e:
        logger.error(f"百度推送失败: {e}")
```

### Google IndexNow

```python
def push_to_indexnow(self, url: str):
    """推送到IndexNow（Google/Bing）"""
    import requests
    
    api = "https://api.indexnow.org/IndexNow"
    key = os.getenv('INDEXNOW_KEY', '')
    
    if not key:
        return
    
    data = {
        "host": "wildtrip.vip",
        "key": key,
        "urlList": [url]
    }
    
    try:
        response = requests.post(api, json=data)
        logger.info(f"IndexNow推送成功: {response.status_code}")
    except Exception as e:
        logger.error(f"IndexNow推送失败: {e}")
```

---

## ✅ 提交检查清单

### 百度
- [ ] 注册百度站长平台账号
- [ ] 添加网站 wildtrip.vip
- [ ] 验证所有权（文件/标签/DNS任选一种）
- [ ] 提交sitemap.xml
- [ ] 记录推送token（用于自动化）
- [ ] 等待1-2周查看收录

### Google
- [ ] 注册Google Search Console账号
- [ ] 添加资源 wildtrip.vip
- [ ] 验证所有权（文件/标签/DNS任选一种）
- [ ] 提交sitemap.xml
- [ ] 等待1-2周查看收录

### 其他搜索引擎（可选）
- [ ] Bing Webmaster Tools
- [ ] 360站长平台
- [ ] 搜狗站长平台

---

## 🚨 注意事项

1. **robots.txt检查**
   ```bash
   # 确保允许搜索引擎爬取
   curl https://wildtrip.vip/robots.txt
   
   # 应该包含:
   User-agent: *
   Allow: /
   Sitemap: https://wildtrip.vip/sitemap.xml
   ```

2. **SSL证书**
   ```bash
   # 确保HTTPS正常
   curl -I https://wildtrip.vip
   # 应该返回 200 OK
   ```

3. **404页面**
   ```bash
   # 测试不存在的页面
   curl -I https://wildtrip.vip/notfound
   # 应该返回 404
   ```

---

**完成后通知我，我帮你检查！** 🚀
