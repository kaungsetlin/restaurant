def allowed_file(filename):
    extensions = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def to_int(checkbox):
    if checkbox == 'on':
        return str(1)
    elif not checkbox:
        return str(0)
    else: return checkbox

