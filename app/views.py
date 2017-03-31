from . import main
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from forms import DeviceForm
from .models import User, Device

@main.route('/hello')
def hello_world():
    return render_template('hello.html')

@main.route('/')
@main.route('/index')
@login_required
def index():
    if current_user.is_authenticated:
        user = {'name': current_user.name}
    else:
        user = {'name': 'guest'}
    return render_template("index.html", title='ITIL Test', user=user)

@main.route('/adddevice', methods=['GET', 'POST'])
@login_required
def adddevice():
    form = DeviceForm(request.form)
    if request.method == 'POST':
        if form.validate():
            dev = Device.find(name=form.name.data)
            if dev:
                flash("Device({0}) \"{1}\" already exists!".format(dev.uuid, dev.name))
            else:
                dev = Device(name=form.name.data, model=form.model.data, warranty=form.warranty.data,
                             serial_num=form.serial_num.data, status=form.status.data).save()
                return redirect(url_for('devices'))
        else:
            flash("Invalid input data!")
    return render_template('device.html', title='Add Device', form=form)
