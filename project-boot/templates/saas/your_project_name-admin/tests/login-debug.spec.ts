import { test } from '@playwright/test';

test('debug login', async ({ page }) => {
  page.on('request', request => {
    if (request.url().includes('/api')) {
      console.log('>>> REQUEST:', request.method(), request.url());
    }
  });
  
  page.on('response', async response => {
    if (response.url().includes('/api')) {
      console.log('<<< RESPONSE:', response.status(), response.url());
      try {
        const body = await response.text();
        console.log('    BODY:', body.substring(0, 150));
      } catch (e) {}
    }
  });

  page.on('pageerror', error => {
    console.log('PAGE ERROR:', error.message);
  });

  await page.goto('http://localhost:3000/login');
  await page.waitForTimeout(1000);
  
  const inputs = page.locator('input');
  const count = await inputs.count();
  console.log('Input count:', count);
  
  await inputs.nth(0).fill('admin');
  await inputs.nth(1).fill('123456');
  await inputs.nth(2).fill('0');
  
  await page.getByRole('button', { name: '登录' }).click();
  
  await page.waitForTimeout(5000);
  console.log('Final URL:', page.url());
  
  await page.screenshot({ path: '/tmp/login-result.png' });
});
