# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Văn Hưởng
**Nhóm:** G35
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

Hai vector biểu diễn văn bản có hướng gần nhau, nên hai văn bản có khả năng cùng chủ đề hoặc cùng ý nghĩa. Điểm cosine đo góc giữa các vector, nằm trong khoảng từ -1 đến 1; điểm cao không tự bảo đảm hai câu hoàn toàn tương đương.

**Ví dụ có độ tương tự CAO:**

- Câu A: "Sinh viên được đăng ký tối đa 8 tín chỉ trong học kỳ hè."
- Câu B: "Kỳ học mùa hè chỉ cho phép người học ghi danh nhiều nhất tám tín chỉ."
- Tại sao tương đồng: Hai câu dùng nhiều từ khác nhau (`sinh viên`/`người học`, `đăng ký`/`ghi danh`, `tối đa`/`nhiều nhất`) nhưng cùng nói về giới hạn 8 tín chỉ của học kỳ hè. MiniLM đa ngữ cục bộ cho cosine **0,8766** trên cặp này.

**Ví dụ có độ tương tự THẤP:**

- Câu A: "Thư viện mở cửa cuối tuần."
- Câu B: "Đồ án tốt nghiệp có điểm quá trình và điểm cuối kỳ."
- Tại sao khác: Một câu nói về lịch phục vụ thư viện, câu kia nói về cách tính điểm đồ án. Cùng MiniLM ở trên cho cosine **0,1946**.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

Cosine tập trung vào hướng của vector, nên độ dài vector ít chi phối phép so sánh hơn khoảng cách Euclid. Nếu mọi embedding đều được chuẩn hóa về độ dài 1 thì hai cách xếp hạng tương đương; lợi thế này chủ yếu rõ khi độ dài vector khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

Số chunk = `ceil((10.000 - 50) / (500 - 50)) = ceil(9.950 / 450) = 23`. Chạy `len(FixedSizeChunker(chunk_size=500, overlap=50).chunk("a" * 10000))` cũng trả **23**; chunk cuối dài 100 ký tự.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

Khi overlap = 100, số chunk là `ceil((10.000 - 100) / (500 - 100)) = ceil(9.900 / 400) = 25`, tăng 2 chunk; chạy lại `FixedSizeChunker` cũng trả **25**. Overlap lớn hơn giúp thông tin nằm sát ranh giới ít bị tách mất ngữ cảnh, nhưng tăng lượng dữ liệu lưu trữ và chi phí truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

Hàm dùng biểu thức chính quy `(?<=[.!?] )|(?<=\.\n)` để tách sau `. `, `! `, `? ` hoặc dấu chấm trước xuống dòng. Mỗi phần được `strip()`, bỏ phần rỗng rồi gom tối đa `max_sentences_per_chunk` câu; tham số này được chặn tối thiểu là 1 và văn bản rỗng trả về danh sách rỗng.

Giới hạn còn lại: chữ viết tắt theo sau khoảng trắng như `TS. Nguyễn` có thể bị nhận nhầm là hết câu. Số thập phân viết chuẩn như `3.14` không bị cắt vì regex yêu cầu khoảng trắng hoặc xuống dòng sau dấu chấm; dữ liệu có khoảng trắng bất thường như `3. 14` vẫn có thể bị tách sai.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

Hàm `_split` thử các dấu phân cách theo thứ tự `\n\n`, `\n`, `. `, dấu cách rồi đến tách cứng; các đoạn vừa kích thước được ghép lại, đoạn quá dài được xử lý đệ quy bằng dấu phân cách ưu tiên tiếp theo. Trường hợp cơ sở là đoạn có độ dài không quá `chunk_size`; nếu hết dấu phân cách thì tách theo đúng giới hạn ký tự.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

`add_documents` chuyển mỗi `Document` thành bản ghi gồm `id`, `content`, `metadata` và embedding rồi thêm vào danh sách trong bộ nhớ. `search` nhúng câu hỏi, lấy tích vô hướng của vector câu hỏi với từng embedding, sắp xếp điểm giảm dần và trả tối đa `top_k` bản ghi; backend mặc định là `MockEmbedder` để bài kiểm thử chạy ổn định.

`add_documents` không tự chia văn bản: tôi gọi `Chunker.chunk()` trước, rồi tạo một `Document` cho từng chunk, nên số bản ghi tăng đúng bằng số `Document` đưa vào. MiniLM và mock đều trả vector đã chuẩn hóa; với các vector này, tích vô hướng bằng cosine similarity.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

`search_with_filter` chọn các bản ghi có mọi cặp khóa–giá trị metadata trùng bộ lọc trước khi tính điểm và xếp hạng. `delete_document` loại tất cả bản ghi có `metadata.doc_id` bằng mã tài liệu được yêu cầu và trả `True` khi thực sự có bản ghi bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

`answer` lấy tối đa `top_k` chunk, đánh số `[1]`, `[2]`... kèm `doc_id`, `chunk_id` và nguồn rồi ghép vào prompt cùng câu hỏi. Prompt yêu cầu LLM chỉ dùng ngữ cảnh, nói rõ khi thiếu thông tin và trích dẫn số chunk; khi kho rỗng hoặc không có kết quả thì trả thông báo phù hợp. Chất lượng câu trả lời vẫn phụ thuộc vào chunk truy xuất và hàm `llm_fn` được truyền vào.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
pytest tests/ -v
python3.13 main.py "Chunking là gì?"
================================================================ test session starts ================================================================
platform darwin -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0 -- /Library/Frameworks/Python.framework/Versions/3.13/bin/python3
cachedir: .pytest_cache
rootdir: /Users/huongne/K4-L3A-Data-Foundations
plugins: anyio-4.12.1
collected 42 items                                                                                                                                  

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                                                         [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                                                  [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                                                           [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                                                            [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                                                 [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                                                 [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                                                       [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                                                        [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                                                      [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                                                        [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                                                        [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                                                   [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                                               [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                                                         [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                                                [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                                                    [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                                              [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                                                    [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                                                        [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                                                          [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                                                            [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                                                  [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                                                       [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                                                         [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                                             [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                                                          [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                                                   [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                                                  [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                                             [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                                                         [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                                                    [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                                                        [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                                              [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                                                        [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED                                     [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                                                   [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                                                  [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED                                      [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                                                 [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED                                          [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED                                [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED                                    [100%]

================================================================ 42 passed in 0.03s =================================================================
=== Manual File Test ===
Accepted file types: .md, .txt
Input file list:
  - data/python_intro.txt
  - data/vector_store_notes.md
  - data/rag_system_design.md
  - data/customer_support_playbook.txt
  - data/chunking_experiment_report.md
  - data/vi_retrieval_notes.md
Skipping missing file: data/customer_support_playbook.txt

Loaded 5 documents
  - python_intro: data/python_intro.txt
  - vector_store_notes: data/vector_store_notes.md
  - rag_system_design: data/rag_system_design.md
  - chunking_experiment_report: data/chunking_experiment_report.md
  - vi_retrieval_notes: data/vi_retrieval_notes.md

Embedding backend: mock embeddings fallback

Stored 5 documents in EmbeddingStore

=== EmbeddingStore Search Test ===
Query: Chunking là gì?
1. score=0.150 source=data/rag_system_design.md
   content preview: # Thiết kế Hệ thống RAG cho Trợ lý Tri thức Nội bộ  ## Bối cảnh  Một nhóm sản phẩm muốn một trợ lý có thể trả lời các câ...
2. score=0.027 source=data/python_intro.txt
   content preview: Python là một ngôn ngữ lập trình bậc cao được sử dụng rộng rãi cho tự động hóa, dịch vụ backend, phân tích dữ liệu, tính...
3. score=0.025 source=data/chunking_experiment_report.md
   content preview: # Báo cáo Thử nghiệm Chia nhỏ văn bản (Chunking Experiment Report)  ## Mục đích  Báo cáo này tóm tắt một thử nghiệm nhỏ ...

=== KnowledgeBaseAgent Test ===
Question: Chunking là gì?
Agent answer:
[DEMO LLM] Generated answer from prompt preview: Bạn chỉ được trả lời dựa trên ngữ cảnh bên dưới. Không bịa thông tin. Nếu ngữ cảnh không đủ, nói rõ là không tìm thấy. Khi dùng một đoạn, trích dẫn số chunk tương ứng, ví dụ [1] hoặc [2].  Ngữ cảnh: [1] (nguồn: rag_system_design) # Thiết kế Hệ thống RAG cho Trợ lý Tri thức Nội bộ  ## Bối cảnh  Một nhóm sản phẩm muốn một trợ lý có thể trả lời các câu hỏi về việc giới thiệu (onboarding), quy trình t...
```

**Số lượng bài test vượt qua (pass):** 42 / 42. Kiểm tra bằng Python 3.13.7 và pytest 9.1.1 ngày 19/09/2026.

Checkpoint riêng `pytest tests/ -k "Chunker or Similarity or Compare" -v`: **23 passed, 19 deselected**.

Chạy tiếp `EMBEDDING_PROVIDER=mock .venv/bin/python main.py "Chunking là gì?"`: nạp 5 tài liệu, lưu 5 bản ghi và chạy đến phần agent; dòng `Skipping missing file: data/customer_support_playbook.txt` là thông báo về file mẫu không có trong repo.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Tôi dùng `compute_similarity(_mock_embed(câu A), _mock_embed(câu B))`; để đối chiếu nhãn, quy ước điểm từ 0,30 trở lên là **cao**, dưới 0,30 là **thấp**. Đây là ngưỡng minh họa, không phải ngưỡng đánh giá chuẩn của lab.

### Bộ cặp từ quy định đào tạo có điểm cao hơn (thử nghiệm bổ sung)

Các cặp sau được diễn đạt từ quy định đào tạo đã thu thập và **được chọn sau khi khảo sát điểm**. Cột dự đoán thể hiện nhận định theo nội dung, không phải dự đoán độc lập trước khi chạy.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
| --- | ----- | ----- | ------- | ------------ | ----- |
| 1 | Giới hạn tín chỉ học kỳ chính của sinh viên không bị cảnh báo là bao nhiêu? | Sinh viên không thuộc diện cảnh báo được đăng ký nhiều nhất bao nhiêu tín chỉ? | Cao | 0,3802 | Có |
| 2 | Sinh viên phải nộp đơn xin trở lại học chậm nhất một tuần trước kỳ mới. | Trước kỳ học mới một tuần, sinh viên cần nộp đơn xin trở lại học theo quy định. | Cao | 0,3274 | Có |
| 3 | Đạt trình độ năm thứ hai của chương trình thứ nhất là điều kiện đăng ký chương trình thứ hai. | Theo quy chế đào tạo, sinh viên chỉ được học chương trình thứ hai khi đã được xếp trình độ năm hai. | Cao | 0,3666 | Có |
| 4 | Theo quy chế đào tạo, nếu một thành viên hội đồng cho dưới 5, điểm bảo vệ tối đa là 4,9. | Một điểm chấm dưới 5 từ hội đồng làm điểm bảo vệ bị giới hạn ở 4,9. | Cao | 0,3081 | Có |
| 5 | ĐHBK Hà Nội xét tốt nghiệp ba đợt mỗi năm. | Theo quy chế đào tạo, số đợt xét tốt nghiệp hằng năm của ĐHBK Hà Nội là ba. | Cao | 0,3488 | Có |

### Bộ dự đoán độc lập ban đầu

Các dự đoán dưới đây được ghi trước khi tính điểm cho bộ cặp đầu tiên; đây là phần đối chiếu hợp lệ với yêu cầu dự đoán trước khi chạy.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
| --- | ----- | ----- | ------- | ------------ | ----- |
| 1 | Sinh viên đăng ký học phần cho học kỳ mới. | Sinh viên đăng ký học phần cho học kỳ mới. | Cao | 1,0000 | Có |
| 2 | Sinh viên chọn môn học cho học kỳ tiếp theo. | Người học đăng ký học phần ở kỳ sau. | Cao | -0,0218 | Không |
| 3 | Sinh viên phải được cho phép nghỉ học tạm thời. | Nghỉ học tạm thời cần quyết định của nhà trường. | Cao | -0,1355 | Không |
| 4 | Thư viện mở cửa cuối tuần. | Đồ án tốt nghiệp có điểm quá trình và điểm cuối kỳ. | Thấp | 0,0441 | Có |
| 5 | Python là ngôn ngữ lập trình. | Sinh viên cần nộp đơn trở lại học trước kỳ mới. | Thấp | -0,1304 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

Hai cặp gần nghĩa trong bộ độc lập (2 và 3) lại có điểm âm. `MockEmbedder` tạo vector giả lập từ mã băm MD5 của toàn bộ câu, nên thay đổi cách diễn đạt có thể làm vector khác hẳn. Điểm cao của bộ bổ sung là do chọn cặp sau khi đo, không chứng minh mô hình hiểu ngữ nghĩa tiếng Việt. Đánh giá retrieval thực tế cần embedding đa ngữ và cùng một bộ câu hỏi được chốt trước khi đo.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Tôi chạy đúng 5 câu hỏi chung của G35 trên 10 tài liệu trong `data/quy-dinh-dao-tao/` (50 chunk). Cấu hình: `RecursiveChunker(separators=["\n## ", "\n\n", "\n", ". ", " ", ""], chunk_size=600)`, `top_k=3`, embedding cục bộ `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 chiều). Riêng Q5 dùng `metadata_filter={"audience": "student"}` cho cả truy xuất lẫn ngữ cảnh truyền vào agent. Sau khi cài phụ thuộc và tải mô hình vào cache, chạy lại bằng `.venv/bin/python scripts/run_g35_benchmark.py`.

### Kết quả top-3

| # | Câu hỏi chung của G35 | Top-1: chunk ID (score) | Top-2: chunk ID (score) | Top-3: chunk ID (score) |
| --- | --- | --- | --- | --- |
| 1 | Sinh viên được đăng ký tối đa bao nhiêu tín chỉ trong học kỳ hè? | `dieu-10-dang-ky-hoc-tap::chunk_005` (0,6885) | `dieu-19-20-canh-bao-hoc-tap-va-buoc-thoi-hoc::chunk_004` (0,6228) | `dieu-10-dang-ky-hoc-tap::chunk_006` (0,6195) |
| 2 | Khi nào sinh viên bị buộc thôi học? | `dieu-16-nghi-hoc-tam-thoi-va-thoi-hoc::chunk_006` (0,7248) | `dieu-19-20-canh-bao-hoc-tap-va-buoc-thoi-hoc::chunk_001` (0,6864) | `dieu-16-nghi-hoc-tam-thoi-va-thoi-hoc::chunk_005` (0,6663) |
| 3 | Nghỉ học tạm thời vì lý do cá nhân thì được nghỉ tối đa bao lâu? | `dieu-16-nghi-hoc-tam-thoi-va-thoi-hoc::chunk_001` (0,7668) | `dieu-16-nghi-hoc-tam-thoi-va-thoi-hoc::chunk_003` (0,7596) | `dieu-16-nghi-hoc-tam-thoi-va-thoi-hoc::chunk_005` (0,7286) |
| 4 | Điều kiện để được xét công nhận tốt nghiệp là gì? | `dieu-14-15-dang-ky-tot-nghiep-va-hang-tot-nghiep::chunk_002` (0,7368) | `dieu-14-15-dang-ky-tot-nghiep-va-hang-tot-nghiep::chunk_003` (0,7216) | `dieu-14-15-dang-ky-tot-nghiep-va-hang-tot-nghiep::chunk_001` (0,6873) |
| 5 | Điểm ĐATN được tính từ điểm quá trình và điểm cuối kỳ theo trọng số nào? (`audience=student`) | `dieu-13-dieu-kien-lam-do-an-tot-nghiep::chunk_001` (0,4873) | `dieu-10-dang-ky-hoc-tap::chunk_008` (0,4758) | `dieu-12-danh-gia-ket-qua-hoc-tap::chunk_002` (0,4731) |

### Đối chiếu với câu trả lời chuẩn và tự chấm

`KnowledgeBaseAgent` trong lần chạy này được truyền `demo_llm` của `main.py`. Hàm đó trả chuỗi bắt đầu bằng `[DEMO LLM] Generated answer from prompt preview:` rồi lặp lại 400 ký tự đầu của prompt; **nó không tạo câu trả lời nội dung**. Bảng dưới ghi đúng kết quả agent và chấm theo `docs/SCORING.md`: 1 điểm khi top-3 có chunk liên quan nhưng câu trả lời agent thiếu, 0 điểm nếu không có chunk liên quan.

| # | Câu trả lời chuẩn kiểm chứng từ corpus | Câu trả lời thực tế của agent | Chunk liên quan | Điểm / 2 |
| --- | --- | --- | --- | ---: |
| 1 | Tối đa **8 TC** trong học kỳ hè (Điều 10 khoản 2a). | Chỉ lặp phần đầu prompt, không nêu 8 TC. | Top-1, đúng khoản 2a. | **1** |
| 2 | Bị cảnh báo mức 3 lần thứ hai liên tiếp, hoặc học chậm tiến độ quá thời gian cho phép/không còn khả năng tốt nghiệp đúng hạn (Điều 19 khoản 3). | Chỉ lặp phần đầu prompt; preview nêu `doc_id` của đoạn **tự nguyện thôi học** ở hạng 1, không trả lời điều kiện buộc thôi học. | Top-2 thuộc Điều 19 nhưng chỉ là chunk tiêu đề, không chứa hai điều kiện; cả top-3 đều thiếu đáp án. | **0** |
| 3 | Nghỉ tối đa **04 học kỳ chính** vì lý do cá nhân và thời gian đó tính vào thời gian học chậm tiến độ (Điều 16 khoản 2d). | Chỉ lặp phần đầu prompt, không nêu 04 học kỳ chính. | Top-2, đúng điểm d; top-1 cùng tài liệu nhưng thiếu đáp án. | **1** |
| 4 | Hoàn thành học phần CTĐT trong thời hạn (kể cả Giáo dục thể chất và Giáo dục quốc phòng–an ninh); đạt chuẩn ngoại ngữ; CPA toàn khóa từ **2,0**; tại thời điểm xét không bị truy cứu trách nhiệm hình sự hoặc không đang bị đình chỉ học tập (Điều 14 khoản 3a–d). | Chỉ lặp phần đầu prompt, không liệt kê 4 điều kiện. | Top-1, chứa đủ 4 điểm a–d. | **1** |
| 5 | Điểm quá trình **0,5** và điểm cuối kỳ **0,5** (Điều 13 khoản 2a, bản `audience=student`). | Chỉ lặp phần đầu prompt, không nêu hai trọng số. | Top-1, đúng điểm a sau khi lọc. | **1** |
| **Tổng** | | | | **4 / 10** |

**Bao nhiêu câu hỏi có chunk chứa đủ đáp án trong top-3?** **4 / 5**; trong top-1: **3 / 5**. Q2 minh họa vì sao chỉ kiểm `doc_id` sẽ tính nhầm một chunk tiêu đề thành câu trả lời. Điểm 4/10 còn phản ánh giới hạn của agent demo.

### Kiểm tra nội dung chunk ở CP6

Tôi chạy MiniLM, cùng năm câu và cấu hình Recursive 600 qua `scripts/evaluate_cp6.py`; log chi tiết nằm ở `report/ket_qua_benchmark.txt`. Script khai báo cụm đặc trưng từ văn bản nguồn cho từng đáp án và kiểm tra **cùng một chunk** có đủ cụm, đồng thời thuộc đúng `doc_id`. Bảng trên dùng ID dạng `file::chunk_001`, còn log CP6 dùng `file#0`; chúng chỉ khác cách đánh số (1-based và 0-based), nội dung và thứ hạng trùng nhau.

| Câu | Hạng đầu tiên của đúng `doc_id` | Hạng chunk đúng nguồn và đủ nội dung | Điểm truy xuất tham khảo |
|---|---:|---:|---:|
| Q1 | 1 | 1 | 2/2 |
| Q2 | 2 | Không có | 0/2 |
| Q3 | 1 | 2 | 1/2 |
| Q4 | 1 | 1 | 2/2 |
| Q5, có lọc `student` | 1 | 1 | 2/2 |
| **Tổng** | | | **7/10** |

Đây là **điểm truy xuất có thể trả lời**, không phải điểm agent theo rubric: `demo_llm` không sinh câu trả lời thật nên điểm phần agent vẫn là 4/10 như bảng trước. Nếu chấm chỉ theo `doc_id`, sẽ bỏ qua lỗi Q2: đúng tài liệu ở top-2 nhưng chunk không chứa hai điều kiện buộc thôi học. Sau khi sửa cách gắn separator `"\n## "` vào **đầu section kế tiếp**, tôi chạy lại toàn bộ; 50 chunk vẫn giữ nguyên nhưng thứ hạng và điểm thay đổi so với phép đo cũ.

A/B Q5 với Recursive: khi **không lọc**, top-3 lần lượt là ba chunk của `dieu-13-cham-diem-do-an-tot-nghiep` (`#1` 0,6761; `#2` 0,5729; `#3` 0,5712), đều mang `audience=faculty`; chunk đúng nguồn sinh viên vắng mặt. Khi **lọc `audience=student`**, `dieu-13-dieu-kien-lam-do-an-tot-nghiep#0` lên hạng 1 (0,4873). Tuy vậy, chunk faculty ở hạng 1 cũng chứa trọng số 0,5/0,5, nên filter đổi **nguồn trích dẫn**, chưa đổi đáp án số học. Bộ câu cần được nhóm điều chỉnh để kiểm tra tác động của filter lên độ đúng của câu trả lời.

### Một trường hợp thất bại và cách cải thiện

Ở Q2, cụm từ “thôi học” khiến đoạn **tự nguyện thôi học** của Điều 16 xếp hạng 1 (0,7248); chunk `dieu-19-20-canh-bao-hoc-tap-va-buoc-thoi-hoc::chunk_001` của đúng tài liệu chỉ đứng hạng 2 (0,6864) và chưa chứa điều kiện Điều 19 khoản 3. Cả top-3 đều không đủ nội dung để trả lời. Đây là lỗi xếp hạng theo chủ đề và ranh giới chunk; đề xuất thử lọc `category=academic-warning` hoặc rerank theo cụm “buộc thôi học”, rồi đo lại thay vì giả định cải thiện.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):** Chưa có ghi chép về phần demo của các thành viên khác để xác nhận nhận xét cá nhân.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                        | Điểm tự đánh giá |
| ----------------------------------------------- | ---------------- |
| Khởi động (Warm-up)                             | / 5              |
| Hướng tiếp cận của tôi (My Approach)            | / 10             |
| Hoàn thiện code (Core Implementation — tests)   | / 30             |
| Dự đoán độ tương tự (Similarity Predictions)    | / 5              |
| Kết quả truy xuất của tôi (Competition Results) | 4 / 10             |
| **Tổng phần cá nhân**                           | **/ 60**         |
