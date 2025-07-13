#!/usr/bin/env python3
"""
RAG Experiment Automation Pipeline
Grid search for chunking, top-k, and temperature parameters
"""

import os
import csv
import time
import argparse
import itertools
from datetime import datetime
from typing import List, Dict, Any
import uuid

import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Base directory setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "experiments", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Default experiment parameters
DEFAULT_CHUNK_SIZES = [256, 512]
DEFAULT_TOP_KS = [3, 5, 8]
DEFAULT_TEMPERATURES = [0.2, 0.5, 0.8]

# Test questions (AI topic)
TEST_QUESTIONS = [
    "Who coined the term 'artificial intelligence'?",
    "What is the Turing Test?",
    "How does machine learning work?",
    "What are neural networks?",
    "Explain deep learning in simple terms"
]

def get_embeddings(texts: List[str]) -> np.ndarray:
    """Get embeddings for a list of texts using OpenAI API"""
    embeddings = []
    for text in texts:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        embeddings.append(response.data[0].embedding)
    return np.array(embeddings)

def chunk_text(text: str, chunk_size: int) -> List[str]:
    """Split text into chunks using RecursiveCharacterTextSplitter"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_size // 4,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return text_splitter.split_text(text)

def create_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """Create and return a Faiss index for similarity search"""
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    index.add(embeddings.astype('float32'))
    return index

def search_similar_chunks(query_embedding: np.ndarray, index: faiss.IndexFlatIP, top_k: int) -> tuple:
    """Search for similar chunks using Faiss"""
    query_embedding = query_embedding.astype('float32').reshape(1, -1)
    scores, indices = index.search(query_embedding, top_k)
    return scores[0], indices[0]

def generate_answer(context: str, question: str, temperature: float) -> str:
    """Generate answer using OpenAI GPT"""
    prompt = f"""Based on the following context, answer the question:

Context:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant. Answer based only on the provided context."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=300
    )
    answer = response.choices[0].message.content
    return answer if answer else "No response generated"

def calculate_recall_at_5(relevant_chunks: List[str], retrieved_chunks: List[str]) -> float:
    """Calculate recall@5 (simplified version)"""
    if not relevant_chunks:
        return 0.0
    
    # For simplicity, we'll consider chunks containing key terms as relevant
    relevant_terms = ["AI", "artificial intelligence", "machine learning", "neural", "turing"]
    relevant_count = 0
    
    for chunk in retrieved_chunks[:5]:
        if any(term.lower() in chunk.lower() for term in relevant_terms):
            relevant_count += 1
    
    return relevant_count / min(5, len(relevant_chunks))

def calculate_f1_score(precision: float, recall: float) -> float:
    """Calculate F1 score"""
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

def run_single_experiment(
    run_id: str,
    chunk_size: int,
    top_k: int,
    temperature: float,
    question: str,
    chunks: List[str],
    chunk_embeddings: np.ndarray,
    faiss_index: faiss.IndexFlatIP
) -> Dict[str, Any]:
    """Run a single experiment and return results"""
    
    start_time = time.time()
    
    # Get query embedding
    query_embedding = get_embeddings([question])[0]
    
    # Search for similar chunks
    scores, indices = search_similar_chunks(query_embedding, faiss_index, top_k)
    retrieved_chunks = [chunks[i] for i in indices]
    
    # Generate answer
    context = "\n\n".join(retrieved_chunks)
    answer = generate_answer(context, question, temperature)
    
    # Calculate metrics
    latency_ms = (time.time() - start_time) * 1000
    
    # Simplified evaluation (in real scenario, you'd have ground truth)
    recall_at_5 = calculate_recall_at_5(retrieved_chunks, retrieved_chunks)
    precision = recall_at_5  # Simplified
    f1 = calculate_f1_score(precision, recall_at_5)
    
    # Estimate cost (rough calculation)
    input_tokens = len(context.split()) + len(question.split())
    output_tokens = len(answer.split())
    cost_cents = (input_tokens * 0.0000015 + output_tokens * 0.000002) * 100
    
    return {
        "run_id": run_id,
        "chunk": chunk_size,
        "k": top_k,
        "temp": temperature,
        "recall@5": round(recall_at_5, 4),
        "f1": round(f1, 4),
        "latency_ms": round(latency_ms, 2),
        "cost_cents": round(cost_cents, 4)
    }

def main():
    parser = argparse.ArgumentParser(description="RAG Experiment Automation")
    parser.add_argument("--k", type=int, nargs="+", default=DEFAULT_TOP_KS,
                       help="Top-k values for retrieval")
    parser.add_argument("--temp", type=float, nargs="+", default=DEFAULT_TEMPERATURES,
                       help="Temperature values for generation")
    parser.add_argument("--chunk", type=int, nargs="+", default=DEFAULT_CHUNK_SIZES,
                       help="Chunk sizes for text splitting")
    
    args = parser.parse_args()
    
    print(f"Starting RAG experiments with:")
    print(f"  Top-k values: {args.k}")
    print(f"  Temperature values: {args.temp}")
    print(f"  Chunk sizes: {args.chunk}")
    
    # Load text data
    text_file = os.path.join(DATA_DIR, "text_chunks.txt")
    if not os.path.exists(text_file):
        print(f"Error: {text_file} not found. Please ensure the data file exists.")
        return
    
    with open(text_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Prepare results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(RESULTS_DIR, f"grid_search_{timestamp}.csv")
    
    # CSV headers as specified by mentor
    fieldnames = ["run_id", "chunk", "k", "temp", "recall@5", "f1", "latency_ms", "cost_cents"]
    
    with open(results_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Run experiments for each chunk size
        for chunk_size in args.chunk:
            print(f"\nProcessing chunk size: {chunk_size}")
            
            # Chunk the text
            chunks = chunk_text(text, chunk_size)
            print(f"Created {len(chunks)} chunks")
            
            # Get embeddings for chunks
            print("Getting embeddings for chunks...")
            chunk_embeddings = get_embeddings(chunks)
            
            # Create Faiss index
            print("Creating Faiss index...")
            faiss_index = create_faiss_index(chunk_embeddings)
            
            # Run experiments for all parameter combinations
            total_experiments = len(args.k) * len(args.temp) * len(TEST_QUESTIONS)
            experiment_count = 0
            
            for top_k in args.k:
                for temperature in args.temp:
                    for question in TEST_QUESTIONS:
                        experiment_count += 1
                        run_id = str(uuid.uuid4())[:8]
                        
                        print(f"Running experiment {experiment_count}/{total_experiments}: "
                              f"k={top_k}, temp={temperature}, chunk={chunk_size}")
                        
                        try:
                            result = run_single_experiment(
                                run_id=run_id,
                                chunk_size=chunk_size,
                                top_k=top_k,
                                temperature=temperature,
                                question=question,
                                chunks=chunks,
                                chunk_embeddings=chunk_embeddings,
                                faiss_index=faiss_index
                            )
                            writer.writerow(result)
                            
                        except Exception as e:
                            print(f"Error in experiment: {e}")
                            # Write error result
                            error_result = {
                                "run_id": run_id,
                                "chunk": chunk_size,
                                "k": top_k,
                                "temp": temperature,
                                "recall@5": 0.0,
                                "f1": 0.0,
                                "latency_ms": 0.0,
                                "cost_cents": 0.0
                            }
                            writer.writerow(error_result)
    
    print(f"\nExperiments completed! Results saved to: {results_file}")
    print(f"Total experiments run: {experiment_count}")

if __name__ == "__main__":
    main() 