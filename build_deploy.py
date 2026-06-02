#!/usr/bin/env python3
"""
生成部署版HTML：用Mock DB替换Dexie，从JSON文件读取数据
"""

import re

def build_deploy_html(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 1. 在 </style> 前插入部署版提示条样式
    deploy_css = '''
        /* 部署版标识条 */
        #deploy-banner {
            background: linear-gradient(90deg, #6B21A8, #9333EA);
            color: white;
            text-align: center;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 500;
        }
        #deploy-banner a { color: #FDE68A; text-decoration: underline; }
    '''
    html = html.replace('    </style>', deploy_css + '    </style>', 1)
    
    # 2. 在 <body> 后插入部署版标识
    deploy_banner = '''
    <div id="deploy-banner">
        🌐 部署版（数据来自JSON文件）| 
        <a href="#" onclick="showVersion()">查看数据版本</a>
    </div>
    '''
    html = html.replace('<body>', '<body>' + deploy_banner, 1)
    
    # 3. 在 const db = new AssessmentDB(); 后插入Mock DB代码
    mock_db_code = '''
    
    // ============================================
    // 部署版：Mock DB（从JSON文件读取数据）
    // ============================================
    (function injectMockDB() {
        // 判断是否在本地环境
        const isLocal = window.location.hostname === 'localhost' 
                    || window.location.hostname === '127.0.0.1'
                    || window.location.protocol === 'file:';
        
        if (isLocal) {
            console.log('💻 本地环境：使用IndexDB');
            return;  // 本地环境不改，仍用IndexedDB
        }
        
        console.log('🌐 部署环境：使用JSON数据');
        window._deployMode = true;
        
        // JSON缓存
        const _jsonCache = {};
        
        async function fetchJSON(type, month) {
            const cacheKey = type + '_' + month;
            if (_jsonCache[cacheKey]) return _jsonCache[cacheKey];
            
            const baseUrl = window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/') + 1);
            const url = baseUrl + 'data/json/' + month + '/' + type + '.json';
            try {
                const resp = await fetch(url);
                if (!resp.ok) { _jsonCache[cacheKey] = []; return []; }
                const json = await resp.json();
                _jsonCache[cacheKey] = json.data || [];
                return _jsonCache[cacheKey];
            } catch (e) {
                console.warn('加载 ' + url + ' 失败:', e.message);
                _jsonCache[cacheKey] = [];
                return [];
            }
        }
        
        // 构建Mock Table对象
        function createMockTable(type) {
            return {
                where: function(field) {
                    return {
                        equals: function(value) {
                            return {
                                toArray: async function() {
                                    return await fetchJSON(type, value);
                                },
                                first: async function() {
                                    const data = await fetchJSON(type, value);
                                    return data.length > 0 ? data[0] : null;
                                }
                            };
                        }
                    };
                },
                bulkAdd: async function() { return; },
                clear: async function() { return; },
                bulkDelete: async function() { return; }
            };
        }
        
        // 覆盖 db 对象的方法
        const origDB = window.db;
        window.db = {
            headcount: createMockTable('headcount'),
            performance: createMockTable('performance'),
            salary: createMockTable('salary'),
            attendance: createMockTable('attendance'),
            absence: createMockTable('absence'),
            overtime: createMockTable('overtime'),
            undertime: createMockTable('undertime'),
            leaveRecord: createMockTable('leaveRecord'),
            cachedStats: {
                where: function() { return { equals: function() { return { first: async () => null }; }; }; },
                clear: async function() { return; }
            },
            settings: {
                where: function() { return { equals: function() { return { first: async () => null }; }; };
            },
            managerSpan: createMockTable('managerSpan'),
            logisticsRatio: createMockTable('logisticsRatio'),
            close: async function() { return; }
        };
        
        console.log('✅ Mock DB 注入成功');
    })();
    '''
    
    # 在 const db = new AssessmentDB(); 后插入
    html = html.replace(
        "    const db = new AssessmentDB();\n",
        "    const db = new AssessmentDB();\n" + mock_db_code + "\n"
    )
    
    # 4. 禁用Firebase（部署版不需要）
    html = html.replace(
        '    // ============================================\n    // Firebase Configuration (Data Sharing)\n    // ============================================',
        '    // ============================================\n    // Firebase Configuration (Data Sharing) - 部署版已禁用\n    // ============================================\n    const FIREBASE_ENABLED = false; // 部署版禁用Firebase'
    )
    
    # 5. 添加 showVersion 函数（在 </script> 前）
    show_version_func = '''
    
    // 部署版：显示数据版本信息
    window.showVersion = function() {
        const month = document.getElementById('stats-month')?.value || '2026-05';
        const baseUrl = window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/') + 1);
        fetch(baseUrl + 'data/json/' + month + '/performance.json')
            .then(r => r.ok ? r.json() : null)
            .then(json => {
                if (json && json._generatedAt) {
                    alert('数据版本：\\n生成时间：' + json._generatedAt + '\\n月份：' + month);
                } else {
                    alert('数据版本信息不可用');
                }
            });
    };
    '''
    html = html.replace('    </script>', show_version_func + '\n    </script>', 1)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print('[OK] Deploy version generated: ' + output_file)
    print('   本地环境自动使用IndexedDB，GitHub Pages自动使用JSON数据')

if __name__ == '__main__':
    build_deploy_html(
        'GPT-Assessment-Dashboard.html',
        'GPT-Assessment-Dashboard-deploy.html'
    )
