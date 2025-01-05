# Use an official Python image as the base
FROM python:3.10-slim

# Install LaTeX and other dependencies
RUN apt-get update && apt-get install -y \
    texlive \
    texlive-latex-extra \
    texlive-pictures \
    texlive-science \
    texlive-fonts-recommended \
    texlive-xetex \
    dvipng \
    pdftk \
    poppler-utils \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Set the command to run the app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
