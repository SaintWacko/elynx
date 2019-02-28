import matplotlib
matplotlib.use('Agg')
import io
import base64
import pandas as pd
import numpy as np
from flask import (Flask,
                   flash,
                   request,
                   redirect,
                   send_from_directory,
                   render_template
                   )
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('results.html', results=process_file(file))
    return render_template('homepage.html')


def process_file(file):
    data = pd.read_csv(file)
    figures = {}
    for column in [col for col in data if np.issubdtype(data[col].dtype, np.number)]:
        figures[column] = create_figure(data, column)
    return figures


def create_figure(data, column):
    plt.clf()
    histo = data[column].plot.hist(bins=50)
    fig = histo.get_figure()
    canvas = FigureCanvas(fig)
    png_output = io.BytesIO()
    canvas.print_png(png_output)
    img64 = base64.b64encode(png_output.getvalue()).decode('ascii')
    return img64


if __name__ == '__main__':
    app.run(host='0.0.0.0')
