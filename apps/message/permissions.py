from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsValidAndroidDevices(permissions.BasePermission):
    VALID_DEVICE_IDS = ['SP1A.210812.016','RP1A.200720.011']
    
    def has_permission(self, request, view):
        device_id = request.headers.get('Device-ID')
        
        if not device_id:
            raise PermissionDenied("Siz kirishingiz cheklangan, faqatgina firma egasi kira oladi.")
            
        if device_id not in self.VALID_DEVICE_IDS:
            raise PermissionDenied("Device ID xato.", device_id)
            
        print("🟢 Device ID:", device_id)
        request.auth_message = "Muvaffaqiyatli ulandingiz!"
        return True