import pandas as pd
import glob
import os

def create_gene_centric_table(input_dir, output_path):
    Tìm kiếm file
    all_files = glob.glob(os.path.join(input_dir, "*.tsv"))
    if not all_files:
        print(f"Không tìm thấy file tại: {input_dir}")
        return

    # Danh sách mapping thuốc
    drug_mapping = {
        'RIFAMPICIN': 'RIF',
        'ISONIAZID': 'INH',
        'FLUOROQUINOLONE': 'LEV',
        'ETHAMBUTOL': 'EMB',
        'LINEZOLID': 'Linezolid',
        'OXAZOLIDINONE': 'Oxazolidinone',
        'BEDAQUILINE': 'Bedaquiline'
    }

    def clean_drug_name(subclass):
        if pd.isna(subclass) or str(subclass).strip() == "":
            return "-"
        name = str(subclass).upper()
        for key, display in drug_mapping.items():
            if key in name:
                return display
        return subclass 

    all_data = []

    # Đọc và xử lý từng file
    for file_path in all_files:
        sample_name = os.path.basename(file_path).replace(".tsv", "")
        try:
            df = pd.read_csv(file_path, sep='\t')
            
            # Chuẩn hóa tên thuốc
            df['Clean_Drug'] = df['Subclass'].apply(clean_drug_name)
            
            # Chọn cột Gene và Thuốc
            temp_df = df[['Element symbol', 'Clean_Drug']].copy()
            temp_df['Sample'] = sample_name
            all_data.append(temp_df)
        except Exception as e:
            print(f"Lỗi xử lý file {sample_name}: {e}")

    if not all_data:
        return

    # Tổng hợp dữ liệu
    combined_df = pd.concat(all_data, ignore_index=True)

    # Gom các loại thuốc lại nếu một Gene kháng nhiều loại (ngăn cách bằng dấu phẩy)
    # Ví dụ: Gene A kháng RIF, INH
    summary = combined_df.groupby(['Sample', 'Element symbol'])['Clean_Drug'].apply(
        lambda x: ', '.join(sorted(set(x)))
    ).reset_index()

    # Xoay bảng: Mẫu làm hàng, Gene làm cột
    pivot_table = summary.pivot(index='Sample', columns='Element symbol', values='Clean_Drug').fillna('-')

    # Xuất kết quả
    pivot_table.to_csv(output_path)
    print(f"Successful results!")
    print(f"Ouput path: {output_path}")
    
    return pivot_table

# ==========================================
# CÀI ĐẶT ĐƯỜNG DẪN TẠI ĐÂY
# ==========================================
if __name__ == "__main__":
    # Đường dẫn thư mục chứa file tsv
    INPUT_PATH = "/data18tb/datnguyen/Tran_AMR/results" 
    
    # Đường dẫn file kết quả
    OUTPUT_FILE = "Table_2.csv"

    create_gene_centric_table(INPUT_PATH, OUTPUT_FILE)