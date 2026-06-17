import os
import sys

# 1. จัดการเรื่อง Path เพื่อให้โค้ดหาโมดูล samfwtool เจอ
# (โค้ดนี้จะดึงตำแหน่งโฟลเดอร์ปัจจุบันที่ไฟล์นี้อยู่โดยอัตโนมัติ)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 2. นำเข้าโมดูลจาก samfwtool ตามคู่มือของคุณ
try:
    from samfwtool.core.parser import FirmwareParser
    from samfwtool.analysis.security import SecurityScanner
    print("[+] นำเข้าโมดูล SamFWTool สำเร็จ!")
except ImportError as e:
    print(f"[-] ไม่สามารถนำเข้าโมดูลได้: {e}")
    print("[-] แนะนำให้รันไฟล์นี้ในโฟลเดอร์หลักของ samfwtool")
    sys.exit(1)

def main():
    # --- ส่วนที่ 1: ตรวจสอบและวิเคราะห์ไฟล์เฟิร์มแวร์ ---
    # เปลี่ยนชื่อไฟล์ "firmware.tar.md5" เป็นชื่อไฟล์เฟิร์มแวร์จริงของคุณ
    firmware_file = "firmware.tar.md5" 
    
    if os.path.exists(firmware_file):
        print(f"\n[1/2] กำลังเริ่มวิเคราะห์ไฟล์: {firmware_file} ...")
        parser = FirmwareParser(firmware_file)
        info = parser.parse()
        print("[+] ผลการวิเคราะห์เฟิร์มแวร์:")
        print(info)
    else:
        print(f"\n[!] ไม่พบไฟล์ {firmware_file} (ข้ามขั้นตอนการ Parse)")

    # --- ส่วนที่ 2: สแกนความปลอดภัยของโฟลเดอร์เฟิร์มแวร์ ---
    # เปลี่ยนชื่อโฟลเดอร์ "firmware_dir/" เป็นโฟลเดอร์ที่คุณแตกไฟล์เฟิร์มแวร์ไว้แล้ว
    firmware_dir = "firmware_dir/" 
    
    if os.path.exists(firmware_dir):
        print(f"\n[2/2] กำลังเริ่มสแกนความปลอดภัยโฟลเดอร์: {firmware_dir} ...")
        scanner = SecurityScanner(firmware_dir)
        results = scanner.scan()
        print("[+] ผลการสแกนความปลอดภัย:")
        print(results)
    else:
        print(f"\n[!] 不พบโฟลเดอร์ {firmware_dir} (ข้ามขั้นตอนการสแกน)")

if __name__ == "__main__":
    # เปิดโหมด Debug ผ่านโค้ด Python (เหมือนการพิมพ์ export SAMFWTOOL_DEBUG=1)
    os.environ["SAMFWTOOL_DEBUG"] = "1"
    
    main()

