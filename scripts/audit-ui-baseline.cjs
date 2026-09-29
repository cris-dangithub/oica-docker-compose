#!/usr/bin/env node

/* Auditoría de solo lectura para la baseline visual de OICA. */
const { chromium } = require('playwright');
const path = require('node:path');

const baseUrl = process.env.OICA_AUDIT_URL || 'http://localhost';
const axePath = path.resolve(__dirname, '../frontend/node_modules/axe-core/axe.min.js');
const routes = ['/', '/subir-cartilla', '/archivos', '/tutorial', '/contact-us'];
const viewports = {
   desktop: { width: 1440, height: 1000 },
   mobile: { width: 390, height: 844 },
};

(async () => {
   const browser = await chromium.launch({ headless: true });
   const report = [];

   for (const [viewportName, viewport] of Object.entries(viewports)) {
      const context = await browser.newContext({ viewport, colorScheme: 'light' });

      for (const route of routes) {
         const page = await context.newPage();
         const consoleErrors = [];
         page.on('console', (message) => {
            if (message.type() === 'error') consoleErrors.push(message.text());
         });

         await page.goto(`${baseUrl}${route}`, { waitUntil: 'networkidle' });
         await page.addScriptTag({ path: axePath });
         const pageData = await page.evaluate(async () => {
            const axeResult = await window.axe.run(document, {
               runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa'] },
            });
            const html = document.documentElement;
            return {
               title: document.title,
               lang: html.lang,
               viewportWidth: html.clientWidth,
               scrollWidth: html.scrollWidth,
               horizontalOverflow: html.scrollWidth > html.clientWidth,
               h1Count: document.querySelectorAll('h1').length,
               navCount: document.querySelectorAll('nav').length,
               unlabeledControls: [...document.querySelectorAll('input, select, textarea')]
                  .filter((control) => !control.labels?.length && !control.getAttribute('aria-label'))
                  .map((control) => `${control.tagName.toLowerCase()}[${control.getAttribute('name') || control.getAttribute('type') || ''}]`),
               violations: axeResult.violations.map((violation) => ({
                  id: violation.id,
                  impact: violation.impact,
                  nodes: violation.nodes.length,
                  help: violation.help,
               })),
            };
         });

         report.push({ route, viewport: viewportName, consoleErrors, ...pageData });
         await page.close();
      }

      await context.close();
   }

   await browser.close();
   process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
})().catch((error) => {
   console.error(error);
   process.exitCode = 1;
});
