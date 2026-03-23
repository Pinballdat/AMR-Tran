import os
import glob

def combine_tab_files(directory, output_file):
    # Pattern to match all .tab files
    tab_files = glob.glob(os.path.join(directory, "*.tab"))
    
    # Filter out the output file itself if it exists in the directory
    tab_files = [f for f in tab_files if os.path.basename(f) != output_file]
    
    if not tab_files:
        print("No .tab files found to combine.")
        return

    # Updated header: Renamed #FILE to SAMPLE, removed RESISTANCE and COVERAGE_MAP
    target_header = "SAMPLE\tSEQUENCE\tSTART\tEND\tSTRAND\tGENE\t%COVERAGE\t%IDENTITY\tDATABASE\tACCESSION\tPRODUCT"
    
    output_path = os.path.join(directory, output_file)
    print(f"Writing to {output_path}...")
    
    with open(output_path, 'w') as outfile:
        outfile.write(target_header + "\n")
        
        for filename in sorted(tab_files):
            print(f"Processing {filename}...")
            with open(filename, 'r') as infile:
                for line in infile:
                    # Skip the header lines from source files (which start with #FILE)
                    if line.startswith("#FILE"):
                        continue
                    # Skip empty lines
                    if not line.strip():
                        continue
                    
                    # Split the line by tabs
                    parts = line.strip('\n').split('\t')
                    
                    if len(parts) < 14:
                        continue
                        
                    # 1. Fix FILE column (index 0)
                    file_val = parts[0]
                    file_val = os.path.basename(file_val).replace("_assembly.fasta", "").replace("__", "_")
                    parts[0] = file_val
                    
                    # 2. Remove COVERAGE_MAP (index 7) and RESISTANCE (index 14+)
                    # Keep indices: 0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13
                    indices_to_keep = [0, 1, 2, 3, 4, 5, 9, 10, 11, 12, 13]
                    new_parts = [parts[i] for i in indices_to_keep]
                    
                    # Join and write
                    outfile.write("\t".join(new_parts) + "\n")
                    
    print(f"Successfully combined {len(tab_files)} files into {output_file}")

if __name__ == "__main__":
    work_dir = "/data18tb/datnguyen/Tran_AMR/VF_genes/"
    summary_filename = "summary.tab"
    combine_tab_files(work_dir, summary_filename)
