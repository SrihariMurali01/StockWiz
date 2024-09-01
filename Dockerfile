# Step 1: Use an official Python runtime as a parent image
FROM python:3.10-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Step 4: Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the current directory contents into the container at /app
COPY . /app/

# Step 6: Install python-dotenv to manage environment variables
RUN pip install python-dotenv

# Step 7: Expose ports for Flask (5000) and Streamlit (8501)
EXPOSE 5000
EXPOSE 8501

# Step 8: Load environment variables from the .env file and run both applications
CMD ["sh", "-c", "python -m dotenv run -- python run.py & streamlit run app.py & wait"]
