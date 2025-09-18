#!/usr/bin/env node
/**
 * Automated test runner for InstaBids Frontend
 * Runs all test suites and generates comprehensive reports
 */

const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');

function printHeader(title) {
    console.log('\n' + '='.repeat(60));
    console.log(` ${title}`);
    console.log('='.repeat(60));
}

function runCommand(command, description) {
    return new Promise((resolve) => {
        console.log(`\n🏃 ${description}`);
        console.log(`Command: ${command}`);
        console.log('-'.repeat(40));
        
        const child = exec(command, { 
            cwd: process.cwd(),
            timeout: 300000 // 5 minute timeout
        });
        
        let stdout = '';
        let stderr = '';
        
        child.stdout.on('data', (data) => {
            const output = data.toString();
            console.log(output);
            stdout += output;
        });
        
        child.stderr.on('data', (data) => {
            const output = data.toString();
            console.error(output);
            stderr += output;
        });
        
        child.on('close', (code) => {
            resolve({
                success: code === 0,
                stdout,
                stderr,
                code
            });
        });
        
        child.on('error', (error) => {
            console.error(`❌ Error: ${error.message}`);
            resolve({
                success: false,
                stdout,
                stderr: error.message,
                code: 1
            });
        });
    });
}

async function checkEnvironment() {
    printHeader('Environment Check');
    
    // Check Node version
    console.log(`Node Version: ${process.version}`);
    
    // Check if package.json exists
    if (fs.existsSync('package.json')) {
        console.log('✅ package.json: Found');
        const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
        console.log(`📦 Project: ${packageJson.name} v${packageJson.version}`);
    } else {
        console.log('❌ package.json: Not found');
        return false;
    }
    
    // Check if Jest is configured
    try {
        const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
        if (packageJson.scripts && packageJson.scripts.test) {
            console.log('✅ Jest test script: Configured');
        } else {
            console.log('❌ Jest test script: Not configured');
        }
        
        if (packageJson.devDependencies && 
            (packageJson.devDependencies.jest || packageJson.devDependencies['@jest/core'])) {
            console.log('✅ Jest dependency: Available');
        } else {
            console.log('❌ Jest dependency: Not found');
        }
    } catch (error) {
        console.log('❌ Error reading package.json');
        return false;
    }
    
    // Check environment variables
    const requiredVars = ['NEXT_PUBLIC_API_URL'];
    for (const varName of requiredVars) {
        const value = process.env[varName];
        if (value) {
            console.log(`✅ ${varName}: ${value}`);
        } else {
            console.log(`⚠️ ${varName}: Not set (may use default)`);
        }
    }
    
    return true;
}

async function runUnitTests() {
    printHeader('Unit Tests');
    return await runCommand('npm test -- --watchAll=false --coverage=false', 'Running unit tests');
}

async function runCoverageTests() {
    printHeader('Coverage Tests');
    return await runCommand('npm run test:coverage', 'Running tests with coverage');
}

async function runComponentTests() {
    printHeader('Component Tests');
    return await runCommand('npm test -- --testPathPattern="components.*test" --watchAll=false', 'Running component tests');
}

async function runIntegrationTests() {
    printHeader('Integration Tests');
    return await runCommand('npm test -- --testPathPattern="integration" --watchAll=false', 'Running integration tests');
}

async function runLinting() {
    printHeader('Linting');
    return await runCommand('npm run lint', 'Running ESLint');
}

async function runTypeChecking() {
    printHeader('Type Checking');
    return await runCommand('npx tsc --noEmit', 'Running TypeScript type checking');
}

async function buildProject() {
    printHeader('Build Test');
    return await runCommand('npm run build', 'Testing production build');
}

function generateTestReport(results) {
    const timestamp = new Date().toISOString().replace('T', ' ').slice(0, 19);
    
    let report = `# InstaBids Frontend Test Report
Generated: ${timestamp}

## Test Results Summary
`;
    
    const totalTests = Object.keys(results).length;
    const passedTests = Object.values(results).filter(r => r.success).length;
    
    report += `
- Total Test Suites: ${totalTests}
- Passed: ${passedTests}
- Failed: ${totalTests - passedTests}
- Success Rate: ${((passedTests/totalTests)*100).toFixed(1)}%

## Individual Test Results
`;
    
    for (const [testName, result] of Object.entries(results)) {
        const status = result.success ? '✅ PASSED' : '❌ FAILED';
        report += `- ${testName}: ${status}\n`;
        
        if (!result.success && result.stderr) {
            report += `  Error: ${result.stderr.split('\n')[0]}\n`;
        }
    }
    
    report += `\n## Recommendations\n`;
    
    if (passedTests === totalTests) {
        report += '🎉 All tests passed! The frontend is ready for deployment.\n';
    } else {
        report += `⚠️ ${totalTests - passedTests} test suite(s) failed. Review the output above and fix issues before deployment.\n`;
    }
    
    // Write report to file
    fs.writeFileSync('test-report.md', report);
    
    console.log(report);
}

async function main() {
    const startTime = Date.now();
    
    printHeader('InstaBids Frontend Automated Test Runner');
    console.log(`Started at: ${new Date().toISOString().replace('T', ' ').slice(0, 19)}`);
    
    // Check environment
    const envOk = await checkEnvironment();
    if (!envOk) {
        console.log('❌ Environment check failed. Please fix issues before running tests.');
        process.exit(1);
    }
    
    // Run all test suites
    const results = {};
    
    // 1. Linting
    results['Linting'] = await runLinting();
    
    // 2. Type Checking
    results['Type Checking'] = await runTypeChecking();
    
    // 3. Unit Tests
    results['Unit Tests'] = await runUnitTests();
    
    // 4. Component Tests
    results['Component Tests'] = await runComponentTests();
    
    // 5. Coverage Tests
    results['Coverage Tests'] = await runCoverageTests();
    
    // 6. Build Test
    results['Build Test'] = await buildProject();
    
    // Generate final report
    const endTime = Date.now();
    const duration = (endTime - startTime) / 1000;
    
    printHeader('Test Run Complete');
    console.log(`Total Duration: ${duration.toFixed(2)} seconds`);
    
    generateTestReport(results);
    
    // Exit with appropriate code
    const allPassed = Object.values(results).every(r => r.success);
    process.exit(allPassed ? 0 : 1);
}

if (require.main === module) {
    main().catch(console.error);
}