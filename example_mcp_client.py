#!/usr/bin/env python3
"""
MCP 客户端示例

演示如何调用蓝鲸日报 MCP 服务的各个工具
"""

import asyncio
import json
from typing import Any


class MCPExampleClient:
    """MCP 客户端示例"""
    
    def __init__(self):
        """初始化客户端"""
        # 这里应该连接到实际的 MCP 服务器
        # 为了演示，我们只模拟调用
        self.tools = {
            'get_bk_auth_status': self._mock_get_auth_status,
            'refresh_bk_credentials': self._mock_refresh_credentials,
            'generate_daily_report': self._mock_generate_report,
            'upload_daily_report': self._mock_upload_report,
            'generate_and_upload_report': self._mock_generate_and_upload,
        }
    
    async def _mock_get_auth_status(self) -> dict:
        """模拟获取认证状态"""
        return {
            "is_authenticated": False,
            "has_bk_ticket": False,
            "has_csrf_token": False,
            "has_sessionid": False,
            "platform_url": "https://bk-training.bkapps-sz.woa.com",
            "report_api_endpoint": "Not set"
        }
    
    async def _mock_refresh_credentials(self, **kwargs) -> dict:
        """模拟刷新认证凭证"""
        return {
            "status": "success",
            "message": "认证凭证已更新",
            "auth_status": {
                "is_authenticated": True,
                "has_bk_ticket": True,
                "has_csrf_token": True,
                "has_sessionid": True,
                "platform_url": "https://bk-training.bkapps-sz.woa.com",
                "report_api_endpoint": "https://bk-training.bkapps-sz.woa.com/api/reports/submit"
            }
        }
    
    async def _mock_generate_report(self, **kwargs) -> dict:
        """模拟生成日报"""
        return {
            "status": "success",
            "message": "日报生成成功",
            "file_path": "/Users/perryyzhang/daily/2025-02-02.md",
            "content": "# Git 工作总结 - 2025-02-02\n\n## 新增功能\n- 实现蓝鲸日报 MCP 服务\n- 支持自动生成 Git 日报\n\n## 修复问题\n- 修复 CSRF 认证问题\n\n## 统计信息\n- 提交数：5\n- 生成时间：2025-02-02 14:30:00"
        }
    
    async def _mock_upload_report(self, **kwargs) -> dict:
        """模拟上传日报"""
        return {
            "status": "success",
            "message": "日报上传成功",
            "file_path": "/Users/perryyzhang/daily/2025-02-02.md",
            "date": "2025-02-02"
        }
    
    async def _mock_generate_and_upload(self, **kwargs) -> dict:
        """模拟一键生成并上传"""
        return {
            "stage_1_generate": {
                "status": "success",
                "message": "日报生成成功",
                "file_path": "/Users/perryyzhang/daily/2025-02-02.md"
            },
            "stage_2_upload": {
                "status": "success",
                "message": "日报上传成功"
            },
            "overall_status": "success"
        }
    
    async def call_tool(self, tool_name: str, **kwargs) -> dict:
        """调用 MCP 工具"""
        if tool_name not in self.tools:
            return {"error": f"工具 {tool_name} 不存在"}
        
        tool_func = self.tools[tool_name]
        return await tool_func(**kwargs)


async def example_1_check_auth():
    """示例 1：检查认证状态"""
    print("\n" + "="*60)
    print("示例 1：检查认证状态")
    print("="*60)
    
    client = MCPExampleClient()
    result = await client.call_tool('get_bk_auth_status')
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if not result['is_authenticated']:
        print("\n⚠️  认证凭证不完整，需要先设置凭证")


async def example_2_update_credentials():
    """示例 2：更新认证凭证"""
    print("\n" + "="*60)
    print("示例 2：更新认证凭证")
    print("="*60)
    
    client = MCPExampleClient()
    result = await client.call_tool(
        'refresh_bk_credentials',
        bk_ticket="YOUR_BK_TICKET",
        bk_csrf_token="YOUR_CSRF_TOKEN",
        bk_sessionid="YOUR_SESSION_ID",
        report_api_endpoint="https://bk-training.bkapps-sz.woa.com/api/reports/submit"
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result['status'] == 'success':
        print("\n✓ 认证凭证已成功更新")


async def example_3_generate_report():
    """示例 3：生成日报"""
    print("\n" + "="*60)
    print("示例 3：生成日报")
    print("="*60)
    
    client = MCPExampleClient()
    result = await client.call_tool('generate_daily_report', output_format='markdown')
    
    if result['status'] == 'success':
        print(f"✓ 日报已生成")
        print(f"  文件路径: {result['file_path']}")
        print(f"\n日报内容预览:")
        print(result['content'][:300] + "...")
    else:
        print(f"✗ 生成失败: {result.get('message', 'Unknown error')}")


async def example_4_upload_report():
    """示例 4：上传日报"""
    print("\n" + "="*60)
    print("示例 4：上传日报")
    print("="*60)
    
    client = MCPExampleClient()
    result = await client.call_tool(
        'upload_daily_report',
        report_date='2025-02-02',
        auto_generate=True
    )
    
    if result['status'] == 'success':
        print(f"✓ 日报已上传")
        print(f"  日期: {result['date']}")
        print(f"  文件: {result['file_path']}")
    else:
        print(f"✗ 上传失败: {result.get('message', 'Unknown error')}")


async def example_5_complete_workflow():
    """示例 5：完整工作流（一键生成并上传）"""
    print("\n" + "="*60)
    print("示例 5：完整工作流（一键生成并上传）")
    print("="*60)
    
    client = MCPExampleClient()
    
    print("\n开始执行完整工作流...")
    print("阶段 1: 检查认证...")
    
    auth_status = await client.call_tool('get_bk_auth_status')
    if not auth_status['is_authenticated']:
        print("⚠️  认证凭证不完整，无法继续")
        print("请先调用 refresh_bk_credentials() 设置凭证")
        return
    
    print("✓ 认证凭证完整")
    
    print("\n阶段 2: 生成并上传日报...")
    result = await client.call_tool('generate_and_upload_report')
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result['overall_status'] == 'success':
        print("\n✓ 完整工作流已完成")
    else:
        print(f"\n✗ 工作流未完全成功: {result['overall_status']}")


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("蓝鲸日报 MCP 客户端示例")
    print("="*60)
    
    try:
        # 示例 1：检查认证状态
        await example_1_check_auth()
        
        # 示例 2：更新认证凭证
        await example_2_update_credentials()
        
        # 示例 3：生成日报
        await example_3_generate_report()
        
        # 示例 4：上传日报
        await example_4_upload_report()
        
        # 示例 5：完整工作流
        await example_5_complete_workflow()
        
        print("\n" + "="*60)
        print("所有示例执行完成")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ 执行出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
