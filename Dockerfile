# Use official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy all files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Cloud Run will listen on
ENV PORT=8080
EXPOSE 8080

# Run the Flask app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
