from pathlib import Path
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..config import CHUNK_SIZE, CHUNK_OVERLAP, FILE_TO_SPORT_MAPPING, PROCESSED_DATA_DIR
from .cleaner import clean_text, extract_structure_metadata, flatten_metadata
from .hierarchy import create_parent_child_data

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
        Returns: (chunks_list, parent_doc_or_None)
        """
        filename = filepath.name
        
        # Check mapping
        if filename not in FILE_TO_SPORT_MAPPING:
            print(f"⚠️ Skipping {filename}: Not in FILE_TO_SPORT_MAPPING")
            return [], None

        mapping = FILE_TO_SPORT_MAPPING[filename]
        is_multi = mapping["is_multi_sport"]
        
        # === H ierarchical Logic (New) ===
        if is_multi:
            # Use hierarchy module to get Parent + Children
            parent_doc, children_chunks = create_parent_child_data(filepath)
            if parent_doc and children_chunks:
                print(f"   👨‍👧 Created Parent-Child data for {filename}")
                return children_chunks, parent_doc

        # === Normal Flat Logic ===
        sports_list = mapping["sports"]
        sport_string = ", ".join(sports_list)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
            return [], None

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
            
        return chunk_data, None

    def process_directory(self, input_dir: Path):
        """
        Process all matching files in a directory.
        """
        all_chunks = []
        all_parents = {}
        
        input_path = Path(input_dir)
        
        # Look for both .md and .markdown just in case
        files = list(input_path.glob("final_*.md"))
        
        print(f"📂 Found {len(files)} files to process in {input_dir}")
        
        for filepath in files:
            print(f"📄 Processing {filepath.name}...")
            chunks, parent = self.process_file(filepath)
            
            if chunks:
                all_chunks.extend(chunks)
                print(f"   ✅ Generated {len(chunks)} chunks")
            
            if parent:
                all_parents[parent['id']] = parent
                print(f"   ✅ Collected Parent: {parent['id']}")
            
        # Save parents to JSON
        if all_parents:
            parents_path = PROCESSED_DATA_DIR / "parents.json"
            print(f"💾 Saving {len(all_parents)} parents to {parents_path}")
            with open(parents_path, 'w', encoding='utf-8') as f:
                json.dump(all_parents, f, ensure_ascii=False, indent=2)
                
        return all_chunks
