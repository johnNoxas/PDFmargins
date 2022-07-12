import os
import uuid

from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter, PdfMerger, PageObject

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def make_page(page: PageObject, left_margin: float, right_margin: float, top_margin: float, bottom_margin: float) -> PageObject:
    output = PageObject.createBlankPage(
        width=page.mediabox.width + left_margin + right_margin,
        height=page.mediabox.height + top_margin + bottom_margin
    )
    output.mergeTranslatedPage(page, left_margin, top_margin)
    return output


@app.route('/uploads/<name>')
def download_file(name):
    return


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        filename = "{0}_{2}{1}".format(
            *os.path.splitext(secure_filename(file.filename)) + (str(uuid.uuid4().clock_seq),))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            print('sex')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            left_margin, right_margin, top_margin, bottom_margin = \
            float(request.form['inputLM']), float(request.form['inputRM']), \
            float(request.form['inputTM']), float(request.form['inputBM'])
            reader = PdfReader(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            writer = PdfWriter()
            for page in reader.pages:
                output = make_page(page, left_margin, right_margin, top_margin, bottom_margin)
                writer.addPage(output)

            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as fh:
                writer.write(fh)

            return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
            # return redirect(url_for('download_file', name=filename))

    return render_template('home.html')


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(host="127.0.0.1", port=8080, debug=True)
