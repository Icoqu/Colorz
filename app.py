import base64
import os

from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import FileField, SelectField, SubmitField
from wtforms.validators import DataRequired

from colorz import k_means, dominant_colour


app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(12).hex()
Bootstrap(app)


class FileForm(FlaskForm):
    file = FileField('Image', [DataRequired()])
    analysis_option = SelectField('Algorithm', choices=['k-means', 'dominant'], default='dominant')
    if 'RECAPTCHA_PUBLIC_KEY' in app.config.keys():
        recaptcha = RecaptchaField()
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = FileForm()
    if form.validate_on_submit():
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            # filename = uploaded_file.filename
            if request.args.get('analysis_option') == 'k-means':
                rgbs = k_means(uploaded_file, 3)
            else:
                rgbs = dominant_colour(uploaded_file, 3)
            uploaded_file.seek(0)
            blob = request.files['file'].read()
            image_string = base64.b64encode(blob)
            return render_template('colours.html', image_string=image_string.decode("utf-8"), rgbs=rgbs, form=form)
    return render_template('colours.html', form=form)


if __name__ == '__main__':
    app.run()
