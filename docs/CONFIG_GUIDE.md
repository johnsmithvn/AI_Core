# 📋 CONFIG GUIDE - AI Core Configuration

**Version**: 2.0.0  
**Last Updated**: 2026-02-01

---

## 🎯 Tổng quan

AI Core sử dụng **3 file YAML** để cấu hình behavior:

```
app/config/
├── persona.yaml    # Tone + Behavior (v2.0: tách biệt)
├── rules.yaml      # Luật bất biến + context detection
└── system.yaml     # System settings (model, memory, api)
```

---

## 📁 1. PERSONA.YAML - Tone + Behavior (v2.0)

### Kiến trúc mới (v2.0)

**Trước đây (v1.x):** Chọn 1 persona cứng (casual HOẶC technical HOẶC cautious)

**Hiện tại (v2.0):** Kết hợp **Tone + Behavior** linh hoạt

```
Tone     + Behavior  = Persona
─────────────────────────────────
casual   + normal    = Vui vẻ, thoải mái
casual   + cautious  = Vui vẻ NHƯNG không bịa  ← Quan trọng!
technical + normal   = Nghiêm túc, chính xác
technical + cautious = Nghiêm túc, không bịa
```

### Cấu trúc mới

```yaml
# TONES - Giọng điệu (quyết định bởi context_type)
tones:
  casual:
    name: "Casual"
    temperature: 0.8
    style: ["thân thiện", "hài hước"]
    prompt_hint: "Trả lời thân thiện, có thể đùa nhẹ."
    
  technical:
    name: "Technical"
    temperature: 0.3
    style: ["rõ ràng", "chính xác"]
    prompt_hint: "Trả lời rõ ràng, có cấu trúc."

# BEHAVIORS - Hành vi (quyết định bởi needs_knowledge)
behaviors:
  normal:
    name: "Normal"
    prompt_hint: "Trả lời tự nhiên."
    
  cautious:
    name: "Cautious"
    prompt_hint: "Không chắc thì thừa nhận. KHÔNG bịa."

defaults:
  tone: "casual"
  behavior: "normal"
```

### Ví dụ thực tế

| Input | context_type | needs_knowledge | Persona |
|-------|--------------|-----------------|---------|
| "haha vui quá" | casual | ❌ | **Casual + Normal** |
| "tìm sách hay" | casual | ✅ | **Casual + Cautious** |
| "giải thích code" | technical | ❌ | **Technical + Normal** |
| "tìm tài liệu ML" | technical | ✅ | **Technical + Cautious** |

### Tại sao tách Tone và Behavior?

**Vấn đề v1.x:**
> User: "tìm sách hay về đồ cổ nha"
> 
> AI (Cautious persona): "Tôi không có thông tin cụ thể..." ← Đúng nhưng khô khan

**Giải pháp v2.0:**
> User: "tìm sách hay về đồ cổ nha"
>
> AI (Casual + Cautious): "Ôi bạn thích đồ cổ à? Gu chất! 😄 Nói thật mình không rành mấy cuốn cụ thể, thử hỏi thư viện đi!" ← Vui VÀ trung thực

### Temperature

| Tone | Temperature | Ý nghĩa |
|------|-------------|---------|
| casual | 0.8 | Sáng tạo, đa dạng |
| technical | 0.3 | Chính xác, ít random |

---

## 📁 2. RULES.YAML - Luật và Detection

### Mục đích
Định nghĩa **2 loại rules**:
1. **Core Principles** - Luật bất biến (không detect, chỉ enforce)
2. **Context Detection** - Nhận biết ngữ cảnh (detect mỗi request)

### Cấu trúc

```yaml
# PHẦN 1: Core Principles (KHÔNG DETECT - inject vào prompt)
core_principles:
  - rule: "Được đùa về thái độ, không đùa về sự thật"
    priority: "CRITICAL"
  - rule: "Không chắc → phải nói 'tôi không chắc'"
    priority: "CRITICAL"

# PHẦN 2: Context Detection (CÓ DETECT - mỗi request)
context_detection:
  casual_chat:
    keywords: ["chơi", "cười", "đùa", ...]
    confidence_threshold: 0.7
  technical_question:
    keywords: ["code", "debug", "lỗi", ...]
    confidence_threshold: 0.6

# PHẦN 3: Output Rules (VALIDATE sau generate)
output_rules:
  max_length: null
  must_be_honest: true
```

### Phân biệt 2 loại rules

| Loại | Khi nào chạy | Mục đích | Thay đổi? |
|------|--------------|----------|-----------|
| **core_principles** | Inject vào prompt | Guardrails an toàn | ❌ Không bao giờ |
| **context_detection** | Mỗi request | Nhận biết context | ✅ Có thể tune |
| **output_rules** | Sau generate | Validate output | ✅ Có thể config |

### Context Detection hoạt động như thế nào?

```
Input: "Debug lỗi Python giúp tôi"
                ↓
Scan keywords: ["debug", "lỗi"] → match technical_question
                ↓
Calculate score: 2/5 = 40%
                ↓
Compare threshold: 40% < 60% → KHÔNG đủ confident
                ↓
Fallback to: casual (default)
```

```
Input: "Code debug lỗi làm sao giải thích"
                ↓
Scan keywords: ["code", "debug", "lỗi", "làm sao", "giải thích"] → 5 match!
                ↓
Calculate score: 5/5 = 100%
                ↓
Compare threshold: 100% > 60% → ĐỦ confident
                ↓
context_type: technical ✅
```

### Tại sao keywords "fix cứng"?

**KHÔNG PHẢI fix cứng theo nghĩa xấu!**

```
Core Principles = Constitution (Hiến pháp)
  → Không bao giờ thay đổi
  → AI tự follow khi đọc prompt
  → Không cần detect violation

Context Detection = Nhận biết tình huống
  → CÓ detect mỗi request
  → Keywords có thể thêm/bớt
  → Threshold có thể tune
```

### Workflow tổng thể

```
User input
    ↓
┌─────────────────────────────────┐
│  Context Detection (dynamic)    │ ← rules.yaml → context_detection
│  - Scan keywords                │
│  - Calculate scores             │
│  - Determine context_type       │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Build Prompt                   │
│  - Core Principles (fixed)      │ ← rules.yaml → core_principles
│  - Persona instructions         │ ← persona.yaml
│  - User input + history         │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Model Generate                 │
│  (Model tự follow principles)   │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Output Validation              │ ← rules.yaml → output_rules
│  - Check honesty                │
│  - Length behavior warnings     │
└─────────────────────────────────┘
    ↓
Response to user
```

---

## 📁 3. SYSTEM.YAML - System Settings

### Mục đích
Cấu hình **infrastructure** - model, memory, API, logging.

### Cấu trúc

```yaml
# Model settings
model:
  default_provider: "openai"   # openai | anthropic | local | mock
  default_model: "gpt-4"
  timeout: 30
  max_retries: 3

# Memory settings
memory:
  short_term_limit: 20         # Messages per session
  long_term_enabled: true
  database_path: "data/memory.db"

# API settings
api:
  host: "0.0.0.0"
  port: 8000
  cors_enabled: true

# Session settings
session:
  timeout: 3600                # 1 hour
  cleanup_interval: 300        # 5 minutes
```

### Lưu ý

**File này KHÔNG được load tự động!**

Hiện tại, settings được đọc từ `.env`:
```dotenv
MODEL_PROVIDER=local
LOCAL_MODEL_URL=http://127.0.0.1:1234
LOCAL_MODEL_NAME=auto
```

**system.yaml** là reference config, có thể integrate sau.

---

## 🔧 Cách thêm/sửa config

### Thêm persona mới

```yaml
# persona.yaml
personas:
  # ...existing personas...
  
  creative:
    name: "Creative"
    description: "Sáng tạo, nghệ thuật, bay bổng"
    temperature: 0.9
    tone:
      - "imaginative"
      - "poetic"
    patterns:
      - "dùng metaphor"
      - "storytelling"
```

### Thêm keywords để detect

```yaml
# rules.yaml
context_detection:
  technical_question:
    keywords:
      - "code"
      - "debug"
      - "lỗi"
      - "api"        # ← Thêm mới
      - "database"   # ← Thêm mới
      - "server"     # ← Thêm mới
```

### Tune confidence threshold

```yaml
# Nếu detect sai quá nhiều → tăng threshold
technical_question:
  confidence_threshold: 0.7  # Strict hơn (từ 0.6)

# Nếu miss quá nhiều → giảm threshold
casual_chat:
  confidence_threshold: 0.5  # Loose hơn (từ 0.7)
```

---

## 📊 So sánh 3 files

| File | Thay đổi thường xuyên? | Ảnh hưởng | Khi nào sửa |
|------|------------------------|-----------|-------------|
| **persona.yaml** | ⚠️ Thỉnh thoảng | AI behavior | Thêm tính cách, tune temperature |
| **rules.yaml** | ✅ Có thể | Detection accuracy | Thêm keywords, tune threshold |
| **system.yaml** | ❌ Hiếm | Infrastructure | Đổi provider, timeout, ports |

---

## 🎯 Best Practices

### ✅ DO
- Tune `confidence_threshold` dựa trên test thực tế
- Thêm keywords phù hợp với domain của bạn
- Giữ `core_principles` CRITICAL không đổi
- Test sau mỗi lần thay đổi config

### ❌ DON'T
- Xóa core_principles CRITICAL
- Set temperature > 1.0 hoặc < 0.0
- Bỏ persona default
- Edit system.yaml mà không restart server

---

## 📚 Tham khảo thêm

- [CODEBASE_ANALYSIS.md](CODEBASE_ANALYSIS.md) - Chi tiết code
- [LENGTH_MANAGEMENT.md](LENGTH_MANAGEMENT.md) - Triết lý độ dài
- [API_REFERENCE.md](API_REFERENCE.md) - API docs

---

**Version**: 2.0.0  
**Status**: ✅ Production-ready configs (Tone + Behavior architecture)
