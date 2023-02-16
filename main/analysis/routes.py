from flask import render_template, url_for, redirect, Blueprint
from main.candidates.forms import UploadFileForm
from main.analysis.analysis import obtenerDF_Email

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route("/get_analysis", methods=['GET', 'POST'])
def get_analysis():
    form=UploadFileForm()
    # user_form = UserAdd()
    if form.validate_on_submit():
        ff = form.file.data.filename
        #return redirect('analysis', file=ff)
        return redirect(url_for('analysis.analysis', file=ff))
    return render_template('get_analysis.html',title='Obtener análisis',form=form)

@analysis_bp.route("/analysis/<string:file>", methods=['GET', 'POST'])
def analysis(file):
    ressume, email, phone = obtenerDF_Email(file)
    plot_img = url_for('static', filename='files/'+'resume_results.png')

    return render_template('analysis.html', tables=[ressume.to_html(classes='data')], titles=ressume.columns.values, file=file, plot_img=plot_img, email=email, phone=phone)
