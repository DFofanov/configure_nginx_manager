# Guide to Creating Let's Encrypt Certificate with DNS Challenge for reg.ru Provider in Nginx Proxy Manager

---

## Prerequisites
- Access to Nginx Proxy Manager (NPM)
- Access to reg.ru account with DNS management permissions
- API key for DNS management in reg.ru (if automatic integration is available)
- Need to obtain certificate for `*.dfv24.com` (wildcard certificate)

---

## Step 1. Getting API Key for reg.ru

1. Log in to reg.ru control panel  
2. Navigate to API management section (if supported)  
3. Create or find API key with DNS records editing permissions  
4. Save API key and secret (Client ID and API Token)

---

## Step 2. Configuring Nginx Proxy Manager to Use DNS Challenge reg.ru

1. In NPM admin panel, go to **SSL Certificates → Add SSL Certificate**  
2. Select **Let's Encrypt** -> **DNS Challenge**  
3. In **Provider** field, select `reg_ru` or `custom` (if provider not available, script will be needed)  
4. Fill in API fields with required parameters:  
   - Client ID  
   - API Token  
5. In **Domain Names** field, specify:  
   `*.dfv24.com` (for wildcard certificate)  
   and main domain `dfv24.com`  
6. Enable other options (Terms of Service, Email)  
7. Click **Save** to request certificate  
8. NPM will automatically add DNS TXT records for domain ownership verification through reg.ru API

---

## Step 3. Verification and Automatic Renewal

- After successful certificate creation, NPM will automatically renew it through DNS Challenge.  
- For successful renewal, it's important that API key remains valid and NPM has access to DNS management.

---

## If NPM Doesn't Have Ready Integration with reg.ru

- Use external script to update DNS TXT records in reg.ru, configured in NPM through **Custom DNS Provider**.  
- Configure curl requests to reg.ru API for adding/removing TXT records.

---

# Summary

For Let's Encrypt wildcard certificates with reg.ru, DNS Challenge must be used with provider's API for automatic DNS record management.  
In Nginx Proxy Manager, configure DNS Challenge considering reg.ru specifics for seamless certificate obtaining and renewal.
