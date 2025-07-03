// index.js
const puppeteer = require('puppeteer');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Konfigurasi
const CONFIG = {
  TUSKY_URL: 'https://testnet.app.tusky.io/vaults',
  TUSKY_API_KEY: '126b0069-e7b1-4eb3-90b4-b2ef4acbc70f',
  UNSPLASH_ACCESS_KEY: 'W23RfN0BihTEhsEiSDQXtyE1f0ehUIV1-VwquAnEBUI',
  UNSPLASH_SECRET_KEY: '-MyiLNfPoKn5J3Dbwr8qzlIPKfl4qKWg0SHNeqX0Wmc',
  UNSPLASH_APP_ID: '772761',
  SUI_RPC_URL: 'https://fullnode.testnet.sui.io/',
  SUI_PRIVATE_KEY: 'suiprivkey1qz7ny8h3dm3c7vehmtrakazkzwqn2fs9gjnv5y9s53dd65fkqumyuen0cm7',
  DOWNLOAD_DIR: path.join(__dirname, 'downloads'),
  UPLOAD_INTERVAL: 10 * 60 * 1000, // 10 menit dalam milidetik
  MAX_RETRIES: 5,
  RETRY_DELAY: 10000, // 10 detik
  BROWSER_TIMEOUT: 60000, // 60 detik
};

// Pastikan direktori download ada
if (!fs.existsSync(CONFIG.DOWNLOAD_DIR)) {
  fs.mkdirSync(CONFIG.DOWNLOAD_DIR, { recursive: true });
}

// Fungsi untuk log dengan timestamp
function logWithTimestamp(message) {
  const timestamp = new Date().toLocaleString();
  console.log(`[${timestamp}] ${message}`);
}

// Fungsi untuk mendapatkan gambar acak dari Unsplash API
async function getRandomImage() {
  try {
    logWithTimestamp('Mengambil gambar acak dari Unsplash...');
    
    const response = await axios.get('https://api.unsplash.com/photos/random', {
      headers: { 'Authorization': `Client-ID ${CONFIG.UNSPLASH_ACCESS_KEY}` },
      params: { 
        orientation: 'landscape',
        featured: true,
        w: 1920,
        h: 1080
      },
      timeout: 30000
    });

    const imageUrl = response.data.urls.regular;
    const imagePath = path.join(CONFIG.DOWNLOAD_DIR, `image_${Date.now()}.jpg`);
    
    logWithTimestamp(`Mengunduh gambar dari: ${imageUrl}`);
    
    const imageResponse = await axios({
      url: imageUrl,
      method: 'GET',
      responseType: 'stream',
      timeout: 30000
    });

    return new Promise((resolve, reject) => {
      const writer = fs.createWriteStream(imagePath);
      imageResponse.data.pipe(writer);
      
      writer.on('finish', () => {
        logWithTimestamp(`Gambar berhasil disimpan ke: ${imagePath}`);
        resolve(imagePath);
      });
      
      writer.on('error', (err) => {
        logWithTimestamp(`Error menyimpan gambar: ${err.message}`);
        reject(err);
      });
    });
  } catch (error) {
    logWithTimestamp(`Error dari Unsplash: ${error.response?.data || error.message}`);
    throw error;
  }
}

// Fungsi untuk menunggu elemen muncul dengan retry
async function waitForSelectorWithRetry(page, selector, options = {}) {
  const timeout = options.timeout || 15000;
  let retries = 0;
  
  while (retries < CONFIG.MAX_RETRIES) {
    try {
      logWithTimestamp(`Menunggu selector: ${selector} (attempt ${retries + 1})`);
      return await page.waitForSelector(selector, { timeout, ...options });
    } catch (error) {
      retries++;
      logWithTimestamp(`Retry ${retries}/${CONFIG.MAX_RETRIES} untuk selector: ${selector}`);
      if (retries >= CONFIG.MAX_RETRIES) {
        logWithTimestamp(`Gagal menemukan selector setelah ${CONFIG.MAX_RETRIES} percobaan: ${selector}`);
        throw error;
      }
      await page.waitForTimeout(CONFIG.RETRY_DELAY);
    }
  }
}

// Fungsi untuk mengklik elemen dengan retry
async function clickWithRetry(page, selector, options = {}) {
  try {
    const element = await waitForSelectorWithRetry(page, selector, options);
    await element.click();
    logWithTimestamp(`Berhasil klik elemen: ${selector}`);
    await page.waitForTimeout(1000); // Tunggu sebentar setelah klik
  } catch (error) {
    logWithTimestamp(`Error klik normal, coba evaluasi: ${selector}`);
    try {
      await page.evaluate(sel => {
        const el = document.querySelector(sel);
        if (el) {
          el.click();
          return true;
        }
        return false;
      }, selector);
      logWithTimestamp(`Berhasil klik dengan evaluate: ${selector}`);
    } catch (evalError) {
      logWithTimestamp(`Gagal klik dengan evaluate: ${selector}`);
      throw evalError;
    }
  }
}

// Fungsi untuk memeriksa apakah elemen ada di halaman
async function elementExists(page, selector, timeout = 5000) {
  try {
    await page.waitForSelector(selector, { timeout });
    return true;
  } catch (error) {
    return false;
  }
}

// Fungsi untuk menutup modal jika muncul
async function handleModal(page) {
  try {
    const modalSelectors = [
      '.modal .close',
      '.dialog .close', 
      '[role="dialog"] .close',
      '.modal button[aria-label="Close"]',
      '.dialog button[aria-label="Close"]',
      '[role="dialog"] button[aria-label="Close"]',
      '.modal .cancel',
      '.dialog .cancel',
      'button:has-text("Cancel")',
      'button:has-text("Close")',
      'button:has-text("Dismiss")'
    ];

    for (const selector of modalSelectors) {
      if (await elementExists(page, selector, 2000)) {
        await clickWithRetry(page, selector);
        logWithTimestamp('Modal ditutup');
        await page.waitForTimeout(2000);
        return true;
      }
    }
    return false;
  } catch (error) {
    logWithTimestamp('Tidak ada modal yang perlu ditutup');
    return false;
  }
}

// Fungsi untuk membersihkan file gambar lama
function cleanupOldImages() {
  try {
    const files = fs.readdirSync(CONFIG.DOWNLOAD_DIR);
    files.forEach(file => {
      if (file.startsWith('image_') && file.endsWith('.jpg')) {
        const filePath = path.join(CONFIG.DOWNLOAD_DIR, file);
        const stats = fs.statSync(filePath);
        const now = Date.now();
        const fileAge = now - stats.mtime.getTime();
        
        // Hapus file yang lebih dari 1 jam
        if (fileAge > 3600000) {
          fs.unlinkSync(filePath);
          logWithTimestamp(`File lama dihapus: ${filePath}`);
        }
      }
    });
  } catch (error) {
    logWithTimestamp(`Error cleanup: ${error.message}`);
  }
}

// Fungsi untuk setup browser dengan konfigurasi optimal
async function setupBrowser() {
  logWithTimestamp('Meluncurkan browser...');
  
  const browserArgs = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--disable-gpu',
    '--window-size=1920,1080',
    '--disable-web-security',
    '--disable-features=VizDisplayCompositor',
    '--disable-extensions',
    '--disable-plugins',
    '--disable-images', // Hemat bandwidth
    '--disable-javascript', // Akan diaktifkan setelah halaman dimuat
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-background-timer-throttling',
    '--disable-renderer-backgrounding',
    '--disable-backgrounding-occluded-windows'
  ];

  const browser = await puppeteer.launch({
    headless: true,
    args: browserArgs,
    defaultViewport: { width: 1920, height: 1080 },
    timeout: CONFIG.BROWSER_TIMEOUT,
    ignoreHTTPSErrors: true,
    ignoreDefaultArgs: ['--disable-extensions']
  });

  return browser;
}

// Fungsi untuk setup halaman dengan konfigurasi optimal
async function setupPage(browser) {
  const page = await browser.newPage();
  
  // Set user agent modern
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36');
  
  // Set headers tambahan
  await page.setExtraHTTPHeaders({
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
  });

  // Log console messages dari halaman
  page.on('console', msg => {
    if (msg.type() === 'error') {
      logWithTimestamp(`Browser Error: ${msg.text()}`);
    }
  });
  
  // Handle dialog JavaScript
  page.on('dialog', async dialog => {
    logWithTimestamp(`Dialog muncul: ${dialog.message()}`);
    await dialog.dismiss();
  });

  // Handle request failures
  page.on('requestfailed', request => {
    logWithTimestamp(`Request failed: ${request.url()}`);
  });

  return page;
}

// Fungsi untuk inject wallet simulation
async function injectWalletSimulation(page) {
  await page.evaluateOnNewDocument(() => {
    const walletData = {
      name: 'Sui Wallet',
      address: '0x1234567890abcdef1234567890abcdef12345678',
      chain: 'sui',
      connected: true
    };
    
    // Fungsi setup wallet
    const setupWallet = () => {
      try {
        localStorage.setItem('suiWallet', JSON.stringify(walletData));
        localStorage.setItem('connectedWallets', JSON.stringify([walletData]));
        
        // Tambahkan wallet object ke window
        window.suiWallet = {
          ...walletData,
          signAndExecuteTransaction: async (tx) => {
            console.log('Simulasi sign transaction:', tx);
            // Simulasi delay untuk transaction
            await new Promise(resolve => setTimeout(resolve, 2000));
            return { success: true, data: "simulated_transaction_result" };
          },
          connect: async () => {
            console.log('Wallet connected');
            return walletData;
          },
          disconnect: async () => {
            console.log('Wallet disconnected');
          }
        };

        // Dispatch event untuk memberitahu aplikasi
        window.dispatchEvent(new CustomEvent('wallet-connected', { detail: walletData }));
        
      } catch (error) {
        console.error('Error setup wallet:', error);
      }
    };
    
    // Jalankan setup segera
    setupWallet();
    
    // Setup ulang setelah DOM ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', setupWallet);
    }
    
    // Observer untuk memastikan wallet tetap ada
    const observer = new MutationObserver(() => {
      if (!localStorage.getItem('suiWallet')) {
        setupWallet();
      }
    });
    
    // Mulai observasi setelah DOM dimuat
    if (document.body) {
      observer.observe(document.body, { childList: true, subtree: true });
    } else {
      document.addEventListener('DOMContentLoaded', () => {
        observer.observe(document.body, { childList: true, subtree: true });
      });
    }
  });
}

// Fungsi utama untuk menjalankan bot
async function runBot() {
  logWithTimestamp('Memulai Tusky Bot...');
  
  // Cleanup file lama
  cleanupOldImages();

  const browser = await setupBrowser();
  let page;

  try {
    page = await setupPage(browser);
    
    // Inject wallet simulation
    await injectWalletSimulation(page);

    logWithTimestamp('Membuka Tusky Testnet...');
    await page.goto(CONFIG.TUSKY_URL, {
      waitUntil: 'networkidle2',
      timeout: 60000
    });

    // Tunggu hingga halaman siap
    await page.waitForTimeout(5000);

    // Loop utama untuk operasi upload
    let uploadCount = 0;
    while (true) {
      try {
        uploadCount++;
        logWithTimestamp(`=== Memulai upload ke-${uploadCount} ===`);

        // Handle modal popup
        await handleModal(page);

        // Refresh halaman setiap 10 upload untuk mencegah memory leak
        if (uploadCount % 10 === 0) {
          logWithTimestamp('Refresh halaman untuk maintenance...');
          await page.reload({ waitUntil: 'networkidle2' });
          await page.waitForTimeout(5000);
        }

        // Navigasi ke halaman vaults jika diperlukan
        if (!page.url().includes('/vaults')) {
          logWithTimestamp('Navigasi ke halaman vaults...');
          await page.goto(CONFIG.TUSKY_URL, { waitUntil: 'networkidle2' });
          await page.waitForTimeout(5000);
        }

        // Cek dan handle koneksi wallet
        await handleWalletConnection(page);

        // Cari atau buat vault
        const vaultAccessible = await handleVaultAccess(page);
        
        if (!vaultAccessible) {
          logWithTimestamp('Gagal mengakses vault, refresh halaman...');
          await page.reload({ waitUntil: 'networkidle2' });
          await page.waitForTimeout(5000);
          continue;
        }

        // Proses upload
        await performUpload(page);

        // Tunggu interval berikutnya
        const minutes = CONFIG.UPLOAD_INTERVAL / 60000;
        logWithTimestamp(`Upload ke-${uploadCount} selesai! Menunggu ${minutes} menit untuk upload berikutnya...`);
        await page.waitForTimeout(CONFIG.UPLOAD_INTERVAL);

      } catch (error) {
        logWithTimestamp(`Error dalam upload ke-${uploadCount}: ${error.message}`);
        
        // Bersihkan file gambar yang tertinggal
        cleanupOldImages();
        
        // Tunggu sebelum mencoba lagi
        await page.waitForTimeout(30000);
        
        // Reload halaman untuk reset state
        try {
          await page.reload({ waitUntil: 'networkidle2' });
          await page.waitForTimeout(5000);
        } catch (reloadError) {
          logWithTimestamp(`Error reload: ${reloadError.message}`);
          // Jika reload gagal, buat halaman baru
          await page.close();
          page = await setupPage(browser);
          await injectWalletSimulation(page);
          await page.goto(CONFIG.TUSKY_URL, { waitUntil: 'networkidle2' });
        }
      }
    }
  } catch (error) {
    logWithTimestamp(`Error utama: ${error.message}`);
    throw error;
  } finally {
    if (page) await page.close();
    await browser.close();
  }
}

// Fungsi untuk handle koneksi wallet
async function handleWalletConnection(page) {
  const connectButtons = [
    'button:has-text("Connect Wallet")',
    'button[data-testid="connect-wallet"]',
    '.connect-wallet-button',
    'button:contains("Connect")'
  ];

  for (const selector of connectButtons) {
    if (await elementExists(page, selector, 3000)) {
      logWithTimestamp('Menghubungkan wallet...');
      await clickWithRetry(page, selector);
      await page.waitForTimeout(3000);
      
      // Pilih Sui Wallet jika opsi tersedia
      const suiWalletSelectors = [
        'button:has-text("Sui Wallet")',
        'button[data-testid="sui-wallet"]',
        '.sui-wallet-option'
      ];

      for (const suiSelector of suiWalletSelectors) {
        if (await elementExists(page, suiSelector, 3000)) {
          await clickWithRetry(page, suiSelector);
          await page.waitForTimeout(5000);
          break;
        }
      }
      break;
    }
  }
}

// Fungsi untuk handle akses vault
async function handleVaultAccess(page) {
  // Cek vault yang sudah ada
  const vaultSelectors = [
    '.vault-card',
    '.vault-item',
    '[data-testid="vault-card"]',
    '.vault-container .vault'
  ];

  for (const selector of vaultSelectors) {
    if (await elementExists(page, selector, 3000)) {
      logWithTimestamp('Mengakses vault yang sudah ada...');
      await clickWithRetry(page, selector);
      await page.waitForTimeout(5000);
      return true;
    }
  }

  // Buat vault baru jika tidak ada
  const createVaultSelectors = [
    'button:has-text("Create Vault")',
    'button[data-testid="create-vault"]',
    '.create-vault-button'
  ];

  for (const selector of createVaultSelectors) {
    if (await elementExists(page, selector, 3000)) {
      logWithTimestamp('Membuat vault baru...');
      await clickWithRetry(page, selector);
      await page.waitForTimeout(3000);
      
      // Isi nama vault
      const nameInputSelectors = [
        'input[placeholder*="vault name"]',
        'input[placeholder*="Vault name"]',
        'input[data-testid="vault-name"]',
        'input[name="vaultName"]'
      ];

      for (const inputSelector of nameInputSelectors) {
        if (await elementExists(page, inputSelector, 3000)) {
          const nameInput = await page.$(inputSelector);
          await nameInput.click({ clickCount: 3 });
          await nameInput.type(`TuskyVault_${Date.now()}`);
          break;
        }
      }
      
      // Submit form
      const submitSelectors = [
        'button:has-text("Create")',
        'button[type="submit"]',
        'button[data-testid="create-vault-submit"]'
      ];

      for (const submitSelector of submitSelectors) {
        if (await elementExists(page, submitSelector, 3000)) {
          await clickWithRetry(page, submitSelector);
          await page.waitForTimeout(8000);
          return true;
        }
      }
    }
  }

  return false;
}

// Fungsi untuk melakukan upload
async function performUpload(page) {
  // Verifikasi berada di halaman vault
  const uploadSelectors = [
    'button:has-text("Upload")',
    'button[data-testid="upload-button"]',
    '.upload-button'
  ];

  let uploadButtonFound = false;
  for (const selector of uploadSelectors) {
    if (await elementExists(page, selector, 3000)) {
      uploadButtonFound = true;
      break;
    }
  }

  if (!uploadButtonFound) {
    throw new Error('Tidak berada di halaman vault yang benar');
  }

  // Dapatkan gambar baru
  logWithTimestamp('Mengunduh gambar acak...');
  const imagePath = await getRandomImage();

  try {
    // Mulai proses upload
    logWithTimestamp('Memulai proses upload...');
    
    for (const selector of uploadSelectors) {
      if (await elementExists(page, selector, 3000)) {
        await clickWithRetry(page, selector);
        break;
      }
    }
    
    // Tunggu input file
    const fileInputSelectors = [
      'input[type="file"]',
      'input[accept*="image"]',
      'input[data-testid="file-input"]'
    ];

    let fileInput = null;
    for (const selector of fileInputSelectors) {
      if (await elementExists(page, selector, 10000)) {
        fileInput = await page.$(selector);
        break;
      }
    }

    if (!fileInput) {
      throw new Error('Input file tidak ditemukan');
    }

    await fileInput.uploadFile(imagePath);
    logWithTimestamp('File diunggah ke input');
    await page.waitForTimeout(3000);

    // Konfirmasi upload
    const confirmSelectors = [
      'button:has-text("Confirm")',
      'button:has-text("Upload")',
      'button[data-testid="confirm-upload"]',
      'button[type="submit"]'
    ];

    for (const selector of confirmSelectors) {
      if (await elementExists(page, selector, 5000)) {
        await clickWithRetry(page, selector);
        logWithTimestamp('Upload dikonfirmasi');
        break;
      }
    }
    
    // Handle persetujuan transaksi
    const approveSelectors = [
      'button:has-text("Approve")',
      'button:has-text("Sign")',
      'button:has-text("Confirm Transaction")',
      'button[data-testid="approve-transaction"]'
    ];

    for (const selector of approveSelectors) {
      if (await elementExists(page, selector, 10000)) {
        await clickWithRetry(page, selector);
        logWithTimestamp('Transaksi disetujui');
        break;
      }
    }

    // Tunggu proses upload selesai
    await page.waitForTimeout(10000);
    logWithTimestamp('Upload berhasil diselesaikan!');

  } finally {
    // Bersihkan file gambar
    if (fs.existsSync(imagePath)) {
      fs.unlinkSync(imagePath);
      logWithTimestamp('File gambar dihapus');
    }
  }
}

// Handle shutdown graceful
process.on('SIGINT', () => {
  logWithTimestamp('Bot dihentikan manual (SIGINT)');
  cleanupOldImages();
  process.exit(0);
});

process.on('SIGTERM', () => {
  logWithTimestamp('Bot dihentikan (SIGTERM)');
  cleanupOldImages();
  process.exit(0);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logWithTimestamp(`Uncaught Exception: ${error.message}`);
  cleanupOldImages();
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logWithTimestamp(`Unhandled Rejection at: ${promise}, reason: ${reason}`);
  cleanupOldImages();
  process.exit(1);
});

// Jalankan bot dengan mekanisme retry
async function startBot() {
  let attempt = 1;
  const maxAttempts = 3;
  
  while (attempt <= maxAttempts) {
    try {
      logWithTimestamp(`=== Memulai bot (Attempt ${attempt}/${maxAttempts}) ===`);
      await runBot();
      break;
    } catch (error) {
      logWithTimestamp(`Attempt ${attempt} gagal: ${error.message}`);
      
      // Cleanup sebelum retry
      cleanupOldImages();
      
      attempt++;
      if (attempt <= maxAttempts) {
        const waitTime = attempt * 30000; // Tunggu lebih lama setiap attempt
        logWithTimestamp(`Menunggu ${waitTime/1000} detik sebelum mencoba lagi...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
      }
    }
  }
  
  if (attempt > maxAttempts) {
    logWithTimestamp(`Bot gagal setelah ${maxAttempts} percobaan`);
    process.exit(1);
  }
}

// Mulai bot
logWithTimestamp('=== Tusky Bot Starting ===');
startBot().catch(error => {
  logWithTimestamp(`Fatal error: ${error.message}`);
  cleanupOldImages();
  process.exit(1);
});
