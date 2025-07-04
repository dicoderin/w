#!/usr/bin/env node
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import randomString from 'random-string';
import chalk from 'chalk';
import { program } from 'commander';
import inquirer from 'inquirer';

// Load environment variables
dotenv.config();

// Initialize plugins
puppeteer.use(StealthPlugin());

// Configure CLI
program
  .name('tusky-bot')
  .description('Automated bot for Tusky Testnet interactions')
  .version('1.0.0')
  .option('-c, --count <number>', 'Number of files to upload', parseInt)
  .option('-h, --headless', 'Run in headless mode')
  .option('-r, --reset', 'Reset browser session')
  .parse(process.argv);

const options = program.opts();

// Constants
const CONFIG = {
  TUSKY_URL: process.env.TUSKY_URL || 'https://testnet.app.tusky.io/vaults',
  HEADLESS: options.headless || process.env.HEADLESS_MODE === 'true',
  FILE_COUNT: options.count || parseInt(process.env.FILE_COUNT) || 1,
  USER_DATA_DIR: path.resolve('./user_data'),
  RANDOM_FILE_DIR: path.resolve('./random_files'),
  WALLET_PASSWORD: process.env.WALLET_PASSWORD,
  PRIVATE_KEY: process.env.PRIVATE_KEY
};

// Utility functions
const ensureDir = (dirPath) => {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
};

const generateRandomFile = () => {
  ensureDir(CONFIG.RANDOM_FILE_DIR);
  
  const fileName = `tusky_${Date.now()}_${randomString({ length: 6 })}.txt`;
  const filePath = path.join(CONFIG.RANDOM_FILE_DIR, fileName);
  const content = randomString({ length: 1024 });
  
  fs.writeFileSync(filePath, content);
  return filePath;
};

const resetSession = () => {
  if (fs.existsSync(CONFIG.USER_DATA_DIR)) {
    fs.rmSync(CONFIG.USER_DATA_DIR, { recursive: true, force: true });
    console.log(chalk.green('✓ Browser session reset successfully'));
  } else {
    console.log(chalk.yellow('ℹ No existing session found'));
  }
};

const validateConfig = () => {
  if (!CONFIG.PRIVATE_KEY) {
    console.log(chalk.red('✖ Error: PRIVATE_KEY is not defined in .env file'));
    process.exit(1);
  }
  
  if (!CONFIG.WALLET_PASSWORD) {
    console.log(chalk.red('✖ Error: WALLET_PASSWORD is not defined in .env file'));
    process.exit(1);
  }
  
  return true;
};

const importWallet = async (page) => {
  console.log(chalk.cyan('⏳ Importing wallet...'));
  
  await page.goto('chrome-extension://opcgpfmipidbgpenhmajoajpbobppdil/ui.html#/welcome');
  
  // Click import existing wallet
  await page.waitForSelector('button:has-text("Import an existing wallet")');
  await page.click('button:has-text("Import an existing wallet")');
  
  // Agree to terms
  await page.waitForSelector('button:has-text("I agree")');
  await page.click('button:has-text("I agree")');
  
  // Enter private key
  await page.waitForSelector('textarea[name="importedPrivateKey"]');
  await page.type('textarea[name="importedPrivateKey"]', CONFIG.PRIVATE_KEY);
  
  // Set password
  await page.type('input[name="password"]', CONFIG.WALLET_PASSWORD);
  await page.type('input[name="confirmPassword"]', CONFIG.WALLET_PASSWORD);
  
  // Import wallet
  await page.click('button:has-text("Import")');
  
  // Wait for import to complete
  await page.waitForSelector('div:has-text("Wallet created successfully")', { timeout: 10000 });
  console.log(chalk.green('✓ Wallet imported successfully'));
};

const connectToTusky = async (page) => {
  console.log(chalk.cyan('⏳ Connecting to Tusky...'));
  await page.goto(CONFIG.TUSKY_URL, { 
    waitUntil: 'networkidle2', 
    timeout: 60000 
  });

  // Connect wallet
  await page.waitForSelector('button:has-text("Connect Wallet")', { timeout: 15000 });
  await page.click('button:has-text("Connect Wallet")');
  
  // Select Sui Wallet
  await page.waitForSelector('.wallet-option', { timeout: 10000 });
  await page.evaluate(() => {
    const wallets = [...document.querySelectorAll('.wallet-option')];
    const suiWallet = wallets.find(w => w.textContent.includes('Sui Wallet'));
    if (suiWallet) suiWallet.click();
  });
  
  // Handle wallet connection in extension
  const pages = await page.browser().pages();
  const walletPage = pages.find(p => p.url().includes('chrome-extension://'));
  
  if (walletPage) {
    await walletPage.bringToFront();
    await walletPage.waitForSelector('button:has-text("Connect")', { timeout: 5000 });
    await walletPage.click('button:has-text("Connect")');
    await page.bringToFront();
  }
  
  console.log(chalk.green('✓ Wallet connected to Tusky'));
};

const createVault = async (page) => {
  try {
    console.log(chalk.cyan('⏳ Checking vault...'));
    await page.waitForSelector('button:has-text("Create Vault")', { timeout: 5000 });
    
    console.log(chalk.cyan('⏳ Creating vault...'));
    await page.click('button:has-text("Create Vault")');
    
    // Confirm in wallet
    const pages = await page.browser().pages();
    const walletPage = pages.find(p => p.url().includes('chrome-extension://'));
    
    if (walletPage) {
      await walletPage.bringToFront();
      await walletPage.waitForSelector('button:has-text("Approve")', { timeout: 5000 });
      await walletPage.click('button:has-text("Approve")');
      await page.bringToFront();
    }
    
    await page.waitForSelector('div:has-text("Vault created successfully")', { timeout: 15000 });
    console.log(chalk.green('✓ Vault created successfully'));
  } catch (error) {
    console.log(chalk.yellow('ℹ Using existing vault'));
  }
};

const uploadFile = async (page, filePath) => {
  console.log(chalk.cyan(`⏳ Uploading file: ${path.basename(filePath)}`));
  
  await page.waitForSelector('button:has-text("Upload")', { timeout: 10000 });
  await page.click('button:has-text("Upload")');
  
  // Select file
  const input = await page.waitForSelector('input[type="file"]', { timeout: 5000 });
  await input.uploadFile(filePath);
  
  // Confirm upload
  await page.waitForSelector('button:has-text("Upload File")', { timeout: 5000 });
  await page.click('button:has-text("Upload File")');
  
  // Confirm transaction in wallet
  const pages = await page.browser().pages();
  const walletPage = pages.find(p => p.url().includes('chrome-extension://'));
  
  if (walletPage) {
    await walletPage.bringToFront();
    await walletPage.waitForSelector('button:has-text("Approve")', { timeout: 5000 });
    await walletPage.click('button:has-text("Approve")');
    await page.bringToFront();
  }
  
  // Wait for success
  await page.waitForSelector('.MuiAlert-filledSuccess', { timeout: 30000 });
  console.log(chalk.green(`✓ File uploaded successfully: ${path.basename(filePath)}`));
};

const main = async () => {
  // Handle reset command
  if (options.reset) {
    resetSession();
    return;
  }

  // Validate configuration
  validateConfig();
  
  console.log(chalk.blue.bold('\n🚀 Starting Tusky Autobot\n'));
  console.log(chalk.cyan(`ℹ Mode: ${CONFIG.HEADLESS ? 'Headless' : 'Visible'}`));
  console.log(chalk.cyan(`ℹ Files to upload: ${CONFIG.FILE_COUNT}`));

  // Prepare directories
  ensureDir(CONFIG.USER_DATA_DIR);
  ensureDir(CONFIG.RANDOM_FILE_DIR);

  // Launch browser
  const browser = await puppeteer.launch({
    headless: CONFIG.HEADLESS,
    userDataDir: CONFIG.USER_DATA_DIR,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-web-security',
      '--disable-features=IsolateOrigins,site-per-process',
      '--disable-extensions-except=./wallet_extension',
      '--load-extension=./wallet_extension'
    ],
    ignoreHTTPSErrors: true,
    defaultViewport: null,
    executablePath: process.env.CHROME_BIN || null // Gunakan chrome yang tersedia di sistem
  });

  try {
    const pages = await browser.pages();
    const page = pages[0] || await browser.newPage();

    // Import wallet if not already done
    const walletPage = await browser.newPage();
    await importWallet(walletPage);
    await walletPage.close();

    // Connect to Tusky
    await connectToTusky(page);
    
    // Create vault if needed
    await createVault(page);
    
    // Upload files
    for (let i = 1; i <= CONFIG.FILE_COUNT; i++) {
      const filePath = generateRandomFile();
      await uploadFile(page, filePath);
      console.log(chalk.cyan(`ℹ Progress: ${i}/${CONFIG.FILE_COUNT}`));
    }
    
    console.log(chalk.green.bold('\n✅ All operations completed successfully!'));
  } catch (error) {
    console.error(chalk.red.bold('\n✖ Error occurred:'));
    console.error(chalk.red(error.stack || error.message));
    
    const pages = await browser.pages();
    for (const p of pages) {
      try {
        await p.screenshot({ path: `error-${Date.now()}.png`, fullPage: true });
      } catch (screenshotError) {
        console.error(chalk.red('Failed to take screenshot:', screenshotError.message));
      }
    }
    console.log(chalk.yellow('ℹ Screenshots saved for debugging'));
  } finally {
    try {
      await browser.close();
    } catch (browserCloseError) {
      console.error(chalk.red('Error closing browser:', browserCloseError.message));
    }
  }
};

// Run the bot
main();
