# core/matcher.py
import os
import numpy as np
import faiss
import google.generativeai as genai

def get_ranked_resumes(job_description_text, resumes):
    """
    Ranks resumes against a job description using Google AI embeddings.
    Args:
        job_description_text (str): The text of the job description.
        resumes (list): A list of Resume model objects.
    Returns:
        A list of tuples, where each tuple contains a resume object and its similarity score,
        ranked from highest to lowest score.
    """
    try:
        # Configure the Google AI client with the API key from environment variables
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("Error: GOOGLE_API_KEY environment variable not set.")
            return []
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error configuring Google AI: {e}")
        return []

    # Filter out resumes that have no extracted text
    valid_resumes = [r for r in resumes if r.extracted_text and r.extracted_text.strip()]
    if not valid_resumes:
        return []

    # --- 1. Generate Embeddings ---
    # Create embeddings for the job description and all valid resumes
    resume_texts = [resume.extracted_text for resume in valid_resumes]
    all_texts = [job_description_text] + resume_texts
    
    try:
        # Use the text-embedding model
        result = genai.embed_content(
            model="models/embedding-001",
            content=all_texts,
            task_type="RETRIEVAL_QUERY" # Use RETRIEVAL_DOCUMENT for documents
        )
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return []

    # Separate the job embedding from the resume embeddings
    job_embedding = np.array(result['embedding'][0]).reshape(1, -1)
    resume_embeddings = np.array(result['embedding'][1:])

    # --- 2. Calculate Similarity using FAISS ---
    # Create a FAISS index
    d = resume_embeddings.shape[1]  # Dimension of the vectors
    index = faiss.IndexFlatL2(d)
    index.add(resume_embeddings)

    # Search for the most similar resumes (k=number of resumes)
    k = len(valid_resumes)
    distances, indices = index.search(job_embedding, k)

    # --- 3. Rank and Return Results ---
    # The distances from FAISS are L2 distances, so lower is better.
    # We can convert this to a similarity score (0 to 1) for better readability.
    # A simple way is to normalize and invert.
    max_dist = np.max(distances)
    min_dist = np.min(distances)
    
    ranked_results = []
    for i in range(len(indices[0])):
        original_index = indices[0][i]
        dist = distances[0][i]
        
        # Normalize the distance to a 0-1 range and subtract from 1 for a similarity score
        # Handle the case where max_dist equals min_dist to avoid division by zero
        if (max_dist - min_dist) > 0:
            similarity_score = 1 - ((dist - min_dist) / (max_dist - min_dist))
        else:
            similarity_score = 1.0 # If all distances are the same, they are all equally similar
            
        ranked_results.append((valid_resumes[original_index], similarity_score))

    return ranked_results