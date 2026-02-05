from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..config import CHUNK_SIZE, CHUNK_OVERLAP, FILE_TO_SPORT_MAPPING
from .cleaner import clean_text, extract_structure_metadata, flatten_metadata

class MarkdownChunker:
    def __init__(self, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", "。", ". ", " ", ""],
            length_function=len
        )

    def process_file(self, filepath: Path):
        """
        Process a single markdown file into chunks with metadata.
        """
        filename = filepath.name
        
        # Check mapping
        if filename not in FILE_TO_SPORT_MAPPING:
            print(f"⚠️ Skipping {filename}: Not in FILE_TO_SPORT_MAPPING")
            return []

        mapping = FILE_TO_SPORT_MAPPING[filename]
        sports_list = mapping["sports"]
        is_multi = mapping["is_multi_sport"]
        sport_string = ", ".join(sports_list)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
            return []

        clean_content = clean_text(content)
        chunks = self.splitter.split_text(clean_content)
        
        chunk_data = []
        file_base = filename.replace("final_", "").replace(".md", "")

        for i, chunk in enumerate(chunks):
            # Reclean chunk just in case
            clean_ck = clean_text(chunk)
            struct_meta = extract_structure_metadata(clean_ck)
            
            metadata = {
                "sport": sport_string,
                "source_file": filename,
                "is_multi_sport": is_multi,
                "chunk_index": i,
                "total_chunks": len(chunks),
                **struct_meta
            }
            
            chunk_id = f"{file_base}_chunk_{i}"
            
            chunk_data.append({
                "chunk_id": chunk_id,
                "content": clean_ck,
                "metadata": metadata,
                "metadata_flat": flatten_metadata(metadata)
            })
            
        return chunk_data

    def process_directory(self, input_dir: Path):
        """
        Process all matching files in a directory.
        """
        all_chunks = []
        input_path = Path(input_dir)
        
        for filepath in input_path.glob("final_*.md"):
            print(f"📄 Chunking {filepath.name}...")
            chunks = self.process_file(filepath)
            all_chunks.extend(chunks)
            print(f"   ✅ Generated {len(chunks)} chunks")
            
        return all_chunks
