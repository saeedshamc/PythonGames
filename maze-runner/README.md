# Maze Runner

یک بازی هزارتو (Maze) دو بعدی بی‌نهایت ساخته‌شده با Python و Pygame. بازیکن باید در هزارتوی تصادفی گشت و گذار کند و راه خروج مخفی را پیدا کند.

## ویژگی‌ها

### گیم‌پلی
- **مراحل بی‌نهایت:** تولید خودکار هزارتو با الگوریتم Recursive Backtracker
- **سختی افزایشی:** با هر مرحله، سایز هزارتو بزرگتر می‌شود
- **خروج مخفی:** نقطه خروج نمایش داده نمی‌شود - بازیکن باید با گشت و گذار آن را پیدا کند
- **حرکت روان:** حرکت پیکسل به پیکسل به جای خانه به خانه برای تجربه بهتر
- **بدون دشمن:** تمرکز کامل بر اکتشاف و حل هزارتو

### سیستم ذخیره
- **ذخیره خودکار:** پیشرفت بازی به صورت خودکار ذخیره می‌شود
- **نقشه مراحل:** هر مرحله با نقشه دقیق ذخیره می‌شود برای بازپخش دقیق
- **بهترین زمان‌ها:** بهترین زمان هر مرحله ذخیره می‌شود
- **لیدربورد:** رتبه‌بندی بر اساس مراحل تکمیل شده و زمان

### رابط کاربری
- **پنجره دینامیک:** سایز پنجره بر اساس سایز هزارتو مرحله تنظیم می‌شود
- **اطلاعات کامل:** نمایش مرحله، زمان، حرکات، بهترین زمان و رتبه
- **خروج آسان:** دکمه Q برای بازگشت به منو و ESC برای خروج

## پیش‌نیازها

- Python 3.8+
- pygame
- numpy (برای افکت‌های صوتی)
- pyinstaller (برای ساخت EXE)

## روش‌های نصب

### روش ۱: نصب با اسکریپت (توصیه می‌شود)

#### ویندوز
```powershell
# اجرا با PowerShell (به صورت Administrator)
.\scripts\install_windows.ps1
```

#### لینوکس
```bash
chmod +x scripts/install_linux.sh
./scripts/install_linux.sh
```

### روش ۲: نصب دستی
```bash
pip install -r requirements.txt
python run.py
```

### روش ۳: نسخه پرتابل (بدون نیاز به نصب)

#### ویندوز
```powershell
.\scripts\build_portable_windows.ps1
```
فایل `MazeRunner_Portable_Windows.zip` ساخته می‌شود. کافیست آن را اکسترکت کنید و `Start.bat` را اجرا کنید.

#### لینوکس
```bash
chmod +x scripts/build_portable_linux.sh
./scripts/build_portable_linux.sh
```
فایل `MazeRunner_Portable_Linux.tar.gz` ساخته می‌شود. کافیست آن را اکسترکت کنید و `./start.sh` را اجرا کنید.

### روش ۴: ساخت فایل EXE (ویندوز)
```bash
pip install -r requirements.txt
python build_exe.py
```
فایل EXE در `dist/MazeRunner.exe` قرار می‌گیرد.

## کنترل‌ها

| کلید | عملکرد |
|---|---|
| فلش‌های جهت‌دار / W A S D | حرکت روان |
| Q | بازگشت به منو |
| ESC | خروج از بازی |
| Enter | شروع / ادامه بازی |
| C | پاک کردن پیشرفت (در منو) |
| R | تکرار مرحله (پس از برد) |

## محل ذخیره داده‌ها

- **ویندوز:** `C:\Users\<username>\.maze_runner\`
- **لینوکس/مک:** `~/.maze_runner/`

شامل:
- `progress.json` - پیشرفت کلی بازی
- `leaderboard.json` - رتبه‌بندی بازیکنان
- `levels/` - نقشه‌های ذخیره شده مراحل

## ساختار پروژه

```
maze-runner/
├── run.py                       # نقطه ورود اصلی
├── build_exe.py                 # اسکریپت ساخت EXE
├── requirements.txt              # وابستگی‌ها
├── pyproject.toml               # تنظیمات پکیج
├── scripts/                     # اسکریپت‌های نصب و ساخت
│   ├── install_windows.ps1      # نصب‌کننده ویندوز
│   ├── install_linux.sh         # نصب‌کننده لینوکس
│   ├── build_portable_windows.ps1  # نسخه پرتابل ویندوز
│   └── build_portable_linux.sh  # نسخه پرتابل لینوکس
├── src/
│   └── maze_runner/
│       ├── __init__.py
│       ├── main.py              # نقطه ورود پکیج
│       ├── game.py              # کلاس Game، حلقه اصلی و رندر
│       ├── maze.py              # تولید هزارتو و مسیریابی BFS
│       ├── audio.py             # مدیریت افکت‌های صوتی
│       ├── config.py            # ثابت‌ها، رنگ‌ها، وضعیت‌های بازی
│       └── save_manager.py      # سیستم ذخیره و لیدربورد
├── LICENSE
└── README.md
```

## تنظیمات

### تغییر سرعت حرکت
در `src/maze_runner/game.py`:
```python
self.move_speed = 4  # pixels per frame
```

### تغییر سایز پایه هزارتو
در `src/maze_runner/game.py`:
```python
base_size = 15  # سایز پایه برای مرحله ۱
```

### تغییر رنگ‌ها
در `src/maze_runner/config.py` می‌توانید رنگ‌های مختلف بازی را تغییر دهید.

## عیب‌یابی

### بازی اجرا نمی‌شود
- مطمئن شوید Python 3.8+ نصب است
- تمام وابستگی‌ها را نصب کنید: `pip install -r requirements.txt`

### صدا کار نمی‌کند
- numpy نصب کنید: `pip install numpy`

### اسکریپت‌های PowerShell اجرا نمی‌شوند
- PowerShell را به صورت Administrator باز کنید
- اجرای اسکریپت‌ها را فعال کنید:
  ```powershell
  Set-ExecutionPolicy RemoteSigned
  ```

## توسعه

برای افزودن ویژگی‌های جدید:
- `game.py` - منطق اصلی بازی
- `maze.py` - الگوریتم‌های تولید هزارتو
- `save_manager.py` - سیستم ذخیره
- `config.py` - تنظیمات ظاهری

## مجوز

MIT
