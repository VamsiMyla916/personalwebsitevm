# Use Python 3.9
FROM python:3.9

# Set the working directory inside the container
WORKDIR /code

# Copy requirements first (better for caching)
COPY ./requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application code
COPY ./app /code/app

# Run the app on port 7860 (Required for Hugging Face Spaces)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]