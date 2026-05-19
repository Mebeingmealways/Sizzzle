import { chromium } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

const BASE_URL = 'http://localhost:5173';
const OUTPUT_DIR = 'd:/Sizzzle/docs/screenshots';

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

const pages = [
  {
    name: '01-landing-page',
    url: BASE_URL,
    delay: 2000,
  },
  {
    name: '02-login-page',
    url: `${BASE_URL}/#/login`,
    delay: 1000,
  },
  {
    name: '03-register-customer',
    url: `${BASE_URL}/#/register`,
    delay: 1000,
  },
  {
    name: '04-register-cook',
    url: `${BASE_URL}/#/register/cook`,
    delay: 1000,
  },
  {
    name: '05-customer-dashboard',
    url: `${BASE_URL}/#/customer/dashboard`,
    delay: 1500,
    authRequired: true,
  },
  {
    name: '06-booking-creation',
    url: `${BASE_URL}/#/customer/booking`,
    delay: 1500,
    authRequired: true,
  },
  {
    name: '07-taste-profile',
    url: `${BASE_URL}/#/customer/taste-profile`,
    delay: 1500,
    authRequired: true,
  },
  {
    name: '08-my-bookings',
    url: `${BASE_URL}/#/customer/my-bookings`,
    delay: 1500,
    authRequired: true,
  },
  {
    name: '09-cook-dashboard',
    url: `${BASE_URL}/#/cook/dashboard`,
    delay: 1500,
    authRequired: true,
  },
  {
    name: '10-cook-jobs',
    url: `${BASE_URL}/#/cook/jobs`,
    delay: 1500,
    authRequired: true,
  },
  {
    name: '11-cook-earnings',
    url: `${BASE_URL}/#/cook/earnings`,
    delay: 1500,
    authRequired: true,
  },
  {
    name: '12-cook-availability',
    url: `${BASE_URL}/#/cook/availability`,
    delay: 1500,
    authRequired: true,
  },
  {
    name: '13-admin-dashboard',
    url: `${BASE_URL}/#/admin/dashboard`,
    delay: 1500,
    authRequired: true,
  },
  {
    name: '14-verification-queue',
    url: `${BASE_URL}/#/manager/verification`,
    delay: 1500,
    authRequired: true,
  },
  {
    name: '15-disputes',
    url: `${BASE_URL}/#/admin/disputes`,
    delay: 1500,
    authRequired: true,
  },
  {
    name: '16-terms-page',
    url: `${BASE_URL}/#/legal/terms`,
    delay: 1000,
  },
];

async function captureScreenshots() {
  const browser = await chromium.launch({ headless: true });
  
  try {
    for (const page of pages) {
      try {
        const context = await browser.newContext({
          viewport: { width: 1280, height: 720 },
          deviceScaleFactor: 1,
        });
        
        const browserPage = await context.newPage();
        
        // Set localStorage for authenticated routes
        if (page.authRequired) {
          await browserPage.evaluate(() => {
            localStorage.setItem('auth_token', 'demo-token-for-screenshots');
            localStorage.setItem('user_role', 'customer');
          });
        }
        
        console.log(`Capturing: ${page.name}...`);
        await browserPage.goto(page.url, { waitUntil: 'networkidle', timeout: 10000 }).catch(() => {});
        await browserPage.waitForTimeout(page.delay);
        
        const filename = path.join(OUTPUT_DIR, `${page.name}.png`);
        await browserPage.screenshot({ path: filename, fullPage: false });
        console.log(`✓ Saved: ${filename}`);
        
        await context.close();
      } catch (error) {
        console.log(`⚠ Skipped ${page.name}: ${error.message}`);
      }
    }
    
    console.log(`\n✅ Screenshots saved to: ${OUTPUT_DIR}`);
  } finally {
    await browser.close();
  }
}

captureScreenshots().catch(console.error);
