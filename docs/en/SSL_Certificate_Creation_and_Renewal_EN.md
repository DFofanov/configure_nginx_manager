# Guide to Creating Wildcard Certificate *.dfv24.com in Nginx Proxy Manager and Configuring Automatic SSL Renewal

---

## Step 1. Preparation

- Ensure Nginx Proxy Manager (NPM) is installed and accessible at http://192.168.10.14:81/
- You have access to DNS records for dfv24.com domain in reg.ru control panel or another registrar

---

## Step 2. Creating Wildcard SSL Certificate in Nginx Proxy Manager

1. Log in to Nginx Proxy Manager admin panel at http://192.168.10.14:81/

2. Navigate to **SSL Certificates** → click **Add SSL Certificate** button

3. Select **Let's Encrypt**

4. Fill in the fields:
   - **Domain Names:**  
     Enter `*.dfv24.com` — for wildcard certificate  
     Also recommended to add main domain `dfv24.com` (comma-separated or in new field)  
   - **Email Address:**  
     Specify your Email for Let's Encrypt notifications (required)  
   - **HTTP Challenge:**  
     Leave HTTP verification if NPM is accessible from internet on ports 80 and 443, or configure DNS Challenge if supported by your DNS  

5. Check "Agree to the Let's Encrypt Terms of Service"

6. Click **Save**

- NPM will begin certificate obtaining process with domain verification.  
- Upon successful certificate request, you'll see new certificate in the list.

---

## Step 3. Configuring Automatic Renewal

- Nginx Proxy Manager automatically handles Let's Encrypt certificate renewal.  
- For this, server must be accessible from internet on ports 80 and 443, and DNS records must correctly point to your server.  
- NPM periodically (usually 30 days before expiration) requests certificate renewal.  
- When using DNS Challenge, NPM must have DNS provider integration configured (if supported).

---

## Step 4. Using Wildcard Certificate in Proxy Hosts

1. Go to **Proxy Hosts** → Create or edit proxy entry

2. In **Domain Names** field, specify needed subdomain from dfv24.com, for example:  
   `api.dfv24.com` or `www.dfv24.com`

3. In **SSL** section, select your wildcard certificate `*.dfv24.com` that you obtained in Step 2

4. Enable options:
   - Use SSL  
   - Force SSL  
   - HSTS (if needed)

5. Save changes.

---

## Step 5. Verification

1. Verify that all subdomains use the same certificate  
2. Visit https://api.dfv24.com or other subdomains from browser  
3. Ensure certificate is valid, not expired, and issued for *.dfv24.com  
4. Check certificate renewal status in SSL Certificates section

---

## Additional Information

- If Let's Encrypt cannot perform HTTP Challenge due to closed port, configure DNS Challenge (may require DNS provider API key)  
- For security and notifications, keep Email up to date  
- Check Nginx Proxy Manager logs to identify renewal errors

---

# Summary

Nginx Proxy Manager allows easy obtaining and automatic renewal of wildcard SSL certificates for *.dfv24.com domain using Let's Encrypt.  
Main requirements — properly configured DNS records and internet access on HTTP/HTTPS ports.  
Then use one global certificate for all your subdomains through Proxy Hosts settings.
