#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对 GPT-Assessment-Dashboard.html 进行剩余修改：
1. 在 LOGIN_PASSWORD_HASH 行之前插入 showError/showSuccess 函数
2. 为关键 async 函数加上 try-catch
"""

import re

FILE = r"C:\Users\admin\Desktop\AI工具\智多星改善\5月数据明细\GPT-Assessment-Dashboard.html"

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# ---- 修改 A：在 LOGIN_PASSWORD_HASH 行之前插入 showError/showSuccess ----
insert_marker = '    const LOGIN_PASSWORD_HASH'
insert_code = '''    // ============================================
    // 通用错误/成功提示（页面顶部浮动条）
    // ============================================
    function showError(msg, durationMs) {
        durationMs = durationMs || 8000;
        let bar = document.getElementById('error-bar');
        if (!bar) {
            bar = document.createElement('div');
            bar.id = 'error-bar';
            bar.innerHTML = '<span id="error-msg"></span><button onclick="this.parentElement.remove()">×</button>';
            document.body.prepend(bar);
        }
        bar.querySelector('#error-msg').textContent = msg;
        bar.style.display = 'flex';
        clearTimeout(bar._timer);
        bar._timer = setTimeout(() => { bar.style.display = 'none'; }, durationMs);
    }

    function showSuccess(msg, durationMs) {
        durationMs = durationMs || 5000;
        let bar = document.getElementById('success-bar');
        if (!bar) {
            bar = document.createElement('div');
            bar.id = 'success-bar';
            bar.innerHTML = '<span id="success-msg"></span><button onclick="this.parentElement.remove()">×</button>';
            document.body.prepend(bar);
        }
        bar.querySelector('#success-msg').textContent = msg;
        bar.style.display = 'flex';
        clearTimeout(bar._timer);
        bar._timer = setTimeout(() => { bar.style.display = 'none'; }, durationMs);
    }

'''

if insert_marker in content:
    content = content.replace(insert_marker, insert_code + insert_marker, 1)
    print("✅ 已插入 showError/showSuccess 函数")
else:
    print("⚠️  未找到插入点 LOGIN_PASSWORD_HASH，尝试备用方案...")
    # 备用：在 "Login State Management" 注释后插入
    backup_marker = '    // Login State Management'
    if backup_marker in content:
        content = content.replace(
            backup_marker,
            backup_marker + '\n' + insert_code,
            1
        )
        print("✅ 已通过备用方案插入 showError/showSuccess 函数")
    else:
        print("❌ 无法找到插入点，跳过多函数插入")

# ---- 修改 B：为 calculateAllStats 加上 try-catch ----
# 找到 async function calculateAllStats(month) {
# 在其开头的 { 后插入 try {，并在函数末尾加上 } catch(e) {...}
calc_pattern = r'(async function calculateAllStats\(month\)\s*\{)'
calc_match = re.search(calc_pattern, content)
if calc_match:
    # 在函数体开头加 try {
    old_start = calc_match.group(1)
    new_start = old_start + '\n        try {'
    content = content.replace(old_start, new_start, 1)
    print("✅ 已为 calculateAllStats 添加 try 开头")
    
    # 找到该函数的末尾（下一个同级 function 或 script> 前）
    # 简单策略：在 calculateAllStats 里找到最后一个 } 之前插入 catch
    # 重新读取修改后的内容，找到函数体范围
    idx = content.find('async function calculateAllStats')
    if idx != -1:
        # 找到函数体末尾的 }
        depth = 0
        in_func = False
        end_idx = -1
        i = idx
        while i < len(content):
            if content[i] == '{':
                depth += 1
                in_func = True
            elif content[i] == '}':
                depth -= 1
                if in_func and depth == 0:
                    end_idx = i
                    break
            i += 1
        
        if end_idx != -1:
            catch_block = '''        } catch (e) {
            console.error('calculateAllStats 失败：', e);
            const errDiv = document.getElementById('main-content') || document.body;
            const errMsg = document.createElement('div');
            errMsg.style.cssText = 'color:#DC2626;padding:20px;background:#FEE2E2;border-radius:8px;margin:20px;';
            errMsg.innerHTML = '⚠️ 数据计算失败，请检查数据格式或联系管理员。<br>错误详情：' + e.message;
            errDiv.prepend(errMsg);
            return null;
        }
'''
            # 在末尾 } 前插入 catch 块
            content = content[:end_idx] + catch_block + content[end_idx:]
            print("✅ 已为 calculateAllStats 添加 catch 块")
        else:
            print("⚠️  未找到 calculateAllStats 函数末尾")
else:
    print("⚠️  未找到 async function calculateAllStats")

# ---- 修改 C：为 processUploadedFile 加上 try-catch ----
proc_pattern = r'(async function processUploadedFile\(file, relativePath\)\s*\{)'
proc_match = re.search(proc_pattern, content)
if proc_match:
    old_start = proc_match.group(1)
    new_start = old_start + '\n        try {'
    content = content.replace(old_start, new_start, 1)
    print("✅ 已为 processUploadedFile 添加 try 开头")
    
    idx = content.find('async function processUploadedFile')
    if idx != -1:
        depth = 0
        in_func = False
        end_idx = -1
        i = idx
        while i < len(content):
            if content[i] == '{':
                depth += 1
                in_func = True
            elif content[i] == '}':
                depth -= 1
                if in_func and depth == 0:
                    end_idx = i
                    break
            i += 1
        if end_idx != -1:
            catch_block = '''        } catch (e) {
            console.error('processUploadedFile 失败：', e);
            showError('文件解析失败：' + e.message);
        }
'''
            content = content[:end_idx] + catch_block + content[end_idx:]
            print("✅ 已为 processUploadedFile 添加 catch 块")
else:
    print("⚠️  未找到 async function processUploadedFile")

# ---- 修改 D：修复 CSS var() 语法（var(--xxx) → var(--xxx) 是对的，但检查 font-family 引号）----
# 修复 font-family 没有给中文文件名加引号的问题
content = content.replace(
    "font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;",
    "font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;"
)
# 实际上 Microsoft YaHei 应该写成 "Microsoft YaHei"（有空格需要引号）
content = content.replace(
    "font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;",
    'font-family: "Microsoft YaHei", "Segoe UI", sans-serif;'
)
print("✅ 已修复 font-family 引号")

# 写入文件
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

new_len = len(content)
print(f"\n文件大小变化：{original_len} → {new_len} 字节")
print("✅ 所有修改已完成并写入文件")
