import os
import uuid
import logging
from typing import Union

from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from google.cloud import storage

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




@app.errorhandler(500)
def server_error(e: Union[Exception, int]) -> str:
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        # Create a Cloud Storage client.
        gcs = storage.Client()

        # Get the bucket that the file will be uploaded to.
        bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

        # Create a new blob and upload the file's content.
        blob = bucket.blob(uploaded_file.filename)

        blob.upload_from_string(
            uploaded_file.read(),
            content_type=uploaded_file.content_type
        )

        # Make the blob public. This is not necessary if the
        # entire bucket is public.
        # See https://cloud.google.com/storage/docs/access-control/making-data-public.
        blob.make_public()

        # The public URL can be used to directly access the uploaded file via HTTP.
        # return blob.public_url

        #TODO: replace file. with blob. ???

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
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
