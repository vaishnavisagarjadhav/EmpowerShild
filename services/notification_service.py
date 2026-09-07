"""
Notification service.
Handles push notifications (FCM) to guardians and an SMS fallback path
for the 'no network dependency' offline requirement.
"""
from typing import List


def send_push_notification(fcm_tokens: List[str], title: str, body: str, data: dict = None):
    """
    Send an FCM push notification to a list of guardian device tokens.
    In production this calls firebase_admin.messaging.send_multicast.
    Kept as a clean stub here so the project runs without live FCM keys.
    """
    print(f"[FCM] -> {fcm_tokens}: {title} | {body} | data={data}")
    return {"sent_to": len(fcm_tokens), "title": title, "body": body}


def send_sms_fallback(phone_numbers: List[str], message: str):
    """
    SMS fallback used when the device has no active internet connection.
    Integrate with an SMS gateway (Twilio, MSG91, etc.) here.
    """
    print(f"[SMS FALLBACK] -> {phone_numbers}: {message}")
    return {"sent_to": len(phone_numbers), "message": message}


def notify_guardians(guardian_contacts: list, incident: dict, offline: bool = False):
    title = "EmpowerShield SOS Alert"
    body = (
        f"Emergency triggered at "
        f"({incident.get('latitude')}, {incident.get('longitude')}). "
        f"Trigger type: {incident.get('trigger_type', 'manual')}."
    )
    fcm_tokens = [c["fcm_token"] for c in guardian_contacts if c.get("fcm_token")]
    phone_numbers = [c["phone"] for c in guardian_contacts if c.get("phone")]

    if offline or not fcm_tokens:
        return send_sms_fallback(phone_numbers, body)
    return send_push_notification(fcm_tokens, title, body, data=incident)
