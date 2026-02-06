#!/usr/bin/env python3
"""
蓝鲸日报上传 MCP 服务

职责：接收外部 Agent 生成的日报内容，上传到蓝鲸平台
说明：日报内容的生成（Git 分析、智能总结）由外部 Agent 完成
"""

import os
import logging
import requests
import yaml
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BKDailyReportMCP')

# 初始化 FastMCP 服务
mcp = FastMCP("bk-daily-report")


# ============================================================================
# 蓝鲸认证管理器
# ============================================================================

class BKAuthManager:
    """蓝鲸平台身份认证管理"""
    
    # 配置文件路径（相对于脚本所在目录）
    CONFIG_FILE = Path(__file__).parent / 'daily_report_config.yml'
    
    def __init__(self):
        """初始化认证管理器，从 YAML 配置文件读取凭证"""
        self.credentials = {
            'bk_ticket': '',
            'bk_csrf_token': '',
            'bk_sessionid': '',
            'bk_platform_url': 'https://bk-training.bkapps-sz.woa.com',
            'report_api_endpoint': 'https://bk-training.bkapps-sz.woa.com/save_daily/',
        }
        
        # 优先级 1：从 YAML 配置文件读取
        self._load_from_yaml_config()
        
        # 优先级 2：从环境变量读取（覆盖 YAML 配置）
        self._load_from_env()
        
        logger.info("认证管理器已初始化")
    
    def _load_from_yaml_config(self):
        """从 daily_report_config.yml 读取凭证"""
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    
                    if not config:
                        logger.warning("配置文件为空")
                        return
                    
                    # 读取凭证
                    if 'credentials' in config:
                        creds = config['credentials']
                        if creds.get('bk_ticket'):
                            self.credentials['bk_ticket'] = creds['bk_ticket']
                        if creds.get('bk_csrf_token'):
                            self.credentials['bk_csrf_token'] = creds['bk_csrf_token']
                        if creds.get('bk_sessionid'):
                            self.credentials['bk_sessionid'] = creds['bk_sessionid']
                    
                    # 读取蓝鲸平台配置
                    if 'blueking' in config:
                        bk = config['blueking']
                        if bk.get('platform_url'):
                            self.credentials['bk_platform_url'] = bk['platform_url']
                        if bk.get('report_api_endpoint'):
                            self.credentials['report_api_endpoint'] = bk['report_api_endpoint']
                    
                logger.info(f"从 YAML 配置文件读取凭证: {self.CONFIG_FILE}")
            else:
                logger.warning(f"配置文件不存在: {self.CONFIG_FILE}")
        except Exception as e:
            logger.error(f"读取 YAML 配置文件失败: {str(e)}")
    
    def _load_from_env(self):
        """从环境变量读取凭证（覆盖 YAML 配置）"""
        env_ticket = os.environ.get('BK_TICKET', '')
        env_csrf = os.environ.get('BK_CSRF_TOKEN', '')
        env_session = os.environ.get('BK_SESSIONID', '')
        
        if env_ticket:
            self.credentials['bk_ticket'] = env_ticket
            logger.debug("从环境变量读取 BK_TICKET")
        if env_csrf:
            self.credentials['bk_csrf_token'] = env_csrf
            logger.debug("从环境变量读取 BK_CSRF_TOKEN")
        if env_session:
            self.credentials['bk_sessionid'] = env_session
            logger.debug("从环境变量读取 BK_SESSIONID")
    
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        required = ['bk_ticket', 'bk_csrf_token', 'bk_sessionid', 'report_api_endpoint']
        return all(self.credentials.get(f) for f in required)
    
    def get_auth_headers(self) -> dict:
        """获取认证请求头"""
        return {
            'X-Csrftoken': self.credentials.get('bk_csrf_token', ''),
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': self.credentials.get('bk_platform_url', ''),
        }
    
    def get_auth_cookies(self) -> dict:
        """获取认证 Cookies"""
        return {
            'csrftoken': self.credentials.get('bk_csrf_token', ''),
            'bk-training_csrftoken': self.credentials.get('bk_csrf_token', ''),
            'bk-training_sessionid': self.credentials.get('bk_sessionid', ''),
            'bk_ticket': self.credentials.get('bk_ticket', ''),
        }


# ============================================================================
# MCP 工具定义
# ============================================================================

# 全局实例
auth_manager = BKAuthManager()


@mcp.tool()
def upload_daily_report(
    today_summary: str,
    tomorrow_plan: str,
    feeling: Optional[str] = None,
    report_date: Optional[str] = None
) -> str:
    """
    上传日报到蓝鲸平台（核心工具）
    
    外部 Agent 负责分析 Git 变动并生成总结，此工具只负责上传。
    
    Args:
        today_summary: 今日总结（每项以 - 开头，换行分隔）
        tomorrow_plan: 明日计划（每项以 - 开头，换行分隔）
        feeling: 感想（可选，默认"无"）
        report_date: 日期（格式: YYYY-MM-DD，默认今天）
    
    Returns:
        上传结果信息
    
    示例:
        today_summary: "- 修复拨测模块引用问题\\n- 优化代码结构"
        tomorrow_plan: "- 验证修复效果\\n- 完善单元测试"
    """
    try:
        # 检查认证状态
        if not auth_manager.is_authenticated():
            missing = []
            for field in ['bk_ticket', 'bk_csrf_token', 'bk_sessionid']:
                if not auth_manager.credentials.get(field):
                    missing.append(field)
            return f"✗ 认证凭证不完整，无法上传\n缺失: {', '.join(missing)}"
        
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
        
        # 处理感想
        feeling = feeling or "无"
        
        # 构建 HTML 内容（蓝鲸日报系统要求的格式）
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
        
        # 获取认证信息
        headers = auth_manager.get_auth_headers()
        cookies = auth_manager.get_auth_cookies()
        endpoint = auth_manager.credentials['report_api_endpoint']
        
        # 上传
        logger.info(f"上传日报: {report_date}")
        logger.info(f"今日总结: {summary_items}")
        logger.info(f"明日计划: {plan_items}")
        logger.info(f"API 端点: {endpoint}")
        logger.info(f"CSRF Token: {auth_manager.credentials['bk_csrf_token'][:20]}...")
        logger.info(f"Session ID: {auth_manager.credentials['bk_sessionid'][:20]}...")

        # 使用 subprocess 调用 curl（解决 Python SSL 握手问题）
        import subprocess
        import shlex

        curl_cmd = [
            'curl', '-k', '-X', 'POST', endpoint,
            '-H', f'X-CSRFToken: {auth_manager.credentials["bk_csrf_token"]}',
            '-H', f'X-Requested-With: XMLHttpRequest',
            '-H', f'Referer: {auth_manager.credentials["bk_platform_url"]}/mine/daily/',
            '-H', f'Origin: {auth_manager.credentials["bk_platform_url"]}',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-b', f'bk-training_csrftoken={auth_manager.credentials["bk_csrf_token"]}; bk-training_sessionid={auth_manager.credentials["bk_sessionid"]}; bk_ticket={auth_manager.credentials["bk_ticket"]}',
            '-d', f'daily_date={report_date}',
            '-d', f'content={html}'
        ]

        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            response_text = result.stdout
            # 检查响应是否包含成功标识
            if '403' in response_text or 'Forbidden' in response_text or 'CSRF' in response_text:
                if 'CSRF' in response_text:
                    return "✗ 权限不足 (403)，CSRF 验证失败，凭证可能已过期"
                return "✗ 权限不足 (403)，请检查认证凭证"
            elif '401' in response_text or 'Unauthorized' in response_text:
                return "✗ 认证失败 (401)，bk_ticket 可能已过期"
            elif '200' in response_text or 'success' in response_text.lower():
                logger.info("日报上传成功")
                return f"✓ 日报上传成功\n日期: {report_date}\n今日总结: {len(summary_items)} 项\n明日计划: {len(plan_items)} 项"
            else:
                # 假设成功（curl 返回 0 且无明显错误）
                logger.info("日报可能已上传成功（未检测到错误）")
                return f"✓ 日报可能已上传成功\n日期: {report_date}\n今日总结: {len(summary_items)} 项\n明日计划: {len(plan_items)} 项\n提示：请登录蓝鲸平台确认"
        else:
            return f"✗ 上传失败: {result.stderr}"
            
    except Exception as e:
        logger.error(f"上传异常: {str(e)}")
        return f"✗ 上传异常: {str(e)}"


@mcp.tool()
def get_bk_auth_status() -> str:
    """
    检查蓝鲸认证状态
    
    Returns:
        认证状态信息
    """
    if auth_manager.is_authenticated():
        return "✓ 认证凭证完整\n- bk_ticket: 已设置\n- bk_csrf_token: 已设置\n- bk_sessionid: 已设置"
    else:
        missing = []
        for field in ['bk_ticket', 'bk_csrf_token', 'bk_sessionid']:
            if not auth_manager.credentials.get(field):
                missing.append(field)
        return f"✗ 认证凭证不完整\n缺失: {', '.join(missing)}"


# ============================================================================
# 主函数
# ============================================================================

def main():
    """启动 MCP 服务"""
    logger.info("蓝鲸日报上传 MCP 服务已启动")
    logger.info("等待外部 Agent 调用 upload_daily_report 工具...")
    mcp.run()


if __name__ == "__main__":
    main()
