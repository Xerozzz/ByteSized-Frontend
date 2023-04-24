# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, flash, send_file
from flask_login import (
    current_user,
    login_required
)
from jinja2 import TemplateNotFound
from apps import login_manager
import requests
import qrcode
from PIL import Image
import io

@blueprint.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
    res = requests.get(f"http://localhost:5000/{current_user.username}/stats")
    data = res.json()
    clicks = 0
    for i in data:
        clicks += i["clicks"]
    stats = {
        "data": data,
        "links": len(data),
        "clicks": clicks
    }
    return render_template('home/index.html', segment='index', stats = stats)

@blueprint.route('/QR', methods = ['GET', 'POST'])
@login_required
def QR():
    if request.method == "POST":
        pass
    return render_template('home/QR.html')


@blueprint.route('/qrmake', methods=['POST'])
def qrmake():
    file = request.files['file'].read()
    link = request.form['link']

    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    # taking url or text
    url = link
    # adding URL or text to QRcode
    QRcode.add_data(url)
    # generating QR code
    QRcode.make()
    # taking color name from user
    QRcolor = 'black'
    # adding color to QR code
    QRimg = QRcode.make_image(
        fill_color=QRcolor, back_color="white").convert('RGB')

    try:
        # convert bytes to image
        logo = Image.open(io.BytesIO(file))

        # taking base width
        basewidth = 60

        # adjust image size
        wpercent = (basewidth/float(logo.size[0]))
        hsize = int((float(logo.size[1])*float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)

        # set size of QR code
        pos = ((QRimg.size[0] - logo.size[0]) // 2,
            (QRimg.size[1] - logo.size[1]) // 2)
        QRimg.paste(logo, pos)
    
    except:
        pass
    
    # create an in-memory buffer to store the image data
    img_buffer = io.BytesIO()
    # save the QR code generated to the buffer
    QRimg.save(img_buffer, format='PNG')
    # move the buffer's position to the start
    img_buffer.seek(0)

    # return the image data as a response
    return send_file(
        img_buffer,
        mimetype='image/png',
        as_attachment=True,
        download_name="qr.png"
    )

@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
