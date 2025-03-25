const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');
const dns = require('dns').promises;
const { URL } = require('url');
const cliProgress = require('cli-progress');
const sharp = require('sharp');
const { v4: uuidv4 } = require('uuid');

// ==============================
// 설정
// ==============================

const LIST_PATH = path.join(__dirname, 'list.txt');
const OUTPUT_PATH = path.join(__dirname, 'result.json');

const MAX_CONCURRENT_TABS = 5;
const IS_HEAD_MODE = false;
const PAGE_TIMEOUT = 15000;

const CAPTURE_ENABLED = true;
const CAPTURE_RETRY_COUNT = 2;
const CAPTURE_FORMAT = 'png';
const CAPTURE_DIR = path.join(__dirname, 'capture');

// ==============================
// 제공자 정보 패턴
// ==============================
const providerMap = [
  { keyword: 'akamai', name: 'AKAMAI' },
  { keyword: 'cloudflare', name: 'CLOUDFLARE' },
  { keyword: 'amazon', name: 'AMAZON' },
  { keyword: 'google', name: 'GOOGLE' },
  { keyword: 'kakao', name: 'KAKAO' },
  { keyword: 'naver', name: 'NAVER' },
  { keyword: 'azure', name: 'AZURE' },
  { keyword: 'oracle', name: 'ORACLE' },
  { keyword: 'netlify', name: 'NETLIFY' },
  { keyword: 'fastly', name: 'FASTLY' },
  { keyword: 'github', name: 'GITHUB' },
  { keyword: 'tistory', name: 'TISTORY' },
  { keyword: 'skcdn', name: 'SK CDN' }
];

function getCurrentTime() {
  const now = new Date();
  return now.toISOString().replace('T', ' ').replace('Z', '');
}

async function getIPAddress(hostname) {
  try {
    const result = await dns.lookup(hostname);
    return result.address;
  } catch {
    return 'Unknown';
  }
}

function detectProvider(ip, headers) {
  const allInfo = [ip, ...Object.values(headers).map(val => String(val).toLowerCase())].join(' ');
  for (const entry of providerMap) {
    if (allInfo.includes(entry.keyword.toLowerCase())) {
      return entry.name;
    }
  }
  return 'Unknown';
}

// 빈 캡처 생성 (DRM 등으로 실패 시)
async function createEmptyCapture(id) {
  const filePath = path.join(CAPTURE_DIR, `${id}.${CAPTURE_FORMAT}`);
  await sharp({
    create: {
      width: 800,
      height: 600,
      channels: 3,
      background: { r: 255, g: 255, b: 255 }
    }
  }).png().toFile(filePath);
}

// 실제 캡처 시도 함수
async function tryCapture(page, id) {
  const filePath = path.join(CAPTURE_DIR, `${id}.${CAPTURE_FORMAT}`);
  try {
    await page.setViewport({ width: 1280, height: 800, deviceScaleFactor: 2 });
    await page.screenshot({ path: filePath, fullPage: true, type: CAPTURE_FORMAT });
    return true;
  } catch {
    return false;
  }
}

// ==============================
// 각 URL 상태 확인
// ==============================
async function checkDomain(browser, inputUrl) {
  let url = inputUrl.trim();
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'https://' + url;
  }

  let id = uuidv4();
  const parsed = new URL(url);
  const domain = parsed.hostname;
  const page = await browser.newPage();

  try {
    const response = await page.goto(url, {
      timeout: PAGE_TIMEOUT,
      waitUntil: 'networkidle2'
    });

    const finalURL = page.url();
    let status = 'UP';
    if (finalURL.includes('warning.or.kr')) {
      status = 'WARNING';
    }

    const headers = response?.headers?.() || {};
    const ip = await getIPAddress(domain);
    const provider = detectProvider(ip, headers);
    const timestamp = getCurrentTime();

    if (CAPTURE_ENABLED) {
      let success = false;
      for (let i = 0; i < CAPTURE_RETRY_COUNT; i++) {
        success = await tryCapture(page, id);
        if (success) break;
      }
      if (!success) {
        await createEmptyCapture(id);
      }
    }

    return { id, domain, ip, status, provider, timestamp };
  } catch (err) {
    let status = 'ERROR';
    if (err.message.includes('ERR_CONNECTION_RESET')) status = 'RESET';
    else if (err.message.includes('ERR_NAME_NOT_RESOLVED')) status = 'NODOMAIN';

    const ip = await getIPAddress(domain);
    const provider = detectProvider(ip, {});
    const timestamp = getCurrentTime();

    if (CAPTURE_ENABLED) {
      await createEmptyCapture(id);
    }

    return { id, domain, ip, status, provider, timestamp };
  } finally {
    await page.close();
  }
}

// ==============================
// 메인 실행 함수
// ==============================
async function run() {
  if (!fs.existsSync(LIST_PATH)) {
    console.error(`❌ list.txt 파일이 없습니다.`);
    process.exit(1);
  }

  if (CAPTURE_ENABLED && !fs.existsSync(CAPTURE_DIR)) {
    fs.mkdirSync(CAPTURE_DIR);
  }

  const urls = fs.readFileSync(LIST_PATH, 'utf-8')
    .split('\n')
    .map(line => line.trim())
    .filter(line => line && !line.startsWith('#'));

  const browser = await puppeteer.launch({ headless: !IS_HEAD_MODE });
  const results = [];
  const progress = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);
  progress.start(urls.length, 0);

  for (let i = 0; i < urls.length; i += MAX_CONCURRENT_TABS) {
    const batch = urls.slice(i, i + MAX_CONCURRENT_TABS);
    const batchResults = await Promise.all(batch.map(url => checkDomain(browser, url)));
    results.push(...batchResults);
    progress.update(results.length);
  }

  progress.stop();
  await browser.close();

  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(results, null, 2), 'utf-8');
  console.log(`✅ 결과 저장 완료: ${OUTPUT_PATH}`);
}

run();
