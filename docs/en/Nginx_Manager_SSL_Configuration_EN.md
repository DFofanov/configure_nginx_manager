# Detailed Guide to Configuring Nginx Proxy Manager with One Global SSL Certificate for All dfv24.com Domains

## Prerequisites
- [Nginx Proxy Manager](http://192.168.10.14:81/) is installed and running
- Main domain: dfv24.com
- Domain hosting and DNS records are on reg.ru
- Need to use one SSL certificate (e.g., wildcard) for all dfv24.com subdomains

---

## Step 1. Purchasing and Obtaining SSL Wildcard Certificate for dfv24.com
1. On reg.ru or any other Certificate Authority (CA), order wildcard certificate for domain `*.dfv24.com`.
2. Obtain certificate files:  
   - Main certificate (CRT)  
   - Intermediate certificates (CA Bundle)  
   - Private key (KEY)

---

## Step 2. Importing Your SSL Certificate to Nginx Proxy Manager
1. Log in to Nginx Proxy Manager at http://192.168.10.14:81/  
2. Go to **SSL Certificates** section → **Add SSL Certificate** button  
3. Select **Custom** (custom certificate)  
4. Paste into fields:  
   - **Certificate** — main CRT + CA Bundle (if CA Bundle is separate, concatenate into one file or paste sequentially)  
   - **Key** — private key content  
   - Name certificate, e.g., `dfv24_wildcard`  
5. Save

---

## Step 3. Configuring Proxy Hosts Using Global Certificate

1. Go to **Proxy Hosts** → **Add Proxy Host**  
2. Fill in fields:  
   - **Domain Names**: For example, `sub1.dfv24.com` (for first subdomain)  
   - **Scheme**: http or https, depending on backend  
   - **Forward Hostname / IP**: IP or DNS address of your internal service  
   - **Forward Port**: service port (e.g., 80 or 443)  
3. Enable **SSL** → Check **Use a shared SSL certificate** (if such option is available) or select previously imported certificate from list  
4. Activate: **Block Common Exploits**, **Websockets Support**, set Redirect HTTP to HTTPS if required  
5. Save proxy host

6. Repeat for all subdomains, specifying needed domains and selecting same wildcard SSL certificate

---

## Step 4. Configuring DNS Records on reg.ru

1. Log in to domain management panel on reg.ru  
2. Create or edit DNS A records:  
   - `dfv24.com` → IP of your Nginx Proxy Manager (e.g., 192.168.10.14)  
   - `*.dfv24.com` → same IP or specific subdomains if there are special ones  
3. Save changes  
4. Wait for DNS update (from few minutes to 24 hours)

---

## Step 5. Testing and Verification

1. In browser, open any subdomain `https://sub1.dfv24.com`  
2. Certificate should be valid, issued for wildcard `*.dfv24.com`  
3. Check proxy functionality and correct certificate assignment  
4. If necessary, check Nginx Proxy Manager logs and fix errors

---

## Additional Information

- If Nginx Proxy Manager doesn't have GUI option to select shared certificate, you can manually configure configs through `/data/nginx/proxy_host` directory and specify SSL certificate for all hosts.  
- When updating certificate — re-import it to Nginx Proxy Manager.  
- You can use Let's Encrypt for automatic wildcard certificate obtaining using DNS validation (if supported by your DNS provider).

---

# Summary

Use one wildcard certificate for all subdomains, import it as custom certificate in Nginx Proxy Manager, when creating proxy hosts select it in SSL settings. Manage DNS records on reg.ru, directing domain to Nginx Proxy Manager IP.  
This allows legitimate use of single certificate for all services with different subdomains under your dfv24.com domain.
