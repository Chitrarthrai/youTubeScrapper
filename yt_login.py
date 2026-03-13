import os
from playwright.sync_api import sync_playwright

def login_and_save_cookies(output_file='cookies.txt', browser_type='chrome'):
    print("\n==============================================")
    print("Launching Live Login Browser...")
    print("1. A new browser window will open.")
    print("2. Please log in to your YouTube/Google account.")
    print("3. Once you are successfully logged in and see the YouTube homepage, you can close the browser manually, or it will close automatically in 2 minutes.")
    print("==============================================\n")
    
    with sync_playwright() as p:
        # Launch persistent context to keep cookies if they close and reopen
        directory = os.path.join(os.getcwd(), '.yt_session')
        
        if browser_type == 'firefox':
            browser = p.firefox.launch_persistent_context(
                user_data_dir=directory,
                headless=False
            )
        elif browser_type == 'edge' or browser_type == 'msedge':
            browser = p.chromium.launch_persistent_context(
                user_data_dir=directory,
                headless=False,
                channel="msedge"
            )
        else: # chrome / chromium
            browser = p.chromium.launch_persistent_context(
                user_data_dir=directory,
                headless=False,
                channel="chrome"
            )
        
        page = browser.new_page()
        page.goto("https://accounts.google.com/signin/v2/identifier?service=youtube&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue&hl=en")
        
        print("[*] Waiting for you to log in...")
        try:
            # Wait for them to navigate back to youtube.com
            page.wait_for_url("https://www.youtube.com/*", timeout=120000)
            print("[+] Login detected! Saving cookies...")
        except Exception:
            print("[-] Timed out waiting for login or browser was closed early. Attempting to save current cookies anyway...")

        # Extract context cookies
        cookies = browser.cookies()
        
        # Save to Netscape format
        with open(output_file, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# Generated securely by Playwright\n\n")
            
            for cookie in cookies:
                domain = cookie['domain']
                domain_specified = "TRUE" if domain.startswith('.') else "FALSE"
                path = cookie['path']
                secure = "TRUE" if cookie['secure'] else "FALSE"
                expires_ts = str(int(cookie['expires'])) if cookie['expires'] > 0 else "0"
                name = cookie['name']
                value = cookie['value']
                
                f.write(f"{domain}\t{domain_specified}\t{path}\t{secure}\t{expires_ts}\t{name}\t{value}\n")
        
        browser.close()
        print(f"[+] Cookies successfully exported to {output_file}!")
        return True

if __name__ == '__main__':
    login_and_save_cookies()
