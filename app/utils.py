"""Utility functions for the YouTube AI Assistant."""

import re
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(youtube_url: str) -> str:
    """
    Extract the transcript from a YouTube video.
    
    Args:
        youtube_url: YouTube video URL
        
    Returns:
        Full transcript text
    """
    # Extract video ID from URL
    video_id = extract_video_id(youtube_url)
    
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item['text'] for item in transcript_list])
        return transcript
    except Exception as e:
        raise Exception(f"Failed to fetch transcript: {str(e)}")


def extract_video_id(youtube_url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    return None


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += " " + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def ask_llm(context: str, question: str) -> str:
    """
    Get an answer from the LLM based on context and question.
    
    Args:
        context: Relevant context from the transcript
        question: User's question
        
    Returns:
        Answer from the LLM
    """
    from core.llm import LLM
    
    llm = LLM()
    prompt = f"""Based on the following context from a YouTube video transcript, answer the user's question.

Context:
{context}

Question: {question}

Answer:"""
    
    answer = llm.generate(prompt)
    return answer
