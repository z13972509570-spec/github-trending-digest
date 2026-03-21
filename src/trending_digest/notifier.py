"""微信推送通知"""
import httpx
from typing import Optional
from .models import TrendReport
import logging
import os

logger = logging.getLogger(__name__)


class WeChatNotifier:
    """微信推送器（通过 QClaw Gateway）"""

    def __init__(
        self,
        gateway_url: Optional[str] = None,
        gateway_token: Optional[str] = None,
        target: Optional[str] = None
    ):
        self.gateway_url = gateway_url or os.getenv("QCLAW_GATEWAY_URL", "http://localhost:18789")
        self.gateway_token = gateway_token or os.getenv("QCLAW_TOKEN", "")
        self.target = target or os.getenv("WECHAT_TARGET", "")
        self.client = httpx.Client(timeout=30.0)

    def send_report(self, report: TrendReport) -> bool:
        """发送报告"""
        message = report.to_wechat_message()
        return self.send_message(message)

    def send_message(self, message: str) -> bool:
        """发送消息"""
        if not self.target:
            logger.warning("No WeChat target configured")
            return False

        try:
            # 通过 QClaw Gateway 发送
            url = f"{self.gateway_url}/api/message/send"
            headers = {
                "Authorization": f"Bearer {self.gateway_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "channel": "wechat",
                "to": self.target,
                "message": message
            }

            response = self.client.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                logger.info("Message sent successfully")
                return True
            else:
                logger.error(f"Failed to send message: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def send_test(self) -> bool:
        """发送测试消息"""
        return self.send_message("📊 GitHub Trending Digest 测试消息")


class ConsoleNotifier:
    """控制台通知（调试用）"""

    def send_report(self, report: TrendReport) -> bool:
        """打印报告"""
        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        message = report.to_wechat_message()

        console.print(Panel(message, title="📊 GitHub Trending Digest", border_style="green"))
        return True

    def send_message(self, message: str) -> bool:
        print(message)
        return True
