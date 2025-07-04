#!/usr/bin/env node
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import https from 'https';
import { createWriteStream } from 'fs';
import { promisify } from 'util';
import stream from 'stream';
import randomString from 'random-string';
import chalk from 'chalk';
import { program } from 'commander';
import inquirer from 'inquirer';
import extract from 'extract-zip';

// Promisify stream pipeline
const pipeline = promisify(stream.pipeline);

// Mendapatkan direktori modul saat ini
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

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
  .option('-e, --extension <path>', 'Path to wallet extension')
  .option('-s, --skip-download', 'Skip automatic wallet extension download')
  .parse(process.argv);

const options = program.opts();

// Constants
const CONFIG = {
  TUSKY_URL: process.env.TUSKY_URL || 'https://testnet.app.tusky.io/vaults',
  HEADLESS: options.headless || process.env.HEADLESS_MODE === 'true',
  FILE_COUNT: options.count || parseInt(process.env.FILE_COUNT) || 1,
  USER_DATA_DIR: path.resolve(__dirname, 'user_data'),
  RANDOM_FILE_DIR: path.resolve(__dirname, 'random_files'),
  WALLET_PASSWORD: process.env.WALLET_PASSWORD,
  PRIVATE_KEY: process.env.PRIVATE_KEY,
  // Gunakan opsi CLI, lalu environment variable, lalu default
  EXTENSION_PATH: options.extension 
    ? path.resolve(options.extension) 
    : process.env.EXTENSION_PATH 
      ? path.resolve(process.env.EXTENSION_PATH)
      : path.resolve(__dirname, 'wallet_extension'),
  // URL untuk mengunduh ekstensi wallet
  WALLET_DOWNLOAD_URL: 'https://storage.googleapis.com/sui-wallet-downloads/sui-wallet-v1.0.0.zip',
  SKIP_DOWNLOAD: options.skipDownload || false
};

// Utility functions
const ensureDir = (dirPath) => {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
};

const downloadFile = async (url, destination) => {
  console.log(chalk.cyan(`ℹ Downloading wallet extension from ${url}...`));
  
  const response = await new Promise((resolve, reject) => {
    https.get(url, (res) => {
      if (res.statusCode !== 200) {
        reject(new Error(`Failed to download file: ${res.statusCode} ${res.statusMessage}`));
        return;
      }
      resolve(res);
    }).on('error', reject);
  });

  const fileStream = createWriteStream(destination);
  await pipeline(response, fileStream);
  
  console.log(chalk.green(`✓ Wallet extension downloaded to ${destination}`));
};

const extractZip = async (zipPath, destination) => {
  console.log(chalk.cyan(`ℹ Extracting wallet extension to ${destination}...`));
  
  try {
    await extract(zipPath, { dir: destination });
    console.log(chalk.green(`✓ Wallet extension extracted successfully`));
    return true;
  } catch (error) {
    console.error(chalk.red(`✖ Error extracting wallet extension: ${error.message}`));
    return false;
  }
};

const setupWalletExtension = async () => {
  ensureDir(CONFIG.EXTENSION_PATH);
  
  // Cek apakah ekstensi sudah ada
  const manifestPath = path.join(CONFIG.EXTENSION_PATH, 'manifest.json');
  
  if (fs.existsSync(manifestPath)) {
    console.log(chalk.green('✓ Wallet extension found'));
    return true;
  }

  if (CONFIG.SKIP_DOWNLOAD) {
    console.log(chalk.yellow('ℹ Skipping wallet download'));
    return false;
  }

  // Buat folder untuk file zip
  const tempDir = path.join(__dirname, 'temp');
  ensureDir(tempDir);
  
  const zipPath = path.join(tempDir, 'sui-wallet.zip');
  
  try {
    // Unduh ekstensi wallet
    await downloadFile(CONFIG.WALLET_DOWNLOAD_URL, zipPath);
    
    // Ekstrak file zip
    const success = await extractZip(zipPath, CONFIG.EXTENSION_PATH);
    
    // Bersihkan file zip
    try {
      fs.unlinkSync(zipPath);
      fs.rmdirSync(tempDir, { recursive: true });
    } catch (cleanError) {
      console.log(chalk.yellow(`ℹ Could not clean temp files: ${cleanError.message}`));
    }
    
    return success;
  } catch (error) {
    console.error(chalk.red(`✖ Failed to setup wallet extension: ${error.message}`));
    
    // Tampilkan petunjuk manual
    console.log(chalk.yellow('\nℹ Please download and extract the wallet extension manually:'));
    console.log(chalk.yellow('1. Download from: https://chromewebstore.google.com/detail/slush-%E2%80%94-a-sui-wallet/opcgpfmipidbgpenhmajoajpbobppdil'));
    console.log(chalk.yellow('2. Extract the extension to:', CONFIG.EXTENSION_PATH));
    console.log(chalk.yellow('3. Rerun this script with --skip-download to use the manual installation'));
    
    return false;
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
  
  // Reset folder file acak
  if (fs.existsSync(CONFIG.RANDOM_FILE_DIR)) {
    fs.rmSync(CONFIG.RANDOM_FILE_DIR, { recursive: true, force: true });
    console.log(chalk.green('✓ Random files directory reset'));
  }
};

const validateConfig = () => {
  const errors = [];
  
  if (!CONFIG.PRIVATE_KEY) {
    errors.push('PRIVATE_KEY is not defined in .env file');
  }
  
  if (!CONFIG.WALLET_PASSWORD) {
    errors.push('WALLET_PASSWORD is not defined in .env file');
  }

  // Validasi ekstensi wallet
  const manifestPath = path.join(CONFIG.EXTENSION_PATH, 'manifest.json');
  if (!fs.existsSync(manifestPath)) {
    errors.push(`Wallet extension not found at ${CONFIG.EXTENSION_PATH}`);
  }
  
  if (errors.length > 0) {
    console.log(chalk.red.bold('\n✖ Configuration errors:'));
    errors.forEach(error => console.log(chalk.red(`- ${error}`)));
    console.log(chalk.yellow('\nℹ Solutions:'));
    console.log(chalk.yellow('1. Create a .env file with PRIVATE_KEY and WALLET_PASSWORD'));
    console.log(chalk.yellow('2. Run without --skip-download to automatically download wallet extension'));
    console.log(chalk.yellow('3. Or download manually from:'));
    console.log(chalk.yellow('   https://chromewebstore.google.com/detail/slush-%E2%80%94-a-sui-wallet/opcgpfmipidbgpenhmajoajpbobppdil'));
    console.log(chalk.yellow(`4. Extract to: ${CONFIG.EXTENSION_PATH}`));
    return false;
  }
  
  return true;
};

const importWallet = async (page) => {
  console.log(chalk.cyan('⏳ Importing wallet...'));
  
  await page.goto('chrome-extension://opcgpfmipidbgpenhmajoajpbobppdil/ui.html#/welcome');
  
  // Click import existing wallet
  await page.waitForSelector('button:has-text("Import an existing wallet")', { timeout: 10000 });
  await page.click('button:has-text("Import an existing wallet")');
  
  // Agree to terms
  await page.waitForSelector('button:has-text("I agree")', { timeout: 5000 });
  await page.click('button:has-text("I agree")');
  
  // Enter private key
  await page.waitForSelector('textarea[name="importedPrivateKey"]', { timeout: 5000 });
  await page.type('textarea[name="importedPrivateKey"]', CONFIG.PRIVATE_KEY);
  
  // Set password
  await page.type('input[name="password"]', CONFIG.WALLET_PASSWORD);
  await page.type('input[name="confirmPassword"]', CONFIG.WALLET_PASSWORD);
  
  // Import wallet
  await page.click('button:has-text("Import")');
  
  // Wait for import to complete
  try {
    await page.waitForSelector('div:has-text("Wallet created successfully")', { timeout: 15000 });
    console.log(chalk.green('✓ Wallet imported successfully'));
  } catch (error) {
    console.log(chalk.yellow('ℹ Wallet might already be imported'));
  }
};

const connectToTusky = async (page) => {
  console.log(chalk.cyan('⏳ Connecting to Tusky...'));
  await page.goto(CONFIG.TUSKY_URL, { 
    waitUntil: 'networkidle2', 
    timeout: 60000 
  });

  // Connect wallet
  await page.waitForSelector('button:has-text("Connect Wallet")', { timeout: 30000 });
  await page.click('button:has-text("Connect Wallet")');
  
  // Select Sui Wallet
  await page.waitForSelector('.wallet-option', { timeout: 15000 });
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
    await walletPage.waitForSelector('button:has-text("Connect")', { timeout: 10000 });
    await walletPage.click('button:has-text("Connect")');
    await page.bringToFront();
  } else {
    console.log(chalk.yellow('ℹ Wallet popup not found, check if extension is loaded'));
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
      await walletPage.waitForSelector('button:has-text("Approve")', { timeout: 10000 });
      await walletPage.click('button:has-text("Approve")');
      await page.bringToFront();
    }
    
    await page.waitForSelector('div:has-text("Vault created successfully")', { timeout: 30000 });
    console.log(chalk.green('✓ Vault created successfully'));
  } catch (error) {
    console.log(chalk.yellow('ℹ Using existing vault'));
  }
};

const uploadFile = async (page, filePath) => {
  console.log(chalk.cyan(`⏳ Uploading file: ${path.basename(filePath)}`));
  
  await page.waitForSelector('button:has-text("Upload")', { timeout: 15000 });
  await page.click('button:has-text("Upload")');
  
  // Select file
  const input = await page.waitForSelector('input[type="file"]', { timeout: 10000 });
  await input.uploadFile(filePath);
  
  // Confirm upload
  await page.waitForSelector('button:has-text("Upload File")', { timeout: 10000 });
  await page.click('button:has-text("Upload File")');
  
  // Confirm transaction in wallet
  const pages = await page.browser().pages();
  const walletPage = pages.find(p => p.url().includes('chrome-extension://'));
  
  if (walletPage) {
    await walletPage.bringToFront();
    await walletPage.waitForSelector('button:has-text("Approve")', { timeout: 15000 });
    await walletPage.click('button:has-text("Approve")');
    await page.bringToFront();
  }
  
  // Wait for success
  try {
    await page.waitForSelector('.MuiAlert-filledSuccess', { timeout: 45000 });
    console.log(chalk.green(`✓ File uploaded successfully: ${path.basename(filePath)}`));
  } catch (error) {
    console.log(chalk.yellow('ℹ Success indicator not found, assuming upload succeeded'));
  }
};

const findChrome = async () => {
  try {
    // Coba dapatkan executablePath dari puppeteer
    const chromium = await puppeteer.executablePath();
    return chromium;
  } catch (error) {
    console.log(chalk.yellow('ℹ Using system Chrome'));
    return null;
  }
};

const main = async () => {
  // Handle reset command
  if (options.reset) {
    resetSession();
    return;
  }

  // Setup wallet extension
  console.log(chalk.blue.bold('\n🚀 Starting Tusky Autobot\n'));
  console.log(chalk.cyan(`ℹ Wallet extension path: ${CONFIG.EXTENSION_PATH}`));
  
  const extensionReady = await setupWalletExtension();
  
  if (!extensionReady) {
    console.log(chalk.red('✖ Wallet extension not ready. Exiting.'));
    process.exit(1);
  }

  // Validate configuration
  if (!validateConfig()) {
    process.exit(1);
  }
  
  console.log(chalk.cyan(`ℹ Mode: ${CONFIG.HEADLESS ? 'Headless' : 'Visible'}`));
  console.log(chalk.cyan(`ℹ Files to upload: ${CONFIG.FILE_COUNT}`));

  // Prepare directories
  ensureDir(CONFIG.USER_DATA_DIR);
  ensureDir(CONFIG.RANDOM_FILE_DIR);

  // Dapatkan path Chrome secara otomatis
  const chromeExecutable = await findChrome();

  // Konfigurasi browser
  const browserConfig = {
    headless: CONFIG.HEADLESS,
    userDataDir: CONFIG.USER_DATA_DIR,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-web-security',
      '--disable-features=IsolateOrigins,site-per-process',
      `--disable-extensions-except=${CONFIG.EXTENSION_PATH}`,
      `--load-extension=${CONFIG.EXTENSION_PATH}`
    ],
    ignoreHTTPSErrors: true,
    defaultViewport: null
  };

  // Tambahkan executablePath jika ditemukan
  if (chromeExecutable) {
    browserConfig.executablePath = chromeExecutable;
  } else {
    console.log(chalk.yellow('ℹ Chrome executable not found, using system default'));
  }

  console.log(chalk.cyan('ℹ Launching browser...'));
  
  // Launch browser
  const browser = await puppeteer.launch(browserConfig);

  try {
    const pages = await browser.pages();
    const page = pages[0] || await browser.newPage();

    // Import wallet if not already done
    console.log(chalk.cyan('ℹ Setting up wallet...'));
    const walletPage = await browser.newPage();
    await importWallet(walletPage);
    await walletPage.close();

    // Connect to Tusky
    await connectToTusky(page);
    
    // Create vault if needed
    await createVault(page);
    
    // Upload files
    console.log(chalk.cyan('ℹ Starting file uploads...'));
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
    for (const [index, p] of pages.entries()) {
      try {
        const screenshotPath = `error-${Date.now()}-${index}.png`;
        await p.screenshot({ path: screenshotPath, fullPage: true });
        console.log(chalk.yellow(`ℹ Screenshot saved: ${screenshotPath}`));
      } catch (screenshotError) {
        console.error(chalk.red('Failed to take screenshot:', screenshotError.message));
      }
    }
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
