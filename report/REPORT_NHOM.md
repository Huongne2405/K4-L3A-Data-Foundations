# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G35
**Thành viên:** Lê Chí Hùng
**Thành viên:** Nguyễn Văn Hưởng
**Ngày:** 19/9

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy chế đào tạo đại học của Đại học Bách khoa Hà Nội (Quyết định 5445/QĐ-ĐHBK, 28/5/2025) — Chương II, các Điều 10–20 về đăng ký học tập, đánh giá kết quả, đồ án tốt nghiệp, tốt nghiệp, nghỉ học, chuyển chương trình, cảnh báo học tập và buộc thôi học.

**Tại sao nhóm chọn chủ đề này?**
> Đây đúng là loại câu hỏi sinh viên hay tra nhất ("được đăng ký tối đa bao nhiêu TC?", "bao giờ bị buộc thôi học?") và câu trả lời phải **chính xác từng con số**, nên là bài kiểm tra tốt cho retrieval — sai chunk là sai đáp án. Văn bản có cấu trúc Điều › Khoản › điểm a/b/c rõ ràng, cho phép nhóm thử chunking theo tiêu đề/mục (yêu cầu L3A) và so sánh với cách cắt theo ký tự. Nguồn là một PDF công khai duy nhất trên cổng thông tin đào tạo HUST, có số hiệu và ngày ban hành, nên `document_version` xác định được rõ ràng và không có vấn đề bản quyền/dữ liệu cá nhân.

### Danh sách tài liệu (Data Inventory)

Một PDF nguồn được tách thành 10 tài liệu, mỗi tài liệu = một Điều (hoặc hai Điều ngắn liên quan) để mỗi `doc_id` là một chủ đề tra cứu riêng và có thể gán `audience`/`category` khác nhau. Số ký tự tính trên phần nội dung (không tính frontmatter). Bảng nguồn dạng máy đọc: `data/quy-dinh-dao-tao/sources.csv`.

| # | Tên tài liệu (`doc_id`) | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Điều 10. Đăng ký học tập chương trình đại học (`dieu-10-dang-ky-hoc-tap`) | [QCDT_2025_5445_QD-DHBK.pdf](https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n%20Qu%E1%BB%91c%20%C4%90%E1%BA%A1t/files/DTDH_QDQC/Hoctap/QCDT_2025_5445_QD-DHBK.pdf) | 2026-09-19 / 5445/QĐ-ĐHBK (28/05/2025) | 3 172 | audience=student, category=registration, article=10 |
| 2 | Điều 11. Công nhận kết quả học tập và chuyển đổi tín chỉ (`dieu-11-cong-nhan-chuyen-doi-tin-chi`) | *như trên* | 2026-09-19 / 5445/QĐ-ĐHBK | 1 412 | audience=student, category=credit-transfer, article=11 |
| 3 | Điều 12. Ý kiến phản hồi của người học, đánh giá kết quả học tập (`dieu-12-danh-gia-ket-qua-hoc-tap`) | *như trên* | 2026-09-19 / 5445/QĐ-ĐHBK | 2 448 | audience=student, category=grading, article=12 |
| 4 | Điều 13. ĐATN — điều kiện được giao đề tài (`dieu-13-dieu-kien-lam-do-an-tot-nghiep`) | *như trên* | 2026-09-19 / 5445/QĐ-ĐHBK | 491 | audience=**student**, category=graduation-thesis, article=13 |
| 5 | Điều 13. ĐATN — cách chấm điểm của người hướng dẫn, phản biện và hội đồng (`dieu-13-cham-diem-do-an-tot-nghiep`) | *như trên* | 2026-09-19 / 5445/QĐ-ĐHBK | 970 | audience=**faculty**, category=graduation-thesis, article=13 |
| 6 | Điều 14–15. Đăng ký tốt nghiệp, điểm TB toàn khóa và hạng tốt nghiệp (`dieu-14-15-dang-ky-tot-nghiep-va-hang-tot-nghiep`) | *như trên* | 2026-09-19 / 5445/QĐ-ĐHBK | 2 638 | audience=student, category=graduation, article=14-15 |
| 7 | Điều 16. Nghỉ học tạm thời và tự nguyện thôi học (`dieu-16-nghi-hoc-tam-thoi-va-thoi-hoc`) | *như trên* | 2026-09-19 / 5445/QĐ-ĐHBK | 2 260 | audience=student, category=leave-of-absence, article=16 |
| 8 | Điều 17. Chuyển chương trình đào tạo, hình thức đào tạo (`dieu-17-chuyen-chuong-trinh-dao-tao`) | *như trên* | 2026-09-19 / 5445/QĐ-ĐHBK | 2 081 | audience=student, category=program-transfer, article=17 |
| 9 | Điều 18. Học cùng lúc hai chương trình (`dieu-18-hoc-cung-luc-hai-chuong-trinh`) | *như trên* | 2026-09-19 / 5445/QĐ-ĐHBK | 1 882 | audience=student, category=dual-program, article=18 |
| 10 | Điều 19–20. Cảnh báo học tập, buộc thôi học và xử lý vi phạm (`dieu-19-20-canh-bao-hoc-tap-va-buoc-thoi-hoc`) | *như trên* | 2026-09-19 / 5445/QĐ-ĐHBK | 2 014 | audience=student, category=academic-warning, article=19-20 |
| | **Tổng** | 1 nguồn | | **19 368** | 10 tài liệu, 9 student + 1 faculty |

Tất cả 10 tài liệu còn có chung: `department=academic-affairs`, `language=vi`, `chapter="Chương II — Đào tạo đại học"`, `issuer`, `issued_date=2025-05-28`, `source_document`.

**Vì sao Điều 13 được tách làm hai tài liệu với `audience` khác nhau?** Khoản 2 Điều 13 gồm điểm a (công thức 0,5/0,5 — sinh viên cần biết) và các điểm b–d (cách người hướng dẫn/phản biện/hội đồng cho điểm, điểm liệt — hướng dẫn cho giảng viên). Tách ra để có một tài liệu `faculty` thật sự trong corpus; nhờ đó câu hỏi số 5 mới chứng minh được `metadata_filter={"audience": "student"}` thay đổi kết quả (không lọc → tài liệu faculty chiếm top-1).

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ. *(PDF công khai trên ctt.hust.edu.vn; nội dung là văn bản quy phạm nội bộ được phổ biến rộng rãi cho sinh viên. Hai file template `data/university/*.md` của đề bài với `source_url` giả `example.edu` đã được xoá khỏi corpus.)*
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata. *(Kiểm tra tự động bằng `load_corpus()` trong `scripts/compare_strategies.py`: 10/10 đủ 4 trường bắt buộc.)*

### Cấu trúc Metadata (Metadata Schema)

Metadata nằm trong YAML frontmatter của từng file `.md`, được đọc khi ingest và gắn vào **mọi chunk** của tài liệu (cộng thêm `doc_id`, `chunk_index`, `section` sinh ra lúc chunk).

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | enum `student` / `faculty` / `staff` / `all` | `student` | Trường lọc bắt buộc của L3A. Cùng một chủ đề (chấm ĐATN) có bản cho sinh viên và bản cho giảng viên; lọc `audience=student` tránh trả về hướng dẫn dành cho hội đồng — Q5 chứng minh filter đổi top-1. |
| `category` | string (slug) | `academic-warning`, `registration`, `graduation` | Chủ đề nghiệp vụ của Điều. Dùng để thu hẹp không gian tìm kiếm khi câu hỏi mơ hồ về từ vựng — ví dụ Q2 "buộc thôi học" bị nhầm sang "tự nguyện thôi học" (`leave-of-absence`); lọc `category=academic-warning` loại nhiễu này. |
| `article` | string | `"10"`, `"14-15"` | Cho phép truy vấn kiểu tra cứu trực tiếp ("Điều 16 nói gì?") và để agent trích dẫn nguồn "theo Điều X". |
| `section` (sinh lúc chunk) | string | `"Điều 19. Cảnh báo học tập và buộc thôi học › Khoản 3. Buộc thôi học"` | Breadcrumb của `SectionChunker` v2: giữ ngữ cảnh Điều/Khoản cho chunk mà không nhồi vào nội dung được embed; agent dùng để trích dẫn "Điều 19 Khoản 3". |
| `source_url` | URL | `https://ctt.hust.edu.vn/.../QCDT_2025_5445_QD-DHBK.pdf` | Truy vết câu trả lời về văn bản gốc; bắt buộc theo đề. |
| `retrieved_at` | date ISO | `2026-09-19` | Biết dữ liệu lấy khi nào để kiểm tra độ mới khi quy chế được sửa đổi. |
| `document_version` | string | `"5445/QĐ-ĐHBK"` (kèm `issued_date=2025-05-28`) | Phân biệt phiên bản quy chế (quy chế cũ 2021 vs 2025) — điều kiện tiên quyết để không trả lời theo quy định đã hết hiệu lực. |
| `department`, `language`, `chapter`, `issuer` | string | `academic-affairs`, `vi`, `Chương II — Đào tạo đại học` | Hiện đồng nhất trong corpus nên chưa dùng để lọc; giữ sẵn để khi mở rộng sang quy định thư viện/ký túc xá/học phí (khác `department`) hoặc bản tiếng Anh (`language=en`) thì filter hoạt động ngay. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.
>
> Toàn bộ số liệu dưới đây được sinh bởi `python scripts/compare_strategies.py` (embedder thật: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, corpus 10 tài liệu trong `data/quy-dinh-dao-tao/`, 19 368 ký tự nội dung sau khi bỏ frontmatter). Chạy lại script sẽ ra đúng các bảng này.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(text, chunk_size=200)` trên 3 tài liệu. Cột cuối đếm số chunk **bắt đầu giữa câu/giữa Khoản** (không mở đầu bằng tiêu đề, chữ hoa hoặc ký hiệu điểm `a)`, `b)`…):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Điều 10 — Đăng ký học tập (6 Khoản) | FixedSizeChunker (`fixed_size`) | 16 | 198 | ✗ 15/16 chunk cắt giữa câu |
| Điều 10 — Đăng ký học tập (6 Khoản) | SentenceChunker (`by_sentences`) | 8 | 394 | ~ 0 chunk cắt giữa câu, nhưng 1 chunk gộp cuối Khoản 1 với đầu Khoản 2 |
| Điều 10 — Đăng ký học tập (6 Khoản) | RecursiveChunker (`recursive`) | 22 | 142 | ~ 2/22 cắt giữa câu; chunk quá vụn (một điểm `a)` = một chunk) |
| Điều 16 — Nghỉ học tạm thời (5 Khoản) | FixedSizeChunker (`fixed_size`) | 12 | 188 | ✗ 11/12 |
| Điều 16 — Nghỉ học tạm thời (5 Khoản) | SentenceChunker (`by_sentences`) | 6 | 374 | ~ 0/6 |
| Điều 16 — Nghỉ học tạm thời (5 Khoản) | RecursiveChunker (`recursive`) | 16 | 140 | ~ 2/16 |
| Điều 19–20 — Cảnh báo học tập (3 Khoản) | FixedSizeChunker (`fixed_size`) | 11 | 183 | ✗ 7/11 |
| Điều 19–20 — Cảnh báo học tập (3 Khoản) | SentenceChunker (`by_sentences`) | 6 | 333 | ~ 0/6 |
| Điều 19–20 — Cảnh báo học tập (3 Khoản) | RecursiveChunker (`recursive`) | 15 | 132 | ✓ 0/15 |

**Nhận xét baseline:**
- `fixed_size` gần như luôn cắt giữa câu (ví dụ chunk bắt đầu bằng `"hè không có đợt điều chỉnh đăng ký. ## Khoản 2…"`), làm mất chủ ngữ của quy định — tệ nhất cho văn bản pháp quy.
- `by_sentences` giữ trọn câu nhưng **không biết ranh giới Khoản**: regex tách câu theo `". "` nên các điểm `a) … ; b) …` (kết thúc bằng `;`) bị dính thành một chunk dài, còn tiêu đề `## Khoản 2` lại bị dính vào cuối chunk của Khoản 1.
- `recursive` với `chunk_size=200` tôn trọng dòng trống nên ít cắt giữa câu, nhưng tạo chunk quá nhỏ (mỗi điểm `a)`, `b)` một chunk) → mất câu dẫn "được quy định như sau:" phía trên → chunk đứng một mình không hiểu đang nói về điều kiện gì.

→ Kết luận chung của nhóm: với quy chế đào tạo, **đơn vị ý nghĩa là Khoản**, nên chiến lược phải nhận biết được tiêu đề `## Khoản`. Hai thành viên đi hai hướng khác nhau để đạt điều đó.

### Chiến lược của từng thành viên

**Thành viên 1 — Lê Chí Hùng**
- **Loại chiến lược:** custom — `SectionChunker` (chia theo tiêu đề Điều/Khoản, có breadcrumb) — đáp ứng yêu cầu L3A "ít nhất một thành viên chunk theo heading/section".
- **Mô tả & lý do chọn cho chủ đề này:** Mỗi Khoản của quy chế là một quy định trọn vẹn (điều kiện + hệ quả), nên cắt đúng tại `## Khoản` giữ được ngữ cảnh pháp lý tốt nhất. Khoản dài hơn `max_chars=900` được tách tiếp theo các điểm `a)…` nhưng **giữ lại câu dẫn** cho từng mảnh; Khoản quá ngắn (< `min_chars=250`) được gộp vào chunk trước để tránh chunk chỉ có một câu. Mỗi chunk đi kèm *breadcrumb* `"<tên Điều> › <tên Khoản>"`: bản v1 ghép breadcrumb vào đầu nội dung; bản v2 (chọn) đưa breadcrumb vào `metadata["section"]` qua `chunk_with_sections()` để agent vẫn trích dẫn được "Điều X Khoản Y" mà embedding không bị loãng bởi tiền tố lặp lại (xem ablation bên dưới).
- **Code snippet:** đầy đủ tại `src/chunking.py` (`class SectionChunker`), phần lõi:
```python
class SectionChunker:
    HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
    FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
    ITEM_RE = re.compile(r"\n(?=[a-zđ]\)\s)")          # ranh giới điểm a) b) c)

    def __init__(self, max_chars=900, min_chars=250, include_breadcrumb=False): ...

    def chunk(self, text: str) -> list[str]:
        pairs = self.chunk_with_sections(text)
        return [body for _, body in pairs]                    # v2: breadcrumb đi vào metadata

    def chunk_with_sections(self, text: str) -> list[tuple[str, str]]:
        text = self.FRONTMATTER_RE.sub("", text).strip()
        pieces = []
        for breadcrumb, body in self._split_sections(text):   # ("Điều 19 … › Khoản 3. Buộc thôi học", "Buộc thôi học là …")
            for piece in self._fit(body):                     # tách theo a) b) c) nếu body > max_chars, giữ câu dẫn
                pieces.append((breadcrumb, piece))
        merged = []                                           # gộp khoản quá ngắn vào chunk liền trước
        for crumb, body in pieces:
            if merged and len(body) < self.min_chars:
                merged[-1] = (merged[-1][0], merged[-1][1] + "\n" + body)
            else:
                merged.append((crumb, body))
        return merged
```
Khi ingest: `Document(content=body, metadata={..., "section": breadcrumb})` (xem `build_store()` trong `scripts/compare_strategies.py`).

**Thành viên 2 — Nguyễn Văn Hưởng**
- **Loại chiến lược:** Recursive (tinh chỉnh) — `RecursiveChunker(separators=["\n## ", "\n\n", "\n", ". ", " ", ""], chunk_size=600)`.
- **Mô tả & lý do chọn:** Giữ nguyên thuật toán built-in nhưng **thêm `"\n## "` lên đầu danh sách separator** để chunker ưu tiên cắt tại Khoản trước khi cắt theo đoạn/câu, và nâng `chunk_size` từ 200 → 600 để một Khoản trung bình (~400–500 ký tự) nằm trọn trong một chunk thay vì bị vỡ thành từng điểm `a)`, `b)`. Ưu điểm là không cần viết code mới, không có breadcrumb nên chunk gọn; nhược điểm là khi cắt bằng separator thì tiêu đề `## ` bị mất dấu `#`, và các Khoản ngắn liên tiếp bị gộp vào nhau theo giới hạn ký tự chứ không theo nghĩa.
- **Code snippet:** không custom — chỉ đổi tham số:
```python
RecursiveChunker(separators=["\n## ", "\n\n", "\n", ". ", " ", ""], chunk_size=600)
```

### Thống kê chunk trên toàn corpus (10 tài liệu)

| Chiến lược | Tổng chunk | Độ dài TB | Min | Max | Chunk bắt đầu đúng ranh giới Khoản/điểm |
|---|---|---|---|---|---|
| Baseline `FixedSizeChunker(500, 50)` | 47 | 451 | 62 | 500 | 11/47 (23%) |
| Baseline `SentenceChunker(3)` | 49 | 393 | 106 | 780 | 49/49 (100%) |
| Hưởng — `RecursiveChunker(600, "\n## ")` | 45 | 428 | 103 | 600 | 45/45 (100%) |
| Hùng — `SectionChunker(900, 250)` v2 | 36 | 511 | 79 | 916 | 36/36 (100%) |

### So Sánh Giữa Các Thành Viên

Chạy 5 câu hỏi đánh giá của nhóm (mục 3) với `top_k=3`. Điểm ở đây **chỉ tính vị trí chunk chứa gold answer**: **2** = top-1, **1** = top-2/3, **0** = không có trong top-3; phần "agent trả lời đúng" mỗi thành viên chấm trên code cá nhân ở `REPORT_CANHAN.md`.

| # | Câu hỏi | Baseline Fixed | Baseline Sentence | Hưởng — Recursive | Hùng — Section v2 |
|---|---|---|---|---|---|
| 1 | Sinh viên được đăng ký tối đa bao nhiêu TC trong học kỳ hè? | 2 | 2 | 2 | 2 |
| 2 | Khi nào sinh viên bị buộc thôi học? | 0 (miss) | 0 (miss) | 1 (top-2) | 1 (top-2) |
| 3 | Nghỉ học tạm thời vì lý do cá nhân được nghỉ tối đa bao lâu? | 2 | 2 | 1 (top-2) | 2 |
| 4 | Điều kiện để được xét công nhận tốt nghiệp là gì? | 2 | 2 | 2 | 2 |
| 5 | Điểm ĐATN tính từ điểm quá trình và điểm cuối kỳ theo trọng số nào? *(filter `audience=student`)* | 2 | 2 | 2 | 2 |
| | **Tổng /10** | **8** | **8** | **8** | **9** |

> Lưu ý: cột "Hưởng — Recursive" ở bảng trên là mô phỏng cùng tham số trong repo này (45 chunk). Trên **code riêng của Hưởng**, cùng tham số nhưng cách gắn separator `"\n## "` vào *đầu* section kế tiếp sinh ra **50 chunk**, trong đó có chunk chỉ chứa dòng tiêu đề; kết quả thật của Hưởng là Q1 2, **Q2 0** (chunk Điều 19 ở top-2 chỉ là tiêu đề, không chứa hai điều kiện), Q3 1, Q4 2, Q5 2 = **7/10** (chi tiết trong `REPORT_CANHAN.md` của Hưởng). Mục 3 dùng số thật của từng người.

Điểm số sát nhau vì corpus nhỏ (19k ký tự) và các câu 1, 4, 5 đều có từ khoá rất đặc trưng — mọi cách cắt đều tìm ra. Khác biệt chỉ xuất hiện ở hai câu khó: **Q2** (baseline miss hoàn toàn, hai chiến lược nhận biết Khoản đưa được đúng chunk vào top-2) và **Q3** (chunk gộp trọn Khoản 2 của Section lên top-1, còn Recursive cắt Khoản 2 thành 2 mảnh nên mảnh chứa điểm `d)` tụt xuống top-2).

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Lê Chí Hùng | `SectionChunker` v2 (custom, theo Điều/Khoản; breadcrumb trong metadata) | 9 | 100% chunk đúng ranh giới Khoản; ít chunk nhất (36) nên ít nhiễu; một Khoản liệt kê điều kiện nằm trọn một chunk (thắng Q3); `metadata["section"]` cho phép agent trích "Điều 16 Khoản 2" | Chunk dài nhất (TB 511, max 916) → tốn token prompt hơn; phụ thuộc vào việc tài liệu có heading Markdown chuẩn (`# Điều`, `## Khoản`); Q2 vẫn thua chunk "tự nguyện thôi học" |
| Nguyễn Văn Hưởng | `RecursiveChunker` tinh chỉnh (`"\n## "`, 600) | 8 (mô phỏng trong repo này) / **7 (code riêng của Hưởng)** | Không cần code mới; chunk vừa phải (TB 428); tôn trọng ranh giới Khoản nhờ separator `"\n## "`; Q2 ngang Section | Cắt theo giới hạn ký tự nên Khoản dài (Điều 16 Khoản 2, ~1000 ký tự) bị vỡ thành 2 mảnh theo dòng trống, mảnh sau mất câu dẫn (thua Q3); tiêu đề mất dấu `##`; không có ngữ cảnh Điều để trích nguồn |
| (baseline) | `FixedSizeChunker(500/50)` | 8 | Overlap 50 tình cờ giữ được câu chứa đáp án ở Q1, Q3, Q5 | 77% chunk cắt giữa câu (ví dụ chunk mở đầu `"hè không có đợt điều chỉnh đăng ký. ## Khoản 2…"`); Q2 miss; điểm similarity thấp nhất ở Q5 (0.487) |
| (baseline) | `SentenceChunker(3)` | 8 | Không cắt giữa câu; Q5 có điểm cao nhất (0.681) vì chunk 3 câu rất ngắn khớp đúng câu "Điểm ĐATN…" | Không biết ranh giới Khoản: các điểm `a); b); c)` kết thúc bằng `;` bị coi là một câu → chunk dài bất thường (max 780); Q2 miss |

**Ablation của `SectionChunker` (cùng 5 câu hỏi) — vì sao chọn v2 với `max_chars=900, min_chars=250`:**

| Biến thể | Số chunk | Q1 | Q2 | Q3 | Q4 | Q5 | Tổng |
|---|---|---|---|---|---|---|---|
| v1: breadcrumb ghép vào nội dung, `min_chars=80` | 55 | 2 | 1 (top-3) | 1 (top-2) | 2 | 2 | 8 |
| v1: breadcrumb ghép vào nội dung, `min_chars=250` | 36 | 2 | 1 (top-2) | 1 (top-2) | 2 | 2 | 8 |
| v2: breadcrumb → metadata, `min_chars=80` | 55 | 2 | **0 (miss)** | 2 | 2 | 2 | 8 |
| **v2: breadcrumb → metadata, `min_chars=250` (chọn)** | 36 | 2 | 1 (top-2) | 2 | 2 | 2 | **9** |
| v2, `max_chars=500` | 43 | 2 | 1 (top-2) | 2 | 2 | 2 | 9 |

- **Breadcrumb trong nội dung làm loãng embedding (v1 → v2):** mọi chunk của Điều 16 đều bắt đầu bằng cùng tiền tố "Điều 16. Nghỉ học tạm thời và tự nguyện thôi học › …" nên chúng giống nhau hơn và chunk định nghĩa (Khoản 1) lấn át chunk chứa thời hạn (Khoản 2) ở Q3. Đưa breadcrumb sang `metadata["section"]` giữ được lợi ích trích dẫn mà không trả giá này.
- **Gộp Khoản ngắn (`min_chars=250`) cứu Q2:** không gộp, chunk "Khoản 3. Buộc thôi học" đứng riêng, ngắn, bị các chunk "tự nguyện thôi học" của Điều 16 đẩy khỏi top-3; gộp Khoản 2 + Khoản 3 của Điều 19 lại thì chunk có thêm ngữ cảnh "cảnh báo học tập" và lên top-2.
- `max_chars=500` cho kết quả bằng nhau (9) nhưng nhiều chunk hơn (43 so với 36) mà không thêm điểm nào; nhóm giữ 900 để một Khoản liệt kê điều kiện (ví dụ 4 điều kiện tốt nghiệp ở Điều 14 Khoản 3) luôn nằm trong **một** chunk khi agent đọc.

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Về điểm truy xuất thuần, bốn chiến lược chỉ chênh nhau 1 điểm (8–9/10) vì corpus nhỏ và 3/5 câu hỏi có từ khoá rất đặc trưng; điểm thắng của hai chiến lược nhận biết Khoản (Section của Hùng, Recursive tinh chỉnh của Hưởng) đều đến từ câu khó Q2/Q3, nơi chunk phải chứa **đủ câu dẫn + toàn bộ Khoản**. Nhóm chọn **`SectionChunker` v2 làm chiến lược chính** vì: (1) điểm cao nhất và là chiến lược duy nhất đưa Q3 lên top-1 nhờ giữ nguyên khối Khoản 2 Điều 16; (2) ít chunk nhất (36 so với 45–49) và 100% chunk là một quy định trọn vẹn → agent đọc đúng một Khoản, không phải ghép mảnh; (3) `metadata["section"]` cho phép trả lời kèm "theo Điều 16 Khoản 2" — đúng cách người dùng quy chế cần. Bài học chung của nhóm: với văn bản quy chế, **ranh giới ngữ nghĩa (Khoản) quan trọng hơn kích thước chunk**, và ngữ cảnh phụ (breadcrumb) nên đi vào metadata chứ không nhồi vào nội dung được embed.

**Failure case còn tồn tại ở mọi chiến lược (đưa vào mục 3.5 / phân tích lỗi):** Q2 "Khi nào sinh viên bị buộc thôi học?" — top-1 của cả 4 chiến lược đều rơi vào Điều 16 (Khoản 4 "khi chế độ nghỉ tạm thời có hiệu lực…" với Section/Recursive, Khoản 5 "Tự nguyện thôi học" với Sentence) chứ không phải Khoản 3 Điều 19 "Buộc thôi học", vì embedding đa ngữ MiniLM bám vào cụm "thôi học"/"nghỉ học" chứ không phân biệt "buộc" với "tự nguyện". Đây là giới hạn của embedder chứ không phải chunking; hướng cải thiện là lọc `metadata_filter={"category": "academic-warning"}` hoặc thêm trường `keywords` khi ingest.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên được đăng ký tối đa bao nhiêu tín chỉ trong học kỳ hè? | **Tối đa 8 TC** trong học kỳ hè (học kỳ chính: tối đa 24 TC, tối thiểu 12 TC nếu không bị cảnh báo học tập). | `dieu-10-dang-ky-hoc-tap` — Điều 10, Khoản 2, điểm a |
| 2 | Khi nào sinh viên bị buộc thôi học? | Khi thuộc một trong hai trường hợp: (a) bị **cảnh báo học tập mức 3 lần thứ hai liên tiếp**; (b) học chậm tiến độ quá thời gian cho phép hoặc không còn đủ khả năng tốt nghiệp trong thời gian cho phép (khoản 3 Điều 3). | `dieu-19-20-canh-bao-hoc-tap-va-buoc-thoi-hoc` — Điều 19, Khoản 3 |
| 3 | Nghỉ học tạm thời vì lý do cá nhân thì được nghỉ tối đa bao lâu? | Với lý do khác ốm đau/thai sản/tai nạn/lực lượng vũ trang: sinh viên phải đã học ít nhất một học kỳ; **nghỉ tối đa 04 học kỳ chính**, thời gian này tính vào thời gian học chậm tiến độ; nghỉ quá 04 học kỳ chính sẽ bị xét buộc thôi học. | `dieu-16-nghi-hoc-tam-thoi-va-thoi-hoc` — Điều 16, Khoản 2, điểm d |
| 4 | Điều kiện để được xét công nhận tốt nghiệp là gì? | Đủ 4 điều kiện: (a) hoàn thành đầy đủ học phần của CTĐT trong thời gian quy định, kể cả GDTC và GDQP-AN; (b) **đạt chuẩn ngoại ngữ đầu ra**; (c) điểm trung bình tích lũy toàn khóa **≥ 2,0**; (d) không bị truy cứu trách nhiệm hình sự / không đang bị kỷ luật đình chỉ học tập. | `dieu-14-15-dang-ky-tot-nghiep-va-hang-tot-nghiep` — Điều 14, Khoản 3 |
| 5 | Điểm ĐATN được tính từ điểm quá trình và điểm cuối kỳ theo trọng số nào? **(chạy với `metadata_filter={"audience": "student"}`)** | Điểm ĐATN = **0,5 × điểm quá trình + 0,5 × điểm cuối kỳ**. | `dieu-13-dieu-kien-lam-do-an-tot-nghiep` (audience = student) — Điều 13, Khoản 2, điểm a. *Không lọc, top-1 là `dieu-13-cham-diem-do-an-tot-nghiep` (audience = faculty, hướng dẫn chấm cho hội đồng) — với Recursive cả top-3 đều là tài liệu faculty.* |

**Tính đa dạng của bộ câu hỏi:** Q1 hỏi một con số; Q2 hỏi điều kiện "khi nào" (nhiều trường hợp); Q3 hỏi thời hạn kèm điều kiện áp dụng; Q4 hỏi danh sách điều kiện; Q5 hỏi công thức và bắt buộc lọc `audience`. Năm câu rơi vào 5 tài liệu khác nhau (Điều 10, 19, 16, 14, 13). Mọi gold answer đều trích nguyên văn từ corpus, không suy đoán.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

Mỗi thành viên chạy trên **code cá nhân** của mình (chi tiết top-3 và câu trả lời trong `REPORT_CANHAN.md` từng người):
- **Hùng** — `SectionChunker` v2 (36 chunk), LLM thật `gpt-4o-mini`.
- **Hưởng** — `RecursiveChunker(600, "\n## ")` (50 chunk), LLM `demo_llm` của `main.py` (chỉ lặp lại prompt, không sinh câu trả lời) → phần "agent trả lời đúng" của Hưởng không đạt được 2 điểm dù retrieval đúng; Hưởng ghi riêng "điểm truy xuất có thể trả lời" = 7/10.

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Tối đa bao nhiêu TC trong học kỳ hè? | Hoà — cả hai top-1 (Section 0,716 / Recursive 0,689) | Hùng ✅ top-1 · Hưởng ✅ top-1 | Agent Hùng: "tối đa 8 tín chỉ… [1]" ✔. Điểm: Hùng **2**, Hưởng **1** (retrieval 2 nhưng demo_llm không trả lời) |
| 2 | Khi nào bị buộc thôi học? | **Section** — chunk Điều 19 K3 trọn vẹn ở top-2; Recursive của Hưởng chỉ có chunk *tiêu đề* Điều 19 ở top-2 | Hùng ✅ top-2 · Hưởng ❌ (top-3 không chunk nào chứa đáp án) | Cả hai top-1 đều rơi vào Điều 16 "tự nguyện thôi học". Agent Hùng (`gpt-4o-mini`) tự bỏ [1], trích [2] và trả lời đúng. Điểm: Hùng **1**, Hưởng **0** |
| 3 | Nghỉ học tạm thời vì lý do cá nhân tối đa bao lâu? | **Section** — giữ trọn Khoản 2 Điều 16 (mảnh d–đ kèm câu dẫn) ở top-1; Recursive cắt Khoản 2 thành 2 mảnh, mảnh chứa điểm d) tụt top-2 | Hùng ✅ top-1 · Hưởng ✅ top-2 | Agent Hùng: "04 học kỳ chính… tính vào thời gian học chậm tiến độ [1]" ✔. Điểm: Hùng **2**, Hưởng **1** |
| 4 | Điều kiện xét công nhận tốt nghiệp? | Hoà — cả hai top-1, chunk chứa đủ 4 điểm a–d | Hùng ✅ top-1 · Hưởng ✅ top-1 | Agent Hùng liệt kê nguyên văn 4 điều kiện ✔. Điểm: Hùng **2**, Hưởng **1** |
| 5 | Trọng số điểm ĐATN? *(filter `audience=student`)* | Hoà — cả hai top-1 **sau khi lọc** | Hùng ✅ top-1 · Hưởng ✅ top-1 | Không lọc: Hùng top-1 là doc faculty (0,62 > 0,53); Hưởng **cả top-3** là doc faculty. Agent Hùng: "0,5 … và 0,5 … [1]" ✔. Điểm: Hùng **2**, Hưởng **1** |
| | **Tổng (rubric 2/1/0)** | Section 9/10 · Recursive 4/10 (retrieval 7/10) | Hùng 5/5 · Hưởng 4/5 | Khoảng cách 9 vs 4 chủ yếu do **LLM**, không phải chunking: cùng retrieval Hưởng nếu có LLM thật sẽ ≈ 7/10 |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Có, ở Q5 (`audience`) — và đo thêm thấy có ở cả Q2 (`category`).** Ở Q5, không lọc thì tài liệu hướng dẫn chấm cho giảng viên (`audience=faculty`) chiếm top-1 với cả hai chiến lược (với Recursive chiếm cả top-3); lọc `audience=student` đưa đúng tài liệu sinh viên lên top-1. Hưởng chỉ ra chính xác một điểm tinh tế: chunk faculty cũng chứa "0,5/0,5", nên ở câu này filter đổi **nguồn trích dẫn đúng đối tượng** chứ chưa đổi đáp án số — đó vẫn là đúng yêu cầu L3A ("tránh lấy tài liệu dành cho đối tượng khác"), nhưng nếu muốn filter quyết định *độ đúng* thì corpus cần một cặp student/faculty có nội dung khác nhau thật sự. Với Q2, nhóm đo thử `metadata_filter={"category": "academic-warning"}` (trường đã có sẵn trong schema): chunk "Buộc thôi học" lên **top-1 với 3/4 chiến lược** (Section 0,649; Recursive 0,658; Sentence 0,632), chỉ Fixed vẫn miss vì chunk cắt giữa câu. Bài học: filter theo `category` giải quyết được lỗi nhầm chủ đề mà embedder không tự phân biệt — nhưng cần một bước định tuyến (router) từ câu hỏi → category, chưa có trong agent hiện tại.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Ranh giới Khoản quan trọng hơn kích thước chunk.** Baseline `fixed_size` cắt giữa câu ở 77% chunk; hai chiến lược nhận biết `## Khoản` (Section, Recursive có separator `"\n## "`) là hai chiến lược duy nhất đưa được câu khó Q2 vào top-3. Nhưng "nhận biết Khoản" chưa đủ: bản Recursive của Hưởng sinh chunk chỉ có tiêu đề, và Q2 rớt về 0 — chunk phải là *một quy định trọn vẹn* (câu dẫn + các điểm a/b/c).
> 2. **Ngữ cảnh phụ nên đi vào metadata, không nhồi vào nội dung embed.** Ablation `SectionChunker` v1 → v2: ghép breadcrumb "Điều X › Khoản Y" vào nội dung làm mọi chunk cùng Điều giống nhau hơn và Q3 tụt hạng; chuyển sang `metadata["section"]` vừa giữ được trích dẫn vừa tăng điểm (8 → 9).
> 3. **Filter metadata là công cụ sửa lỗi ngữ nghĩa của embedder.** MiniLM không phân biệt "buộc thôi học" với "tự nguyện thôi học" (Q2) và xếp hướng dẫn cho giảng viên trên quy định cho sinh viên (Q5). `audience=student` sửa Q5; `category=academic-warning` sửa Q2 cho 3/4 chiến lược. Demo live: chạy `python scripts/compare_strategies.py --llm` và bật/tắt filter ở Q5.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng 10 tài liệu, cùng 5 câu hỏi, cùng embedder, nhưng điểm truy xuất dao động 7–9/10 chỉ vì cách cắt; và khi tính cả agent thì 4 với 9 — khoảng cách lớn nhất không đến từ chunking mà từ việc **có LLM thật hay không** (Hưởng chạy `demo_llm` nên mất 1 điểm ở mỗi câu retrieval đúng). Hai bản `RecursiveChunker` cùng tham số nhưng khác một chi tiết cài đặt (separator gắn vào cuối hay đầu section) cho 45 và 50 chunk và lệch 1 điểm — nhắc nhóm rằng **so sánh chiến lược phải so trên cùng một cài đặt hoặc ghi rõ khác biệt**, không chỉ so tên chiến lược. Cuối cùng, câu hỏi khó (Q2) mới phân biệt được chiến lược; ba câu dễ ai cũng 2 điểm nên không nói lên gì.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> (1) **Thiết kế corpus để filter có ý nghĩa thật:** thêm ít nhất một cặp tài liệu student/faculty (hoặc staff) có nội dung *khác nhau* về cùng chủ đề — ví dụ quy trình phúc khảo cho sinh viên và quy trình chấm phúc khảo cho giảng viên — để `audience` quyết định độ đúng chứ không chỉ nguồn trích dẫn. (2) **Gán `keywords`/`aliases` khi ingest** ("ĐATN" ↔ "đồ án tốt nghiệp", "buộc thôi học") vì Q5 có score thấp nhất (0,53) do câu hỏi dùng viết tắt. (3) **Chốt bộ câu hỏi và tiêu chí chấm (chuỗi gold phải nằm trong *một* chunk) trước khi ai đo gì**, và mỗi người ghi rõ số chunk + bản cài đặt để kết quả đối chiếu được — điều nhóm chỉ làm được ở lần chạy thứ hai.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 — 10 tài liệu một nguồn công khai, metadata đầy đủ; trừ 1 vì chỉ có 1 tài liệu faculty nên filter `audience` mới đổi nguồn chứ chưa đổi đáp án |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 — 2 chiến lược khác nhau + baseline, có ablation và giải thích; trừ 1 vì bản Recursive của hai người không đồng nhất |
| Chất lượng truy xuất (Retrieval Quality) | 7 / 10 — Section 9/10 với LLM thật; Recursive 7/10 retrieval nhưng 4/10 theo rubric vì chưa dùng LLM thật |
| Thuyết trình (Demo) | 4 / 5 — có script chạy live và 3 insight; chưa tập trình bày |
| **Tổng phần nhóm** | **34 / 40** |
