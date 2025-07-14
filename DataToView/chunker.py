import os

def split_jsonl_file(input_path, max_size_bytes=1_000_000_000): #1 gig per file
    print("Chunking file...")
    part_num = 1
    current_size = 0
    output_file = open(f"{input_path}_part{part_num}.jsonl", "w", encoding="utf-8")

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line_size = len(line.encode("utf-8"))
            if current_size + line_size > max_size_bytes:
                output_file.close()
                part_num += 1
                current_size = 0
                output_file = open(f"{input_path}_part{part_num}.jsonl", "w", encoding="utf-8")
            output_file.write(line)
            print(f"Writing to file: {input_path}_part{part_num}.jsonl")
            current_size += line_size
    output_file.close()

split_jsonl_file("monks_data.jsonl")