from typing import Dict, Any

class NotificationService:
    def send_notification(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        recipients = payload.get("recipients", [])
        subject = payload.get("subject", "成績通知")
        message = payload.get("message", "")
        if not recipients:
            return {"success": False, "message": "收件人列表為空"}

        # 模擬發送通知
        return {
            "success": True,
            "message": f"已向 {len(recipients)} 位收件人發送通知: {subject}"
        }
