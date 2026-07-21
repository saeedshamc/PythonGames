# بازی مار (Snake Game)

## نحوه راه‌اندازی

### پیش‌نیاز
پایتون باید روی سیستم نصب باشه (نسخه‌ی ۳.۸ به بالا کافیه).

### ۱. نصب کتابخانه‌ی pygame
توی ترمینال یا CMD، توی پوشه‌ی پروژه این دستور رو بزن:
```
pip install pygame-ce
```
> اگه نسخه‌ی پایتونت خیلی جدید باشه (مثلاً ۳.۱۳ یا ۳.۱۴) و نصب `pygame` معمولی خطای build بده، به‌جاش از `pygame-ce` استفاده کن؛ چون این نسخه wheel آماده داره و کامپایل لازم نداره. اسم import شده هم همون `pygame` می‌مونه، پس کد بدون تغییر کار می‌کنه.

### ۲. اجرای بازی
فایل بازی رو (مثلاً با نام `snake_game.py`) توی همون پوشه قرار بده و بزن:
```
python snake_game.py
```

## ویژگی‌های بازی

### منوی اصلی
- **Start Game**: شروع بازی
- **Settings**: تنظیمات بازی
- **High Scores**: نمایش امتیازات برتر و آمار
- **Quit**: خروج از بازی

### کنترل بازی
| کلید | عملکرد |
|---|---|
| جهت‌دارها یا W/A/S/D | تغییر جهت حرکت مار |
| Space یا P | Pause کردن بازی |
| R | شروع دوباره‌ی بازی (بعد از باخت یا در Pause) |
| Esc | بازگشت به منوی اصلی |
| Q | خروج به منو (در حالت Pause) |

### تنظیمات
- **Difficulty**: Easy (آسان)، Medium (متوسط)، Hard (سخت)
- **Snake Color**: Green (سبز)، Blue (آبی)، Purple (بنفش)، Red (قرمز)
- **Wrap-Around**: فعال/غیرفعال کردن عبور از لبه‌ها
- **Game Mode**: Classic (کلاسیک)، Wall (دیواری)، Obstacles (با مانع)

### حالت‌های بازی
- **Classic**: مار می‌تونه از لبه‌ها عبور کنه و از طرف مقابل بیاد
- **Wall**: برخورد با دیوار باعث Game Over می‌شه
- **Obstacles**: موانع ثابت روی صفحه وجود دارن که باید ازشون دوری کنی

### Power-upها
- **طلایی (Golden)**: امتیاز دو برابر (+20)
- **آبی (Blue)**: سرعت موقت کم می‌شه (برای 5 ثانیه)
- **بنفش (Purple)**: سرعت موقت زیاد می‌شه (برای 5 ثانیه)

### آمار و رکوردها
- ذخیره‌سازی High Score در فایل JSON
- نمایش 10 امتیاز برتر با تاریخ و حالت بازی
- آمار کلی: تعداد بازی‌ها، مجموع امتیازات، میانگین امتیاز، بهترین زمان

## قوانین بازی
مار با خوردن جایزه‌ی قرمز رشد می‌کنه و امتیاز می‌گیره. بسته به تنظیمات، می‌تونه از لبه‌ها عبور کنه یا با دیوار برخورد کنه. برخورد با بدنه‌ی خودش یا موانع باعث پایان بازی میشه.

---

# توضیح خط‌به‌خط کد بازی مار (Snake Game)

## بخش ۱: ایمپورت کتابخانه‌ها

```python
import pygame
import random
import sys
```

- **خط ۱:** کتابخانه‌ی `pygame` رو وارد می‌کنیم؛ این کتابخانه ابزارهای لازم برای ساخت بازی (پنجره، رسم، کیبورد، زمان‌بندی) رو در اختیارمون می‌ذاره.
- **خط ۲:** ماژول `random` برای انتخاب موقعیت تصادفی جایزه (خوراک مار) استفاده میشه.
- **خط ۳:** ماژول `sys` برای خروج تمیز از برنامه (`sys.exit()`) به کار می‌ره.

---

## بخش ۲: تنظیمات کلی بازی

```python
CELL_SIZE = 15
GRID_WIDTH = 70
GRID_HEIGHT = 46
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS_START = 10
FPS_INCREASE_EVERY = 5
MAX_FPS = 25
```

- **`CELL_SIZE = 15`**: اندازه‌ی هر خونه (بلوک) روی صفحه، به پیکسل. هرچی این عدد کوچیک‌تر باشه، مار و خونه‌ها ریزتر دیده میشن.
- **`GRID_WIDTH = 70`**: تعداد خونه‌ها در جهت افقی (عرض صفحه‌ی بازی).
- **`GRID_HEIGHT = 46`**: تعداد خونه‌ها در جهت عمودی (ارتفاع صفحه‌ی بازی).
- **`WIDTH = CELL_SIZE * GRID_WIDTH`**: عرض واقعی پنجره به پیکسل، از ضرب اندازه‌ی خونه در تعداد خونه‌های افقی به دست میاد.
- **`HEIGHT = CELL_SIZE * GRID_HEIGHT`**: ارتفاع واقعی پنجره، به همون شکل محاسبه میشه.
- **`FPS_START = 10`**: سرعت اولیه‌ی بازی (فریم بر ثانیه) در شروع بازی.
- **`FPS_INCREASE_EVERY = 5`**: هر چند امتیاز (ضرب‌شده در ۱۰ در کد پایین‌تر)، سرعت بازی یک واحد زیاد میشه.
- **`MAX_FPS = 25`**: سقف سرعت؛ برای اینکه بازی بیش از حد سریع و غیرقابل‌کنترل نشه.

---

## بخش ۳: تعریف رنگ‌ها

```python
BLACK = (15, 15, 15)
GREEN = (50, 205, 50)
DARK_GREEN = (30, 140, 30)
RED = (220, 50, 50)
WHITE = (240, 240, 240)
GRAY = (60, 60, 60)
GRID_LINE = (35, 35, 35)
```

هرکدوم از این متغیرها یه رنگ رو به فرمت RGB (قرمز، سبز، آبی — هرکدوم بین ۰ تا ۲۵۵) نگه می‌دارن:
- `BLACK`: رنگ پس‌زمینه‌ی صفحه.
- `GREEN` و `DARK_GREEN`: رنگ بدنه و سر مار.
- `RED`: رنگ جایزه (خوراک) و پیام «باخت».
- `WHITE`: رنگ متن امتیاز.
- `GRAY`: رنگ متن راهنمای «دوباره شروع کن».
- `GRID_LINE`: رنگ خطوط ریز شبکه‌ای که پس‌زمینه رو تقسیم‌بندی می‌کنه.

---

## بخش ۴: کلاس اصلی بازی — `SnakeGame`

### متد `__init__` (سازنده‌ی کلاس)

```python
class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 48, bold=True)
        self.high_score = 0
        self.reset()
```

- **`class SnakeGame:`**: تعریف کلاسی که کل منطق بازی درونش قرار داره.
- **`def __init__(self):`**: متد سازنده؛ وقتی یک نمونه (`instance`) از این کلاس ساخته میشه، این کد اجرا میشه.
- **`pygame.init()`**: تمام زیرسیستم‌های pygame (گرافیک، صدا، فونت و...) رو راه‌اندازی می‌کنه. همیشه باید اول از همه صدا زده بشه.
- **`self.screen = pygame.display.set_mode((WIDTH, HEIGHT))`**: پنجره‌ی بازی رو با عرض و ارتفاع تعیین‌شده می‌سازه و اون رو در `self.screen` ذخیره می‌کنه تا بعداً روش رسم کنیم.
- **`pygame.display.set_caption("Snake Game")`**: عنوان پنجره رو تنظیم می‌کنه.
- **`self.clock = pygame.time.Clock()`**: یک شیء ساعت می‌سازه که برای کنترل سرعت بازی (فریم بر ثانیه) استفاده میشه.
- **`self.font = ...` و `self.big_font = ...`**: دو فونت مختلف (کوچیک برای امتیاز، بزرگ برای پیام «Game Over») بارگذاری می‌کنه.
- **`self.high_score = 0`**: بالاترین امتیازی که در طول اجرای برنامه ثبت شده، مقدار اولیه‌اش صفره.
- **`self.reset()`**: متد `reset` رو صدا می‌زنه تا بقیه‌ی متغیرهای بازی (مار، جهت، امتیاز و...) مقداردهی اولیه بشن.

### متد `reset`

```python
    def reset(self):
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = (1, 0)
        self.next_direction = self.direction
        self.score = 0
        self.food = self.spawn_food()
        self.game_over = False
        self.fps = FPS_START
```

- **`start_x`, `start_y`**: مختصات وسط شبکه‌ی بازی رو محاسبه می‌کنه (تقسیم صحیح `//` یعنی نتیجه رند به پایین میشه).
- **`self.snake = [...]`**: مار به‌صورت لیستی از مختصات (خونه‌ها) نگه داشته میشه. اولین عضو لیست، سر ماره. اینجا مار با طول ۳ و رو به راست ساخته میشه.
- **`self.direction = (1, 0)`**: جهت حرکت فعلی؛ `(1, 0)` یعنی یک واحد در محور x به جلو (حرکت به راست).
- **`self.next_direction = self.direction`**: جهت بعدی که کاربر با کیبورد انتخاب می‌کنه، جدا از `direction` نگه داشته میشه تا از تغییر جهت ناگهانی و برخورد با خود مار جلوگیری بشه.
- **`self.score = 0`**: امتیاز بازی صفر میشه.
- **`self.food = self.spawn_food()`**: با صدا زدن متد `spawn_food`، یه موقعیت تصادفی برای جایزه انتخاب میشه.
- **`self.game_over = False`**: در ابتدا بازی هنوز تموم نشده.
- **`self.fps = FPS_START`**: سرعت بازی روی مقدار اولیه تنظیم میشه.

### متد `spawn_food`

```python
    def spawn_food(self):
        """Places food on a random empty cell."""
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake:
                return pos
```

- **`while True:`**: یک حلقه‌ی بی‌نهایت که تا وقتی موقعیت مناسب پیدا نشه، ادامه پیدا می‌کنه.
- **`pos = (random.randint(...), random.randint(...))`**: یک مختصات تصادفی داخل محدوده‌ی شبکه انتخاب می‌کنه.
- **`if pos not in self.snake:`**: چک می‌کنه که این موقعیت، روی بدنه‌ی مار نباشه (تا جایزه داخل مار قرار نگیره).
- **`return pos`**: اگه موقعیت خالی بود، همون رو برمی‌گردونه و حلقه تموم میشه.

### متد `handle_input`

```python
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w) and self.direction != (0, 1):
                    self.next_direction = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s) and self.direction != (0, -1):
                    self.next_direction = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a) and self.direction != (1, 0):
                    self.next_direction = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.direction != (-1, 0):
                    self.next_direction = (1, 0)
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
```

- **`for event in pygame.event.get():`**: تمام رویدادهایی که از آخرین فریم اتفاق افتادن (کلیک، فشردن کلید، بستن پنجره و...) رو بررسی می‌کنه.
- **`if event.type == pygame.QUIT:`**: اگه کاربر روی دکمه‌ی بستن پنجره کلیک کنه، این شرط برقرار میشه و بازی با `pygame.quit()` و `sys.exit()` بسته میشه.
- **`if event.type == pygame.KEYDOWN:`**: بررسی می‌کنه آیا کلیدی از کیبورد فشرده شده.
- **چهار شرط جهت (بالا/پایین/چپ/راست)**: هرکدوم، هم کلید جهت‌دار و هم کلید WASD رو پشتیبانی می‌کنن. شرط دومِ هرکدوم (مثلاً `self.direction != (0, 1)`) جلوی این رو می‌گیره که مار مستقیماً به سمت عکس جهت فعلی‌اش برگرده و با خودش برخورد کنه.
- **`elif event.key == pygame.K_r and self.game_over:`**: اگه بازی تموم شده باشه و کاربر کلید `R` رو بزنه، بازی با `reset()` از نو شروع میشه.
- **`elif event.key == pygame.K_ESCAPE:`**: کلید Esc هم بازی رو می‌بنده.

### متد `update` — منطق اصلی حرکت

```python
    def update(self):
        if self.game_over:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction

        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)

        if new_head in self.snake:
            self.game_over = True
            self.high_score = max(self.high_score, self.score)
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            self.food = self.spawn_food()
            if self.score % (FPS_INCREASE_EVERY * 10) == 0 and self.fps < MAX_FPS:
                self.fps += 1
        else:
            self.snake.pop()
```

- **`if self.game_over: return`**: اگه بازی تموم شده، دیگه هیچ منطقی اجرا نمیشه (مار حرکت نمی‌کنه).
- **`self.direction = self.next_direction`**: جهت واقعی حرکت، با جهتی که کاربر انتخاب کرده به‌روزرسانی میشه.
- **`head_x, head_y = self.snake[0]`**: مختصات فعلی سر مار رو می‌گیره.
- **`dx, dy = self.direction`**: میزان جابه‌جایی در هر محور رو از جهت فعلی استخراج می‌کنه.
- **`new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)`**: مختصات سر جدید محاسبه میشه. استفاده از عملگر باقیمانده (`%`) باعث میشه اگه مار از یک لبه بیرون بره، از لبه‌ی مقابل دوباره وارد صفحه بشه (به‌جای برخورد با دیوار).
- **`if new_head in self.snake:`**: اگه خونه‌ی جدید همون‌جایی باشه که بدنه‌ی مار قبلاً اونجاست، یعنی مار به خودش برخورد کرده.
  - **`self.game_over = True`**: پرچم پایان بازی فعال میشه.
  - **`self.high_score = max(self.high_score, self.score)`**: اگه امتیاز این دور از رکورد قبلی بیشتر بود، رکورد به‌روز میشه.
  - **`return`**: از تابع خارج میشه؛ بقیه‌ی کد اجرا نمیشه.
- **`self.snake.insert(0, new_head)`**: سر جدید به ابتدای لیست مار اضافه میشه (یعنی مار به اون سمت حرکت کرده).
- **`if new_head == self.food:`**: اگه سر مار دقیقاً روی جایزه فرود اومده باشه:
  - **`self.score += 10`**: امتیاز ۱۰ واحد زیاد میشه.
  - **`self.food = self.spawn_food()`**: یه جایزه‌ی جدید در جای دیگه ساخته میشه.
  - **`if self.score % (FPS_INCREASE_EVERY * 10) == 0 and self.fps < MAX_FPS:`**: هر وقت امتیاز به مضرب ۵۰ برسه (۵ ضرب‌در ۱۰) و سرعت هنوز به سقف نرسیده باشه، سرعت یک واحد زیاد میشه.
- **`else: self.snake.pop()`**: اگه جایزه‌ای خورده نشده، آخرین خونه‌ی دم مار حذف میشه تا طول مار ثابت بمونه (چون یه خونه‌ی جدید به سر اضافه شده بود).

### متد `draw_cell`

```python
    def draw_cell(self, pos, color):
        rect = pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 1)
```

- **`rect = pygame.Rect(...)`**: یک مستطیل با موقعیت و اندازه‌ی یک خونه‌ی شبکه می‌سازه. مختصات خونه (`pos[0]`, `pos[1]`) در `CELL_SIZE` ضرب میشه تا به مختصات واقعی پیکسل تبدیل بشه.
- **`pygame.draw.rect(self.screen, color, rect)`**: مستطیل رو با رنگ داده‌شده (توپُر) رسم می‌کنه.
- **`pygame.draw.rect(self.screen, BLACK, rect, 1)`**: یک حاشیه‌ی نازک مشکی (ضخامت ۱ پیکسل) دور همون مستطیل می‌کشه تا خونه‌ها از هم جدا دیده بشن.

### متد `draw_grid`

```python
    def draw_grid(self):
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_LINE, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_LINE, (0, y), (WIDTH, y))
```

- **حلقه‌ی اول**: به فاصله‌ی هر `CELL_SIZE` پیکسل، یک خط عمودی از بالا تا پایین صفحه می‌کشه.
- **حلقه‌ی دوم**: به همون شکل، خطوط افقی می‌کشه.
- نتیجه‌ی این دو حلقه، یک شبکه‌ی ریز پس‌زمینه‌ست که کمک می‌کنه خونه‌های بازی بهتر دیده بشن.

### متد `draw` — رسم کل صحنه

```python
    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()

        for i, segment in enumerate(self.snake):
            color = DARK_GREEN if i == 0 else GREEN
            self.draw_cell(segment, color)

        self.draw_cell(self.food, RED)

        score_text = self.font.render(
            f"Score: {self.score}   Length: {len(self.snake)}   Best: {self.high_score}",
            True, WHITE
        )
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            over_text = self.big_font.render("Game Over!", True, RED)
            info_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press R to restart", True, GRAY)

            self.screen.blit(over_text, over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
            self.screen.blit(info_text, info_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))
            self.screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

        pygame.display.flip()
```

- **`self.screen.fill(BLACK)`**: کل صفحه رو با رنگ مشکی پاک می‌کنه (قبل از رسم فریم جدید).
- **`self.draw_grid()`**: خطوط شبکه رو رسم می‌کنه.
- **`for i, segment in enumerate(self.snake):`**: روی تک‌تک خونه‌های بدنه‌ی مار پیمایش می‌کنه. `enumerate` هم مقدار و هم اندیس (شماره) رو برمی‌گردونه.
  - **`color = DARK_GREEN if i == 0 else GREEN`**: اگه اندیس صفر باشه (یعنی سر مار)، رنگ تیره‌تری استفاده میشه؛ بقیه‌ی بدنه سبز روشنه.
  - **`self.draw_cell(segment, color)`**: هر خونه با رنگ مناسبش رسم میشه.
- **`self.draw_cell(self.food, RED)`**: جایزه با رنگ قرمز رسم میشه.
- **`score_text = self.font.render(...)`**: یک تصویر متنی (surface) از رشته‌ی امتیاز، طول مار و رکورد می‌سازه.
- **`self.screen.blit(score_text, (10, 10))`**: اون متن رو در گوشه‌ی بالا-چپ صفحه می‌چسبونه.
- **بلوک `if self.game_over:`**:
  - **`overlay = pygame.Surface((WIDTH, HEIGHT))`**: یک لایه‌ی نیمه‌شفاف مشکی روی کل صفحه می‌سازه تا پس‌زمینه‌ی بازی کم‌رنگ‌تر دیده بشه.
  - **`overlay.set_alpha(180)`**: میزان شفافیت این لایه رو تنظیم می‌کنه (از ۰ کاملاً شفاف تا ۲۵۵ کاملاً توپُر).
  - **سه خط بعدی**: متن‌های «Game Over!»، امتیاز نهایی و راهنمای ری‌استارت رو می‌سازه.
  - **سه خط `blit` آخر**: هرکدوم از این متن‌ها رو در مرکز صفحه، با فاصله‌ی عمودی مشخص از هم، قرار می‌ده.
- **`pygame.display.flip()`**: تمام چیزهایی که روی `self.screen` رسم شده رو واقعاً روی پنجره نمایش میده (بدون این خط، هیچی دیده نمیشه).

### متد `run` — حلقه‌ی اصلی بازی

```python
    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
```

- **`while True:`**: حلقه‌ی اصلی بازی که تا زمان بسته شدن برنامه ادامه داره.
- **`self.handle_input()`**: ورودی کاربر (کیبورد) رو بررسی می‌کنه.
- **`self.update()`**: منطق بازی (حرکت مار، برخورد، امتیاز) رو به‌روز می‌کنه.
- **`self.draw()`**: صحنه‌ی جدید رو رسم می‌کنه.
- **`self.clock.tick(self.fps)`**: برنامه رو به اندازه‌ی لازم مکث می‌ده تا سرعت بازی دقیقاً برابر با `self.fps` فریم بر ثانیه بمونه (نه سریع‌تر و نه کندتر).

---

## بخش ۵: نقطه‌ی شروع برنامه

```python
if __name__ == "__main__":
    game = SnakeGame()
    game.run()
```

- **`if __name__ == "__main__":`**: این شرط تضمین می‌کنه که کد داخلش فقط وقتی اجرا بشه که فایل مستقیماً با پایتون اجرا شده باشه (نه وقتی که به‌عنوان یک ماژول در فایل دیگه‌ای import شده).
- **`game = SnakeGame()`**: یک نمونه از کلاس بازی ساخته میشه؛ در همین لحظه `__init__` و به‌دنبالش `reset()` اجرا میشن.
- **`game.run()`**: حلقه‌ی اصلی بازی رو استارت می‌زنه و بازی شروع به کار می‌کنه.