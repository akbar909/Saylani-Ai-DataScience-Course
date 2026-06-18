# Use a lightweight Python base image
FROM python:3.9-slim

# Set environment variables to prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user with UID 1000 (Hugging Face runs containers as UID 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set working directory inside the user's home folder
WORKDIR $HOME/app

# Copy requirements first to leverage Docker cache
COPY --chown=user:user requirements.txt .

# Install CPU-specific PyTorch (much smaller file size) and other dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=user:user . .

# Expose port 7860 (Hugging Face routes incoming traffic to port 7860)
EXPOSE 7860

# Start Uvicorn pointing to your app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
