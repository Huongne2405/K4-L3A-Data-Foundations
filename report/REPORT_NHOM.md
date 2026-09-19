# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G35

**Thành viên đã xác nhận:** Nguyễn Văn Hưởng; các thành viên khác bổ sung khi nhóm chốt.

**Ngày ghi nhận kết quả:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy chế đào tạo đại học của Đại học Bách khoa Hà Nội, tập trung vào đăng ký học tập, đánh giá, tốt nghiệp và buộc thôi học.

**Tại sao nhóm chọn chủ đề này?**
Corpus có 10 tài liệu Markdown theo từng điều/khoản của cùng quy chế, phù hợp để thử truy xuất câu trả lời có dẫn nguồn. Các điều có nhiều mức và điều kiện gần nghĩa nhau, tạo trường hợp khó thực tế cho truy xuất; ví dụ “tự nguyện thôi học” ở Điều 16 và “buộc thôi học” ở Điều 19.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | `dieu-10-dang-ky-hoc-tap` | [Quy chế 5445/QĐ-ĐHBK](https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n%20Qu%E1%BB%91c%20%C4%90%E1%BA%A1t/files/DTDH_QDQC/Hoctap/QCDT_2025_5445_QD-DHBK.pdf) | Lấy 19/09/2026; bản 28/05/2025 | 3172 | `student`, `registration` |
| 2 | `dieu-11-cong-nhan-chuyen-doi-tin-chi` | Như trên | Như trên | 1412 | `student`, `credit-transfer` |
| 3 | `dieu-12-danh-gia-ket-qua-hoc-tap` | Như trên | Như trên | 2448 | `student`, `grading` |
| 4 | `dieu-13-dieu-kien-lam-do-an-tot-nghiep` | Như trên | Như trên | 491 | `student`, `graduation-thesis` |
| 5 | `dieu-13-cham-diem-do-an-tot-nghiep` | Như trên | Như trên | 970 | `faculty`, `graduation-thesis` |
| 6 | `dieu-14-15-dang-ky-tot-nghiep-va-hang-tot-nghiep` | Như trên | Như trên | 2638 | `student`, `graduation` |
| 7 | `dieu-16-nghi-hoc-tam-thoi-va-thoi-hoc` | Như trên | Như trên | 2260 | `student`, `leave-of-absence` |
| 8 | `dieu-17-chuyen-chuong-trinh-dao-tao` | Như trên | Như trên | 2081 | `student`, `program-transfer` |
| 9 | `dieu-18-hoc-cung-luc-hai-chuong-trinh` | Như trên | Như trên | 1882 | `student`, `dual-program` |
| 10 | `dieu-19-20-canh-bao-hoc-tap-va-buoc-thoi-hoc` | Như trên | Như trên | 2014 | `student`, `academic-warning` |

Số ký tự chỉ tính phần thân sau frontmatter YAML; dữ liệu nguồn và metadata nằm trong `data/quy-dinh-dao-tao/`.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | Chuỗi | `dieu-10-dang-ky-hoc-tap` | Gộp các chunk về đúng tài liệu nguồn; xoá theo file gốc. |
| `source_url`, `document_version`, `retrieved_at` | Chuỗi | `5445/QĐ-ĐHBK`, `2026-09-19` | Kiểm tra nguồn và phiên bản của câu trả lời. |
| `audience` | Chuỗi | `student`, `faculty` | Giới hạn tập ứng viên trước khi tìm kiếm. |
| `category`, `article` | Chuỗi | `academic-warning`, `19-20` | Khoanh vùng điều khoản khi truy vấn mơ hồ. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(body, chunk_size=200)` trên ba tài liệu. `body` là phần sau frontmatter YAML; độ dài và trung bình làm tròn một chữ số thập phân. Cột cuối là nhận xét cấu trúc chunk, chưa phải điểm truy xuất.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Điều 10 (3172 ký tự) | FixedSizeChunker (`fixed_size`) | 21 | 198,7 | Có thể cắt ngang câu/khoản. |
| Điều 10 | SentenceChunker (`by_sentences`) | 8 | 394,4 | Giữ dấu câu, nhưng chunk dài nhất 774 ký tự. |
| Điều 10 | RecursiveChunker (`recursive`) | 31 | 102,3 | Ưu tiên ranh giới đoạn; khá nhiều chunk ngắn. |
| Điều 16 (2260 ký tự) | FixedSizeChunker (`fixed_size`) | 15 | 197,3 | Có thể trộn hai ý qua ranh giới cố định. |
| Điều 16 | SentenceChunker (`by_sentences`) | 6 | 374,5 | Chunk dài nhất 720 ký tự. |
| Điều 16 | RecursiveChunker (`recursive`) | 24 | 94,2 | Giữ ranh giới lớn nhưng bị phân mảnh. |
| Điều 19–20 (2014 ký tự) | FixedSizeChunker (`fixed_size`) | 14 | 190,3 | Có thể mất tiêu đề khoản liên quan. |
| Điều 19–20 | SentenceChunker (`by_sentences`) | 6 | 333,3 | Chunk dài nhất 478 ký tự. |
| Điều 19–20 | RecursiveChunker (`recursive`) | 16 | 125,9 | Có thể tách phần sau khỏi heading khoản. |

Thử nghiệm bổ sung: `HeadingSectionChunker(chunk_size=600)` tách ở dòng `##`, giữ cả khoản khi vừa ngưỡng và lặp lại heading cho mọi mảnh con của khoản dài. Có thể chọn chiến lược này bằng cách đổi đúng dòng `CHUNKER = ...` trong `bench.py`.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Nguyễn Văn Hưởng**
- **Loại chiến lược:** Recursive, `separators=["\n## ", "\n\n", "\n", ". ", " ", ""]`, `chunk_size=600`.
- **Mô tả & lý do chọn:** Ưu tiên tách theo khoản Markdown và đoạn văn trước khi tách theo câu/từ. Trong `_split`, separator `"\n## "` được giữ ở **đầu section phía sau** để heading không mắc ở cuối chunk trước. Mục tiêu là giữ điều kiện và số liệu gần nhau trong top-k; phần đánh giá cá nhân ghi trong `REPORT_CANHAN.md`.
- **Code:** Cấu hình ở dòng `CHUNKER` của `bench.py`.

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

Hiện chỉ có cấu hình cá nhân của Nguyễn Văn Hưởng được xác nhận. Bảng dưới so sánh **ba cấu hình thử nghiệm** trên cùng 10 file, năm câu hỏi, MiniLM và `top_k=3`; không gán kết quả Fixed/Heading cho thành viên chưa gửi bài. Điểm là *điểm truy xuất theo nội dung* của `scripts/evaluate_cp6.py`, chưa phải điểm rubric có xác nhận câu trả lời từ LLM.

| Người / cấu hình thử nghiệm | Chiến lược (Strategy) | Điểm truy xuất tham khảo (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Thử nghiệm | FixedSize 600, overlap 50; 39 chunk | 7 | Q1, Q4, Q5 có đáp án ngay top-1. | Q2 không lấy được Điều 19; Q3 đáp án ở top-2. |
| Nguyễn Văn Hưởng | Recursive 600; 50 chunk | 7 | Q1, Q4, Q5 chứa đủ đáp án ở top-1; Q3 ở top-2. | Q2 có đúng tài liệu ở top-2 nhưng chunk không chứa điều kiện. |
| Thử nghiệm | Heading 600; 70 chunk | 7 | Q1, Q3, Q5 đúng ở top-1; heading được lặp khi section dài. | Q2 trả đúng tài liệu ở top-2 nhưng sai section, không có điều kiện trả lời. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
Sau khi sửa cách gắn `"\n## "` vào đầu section kế tiếp và chạy lại trên cả ba cấu hình, Fixed, Recursive và Heading đều đạt **7/10** về *khả năng truy xuất đủ nội dung*. Không có chiến lược thắng toàn bộ năm câu: Heading đưa đáp án Q3 lên top-1, Fixed và Recursive giữ bốn điều kiện Q4 ở top-1. Kết quả chưa đo chất lượng câu trả lời agent, vì agent demo chỉ xem trước prompt.

**Failure case cụ thể:** Q2 hỏi điều kiện *buộc thôi học*. Với Recursive của Hưởng và Heading, `dieu-19-20-canh-bao-hoc-tap-va-buoc-thoi-hoc#0` ở hạng 2 (0,6864) nên cách chấm theo `doc_id` sẽ tính là trúng; cả ba chunk top-3 đều không chứa đồng thời hai điều kiện của Điều 19 khoản 3. Đoạn “tự nguyện thôi học” của Điều 16 lại đứng hạng 1 (Recursive: 0,7248; Heading: 0,7248). Nguyên nhân là cosine ưu tiên chủ đề “thôi học”, và chunk tiêu đề cùng tài liệu gần chủ đề dù thiếu số liệu. Cách sửa đề xuất: không lập index riêng cho tiêu đề ngắn, gắn tiêu đề vào section có nội dung; hoặc lọc/rerank theo khoản 3 và cụm “buộc thôi học” rồi đánh giá lại trên cùng năm câu.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên được đăng ký tối đa bao nhiêu tín chỉ trong học kỳ hè? | 8 TC (Điều 10 khoản 2a). | `dieu-10-dang-ky-hoc-tap#4` |
| 2 | Khi nào sinh viên bị buộc thôi học? | Bị cảnh báo học tập mức 3 lần thứ hai liên tiếp; hoặc chậm tiến độ quá thời gian cho phép/không còn khả năng tốt nghiệp trong thời gian cho phép (Điều 19 khoản 3a–b). | `dieu-19-20-canh-bao-hoc-tap-va-buoc-thoi-hoc#4` |
| 3 | Nghỉ học tạm thời vì lý do cá nhân thì được nghỉ tối đa bao lâu? | 04 học kỳ chính, tính vào thời gian học chậm tiến độ (Điều 16 khoản 2d). | `dieu-16-nghi-hoc-tam-thoi-va-thoi-hoc#2` |
| 4 | Điều kiện để được xét công nhận tốt nghiệp là gì? | Hoàn thành học phần CTĐT gồm GDTC và GDQP-AN; đạt chuẩn ngoại ngữ; điểm trung bình tích lũy toàn khóa từ 2,0; tại thời điểm xét tốt nghiệp không bị truy cứu trách nhiệm hình sự hoặc không đang bị đình chỉ học tập (Điều 14 khoản 3a–d). | `dieu-14-15-dang-ky-tot-nghiep-va-hang-tot-nghiep#1` |
| 5 | Điểm ĐATN được tính từ điểm quá trình và điểm cuối kỳ theo trọng số nào? | 0,5 cho điểm quá trình và 0,5 cho điểm cuối kỳ (Điều 13 khoản 2a). | `dieu-13-dieu-kien-lam-do-an-tot-nghiep#0`, với `metadata_filter={"audience": "student"}` |

**Lưu ý về câu 5:** Đây là bộ 5 câu nhóm đã chốt trước đó. Bộ lọc `student` được áp dụng khi chạy, nhưng tài liệu `faculty` hiện cũng ghi trọng số 0,5/0,5. Vì vậy câu này chưa chứng minh rằng bộ lọc *cần thiết* để chọn giữa hai đáp án khác nhau. Nhóm cần thay câu hỏi/corpus theo đúng tiêu chí đó trước khi chấm kết quả cuối cùng; không nên ghi rằng lọc metadata đã cải thiện độ đúng cho câu này.

Bộ câu hiện có câu hỏi số liệu, điều kiện và liệt kê nhưng thiếu dạng hỏi quy trình. Một câu thay thế có thể kiểm chứng trong Điều 10 khoản 1 là “Quá trình đăng ký học tập gồm ba giai đoạn nào?” với đáp án: đăng ký học phần, đăng ký lớp chính thức, điều chỉnh đăng ký. R2 cần chốt thay câu nào để mọi thành viên dùng đúng cùng một bộ năm câu.

Chạy benchmark từ thư mục dự án sau khi cài `requirements.txt` và `requirements-local.txt` vào môi trường ảo:

```bash
source .venv/bin/activate
python bench.py
```

Lần chạy đã kiểm tra: `RecursiveChunker` nạp 50 chunk từ 10 file, in đủ top-3 của 5 câu kèm `score` và `doc_id`. Khi thử chiến lược heading, đổi **một dòng** trong `bench.py` thành `CHUNKER = HeadingSectionChunker(chunk_size=600)`. Log đầy đủ ba cấu hình, cả sáu lần chạy A/B và chuỗi kiểm chứng đáp án nằm trong `report/so_sanh_chien_luoc.txt`; log cá nhân Recursive nằm trong `report/ket_qua_benchmark.txt`.

### Tổng hợp chất lượng truy xuất của nhóm

`scripts/evaluate_cp6.py` khai báo cụm từ đặc trưng của đáp án từ từng điều khoản; chỉ xem top-3 là trả lời được khi các cụm đó có thật trong nội dung. `gold_doc_rank` cho biết hạng đầu tiên của đúng tài liệu, `answer_chunk_rank` cho biết hạng đầu tiên của chunk chứa đủ cụm dù thuộc nguồn nào, còn `source_answer_rank` đòi hỏi **đúng nguồn và đủ cụm trong cùng chunk**. Điểm tham khảo: 2 khi `source_answer_rank=1`, 1 khi ở hạng 2/3, 0 khi vắng. Theo `docs/SCORING.md`, 2 điểm chính thức còn cần **agent trả lời đúng**; `demo_llm` chưa đáp ứng điều đó.

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Giới hạn TC học kỳ hè | Fixed, Recursive, Heading đồng hạng | Có, top-1 ở cả ba | Đều chứa “tối đa 8 TC trong học kỳ hè”. |
| 2 | Buộc thôi học | Chưa có chiến lược đạt | Cả ba đều thiếu chunk đáp án | Recursive và Heading có đúng `doc_id` ở top-2 nhưng chunk không chứa hai điều kiện. |
| 3 | Nghỉ học lý do cá nhân | Heading | Có ở cả ba | Fixed và Recursive có đáp án ở top-2; Heading top-1. |
| 4 | Điều kiện công nhận tốt nghiệp | Fixed, Recursive | Có ở cả ba | Heading có đủ bốn điều kiện ở top-2. |
| 5 | Trọng số điểm ĐATN, có lọc `student` | Fixed, Recursive, Heading đồng hạng | Có, top-1 ở cả ba | A/B cho thấy thay đổi nguồn, chưa chứng minh thay đổi đáp án. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
Ở Q5, lọc `audience=student` giúp chọn đúng tài liệu hướng tới sinh viên. Với Recursive, **không lọc** thì cả top-3 đều là tài liệu `faculty`; **có lọc** thì chunk `student` chứa đáp án lên top-1. Tuy nhiên hai tài liệu đều ghi 0,5/0,5, nên bộ lọc cải thiện truy vết nguồn nhưng chưa chứng minh câu trả lời số học sẽ sai nếu bỏ lọc. Đây vẫn là tiêu chí còn phải sửa ở bộ câu hỏi/corpus.

| Chiến lược | Q5 có lọc `student`: top-1 → top-3 (score) | Q5 không lọc: top-1 → top-3 (score) | Khác biệt |
|---|---|---|---|
| Fixed 600 | `dieu-13-dieu-kien-lam-do-an-tot-nghiep#0` (0,4873) → `dieu-10-dang-ky-hoc-tap#5` (0,4774) → `dieu-12-danh-gia-ket-qua-hoc-tap#1` (0,4663) | `dieu-13-cham-diem-do-an-tot-nghiep#0` (0,6318) → `dieu-13-dieu-kien-lam-do-an-tot-nghiep#0` (0,4873) → `dieu-10-dang-ky-hoc-tap#5` (0,4774) | Nguồn student từ hạng 2 lên 1. |
| Recursive 600 | `dieu-13-dieu-kien-lam-do-an-tot-nghiep#0` (0,4873) → `dieu-10-dang-ky-hoc-tap#7` (0,4758) → `dieu-12-danh-gia-ket-qua-hoc-tap#1` (0,4731) | `dieu-13-cham-diem-do-an-tot-nghiep#1` (0,6761) → `#2` (0,5729) → `#3` (0,5712), đều thuộc `dieu-13-cham-diem-do-an-tot-nghiep` | Không lọc: nguồn student vắng khỏi top-3. |
| Heading 600 | `dieu-13-dieu-kien-lam-do-an-tot-nghiep#2` (0,6806) → `dieu-10-dang-ky-hoc-tap#9` (0,4758) → `dieu-12-danh-gia-ket-qua-hoc-tap#2` (0,4731) | `dieu-13-dieu-kien-lam-do-an-tot-nghiep#2` (0,6806) → `dieu-13-cham-diem-do-an-tot-nghiep#1` (0,6761) → `dieu-13-cham-diem-do-an-tot-nghiep#3` (0,6113) | Top-1 không đổi, hai slot sau đổi. |

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

- Q2 với Recursive của Hưởng và Heading: đúng tài liệu ở top-2 nhưng cả top-3 thiếu hai điều kiện buộc thôi học; kiểm `doc_id` một mình cho kết luận sai.
- Q5: filter cải thiện nguồn dẫn, đặc biệt với Recursive; đáp án 0,5/0,5 không đổi vì cả hai nhóm tài liệu đều ghi giống nhau.
- MiniLM được dùng cho cả ba chiến lược, vì `MockEmbedder` không biểu diễn ngữ nghĩa; Fixed/Recursive/Heading lần lượt nạp 39/50/70 chunk.

**Bài học rút ra khi so sánh trong nhóm:**
Trên cùng corpus và embedder, cả ba cấu hình đều thiếu đáp án Q2 trong top-3, dù Recursive và Heading đã lấy được đúng tài liệu. Khi một đoạn đúng nguồn nhưng thiếu điều kiện vẫn được xếp cao, cần xem nội dung từng chunk và khả năng trả lời trước khi gán điểm. Kết quả của thành viên khác sẽ được bổ sung khi nhóm nộp log riêng.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
Tách các mục dài theo heading nhưng tránh tạo chunk chỉ có tiêu đề; khi cắt nhỏ phải lặp tiêu đề vào mảnh con. Thiết kế lại Q5 với hai tài liệu cùng chủ đề nhưng **đáp án khác nhau theo `audience`**, rồi chạy lại A/B để chứng minh filter giúp đúng đáp án, không chỉ đúng nguồn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
