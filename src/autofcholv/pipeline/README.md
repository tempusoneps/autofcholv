# STREP Transform – Sub-steps Description

## 1. Clean

### 🎯 Mục tiêu
Loại bỏ dữ liệu nhiễu, sai lệch hoặc không hợp lệ khỏi dataset.

### 🔧 Nhiệm vụ
- Xóa duplicate records
- Xử lý missing values (drop / fill)
- Chuẩn hóa định dạng (date, number, encoding)
- Loại bỏ outliers bất thường
- Fix dữ liệu sai cấu trúc (malformed records)

### 📌 Kết quả
Dataset sạch, nhất quán, sẵn sàng cho các bước xử lý tiếp theo.

---

## 2. Validate

### 🎯 Mục tiêu
Đảm bảo dữ liệu tuân thủ schema và rule nghiệp vụ.

### 🔧 Nhiệm vụ
- Kiểm tra data type (int, float, string, datetime)
- Kiểm tra range hợp lệ (ví dụ: age > 0)
- Validate uniqueness (primary key)
- Validate foreign key (nếu có)
- Áp dụng business rules (ví dụ: trạng thái đơn hàng hợp lệ)

### 📌 Kết quả
Dataset hợp lệ về mặt kỹ thuật và nghiệp vụ.

---

## 3. Feature Engineering

### 🎯 Mục tiêu
Tạo thêm feature mới giúp model hoặc hệ thống phân tích hoạt động tốt hơn.

### 🔧 Nhiệm vụ
- Tạo derived columns (ví dụ: total_price = qty * price)
- Encoding categorical variables (one-hot, label encoding)
- Aggregation (sum, avg theo group)
- Tạo time-based features (day_of_week, month, season)
- Feature scaling (standardization / normalization)

### 📌 Kết quả
Dataset giàu thông tin hơn, tăng khả năng học của model.

---

## 4. Labeling

### 🎯 Mục tiêu
Gán nhãn cho dữ liệu để phục vụ supervised learning.

### 🔧 Nhiệm vụ
- Xác định target variable
- Gán nhãn thủ công hoặc tự động
- Mapping trạng thái sang class (vd: success = 1, fail = 0)
- Kiểm tra tính cân bằng của label (class imbalance)
- Loại bỏ sample không xác định label

### 📌 Kết quả
Dataset có target rõ ràng, sẵn sàng cho training.

---

## 5. Preprocessing

### 🎯 Mục tiêu
Chuẩn bị dữ liệu theo format phù hợp với model hoặc hệ thống downstream.

### 🔧 Nhiệm vụ
- Train/test split
- Tokenization (nếu NLP)
- Vectorization (TF-IDF, embeddings)
- Padding / Truncation (sequence data)
- Scaling final dataset
- Chuyển đổi sang format phù hợp (CSV, Parquet, Tensor format)

### 📌 Kết quả
Dataset ở dạng cuối cùng, sẵn sàng cho training hoặc inference.

---

# Tổng quan luồng xử lý

Raw Data  
→ Clean  
→ Validate  
→ Feature Engineering  
→ Labeling  
→ Preprocessing  
→ Model / Analytics