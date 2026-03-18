import os
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

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
        
        # Essential stealth arguments
        args = [
            "--disable-blink-features=AutomationControlled",
        ]
        
        # A very recent User-Agent (Chrome 133 on Windows 10/11)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        
        if browser_type == 'firefox':
            browser = p.firefox.launch_persistent_context(
                user_data_dir=directory,
                headless=False,
                args=args,
                user_agent=user_agent,
                ignore_default_args=["--enable-automation"]
            )
        elif browser_type == 'edge' or browser_type == 'msedge':
            browser = p.chromium.launch_persistent_context(
                user_data_dir=directory,
                headless=False,
                channel="msedge",
                args=args,
                user_agent=user_agent,
                ignore_default_args=["--enable-automation"]
            )
        else: # chrome / chromium
            browser = p.chromium.launch_persistent_context(
                user_data_dir=directory,
                headless=False,
                channel="chrome",
                args=args,
                user_agent=user_agent,
                ignore_default_args=["--enable-automation"]
            )
        
        page = browser.new_page()
        
        # Apply stealth to both context and page
        Stealth().apply_stealth_sync(browser)
        Stealth().apply_stealth_sync(page)
        
        # Comprehensive JS overrides to look like a real browser
        page.add_init_script("""
            // 1. Hide webdriver
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            
            // 2. Mock chrome.runtime
            window.chrome = { runtime: {} };
            
            // 3. Mock plugins (must not be empty)
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            
            // 4. Mock languages
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            
            // 5. Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
        """)
        
        # Start at YouTube instead of a direct Google Sign-in URL
        # This often bypasses the "insecure browser" block because it looks like a natural user action
        page.goto("https://www.youtube.com")
        
        print("[*] Navigating to YouTube... Please click 'Sign In' if you aren't automatically redirected.")
        
        # Try to find and click the sign in button if we aren't already on a login page
        try:
            # Check if we are already logged in (no sign in button)
            if not page.query_selector('a[aria-label="Sign in"]'):
                 # We might be logged in or on the login page already
                 if "accounts.google.com" not in page.url:
                      # If not logged in and not on login page, click sign in
                      login_button = page.query_selector('a[aria-label="Sign in"]')
                      if login_button:
                          login_button.click()
        except:
            pass

        print("[*] Waiting for you to log in...")
        try:
            # Wait for them to be logged in (presence of an avatar or being on youtube with cookies)
            # Timeout is 3 minutes for 2FA
            page.wait_for_selector('#avatar-btn', timeout=180000)
            print("[+] Login successful! Detected YouTube avatar.")
        except Exception:
            print("[-] Still waiting or login was manual. Please ensure you are logged in to YouTube.")
            print("[*] If you have finished logging in, you can close the browser window now.")
            
            # Keep browser open for a bit more if they are still working
            try:
                page.wait_for_timeout(5000) # Give it 5 seconds to settle
            except:
                pass

        # Extract context cookies
        cookies = browser.cookies()
        
        # Save to Netscape format
        with open(output_file, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# Generated securely by Playwright\n\n")
            
            for cookie in cookies:
                domain = cookie.get('domain', '')
                domain_specified = "TRUE" if domain.startswith('.') else "FALSE"
                path = cookie.get('path', '/')
                secure = "TRUE" if cookie.get('secure') else "FALSE"
                expires_ts = str(int(cookie.get('expires', 0))) if cookie.get('expires', 0) > 0 else "0"
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                
                f.write(f"{domain}\t{domain_specified}\t{path}\t{secure}\t{expires_ts}\t{name}\t{value}\n")
        
        browser.close()
        print(f"[+] Cookies successfully exported to {output_file}!")
        return True

if __name__ == '__main__':
    login_and_save_cookies()
