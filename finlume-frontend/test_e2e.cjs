const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to login page...');
    await page.goto('http://localhost:5173/login');
    
    // Switch to Register
    console.log('Switching to Register...');
    await page.click('text="Don\'t have an account? Sign Up"');
    
    console.log('Filling registration form...');
    await page.fill('input[name="username"]', 'playwright_user');
    await page.fill('input[name="password"]', 'playwright_pass');
    await page.click('button[type="submit"]');
    
    console.log('Waiting for success message...');
    await page.waitForSelector('text="Registration successful! Please log in now."');
    console.log('Registration succeeded in UI!');
    
    console.log('Filling login form...');
    await page.fill('input[name="password"]', 'playwright_pass'); // username is already playwright_user
    
    const [response] = await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/auth/login')),
      page.click('button[type="submit"]')
    ]);
    
    console.log(`Login response status: ${response.status()}`);
    
    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard');
    console.log('Successfully redirected to dashboard!');
    
  } catch (err) {
    console.error('E2E Test Failed:', err);
  } finally {
    await browser.close();
  }
})();
