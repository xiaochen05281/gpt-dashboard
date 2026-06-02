# 项目记忆 - GPT考核驾驶舱

## 项目结构
- `GPT-Assessment-Dashboard.html`: 主应用文件，圆通速递GPT考核驾驶舱
- `excel_to_json.py`: Excel转JSON数据转换脚本
- `.github/workflows/update-data.yml`: GitHub Actions自动更新配置
- `data/json/2026-05/`: JSON数据文件目录（已从Git中移除，因文件过大）

## 关键Bug修复记录
1. **storeData致命Bug**: `await table.clear()` 每次上传清空整张表，改为按月份+岗位删除
2. **VALID_LEAVE_STATUSES**: 移除'销假成功'（已回岗不应算请假）
3. **normalizeDataCenters()**: 封装为独立函数
4. **CSS变量补全**: 添加 --gray-50, --gray-400, --gray-500
5. **showError()/showSuccess()**: 添加错误提示功能

## GitHub仓库
- 仓库: https://github.com/xiaochen05281/gpt-dashboard
- Pages地址: https://xiaochen05281.github.io/gpt-dashboard
- 本地分支: master，远程分支: main

## 注意事项
- 公司网络防火墙会拦截GitHub HTTPS连接（443端口），推送需换网络
- JSON数据文件过大（salary.json 130MB），已从Git历史中移除
- 后续数据更新建议通过GitHub Actions在CI中生成JSON
