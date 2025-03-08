# user python official package
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app


# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Run gunicorn to serve the django app
CMD ["gunicorn", "PBackend.wsgi:application", "--bind", "0.0.0.0:8000"]


