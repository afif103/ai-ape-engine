#!/usr/bin/env node

/**
 * Simple test script to verify extraction functionality
 * This simulates the frontend API calls without a browser
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';
let accessToken = '';

// Colors for console output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function testHealthCheck() {
  log('🔍 Testing API Health Check...', 'blue');
  try {
    const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/health`);
    const data = await response.json();
    if (data.status === 'healthy') {
      log('✅ API is healthy', 'green');
      return true;
    } else {
      log('❌ API health check failed', 'red');
      return false;
    }
  } catch (error) {
    log(`❌ Health check error: ${error.message}`, 'red');
    return false;
  }
}

async function testLogin() {
  log('🔐 Testing User Login...', 'blue');
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: 'user@example.com',
        password: 'password123'
      })
    });

    const data = await response.json();

    if (data.access_token) {
      accessToken = data.access_token;
      log('✅ Login successful, got access token', 'green');
      return true;
    } else {
      log('❌ Login failed - no access token', 'red');
      return false;
    }
  } catch (error) {
    log(`❌ Login error: ${error.message}`, 'red');
    return false;
  }
}

async function testExtractionAPI() {
  log('📄 Testing Extraction API...', 'blue');
  try {
    const response = await fetch(`${API_BASE_URL}/extraction/extract`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        file_path: 'sample_document.pdf'
      })
    });

    const data = await response.json();

    if (data.text && data.metadata) {
      log('✅ Extraction API working', 'green');
      log(`📝 Extracted text: "${data.text.substring(0, 50)}..."`, 'yellow');
      log(`📊 Metadata: ${JSON.stringify(data.metadata)}`, 'yellow');
      if (data.note) {
        log(`ℹ️ Note: ${data.note}`, 'blue');
      }
      return true;
    } else {
      log('❌ Extraction API returned invalid response', 'red');
      return false;
    }
  } catch (error) {
    log(`❌ Extraction API error: ${error.message}`, 'red');
    return false;
  }
}

async function testFrontendAccessibility() {
  log('🌐 Testing Frontend Accessibility...', 'blue');
  try {
    const response = await fetch('http://localhost:3001');
    if (response.status === 200) {
      log('✅ Frontend is accessible on port 3001', 'green');

      // Check if extraction page is accessible
      const extractionResponse = await fetch('http://localhost:3001/extraction');
      if (extractionResponse.status === 200) {
        log('✅ Extraction page is accessible', 'green');
        return true;
      } else {
        log('❌ Extraction page not accessible', 'red');
        return false;
      }
    } else {
      log('❌ Frontend not accessible on port 3001', 'red');
      return false;
    }
  } catch (error) {
    log(`❌ Frontend accessibility error: ${error.message}`, 'red');
    log('💡 Make sure frontend container is running: docker-compose up -d frontend', 'yellow');
    return false;
  }
}

async function runTests() {
  log('🚀 Starting APE Extraction Functionality Tests', 'bold');
  log('=' .repeat(50), 'bold');

  const results = [];

  // Test 1: API Health
  results.push(await testHealthCheck());

  // Test 2: Frontend Accessibility
  results.push(await testFrontendAccessibility());

  // Test 3: Authentication
  results.push(await testLogin());

  // Test 4: Extraction API
  if (accessToken) {
    results.push(await testExtractionAPI());
  } else {
    log('⏭️ Skipping extraction test - login failed', 'yellow');
    results.push(false);
  }

  // Summary
  log('\n' + '='.repeat(50), 'bold');
  log('📊 TEST RESULTS SUMMARY', 'bold');

  const passed = results.filter(r => r).length;
  const total = results.length;

  log(`✅ Passed: ${passed}/${total}`, passed === total ? 'green' : 'yellow');
  log(`❌ Failed: ${total - passed}/${total}`, total - passed === 0 ? 'green' : 'red');

  if (passed === total) {
    log('\n🎉 ALL TESTS PASSED! Extraction functionality is working correctly.', 'green');
    log('🌐 Frontend URL: http://localhost:3001/extraction', 'blue');
    log('🔐 Test credentials: user@example.com / password123', 'blue');
  } else {
    log('\n⚠️ Some tests failed. Check the output above for details.', 'red');
  }

  log('=' .repeat(50), 'bold');
}

// Run the tests
runTests().catch(error => {
  log(`💥 Test runner error: ${error.message}`, 'red');
  process.exit(1);
});