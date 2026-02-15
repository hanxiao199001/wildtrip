#!/usr/bin/env node
/**
 * 懒懒途登录工具
 * 手机号 + 验证码登录，保存 SESSION_ID
 */

const fs = require('fs')
const path = require('path')
const readline = require('readline')

const CONFIG_FILE = path.join(__dirname, 'llt-config.json')

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
})

function question(prompt) {
  return new Promise(resolve => rl.question(prompt, resolve))
}

async function sendCode(phone) {
  const response = await fetch('https://llt-app.vvinv.cn/api/auth/send-code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone })
  })

  const result = await response.json()
  if (result.code !== 0) {
    throw new Error(result.msg || '发送验证码失败')
  }

  return result.data
}

async function login(phone, code) {
  const response = await fetch('https://llt-app.vvinv.cn/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, code })
  })

  const result = await response.json()
  if (result.code !== 0) {
    throw new Error(result.msg || '登录失败')
  }

  return result.data
}

async function main() {
  console.log('=== 懒懒途登录 ===\n')

  const phone = await question('手机号: ')
  
  console.log('\n发送验证码...')
  await sendCode(phone)
  console.log('✅ 验证码已发送\n')

  const code = await question('验证码: ')

  console.log('\n登录中...')
  const data = await login(phone, code)

  const config = {
    phone,
    sessionId: data.session_id,
    userId: data.user_id,
    timestamp: Date.now()
  }

  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2))
  console.log('\n✅ 登录成功！')
  console.log(`用户ID: ${data.user_id}`)
  console.log(`配置已保存: ${CONFIG_FILE}`)

  rl.close()
}

main().catch(err => {
  console.error('\n❌ 错误:', err.message)
  rl.close()
  process.exit(1)
})
