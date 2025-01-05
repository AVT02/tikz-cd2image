from flask import Flask, render_template, request, send_file
import os
import subprocess
from pdf2image import convert_from_path

app = Flask(__name__)

def write_latex_file(tikz_code, output_filename="tikz_image.tex"):
    """
    Creates a LaTeX file from TikZ-CD code.
    """
    latex_template = r"""
    \documentclass[tikz,border=3.14mm]{standalone}
    \usepackage{tikz-cd}
    \usepackage{amsmath,amssymb,amsfonts,mathtools}
    \begin{document}
    """ + tikz_code + r"""
    \end{document}
    """
    with open(output_filename, "w") as f:
        f.write(latex_template)

def compile_latex(commands):
    """
    Compiles LaTeX commands and logs detailed errors if any.
    """
    for command in commands:
        process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode != 0:
            error_details = (
                f"Command: {command}\n"
                f"STDOUT: {process.stdout.decode()}\n"
                f"STDERR: {process.stderr.decode()}"
            )
            raise Exception(f"LaTeX compilation failed.\nDetails:\n{error_details}")
    return True

def generate_images(tikz_code, output_png="static/tikz_image.png", output_svg="static/tikz_image.svg", dpi=300):
    """
    Generates PNG and SVG images from TikZ-CD code.
    """
    # Process the TikZ-CD code: Replace newlines with spaces
    tikz_code = tikz_code.replace("\n", " ")

    # Write the LaTeX file
    write_latex_file(tikz_code)

    # Compile LaTeX to DVI (for SVG) and PDF (for PNG)
    try:
        compile_latex([
            "latex -interaction=nonstopmode tikz_image.tex",
            "pdflatex -interaction=nonstopmode tikz_image.tex"
        ])
    except Exception as e:
        raise Exception(f"Compilation failed: {str(e)}")

    # Generate SVG
    os.system(f"pdftocairo -svg tikz_image.pdf {output_svg}")

    # Generate PNG
    images = convert_from_path("tikz_image.pdf", dpi=dpi)
    images[0].save(output_png, "PNG")

    # Clean up intermediate files
    for ext in ["pdf", "aux", "log", "tex", "dvi"]:
        file_to_remove = f"tikz_image.{ext}"
        if os.path.exists(file_to_remove):
            os.remove(file_to_remove)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        tikz_code = request.form["tikz_code"].strip()
        try:
            generate_images(tikz_code)
            return render_template("result.html")
        except Exception as e:
            error_message = str(e)
            return render_template("index.html", error=error_message)
    return render_template("index.html")

@app.route("/download/<file_type>")
def download(file_type):
    if file_type == "png":
        return send_file("static/tikz_image.png", as_attachment=True)
    elif file_type == "svg":
        return send_file("static/tikz_image.svg", as_attachment=True)
    else:
        return "Invalid file type", 400

if __name__ == "__main__":
    app.run(debug=True)
