import os
import shutil
import time
import sys
import ctypes
from datetime import datetime

# ===============================================
# PATH KONFIGURASI
# ===============================================
XAMPP_DATA = r"C:\xampp\mysql\data"
XAMPP_BACKUP = r"C:\xampp\mysql\backup"
BCK_BASE = r"C:\BCK_MYSQL"

XAMPP_HTDOCS = r"C:\xampp\htdocs"
HTDOCS_BACKUP = r"C:\BCK_HTDOCS"
HTDOCS_DEFAULT_SRC = r"C:\DTAEXTX"   

LOG_FILE = "hapibesday.log"

EXCLUDE_BACKUP = [
    "mysql",
    "performance_schema",
    "phpmyadmin",
    "aria_log.00000001",
    "aria_log_control",
    "ib_buffer_pool",
    "ib_logfile0",
    "ib_logfile1",
    "ibtmp1",
    "multi-master.info",
    "my.ini",
    "mysql.pid",
    "mysql_error.log",
]

EXCLUDE_HTDOCS = [
    "dashboard",
    "img",
    "webalizer",
    "xampp",
    "applications.html",
    "bitnami.css",
    "favicon.ico",
    "index.php",
]

DEFAULT_HTDOCS = [
    "dashboard",
    "img",
    "webalizer",
    "xampp",
    "applications.html",
    "bitnami.css",
    "favicon.ico",
    "index.php",
]

# ===============================================
# LOGGING
# ===============================================

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except Exception:
        pass

# ===============================================
# UTILITY
# ===============================================

def clear():
    os.system("cls")

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def progress_bar(current, total, bar_length=40):
    if total <= 0:
        bar = " " * bar_length
        sys.stdout.write(f"\r[{bar}] 0%")
        sys.stdout.flush()
        return
    percent = int((current / total) * 100)
    if percent > 100:
        percent = 100
    filled = int(bar_length * percent // 100)
    if filled >= bar_length:
        filled = bar_length - 1
    bar = "=" * filled + ">" + " " * (bar_length - filled - 1)
    sys.stdout.write(f"\r[{bar}] {percent}%")
    sys.stdout.flush()

def press():
    input("\nTekan apa saja untuk lanjut...")

def make_unique_folder(base, label=""):

    if not os.path.exists(base):
        try:
            os.makedirs(base)
        except Exception as e:
            log(f"ERROR membuat folder {base}: {e}")
        log(f"Membuat folder {label} baru: {base}")
        return base

    n = 1
    while True:
        suffix = "_OLD" + ("_OLD" * (n - 1) if n > 1 else "")
        new_name = base + suffix
        if not os.path.exists(new_name):
            try:
                os.rename(base, new_name)
                log(f"Rename {label} lama: {base} -> {new_name}")
            except Exception as e:
                log(f"ERROR rename {label}: {e}")
            break
        n += 1

    try:
        os.makedirs(base)
    except Exception as e:
        log(f"ERROR membuat folder baru setelah rename {base}: {e}")

    log(f"Membuat folder {label} baru: {base}")
    return base

# ===============================================
# SAFE COPY UTILITY
# ===============================================

def safe_copy(src, dst):

    try:
        if os.path.isdir(src):
            if os.path.exists(dst):
                try:
                    shutil.rmtree(dst)
                except Exception as e:
                    log(f"ERROR menghapus tujuan sebelum copytree {dst}: {e}")
            shutil.copytree(src, dst)
        else:
            dst_dir = os.path.dirname(dst)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
            shutil.copy2(src, dst)
        return True
    except Exception as e:
        log(f"ERROR safe_copy {src} -> {dst}: {e}")
        return False

# ===============================================
# COPY DENGAN PROGRESS BAR + LOG
# ===============================================

def copy_with_progress(src, dst, exclude_list=None):

    if not os.path.exists(src):
        print(f"Sumber {src} tidak ditemukan!")
        log(f"Gagal: sumber {src} tidak ditemukan.")
        return

    try:
        os.makedirs(dst, exist_ok=True)
    except Exception as e:
        log(f"ERROR membuat folder tujuan {dst}: {e}")
        print(f"Gagal membuat folder tujuan: {dst}")
        return

    items = os.listdir(src)
    total_items = len(items)
    if total_items == 0:
        print("\nTidak ada file/folder untuk disalin.")
        log(f"Tidak ada file/folder di sumber {src}.")
        return

    copied = 0
    log(f"Mulai menyalin dari {src} ke {dst}")
    for item in items:
        if exclude_list and item in exclude_list:
            log(f"Skip (by exclude_list): {item}")
            copied += 1
            progress_bar(copied, total_items)
            continue

        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        safe_copy(src_path, dst_path)

        copied += 1
        progress_bar(copied, total_items)
        time.sleep(0.03)

    progress_bar(total_items, total_items)
    print()
    log(f"Selesai menyalin dari {src} ke {dst} ({total_items} item).")

# ===============================================
# MENU 1: BACKUP DATABASE
# ===============================================

def menu_backup():
    clear()
    print("=== Backup Database MySql ===\n")
    log("Menu Backup Database dibuka.")

    print("Menyiapkan folder backup...")
    backup_folder = make_unique_folder(BCK_BASE, "backup database")

    print("Memulai proses backup MySql...\n")
    copy_with_progress(XAMPP_DATA, backup_folder, EXCLUDE_BACKUP)

    print("\nBackup Database Berhasil!")
    log("Backup database selesai.")
    press()

# ===============================================
# MENU 2: BACKUP HTDOCS (UPDATED)
#   - normal items -> C:\BCK_HTDOCS
#   - excluded items -> C:\DTAEXTX
# ===============================================

def menu_backup_htdocs():
    clear()
    print("=== Backup HTDOCS XAMPP ===\n")
    log("Menu Backup HTDOCS dibuka.")

    print("Menyiapkan folder backup BCK_HTDOCS dan DTAEXTX...")
    backup_main = make_unique_folder(HTDOCS_BACKUP, "backup HTDOCS")
    backup_excluded = make_unique_folder(HTDOCS_DEFAULT_SRC, "default HTDOCS (EXCLUDE)")

    if not os.path.exists(XAMPP_HTDOCS):
        print(f"Sumber HTDOCS tidak ditemukan: {XAMPP_HTDOCS}")
        log(f"Gagal: sumber HTDOCS tidak ditemukan: {XAMPP_HTDOCS}")
        press()
        return

    items = os.listdir(XAMPP_HTDOCS)
    total = len(items)
    if total == 0:
        print("Tidak ada isi di HTDOCS untuk dibackup.")
        log("Tidak ada isi di HTDOCS.")
        press()
        return

    print("\nMemulai proses backup...\n")
    done = 0
    for item in items:
        src = os.path.join(XAMPP_HTDOCS, item)
        if item in EXCLUDE_HTDOCS:
            dst = os.path.join(backup_excluded, item)
        else:
            dst = os.path.join(backup_main, item)

        safe_copy(src, dst)
        done += 1
        progress_bar(done, total)
        time.sleep(0.03)

    progress_bar(total, total)
    print()
    log(f"Backup HTDOCS selesai. Main->{backup_main}, Excluded->{backup_excluded}")
    print("\nBackup HTDOCS Berhasil!")
    press()

# ===============================================
# MENU 3: BUAT DATABASE BARU
# ===============================================

def menu_newdb():
    clear()
    print("=== Buat Database Baru ===\n")
    log("Menu Buat Database Baru dibuka.")

    data_old = XAMPP_DATA + "_old"

    if os.path.exists(data_old):
        try:
            shutil.rmtree(data_old, ignore_errors=True)
            log(f"Hapus folder lama: {data_old}")
        except Exception as e:
            log(f"ERROR menghapus data_old yang lama: {e}")

    try:
        if os.path.exists(XAMPP_DATA):
            os.rename(XAMPP_DATA, data_old)
            log(f"Rename data lama: {XAMPP_DATA} -> {data_old}")
    except Exception as e:
        log(f"ERROR rename folder data: {e}")

    try:
        os.makedirs(XAMPP_DATA, exist_ok=True)
    except Exception as e:
        log(f"ERROR membuat folder data baru: {e}")
    log(f"Membuat folder data baru: {XAMPP_DATA}")

    print("Mengcopy file dari backup MySql...\n")
    copy_with_progress(XAMPP_BACKUP, XAMPP_DATA, exclude_list=["ibdata1"])

    print("\nProses buat database baru sudah selesai!")
    log("Database baru dibuat.")
    press()

# ===============================================
# MENU 4: BUAT HTDOCS BARU (UPDATED)
#   - rename old
#   - buat folder baru
#   - copy DEFAULT_HTDOCS dari C:\DTAEXTX
# ===============================================

def menu_new_htdocs():
    clear()
    print("=== Buat HTDOCS Baru ===\n")
    log("Menu Buat HTDOCS Baru dibuka.")

    htdocs_old = XAMPP_HTDOCS + "_old"
    if os.path.exists(htdocs_old):
        try:
            shutil.rmtree(htdocs_old, ignore_errors=True)
            log(f"Hapus folder HTDOCS lama: {htdocs_old}")
        except Exception as e:
            log(f"ERROR hapus htdocs_old lama: {e}")

    try:
        if os.path.exists(XAMPP_HTDOCS):
            os.rename(XAMPP_HTDOCS, htdocs_old)
            log(f"Rename HTDOCS lama: {XAMPP_HTDOCS} -> {htdocs_old}")
    except Exception as e:
        log(f"ERROR rename HTDOCS: {e}")

    try:
        os.makedirs(XAMPP_HTDOCS, exist_ok=True)
    except Exception as e:
        log(f"ERROR membuat htdocs baru: {e}")
    log(f"Membuat folder HTDOCS baru: {XAMPP_HTDOCS}")

    print("Mengcopy DEFAULT_HTDOCS dari C:\\DTAEXTX ke HTDOCS baru...\n")
    if not os.path.exists(HTDOCS_DEFAULT_SRC):
        print("Folder C:\\DTAEXTX (default HTDOCS) tidak ditemukan!")
        log("ERROR: C:\\DTAEXTX tidak ditemukan. Jalankan menu backup HTDOCS terlebih dahulu.")
        press()
        return

    items = os.listdir(HTDOCS_DEFAULT_SRC)
    total = len(items)
    if total == 0:
        log("WARNING: C:\\DTAEXTX kosong.")
    copied = 0
    for item in items:
        src = os.path.join(HTDOCS_DEFAULT_SRC, item)
        dst = os.path.join(XAMPP_HTDOCS, item)
        safe_copy(src, dst)
        copied += 1
        progress_bar(copied, total)
        time.sleep(0.02)

    progress_bar(total, total)
    print()
    log("DEFAULT HTDOCS berhasil dicopy dari C:\DTAEXTX.")
    print("\nHTDOCS baru berhasil dibuat!")
    press()

# ===============================================
# MENU 5: RESTORE DATABASE
# ===============================================

def menu_restore():
    clear()
    print("=== Restore Database ===\n")
    log("Menu Restore Database dibuka.")

    if not os.path.exists(BCK_BASE):
        print("Folder backup tidak ditemukan!")
        log("ERROR: folder backup database tidak ditemukan.")
        press()
        return

    print("Memulai restore MySql\n")
    print("Proses restore isi C:\\BCK_MYSQL ke C:\\xampp\\mysql\data ...\n")
    copy_with_progress(BCK_BASE, XAMPP_DATA)

    print("\nProses restore database sudah selesai!")
    log("Restore database selesai.")
    press()

# ===============================================
# MENU 6: RESTORE HTDOCS (UPDATED)
#   - hanya meng-copy isi C:\BCK_HTDOCS ke C:\xampp\htdocs
#   - HTDOCS sudah dibuat (menu 4)
# ===============================================

def menu_restore_htdocs():
    clear()
    print("=== Restore HTDOCS ===\n")
    log("Menu Restore HTDOCS dibuka.")

    if not os.path.exists(HTDOCS_BACKUP):
        print("Backup HTDOCS (C:\\BCK_HTDOCS) tidak ditemukan!")
        log("ERROR: backup HTDOCS tidak ditemukan.")
        press()
        return

    if not os.path.exists(XAMPP_HTDOCS):
        print("Folder HTDOCS belum ada. Jalankan 'Buat HTDOCS Baru' (menu 4) terlebih dahulu.")
        log("ERROR: HTDOCS tujuan belum ada. Batal restore HTDOCS.")
        press()
        return

    print("Memulai restore HTDOCS\n")
    print("Proses restore isi C:\\BCK_HTDOCS ke C:\\xampp\\htdocs ...\n")
    copy_with_progress(HTDOCS_BACKUP, XAMPP_HTDOCS)

    print("\nRestore HTDOCS selesai!")
    log("Restore HTDOCS selesai.")
    press()

# ===============================================
# MAIN PROGRAM
# ===============================================

def main():
    clear()
    print("Mengecek Status Administrator...\n")

    if not is_admin():
        print("Program tidak berjalan sebagai Administrator!")
        print("Klik kanan → Run as Administrator\n")
        log("ERROR: program tidak dijalankan sebagai Administrator.")
        press()
        return

    log("Program dimulai dengan akses administrator.")

    while True:
        clear()
        print("Selamat datang di hapibesday, Program Backup dan Restore XAMPP.")
        print("\nApa yang ingin anda lakukan?")
        print("1. Backup Database")
        print("2. Backup HTDOCS")
        print("3. Buat Database Baru")
        print("4. Buat HTDOCS Baru")
        print("5. Restore Database")
        print("6. Restore HTDOCS")
        print("7. Exit")
        print("\n2025 - Dinnz\n")

        choice = input("Pilih menu: ").strip()

        if choice == "1":
            menu_backup()
        elif choice == "2":
            menu_backup_htdocs()
        elif choice == "3":
            menu_newdb()
        elif choice == "4":
            menu_new_htdocs()
        elif choice == "5":
            menu_restore()
        elif choice == "6":
            menu_restore_htdocs()
        elif choice == "7":
            clear()
            print("Terima kasih telah menggunakan hapibesday.exe")
            log("Program dihentikan oleh user.")
            time.sleep(1)
            break
        else:
            print("Pilihan tidak valid!")
            log(f"Input tidak valid: {choice}")
            time.sleep(1)

if __name__ == "__main__":
    main()
