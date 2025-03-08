# Use an official Python image
FROM python:3.9.1

# Set the working directory
WORKDIR /app

# Copy files to the container
COPY . /app

# Install dependencies
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-dotenv


# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations
RUN python manage.py migrate

# Expose port 8000
EXPOSE 8000

# Start the app using Gunicorn
CMD ["gunicorn", "PBackend.wsgi:application", "--bind", "0.0.0.0:8000"]
