import { test } from '@playwright/test'

const BASE = 'http://localhost:5175'

const pages = [
  { name: '01-landing-hero', url: '/', waitFor: '.hero' },
  { name: '02-landing-features', url: '/', scroll: '.section:nth-of-type(3)' },
  { name: '03-landing-footer', url: '/', scroll: 'footer' },
  { name: '04-login', url: '/login' },
  { name: '05-register', url: '/register' },
  { name: '06-register-cook', url: '/register/cook' },
  { name: '07-terms', url: '/terms' },
  { name: '08-privacy', url: '/privacy' },
  { name: '09-cancellation', url: '/cancellation-policy' },
  { name: '10-refund', url: '/refund-policy' },
]

// Desktop screenshots
test.describe('Desktop Screenshots', () => {
  test.use({ viewport: { width: 1440, height: 900 } })

  for (const p of pages) {
    test(`desktop - ${p.name}`, async ({ page }) => {
      await page.goto(`${BASE}${p.url}`, { waitUntil: 'networkidle' })
      if (p.waitFor) await page.waitForSelector(p.waitFor, { timeout: 5000 }).catch(() => {})
      if (p.scroll) {
        const el = await page.$(p.scroll)
        if (el) await el.scrollIntoViewIfNeeded()
        await page.waitForTimeout(500)
      }
      await page.waitForTimeout(1000) // let animations settle
      await page.screenshot({ path: `screenshots/desktop/${p.name}.png`, fullPage: !p.scroll })
    })
  }
})

// Mobile screenshots
test.describe('Mobile Screenshots', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  for (const p of pages) {
    test(`mobile - ${p.name}`, async ({ page }) => {
      await page.goto(`${BASE}${p.url}`, { waitUntil: 'networkidle' })
      if (p.waitFor) await page.waitForSelector(p.waitFor, { timeout: 5000 }).catch(() => {})
      if (p.scroll) {
        const el = await page.$(p.scroll)
        if (el) await el.scrollIntoViewIfNeeded()
        await page.waitForTimeout(500)
      }
      await page.waitForTimeout(1000)
      await page.screenshot({ path: `screenshots/mobile/${p.name}.png`, fullPage: !p.scroll })
    })
  }
})

// Full-page screenshots of landing
test('full-page landing desktop', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(2000)
  await page.screenshot({ path: 'screenshots/desktop/00-landing-full.png', fullPage: true })
})

test('full-page landing mobile', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(2000)
  await page.screenshot({ path: 'screenshots/mobile/00-landing-full.png', fullPage: true })
})
