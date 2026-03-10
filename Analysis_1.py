import pandas as pd
import glob
import os

# Định nghĩa hàm tạo báo cáo kết quả
def create_amr_summary(input_dir, output_path):
    # Các tập hợp thuốc quan tâm (Bắt buộc phải có trong báo cáo)
    main_drugs_mapping = {
        'RIFAMPICIN': 'Rifampicin (RIF)',
        'ISONIAZID': 'Isoniazid (INH)',
        'FLUOROQUINOLONE': 'Levofloxacin (LEV)',
        'ETHAMBUTOL': 'Ethambutol (EMB)',
        'LINEZOLID': 'Linezolid',
        'OXAZOLIDINONE': 'Oxazolidinone',
        'BEDAQUILINE': 'Bedaquiline'
    }
    
    # Liệt kê tên thuốc theo dictionary
    main_drug_names = list(set(main_drugs_mapping.values()))
    
    # Lặp qua các file có đuôi tsv trong results
    all_files = glob.glob(os.path.join(input_dir, "*.tsv"))
    if not all_files:
        print(f"Không tìm thấy file tại: {input_dir}")
        return

    all_data = []

    for file_path in all_files:
        sample_name = os.path.basename(file_path).replace("_report.plus.tsv", "")
        try:
            df = pd.read_csv(file_path, sep='\t')
            
            # Xử lý các gene dựa trên Subclass
            def classify_drug(row):
                subclass = str(row['Subclass']).upper() if pd.notna(row['Subclass']) else "NAN"
                
                # Nếu Subclass trống
                if subclass == "NAN" or subclass.strip() == "":
                    return "-"
                
                # Kiểm tra việc ánh xạ các thuốc chính
                for key, display in main_drugs_mapping.items():
                    if key in subclass:
                        return display
                
                # Liệt kê các thuốc không có trong các thuốc chính
                return subclass.capitalize()

            df['Drug_Group'] = df.apply(classify_drug, axis=1)
            
            # Chỉ lấy các cột cần thiết
            temp_df = df[['Drug_Group', 'Element symbol']].copy()
            temp_df['Sample'] = sample_name
            all_data.append(temp_df)
            
        except Exception as e:
            print(f"Lỗi file {sample_name}: {e}")

    if not all_data: return

    # Hợp nhất dữ liệu
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Gom nhóm gene
    summary = combined_df.groupby(['Sample', 'Drug_Group'])['Element symbol'].apply(
        lambda x: ', '.join(sorted(set(x)))
    ).reset_index()

    # Tạo bảng Pivot
    pivot_table = summary.pivot(index='Sample', columns='Drug_Group', values='Element symbol').fillna('-')

    # Đảm bảo các cột thuốc chính LUÔN XUẤT HIỆN và dấu '-' nếu trống
    for drug in main_drug_names:
        if drug not in pivot_table.columns:
            pivot_table[drug] = '-'

    # Sắp xếp thứ tự cột: Thuốc chính -> Các thuốc khác
    other_cols = [c for c in pivot_table.columns if c not in main_drug_names and c != "-"]
    sorted_cols = main_drug_names + (["-"] if "-" in pivot_table.columns else []) + sorted(other_cols)
    
    final_table = pivot_table[sorted_cols]

    # Xuất kết quả
    final_table.to_csv(output_path)
    print(f"Results in path: {output_path}")
    return final_table

# ==========================================
# CÀI ĐẶT ĐƯỜNG DẪN TẠI ĐÂY
# ==========================================
if __name__ == "__main__":
    # Thay đổi đường dẫn thư mục input và file output của bạn
    MY_INPUT = "/data18tb/datnguyen/Tran_AMR/results"  # Thư mục chứa 5 file tsv
    MY_OUTPUT = "Table_1.csv"

    create_amr_summary(MY_INPUT, MY_OUTPUT)