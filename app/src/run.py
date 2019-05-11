#!/usr/bin/python
# -*- coding: utf-8 -*-

# [Import start]
from flask import Flask, render_template, request, send_from_directory
import os
from werkzeug import secure_filename
import cv2
import pickle
import glob
from operator import itemgetter
# [Import end]

app = Flask(__name__, template_folder='./templates')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])
UPLOAD_FOLDER = './ownerdata/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
M = 400 #resize

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
        if img_file:
            filename = secure_filename(img_file.filename)
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_url = '/ownerdata/' + filename
            orb = cv2.ORB_create()
            img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename), 0)
            orig_width = img.shape[1]
            orig_height = img.shape[0]
            (target_width, target_height) = (M, orig_height * M // orig_width) if orig_width > orig_height else (orig_width * M // orig_height, M)
            img = cv2.resize(img, dsize=(target_height, target_width))
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
                    datnum, name, ownerid, des = pickle.load(f)
                    data.append(name)
                    data.append(ownerid)
                bf = cv2.BFMatcher()
                matches = bf.knnMatch(des_up, des, k=2)
                ratio = 0.75
                goodnum = 0
                for m, n in matches:
                    if m.distance < ratio * n.distance:
                        goodnum += 1
                data.append(goodnum)
                matchdata.append(data)        
            matchdata.sort(key=itemgetter(2), reverse=True)
            return render_template('owner.html', sdatas = matchdata[:10])
        else:
            return ''' <p>許可されていない拡張子です</p> '''
    else:
        return redirect(url_for('index'))

@app.route('/owner/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        img_file = request.files['img_file']
        if img_file:
            filename = secure_filename(img_file.filename)
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_url = '/ownerdata/' + filename

            orb = cv2.ORB_create()
            img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename), 0)
            orig_width = img.shape[1]
            orig_height = img.shape[0]
            (target_width, target_height) = (M, orig_height * M // orig_width) if orig_width > orig_height else (orig_width * M // orig_height, M)
            img = cv2.resize(img, dsize=(target_height, target_width))
            # find the keypoints with ORB
            kp = orb.detect(img,None)
            # compute the descriptors with ORB
            kp, des = orb.compute(img, kp)
            # draw only keypoints location,not size and orientation
            img2 = cv2.drawKeypoints(img,kp,None,color=(0,255,0), flags=0)
            

            name = request.form['charaname']
            ownerid = request.form['twitterid']
            
            if not os.path.exists('./ownerdata/datanum.dat'):
                with open('./ownerdata/datanum.dat', mode='wb') as f:
                    pickle.dump(0, f)
            with open('./ownerdata/datanum.dat', mode='rb') as f:
                datnum = pickle.load(f)
                os.remove('./ownerdata/datanum.dat')
            with open('./ownerdata/datanum.dat', mode='wb') as f:
                pickle.dump(datnum + 1, f)

            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], str(datnum) + "_keyed.png"), img2)
            with open('./ownerdata/csv/' + str(datnum) + '.pickle', mode='wb') as f:
                pickle.dump((datnum, name, ownerid, des), f)

            return render_template('owner.html', img_url='/ownerdata/' + str(datnum) + '_keyed.png')
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
                datnum, name, ownerid, des = pickle.load(f)
                datas.append((datnum, name, ownerid))
        return render_template('owner.html', datas = datas)
    else:
        return redirect(url_for('index'))

@app.route('/ownerdata/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run()
