# Use an official Python runtime as the base image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy project files to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Run database migrations
RUN python manage.py migrate

# Expose the application port
EXPOSE 8000

# Start the Django application with Gunicorn
CMD ["gunicorn", "PBackend.wsgi:application", "--bind", "0.0.0.0:8000"]
