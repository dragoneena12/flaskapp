#!/usr/bin/python
# -*- coding: utf-8 -*-

# [Import start]
from flask import Flask, render_template, request, send_from_directory
import os
from werkzeug import secure_filename
import cv2
import pickle
import glob
# [Import end]

app = Flask(__name__, template_folder='./templates')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])
UPLOAD_FOLDER = './ownerdata/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def top():
    return render_template("index.html")

@app.route('/owner')
def owner():
    return render_template("owner.html")

@app.route('/owner/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        img_file = request.files['img_file']
        if img_file and allowed_file(img_file.filename):
            filename = secure_filename(img_file.filename)
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_url = '/ownerdata/' + filename
            orb = cv2.ORB_create()
            img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename), 0)
            # find the keypoints with ORB
            kp = orb.detect(img,None)
            # compute the descriptors with ORB
            kp, des_up = orb.compute(img, kp)
            matchdata = []
            files = glob.glob("./ownerdata/csv/*")
            for file in files:
                data = []
                des = []
                with open(file, 'rb') as f:
                    name, ownerid, des = pickle.load(f)
                    data.append(name)
                    data.append(ownerid)
                bf = cv2.BFMatcher()
                matches = bf.knnMatch(des_up, des, k=2)
                ratio = 0.5
                goodnum = 0
                for m, n in matches:
                    if m.distance < ratio * n.distance:
                        goodnum += 1
                data.append(goodnum)
                matchdata.append(data)        
            return render_template('owner.html', sdatas = matchdata)
        else:
            return ''' <p>許可されていない拡張子です</p> '''
    else:
        return redirect(url_for('index'))

@app.route('/owner/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        img_file = request.files['img_file']
        if img_file and allowed_file(img_file.filename):
            filename = secure_filename(img_file.filename)
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_url = '/ownerdata/' + filename

            orb = cv2.ORB_create()
            img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename), 0)
            # find the keypoints with ORB
            kp = orb.detect(img,None)
            # compute the descriptors with ORB
            kp, des = orb.compute(img, kp)
            # draw only keypoints location,not size and orientation
            img2 = cv2.drawKeypoints(img,kp,None,color=(0,255,0), flags=0)
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], + name + ownerid + "keyed.png"), img2)

            name = request.form['charaname']
            ownerid = request.form['twitterid']

            index = []
            index.append((name, ownerid))
            for p in des:
                index.append(p)
            with open('./ownerdata/csv/' + name + ownerid + '.pickle', mode='wb') as f:
                pickle.dump((name, ownerid, des), f)

            return render_template('owner.html', img_url='/ownerdata/' + name + ownerid + 'keyed.png')
        else:
            return ''' <p>許可されていない拡張子です</p> '''
    else:
        return redirect(url_for('index'))

@app.route('/owner/datashow', methods=['GET', 'POST'])
def datashow():
    if request.method == 'POST':
        datas = []
        files = glob.glob("./ownerdata/csv/*")
        for file in files:
            with open(file, 'rb') as f:
                name, ownerid, des = pickle.load(f)
                datas.append((name, ownerid))
        return render_template('owner.html', datas = datas)
    else:
        return redirect(url_for('index'))

@app.route('/ownerdata/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run()
