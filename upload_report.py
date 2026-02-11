#!/usr/bin/env python3
"""
直接上传日报脚本（独立于 MCP 服务）
"""

import sys
import yaml
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BKDailyReportUpload')

# 配置文件路径
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / 'daily_report_config.yml'

def load_credentials():
    """从配置文件加载凭证"""
    try:
        if not CONFIG_FILE.exists():
            logger.error(f"配置文件不存在: {CONFIG_FILE}")
            return None

        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if not config:
            logger.error("配置文件为空")
            return None

        credentials = {
            'bk_ticket': config['credentials']['bk_ticket'],
            'bk_csrf_token': config['credentials']['bk_csrf_token'],
            'bk_sessionid': config['credentials']['bk_sessionid'],
            'bk_platform_url': config['blueking']['platform_url'],
            'report_api_endpoint': config['blueking']['report_api_endpoint'],
        }

        # 验证必需字段
        for key in ['bk_ticket', 'bk_csrf_token', 'bk_sessionid', 'report_api_endpoint']:
            if not credentials.get(key):
                logger.error(f"缺失必需字段: {key}")
                return None

        return credentials

    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return None

def upload_daily_report(today_summary: str, tomorrow_plan: str, feeling: str = "无", report_date: str = None):
    """上传日报到蓝鲸平台"""

    # 加载凭证
    credentials = load_credentials()
    if not credentials:
        return "✗ 认证凭证加载失败"

    # 解析今日总结
    summary_items = [line.strip().lstrip('- ').strip() for line in today_summary.strip().split('\n') if line.strip()]
    if not summary_items:
        return "✗ 今日总结不能为空"

    # 解析明日计划
    plan_items = [line.strip().lstrip('- ').strip() for line in tomorrow_plan.strip().split('\n') if line.strip()]
    if not plan_items:
        return "✗ 明日计划不能为空"

    # 处理日期
    report_date = report_date or datetime.now().strftime('%Y-%m-%d')
    tomorrow_date = (datetime.strptime(report_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

    # 构建 HTML 内容
    html = '<p><span><strong>今日总结：</strong></span></p>'
    html += '<ol>'
    for item in summary_items:
        html += f'<li>{item}</li>'
    html += '</ol>'

    html += f'<p><span><strong>{tomorrow_date}计划：</strong></span></p>'
    html += '<ol>'
    for item in plan_items:
        html += f'<li><span>{item}</span></li>'
    html += '</ol>'

    html += '<p><strong>感想：</strong></p>'
    html += f'<p>{feeling}</p>'

    # 准备请求数据
    payload = {
        'daily_date': report_date,
        'content': html,
    }

    # 构建请求头
    headers = {
        'X-CSRFToken': credentials['bk_csrf_token'],
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f"{credentials['bk_platform_url']}/mine/daily/",
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # 构建 Cookies
    cookies = {
        'bk-training_csrftoken': credentials['bk_csrf_token'],
        'bk-training_sessionid': credentials['bk_sessionid'],
        'bk_ticket': credentials['bk_ticket'],
    }

    endpoint = credentials['report_api_endpoint']

    logger.info(f"上传日报: {report_date}")
    logger.info(f"今日总结: {len(summary_items)} 项")
    logger.info(f"明日计划: {len(plan_items)} 项")
    logger.info(f"API 端点: {endpoint}")

    try:
        # 发送请求
        response = requests.post(
            endpoint,
            data=payload,
            headers=headers,
            cookies=cookies,
            timeout=30
        )

        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应内容: {response.text[:200]}")

        if response.status_code == 200:
            return f"✓ 日报上传成功！\n日期: {report_date}\n今日总结: {len(summary_items)} 项\n明日计划: {len(plan_items)} 项"
        else:
            return f"✗ 上传失败\n状态码: {response.status_code}\n响应: {response.text[:200]}"

    except Exception as e:
        logger.error(f"上传请求失败: {e}")
        return f"✗ 上传失败: {str(e)}"

if __name__ == "__main__":
    # 命令行参数
    if len(sys.argv) < 3:
        print("用法: python3 upload_report.py <今日总结> <明日计划> [感想] [日期]")
        sys.exit(1)

    today_summary = sys.argv[1]
    tomorrow_plan = sys.argv[2]
    feeling = sys.argv[3] if len(sys.argv) > 3 else "无"
    report_date = sys.argv[4] if len(sys.argv) > 4 else None

    result = upload_daily_report(today_summary, tomorrow_plan, feeling, report_date)
    print(result)
