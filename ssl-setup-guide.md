# SSL Certificate Setup Guide

## Railway (Automatic - Recommended)

Railway provides free SSL certificates automatically:

1. **Default Railway Domain:**
   - Your app is already HTTPS: `https://your-app.railway.app`
   - SSL certificate is automatically managed

2. **Custom Domain:**
   - Add custom domain in Railway dashboard
   - Railway automatically issues SSL certificate
   - DNS configuration required

## Let's Encrypt (Manual)

### Using Certbot

1. **Install Certbot:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Get Certificate:**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

3. **Auto-renewal:**
   ```bash
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Using Cloudflare (Free)

1. **Add domain to Cloudflare**
2. **Update nameservers**
3. **Enable SSL/TLS:**
   - Go to SSL/TLS settings
   - Set encryption mode to "Full (strict)"
   - Enable "Always Use HTTPS"

## SSL Configuration for FastAPI

### Force HTTPS Redirect

```python
from fastapi import FastAPI, Request
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# Force HTTPS redirect
app.add_middleware(HTTPSRedirectMiddleware)
```

### Security Headers

```python
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# Add security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

## Testing SSL

### Check Certificate
```bash
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

### Test HTTPS
```bash
curl -I https://yourdomain.com
```

### SSL Labs Test
Visit: https://www.ssllabs.com/ssltest/

## Common Issues

1. **Mixed Content:** Ensure all resources use HTTPS
2. **Certificate Chain:** Include intermediate certificates
3. **HSTS:** Implement HTTP Strict Transport Security
4. **CORS:** Update CORS origins to use HTTPS
